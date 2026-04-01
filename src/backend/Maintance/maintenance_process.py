from db import get_db_connection


class MaintenanceProcessBackend:
	def __init__(self, user_id=None, username=None):
		self.user_id = user_id
		self.username = username

	def _db(self):
		return get_db_connection()

	def _safe_query(self, query, params=(), fetch_one=False):
		conn = None
		cursor = None
		try:
			conn = self._db()
			cursor = conn.cursor(dictionary=True)
			cursor.execute(query, params)
			if fetch_one:
				return cursor.fetchone()
			return cursor.fetchall()
		except Exception:
			return None
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()

	def get_maintenance_staff_id(self):
		if self.user_id is None:
			return None
		row = self._safe_query(
			"SELECT maintenance_staff_id FROM maintenance_staff WHERE user_id = %s",
			(self.user_id,),
			fetch_one=True,
		)
		return row.get("maintenance_staff_id") if row else None

	def get_assigned_work_orders(self):
		maintenance_staff_id = self.get_maintenance_staff_id()
		if maintenance_staff_id is None:
			return []

		rows = self._safe_query(
			"""
			SELECT
				m.request_id,
				a.apartment_number AS room,
				CONCAT(u.first_name, ' ', u.last_name) AS resident_name,
				m.description AS issue,
				m.status,
				m.reported_at,
				m.resolved_at
			FROM maintenance_requests m
			JOIN apartments a ON m.apartment_id = a.apartment_id
			JOIN tenants t ON m.tenant_id = t.tenant_id
			JOIN users u ON t.user_id = u.user_id
			WHERE m.assigned_to = %s
			ORDER BY m.reported_at DESC
			""",
			(maintenance_staff_id,),
		) or []

		for row in rows:
			row["id"] = f"MR-{row['request_id']}"
			row["reportedDate"] = row["reported_at"].strftime("%Y-%m-%d") if row.get("reported_at") else "-"
			row["completionDate"] = row["resolved_at"].strftime("%Y-%m-%d") if row.get("resolved_at") else "-"
		return rows

	def get_dashboard_stats(self):
		work_orders = self.get_assigned_work_orders()
		return {
			"new_requests": sum(1 for item in work_orders if item["status"] == "Pending"),
			"ongoing": sum(1 for item in work_orders if item["status"] == "In Progress"),
			"resolved": sum(1 for item in work_orders if item["status"] == "Resolved"),
		}

	def get_urgent_tasks(self, limit=3):
		tasks = [
			item for item in self.get_assigned_work_orders()
			if item["status"] in {"Pending", "In Progress"}
		]
		return tasks[:limit]

	def update_work_order_status(self, request_id, new_status):
		maintenance_staff_id = self.get_maintenance_staff_id()
		if maintenance_staff_id is None:
			return False, "Maintenance staff account is not linked to a staff record"

		conn = None
		cursor = None
		try:
			conn = self._db()
			cursor = conn.cursor()
			if new_status == "Resolved":
				cursor.execute(
					"""
					UPDATE maintenance_requests
					SET status = %s,
						resolved_at = NOW()
					WHERE request_id = %s AND assigned_to = %s
					""",
					(new_status, request_id, maintenance_staff_id),
				)
			else:
				cursor.execute(
					"""
					UPDATE maintenance_requests
					SET status = %s,
						resolved_at = NULL
					WHERE request_id = %s AND assigned_to = %s
					""",
					(new_status, request_id, maintenance_staff_id),
				)
			conn.commit()
			if cursor.rowcount == 0:
				return False, "Assigned work order not found"
			return True, f"Work order updated to {new_status}"
		except Exception as ex:
			if conn:
				conn.rollback()
			return False, str(ex)
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()
