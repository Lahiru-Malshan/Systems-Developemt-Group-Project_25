from datetime import datetime

from db import get_db_connection


DEFAULT_FRONTDESK_LOCATION_ID = 1


class FrontDeskBackend:
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

	def _get_frontdesk_staff_id(self):
		if self.user_id is None:
			return None
		row = self._safe_query(
			"SELECT frontdesk_staff_id FROM frontdesk_staff WHERE user_id = %s",
			(self.user_id,),
			fetch_one=True,
		)
		return row.get("frontdesk_staff_id") if row else None

	def get_location_id(self):
		if self.user_id is None:
			return DEFAULT_FRONTDESK_LOCATION_ID
		row = self._safe_query(
			"SELECT location_id FROM frontdesk_staff WHERE user_id = %s",
			(self.user_id,),
			fetch_one=True,
		)
		return row.get("location_id") if row else DEFAULT_FRONTDESK_LOCATION_ID

	def ensure_parcels_table(self):
		conn = None
		cursor = None
		try:
			conn = self._db()
			cursor = conn.cursor()
			cursor.execute(
				"""
				CREATE TABLE IF NOT EXISTS parcels (
					parcel_id INT NOT NULL AUTO_INCREMENT,
					apartment_id INT NOT NULL,
					tenant_id INT DEFAULT NULL,
					logged_by INT DEFAULT NULL,
					recipient_name VARCHAR(120) DEFAULT NULL,
					carrier VARCHAR(100) NOT NULL,
					storage_type ENUM('Standard','Cold/Food','Fragile/Large') DEFAULT 'Standard',
					note TEXT DEFAULT NULL,
					status ENUM('Pending','Picked Up') DEFAULT 'Pending',
					received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
					picked_up_at TIMESTAMP NULL DEFAULT NULL,
					PRIMARY KEY (parcel_id),
					KEY apartment_id (apartment_id),
					KEY tenant_id (tenant_id),
					KEY logged_by (logged_by),
					CONSTRAINT parcels_ibfk_1 FOREIGN KEY (apartment_id) REFERENCES apartments (apartment_id),
					CONSTRAINT parcels_ibfk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id),
					CONSTRAINT parcels_ibfk_2 FOREIGN KEY (logged_by) REFERENCES frontdesk_staff (frontdesk_staff_id)
				) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
				"""
			)

			cursor.execute(
				"""
				SELECT COUNT(*)
				FROM information_schema.COLUMNS
				WHERE TABLE_SCHEMA = DATABASE()
				  AND TABLE_NAME = 'parcels'
				  AND COLUMN_NAME = 'tenant_id'
				"""
			)
			has_tenant_column = cursor.fetchone()[0] > 0
			if not has_tenant_column:
				cursor.execute("ALTER TABLE parcels ADD COLUMN tenant_id INT DEFAULT NULL AFTER apartment_id")
				cursor.execute("ALTER TABLE parcels ADD KEY tenant_id (tenant_id)")

			cursor.execute(
				"""
				SELECT COUNT(*)
				FROM information_schema.TABLE_CONSTRAINTS
				WHERE TABLE_SCHEMA = DATABASE()
				  AND TABLE_NAME = 'parcels'
				  AND CONSTRAINT_NAME = 'parcels_ibfk_tenant'
				  AND CONSTRAINT_TYPE = 'FOREIGN KEY'
				"""
			)
			has_tenant_fk = cursor.fetchone()[0] > 0
			if not has_tenant_fk:
				cursor.execute(
					"ALTER TABLE parcels ADD CONSTRAINT parcels_ibfk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants (tenant_id)"
				)

			cursor.execute(
				"""
				UPDATE parcels p
				JOIN apartments a ON p.apartment_id = a.apartment_id
				JOIN lease_agreements la ON la.apartment_id = a.apartment_id AND la.status = 'Active'
				JOIN tenants t ON la.tenant_id = t.tenant_id
				JOIN users u ON t.user_id = u.user_id
				SET p.tenant_id = t.tenant_id
				WHERE p.tenant_id IS NULL
				  AND p.recipient_name IS NOT NULL
				  AND CONCAT(u.first_name, ' ', u.last_name) = p.recipient_name
				"""
			)
			conn.commit()
			return True
		except Exception:
			return False
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()

	def get_dashboard_stats(self):
		location_id = self.get_location_id()
		self.ensure_parcels_table()
		apartment_stats = self._safe_query(
			"""
			SELECT
				COUNT(*) AS total_units,
				SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_units,
				SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS vacant_units
			FROM apartments
			WHERE location_id = %s
			""",
			(location_id,),
			fetch_one=True,
		) or {}
		parcel_stats = self.get_parcel_stats()
		open_orders_row = self._safe_query(
			"""
			SELECT COUNT(*) AS open_orders
			FROM maintenance_requests m
			JOIN apartments a ON m.apartment_id = a.apartment_id
			WHERE a.location_id = %s
			  AND m.status IN ('Pending', 'In Progress')
			""",
			(location_id,),
			fetch_one=True,
		) or {}

		occupied_units = apartment_stats.get("occupied_units") or 0
		total_units = apartment_stats.get("total_units") or 0
		vacant_units = apartment_stats.get("vacant_units") or 0

		return {
			"occupied_units_label": f"{occupied_units}/{total_units}" if total_units else "0/0",
			"occupied_units": occupied_units,
			"vacant_units": vacant_units,
			"pending_parcels": parcel_stats.get("pending_count", 0),
			"received_today": parcel_stats.get("received_today", 0),
			"open_orders": open_orders_row.get("open_orders", 0),
		}

	def get_recent_open_orders(self, limit=5):
		location_id = self.get_location_id()
		rows = self._safe_query(
			f"""
			SELECT
				m.request_id,
				a.apartment_number,
				m.description,
				m.status,
				m.reported_at,
				CONCAT(u.first_name, ' ', u.last_name) AS resident_name
			FROM maintenance_requests m
			JOIN apartments a ON m.apartment_id = a.apartment_id
			JOIN tenants t ON m.tenant_id = t.tenant_id
			JOIN users u ON t.user_id = u.user_id
			WHERE a.location_id = %s
			  AND m.status IN ('Pending', 'In Progress')
			ORDER BY m.reported_at DESC
			LIMIT {int(limit)}
			""",
			(location_id,),
		) or []

		for row in rows:
			reported_at = row.get("reported_at")
			row["reported_label"] = reported_at.strftime("%Y-%m-%d") if reported_at else "Unknown"
		return rows

	def get_resident_directory(self):
		location_id = self.get_location_id()
		rows = self._safe_query(
			"""
			SELECT
				t.tenant_id,
				u.user_id,
				a.apartment_number AS room,
				CONCAT(u.first_name, ' ', u.last_name) AS name,
				'Tenant' AS type,
				COALESCE(u.phone_number, '') AS contact,
				COALESCE(u.email, '') AS email,
				a.status AS apartment_status,
				CASE
					WHEN a.apartment_number REGEXP '^[A-Za-z]' THEN UPPER(LEFT(a.apartment_number, 1))
					ELSE 'N/A'
				END AS block,
				u.created_at,
				la.start_date
			FROM lease_agreements la
			JOIN apartments a ON la.apartment_id = a.apartment_id
			JOIN tenants t ON la.tenant_id = t.tenant_id
			JOIN users u ON t.user_id = u.user_id
			WHERE a.location_id = %s
			  AND la.status = 'Active'
			  AND u.account_status = 'Active'
			ORDER BY a.apartment_number, u.first_name, u.last_name
			""",
			(location_id,),
		) or []
		return rows

	def get_resident_stats(self):
		location_id = self.get_location_id()
		apartment_stats = self._safe_query(
			"""
			SELECT
				SUM(CASE WHEN status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_units,
				SUM(CASE WHEN status = 'Available' THEN 1 ELSE 0 END) AS vacant_units
			FROM apartments
			WHERE location_id = %s
			""",
			(location_id,),
			fetch_one=True,
		) or {}

		residents = self.get_resident_directory()
		recent_residents = sorted(
			residents,
			key=lambda item: item.get("start_date") or item.get("created_at") or datetime.min,
			reverse=True,
		)[:3]

		return {
			"occupied_units": apartment_stats.get("occupied_units") or 0,
			"vacant_units": apartment_stats.get("vacant_units") or 0,
			"resident_count": len(residents),
			"recent_residents": recent_residents,
		}

	def get_apartment_options(self):
		location_id = self.get_location_id()
		rows = self._safe_query(
			"""
			SELECT DISTINCT a.apartment_number
			FROM apartments a
			JOIN lease_agreements la ON la.apartment_id = a.apartment_id AND la.status = 'Active'
			JOIN tenants t ON la.tenant_id = t.tenant_id
			JOIN users u ON t.user_id = u.user_id AND u.account_status = 'Active'
			WHERE a.location_id = %s
			ORDER BY a.apartment_number
			""",
			(location_id,),
		) or []
		return [row["apartment_number"] for row in rows]

	def get_apartment_residents(self, apartment_number):
		location_id = self.get_location_id()
		rows = self._safe_query(
			"""
			SELECT
				t.tenant_id,
				u.user_id,
				CONCAT(u.first_name, ' ', u.last_name) AS name,
				a.apartment_number AS room,
				u.phone_number,
				u.email
			FROM lease_agreements la
			JOIN apartments a ON la.apartment_id = a.apartment_id
			JOIN tenants t ON la.tenant_id = t.tenant_id
			JOIN users u ON t.user_id = u.user_id
			WHERE a.location_id = %s
			  AND a.apartment_number = %s
			  AND la.status = 'Active'
			  AND u.account_status = 'Active'
			ORDER BY u.first_name, u.last_name
			""",
			(location_id, apartment_number),
		) or []
		return rows

	def get_parcels(self, limit=None):
		self.ensure_parcels_table()
		location_id = self.get_location_id()
		limit_clause = f"LIMIT {int(limit)}" if limit is not None else ""
		rows = self._safe_query(
			f"""
			SELECT
				p.parcel_id,
				a.apartment_number AS room,
				p.tenant_id,
				p.carrier,
				p.storage_type AS type,
				p.status,
				p.note,
				p.recipient_name,
				p.received_at,
				p.picked_up_at,
				COALESCE(NULLIF(p.recipient_name, ''), CONCAT(tu.first_name, ' ', tu.last_name), recipients.resident_names, 'Unassigned') AS display_recipient
			FROM parcels p
			JOIN apartments a ON p.apartment_id = a.apartment_id
			LEFT JOIN tenants pt ON p.tenant_id = pt.tenant_id
			LEFT JOIN users tu ON pt.user_id = tu.user_id
			LEFT JOIN (
				SELECT
					la.apartment_id,
					GROUP_CONCAT(CONCAT(u.first_name, ' ', u.last_name) ORDER BY u.first_name, u.last_name SEPARATOR ', ') AS resident_names
				FROM lease_agreements la
				JOIN tenants t ON la.tenant_id = t.tenant_id
				JOIN users u ON t.user_id = u.user_id
				WHERE la.status = 'Active'
				  AND u.account_status = 'Active'
				GROUP BY la.apartment_id
			) AS recipients ON recipients.apartment_id = a.apartment_id
			WHERE a.location_id = %s
			ORDER BY p.received_at DESC
			{limit_clause}
			""",
			(location_id,),
		) or []

		for row in rows:
			received_at = row.get("received_at")
			if received_at:
				row["time"] = received_at.strftime("%I:%M %p")
				row["days"] = max((datetime.now() - received_at).days, 0)
			else:
				row["time"] = "Unknown"
				row["days"] = 0
		return rows

	def get_recent_parcels(self, limit=5):
		return self.get_parcels(limit=limit)

	def get_parcel_stats(self):
		self.ensure_parcels_table()
		location_id = self.get_location_id()
		row = self._safe_query(
			"""
			SELECT
				SUM(CASE WHEN p.status = 'Pending' THEN 1 ELSE 0 END) AS pending_count,
				SUM(CASE WHEN DATE(p.received_at) = CURDATE() THEN 1 ELSE 0 END) AS received_today,
				SUM(CASE WHEN p.status = 'Pending' AND TIMESTAMPDIFF(DAY, p.received_at, NOW()) >= 3 THEN 1 ELSE 0 END) AS overdue_count
			FROM parcels p
			JOIN apartments a ON p.apartment_id = a.apartment_id
			WHERE a.location_id = %s
			""",
			(location_id,),
			fetch_one=True,
		) or {}
		return {
			"pending_count": row.get("pending_count") or 0,
			"received_today": row.get("received_today") or 0,
			"overdue_count": row.get("overdue_count") or 0,
		}

	def create_parcel(self, apartment_number, carrier, storage_type="Standard", note=None, tenant_id=None, recipient_name=None):
		self.ensure_parcels_table()
		conn = None
		cursor = None
		try:
			location_id = self.get_location_id()
			residents = self.get_apartment_residents(apartment_number)
			resident_lookup = {resident["tenant_id"]: resident for resident in residents}
			if resident_lookup:
				if tenant_id is None:
					if len(resident_lookup) == 1:
						tenant_id = next(iter(resident_lookup))
					else:
						return False, "Select the tenant who should receive this parcel"
				elif tenant_id not in resident_lookup:
					return False, "Recipient tenant must be actively linked to the selected apartment"
				if not recipient_name:
					recipient_name = resident_lookup[tenant_id]["name"]

			apartment = self._safe_query(
				"SELECT apartment_id FROM apartments WHERE apartment_number = %s AND location_id = %s",
				(apartment_number, location_id),
				fetch_one=True,
			)
			if not apartment:
				return False, "Apartment not found for this front desk location"

			conn = self._db()
			cursor = conn.cursor()
			cursor.execute(
				"""
				INSERT INTO parcels (apartment_id, tenant_id, logged_by, recipient_name, carrier, storage_type, note, status)
				VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
				""",
				(
					apartment["apartment_id"],
					tenant_id,
					self._get_frontdesk_staff_id(),
					recipient_name or None,
					carrier,
					storage_type or "Standard",
					note or None,
				),
			)
			conn.commit()
			return True, "Parcel logged successfully"
		except Exception as ex:
			if conn:
				conn.rollback()
			return False, str(ex)
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()

	def get_maintenance_requests(self):
		location_id = self.get_location_id()
		rows = self._safe_query(
			"""
			SELECT
				m.request_id,
				a.apartment_number AS room,
				CONCAT(u.first_name, ' ', u.last_name) AS resident_name,
				m.description,
				m.status,
				m.reported_at,
				CONCAT(mu.first_name, ' ', mu.last_name) AS assigned_name,
				ms.maintenance_staff_id AS assigned_staff_id
			FROM maintenance_requests m
			JOIN apartments a ON m.apartment_id = a.apartment_id
			JOIN tenants t ON m.tenant_id = t.tenant_id
			JOIN users u ON t.user_id = u.user_id
			LEFT JOIN maintenance_staff ms ON m.assigned_to = ms.maintenance_staff_id
			LEFT JOIN users mu ON ms.user_id = mu.user_id
			WHERE a.location_id = %s
			ORDER BY m.reported_at DESC
			""",
			(location_id,),
		) or []

		for row in rows:
			reported_at = row.get("reported_at")
			row["id"] = f"MR-{row['request_id']}"
			row["date"] = reported_at.strftime("%Y-%m-%d") if reported_at else "Unknown"
			row["assigned_name"] = row.get("assigned_name") or "Unassigned"
		return rows

	def get_maintenance_staff_options(self):
		location_id = self.get_location_id()
		rows = self._safe_query(
			"""
			SELECT
				ms.maintenance_staff_id,
				CONCAT(u.first_name, ' ', u.last_name) AS name
			FROM maintenance_staff ms
			JOIN users u ON ms.user_id = u.user_id
			WHERE ms.location_id = %s
			  AND u.account_status = 'Active'
			ORDER BY u.first_name, u.last_name
			""",
			(location_id,),
		) or []
		return rows

	def create_maintenance_request(self, apartment_number, tenant_id, description):
		if not apartment_number or not tenant_id or not description:
			return False, "Apartment, tenant, and description are required"

		conn = None
		cursor = None
		try:
			location_id = self.get_location_id()
			apartment = self._safe_query(
				"SELECT apartment_id FROM apartments WHERE apartment_number = %s AND location_id = %s",
				(apartment_number, location_id),
				fetch_one=True,
			)
			if not apartment:
				return False, "Apartment not found for this front desk location"

			resident = self._safe_query(
				"""
				SELECT t.tenant_id
				FROM lease_agreements la
				JOIN apartments a ON la.apartment_id = a.apartment_id
				JOIN tenants t ON la.tenant_id = t.tenant_id
				JOIN users u ON t.user_id = u.user_id
				WHERE a.location_id = %s
				  AND a.apartment_number = %s
				  AND t.tenant_id = %s
				  AND la.status = 'Active'
				  AND u.account_status = 'Active'
				""",
				(location_id, apartment_number, tenant_id),
				fetch_one=True,
			)
			if not resident:
				return False, "Selected tenant is not linked to the apartment"

			conn = self._db()
			cursor = conn.cursor()
			cursor.execute(
				"""
				INSERT INTO maintenance_requests (tenant_id, apartment_id, description, status, reported_at)
				VALUES (%s, %s, %s, 'Pending', NOW())
				""",
				(tenant_id, apartment["apartment_id"], description),
			)
			conn.commit()
			return True, "Maintenance request logged successfully"
		except Exception as ex:
			if conn:
				conn.rollback()
			return False, str(ex)
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()

	def assign_maintenance_request(self, request_id, maintenance_staff_id):
		conn = None
		cursor = None
		try:
			conn = self._db()
			cursor = conn.cursor()
			cursor.execute(
				"""
				UPDATE maintenance_requests
				SET assigned_to = %s,
					status = 'In Progress'
				WHERE request_id = %s
				""",
				(maintenance_staff_id, request_id),
			)
			conn.commit()
			if cursor.rowcount == 0:
				return False, "Maintenance request not found"
			return True, "Maintenance request assigned"
		except Exception as ex:
			if conn:
				conn.rollback()
			return False, str(ex)
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()

	def update_maintenance_request_status(self, request_id, new_status):
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
					WHERE request_id = %s
					""",
					(new_status, request_id),
				)
			else:
				cursor.execute(
					"""
					UPDATE maintenance_requests
					SET status = %s,
						resolved_at = NULL
					WHERE request_id = %s
					""",
					(new_status, request_id),
				)
			conn.commit()
			if cursor.rowcount == 0:
				return False, "Maintenance request not found"
			return True, f"Maintenance request updated to {new_status}"
		except Exception as ex:
			if conn:
				conn.rollback()
			return False, str(ex)
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()

	def mark_parcel_picked_up(self, parcel_id):
		self.ensure_parcels_table()
		conn = None
		cursor = None
		try:
			conn = self._db()
			cursor = conn.cursor()
			cursor.execute(
				"""
				UPDATE parcels
				SET status = 'Picked Up', picked_up_at = NOW()
				WHERE parcel_id = %s
				""",
				(parcel_id,),
			)
			conn.commit()
			if cursor.rowcount == 0:
				return False, "Parcel not found"
			return True, "Parcel marked as picked up"
		except Exception as ex:
			if conn:
				conn.rollback()
			return False, str(ex)
		finally:
			if cursor:
				cursor.close()
			if conn:
				conn.close()
