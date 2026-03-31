
import traceback
from datetime import datetime, date
from typing import List, Dict

from db import get_db_connection


def _nice_date_and_days(ts: datetime) -> tuple[str, int]:
	if not ts:
		return "Unknown", 9999
	if isinstance(ts, date) and not isinstance(ts, datetime):
		ts = datetime.combine(ts, datetime.min.time())
	now = datetime.now()
	delta = now - ts
	days = delta.days
	if days <= 0:
		human = "Today"
	elif days == 1:
		human = "Yesterday"
	else:
		human = f"{days} days ago"
	return human, days


def fetch_notifications_for_user(user_id: int, limit: int = 50) -> List[Dict]:
	"""Return a list of notification dicts suitable for the UI.

	Each item contains: type, title, msg, date (human), days (int), unread (bool)
	"""
	try:
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		# Try to read an explicit notifications table if present
		try:
			cursor.execute(
				"""
				SELECT n.notification_id AS id,
					   COALESCE(n.category, n.type, 'General') AS type,
					   COALESCE(n.title, n.subject, '') AS title,
					   COALESCE(n.msg, n.message, n.content, '') AS msg,
					   COALESCE(n.status, 'unread') AS status,
					   COALESCE(n.created_at, n.time, CURRENT_TIMESTAMP) AS created_at
				FROM notifications n
				WHERE n.user_id = %s OR n.tenant_id = (
					SELECT t.tenant_id FROM tenants t WHERE t.user_id = %s LIMIT 1
				)
				ORDER BY created_at DESC
				LIMIT %s
				""",
				(user_id, user_id, limit),
			)
			rows = cursor.fetchall()
			if rows:
				out = []
				for r in rows:
					created = r.get("created_at")
					human, days = _nice_date_and_days(created)
					out.append(
						{
							"type": r.get("type") or "Info",
							"title": r.get("title") or "(no title)",
							"msg": r.get("msg") or "",
							"date": human,
							"days": days,
							"unread": str(r.get("status")).lower() != "read" and str(r.get("status")).lower() != "seen",
						}
					)
				cursor.close()
				conn.close()
				return out
		except Exception:
			# Table might not exist or columns differ; fall through to aggregated sources
			pass

		# Fallback: aggregate interesting items from invoices, maintenance requests and broadcasts
		# 1) Unpaid or recent invoices
		try:
			# get tenant id
			cursor.execute("SELECT tenant_id FROM tenants WHERE user_id = %s", (user_id,))
			tenant_row = cursor.fetchone()
			tenant_id = tenant_row.get("tenant_id") if tenant_row else None

			items = []

			if tenant_id:
				cursor.execute(
					"SELECT invoice_id, amount, issue_date, due_date, status FROM invoices WHERE tenant_id = %s ORDER BY issue_date DESC LIMIT 10",
					(tenant_id,),
				)
				for r in cursor.fetchall():
					created = r.get("issue_date") or r.get("due_date")
					human, days = _nice_date_and_days(created if isinstance(created, datetime) else (datetime.combine(created, datetime.min.time()) if created else None))
					items.append(
						{
							"type": "Billing",
							"title": f"Invoice #{r.get('invoice_id')}",
							"msg": f"Amount: £{float(r.get('amount') or 0):.2f} — Status: {r.get('status')}",
							"date": human,
							"days": days,
							"unread": (r.get("status") or "").lower() != "paid",
						}
					)

				# 2) Maintenance requests
				cursor.execute(
					"SELECT request_id, description, status, reported_at FROM maintenance_requests WHERE tenant_id = %s ORDER BY reported_at DESC LIMIT 10",
					(tenant_id,),
				)
				for r in cursor.fetchall():
					created = r.get("reported_at")
					human, days = _nice_date_and_days(created)
					items.append(
						{
							"type": "Maintenance",
							"title": f"Maintenance #{r.get('request_id')}",
							"msg": r.get("description") or "",
							"date": human,
							"days": days,
							"unread": (r.get("status") or "").lower() != "resolved",
						}
					)

			# 3) Recent broadcasts targeted at residents or All
			cursor.execute(
				"SELECT broadcast_id, title, content, urgency, target_audience, created_at FROM broadcasts ORDER BY created_at DESC LIMIT 20"
			)
			for r in cursor.fetchall():
				ta = (r.get("target_audience") or "").strip().lower()
				# include broadcasts addressed exactly to 'All' or to residents (e.g. 'All Residents' or contains 'resident')
				if ta == "all" or ta == "all residents" in ta:
					created = r.get("created_at")
					human, days = _nice_date_and_days(created)
					notif_type = r.get("urgency") or "Info"
					items.append(
						{
							"type": notif_type,
							"title": r.get("title") or "Broadcast",
							"msg": r.get("content") or "",
							"date": human,
							"days": days,
							"unread": True,
						}
					)

			# Sort and limit
			items_sorted = sorted(items, key=lambda x: (not x.get("unread", False), x.get("days", 999)))
			cursor.close()
			conn.close()
			return items_sorted[:limit]
		except Exception:
			traceback.print_exc()
			cursor.close()
			conn.close()
			return []
	except Exception:
		traceback.print_exc()
		return []


def mark_notification_read(notification_id: int) -> bool:
	"""Mark a notification read if notifications table exists. Returns True on success or False."""
	try:
		conn = get_db_connection()
		cursor = conn.cursor()
		try:
			cursor.execute("UPDATE notifications SET status = 'read' WHERE notification_id = %s", (notification_id,))
			conn.commit()
			cursor.close()
			conn.close()
			return True
		except Exception:
			# Table missing or different schema
			cursor.close()
			conn.close()
			return False
	except Exception:
		return False