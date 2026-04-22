# Elena Ho - 25044389

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

	Each item contains: type (Info or Urgent), title, msg, date (human), days (int)
	"""
	try:
		conn = get_db_connection()
		cursor = conn.cursor(dictionary=True)

		# Fetch from broadcasts table (used for notifications)
		cursor.execute(
			"""
			SELECT b.broadcast_id AS id,
				   b.urgency AS type,
				   b.title,
				   b.content AS msg,
				   b.created_at
			FROM broadcasts b
			WHERE b.target_audience IN ('All', 'All Residents', 'All residents')
			ORDER BY b.created_at DESC
			LIMIT %s
			""",
			(limit,),
		)
		rows = cursor.fetchall()
		out = []

		if rows:
			for r in rows:
				created = r.get("created_at")
				human, days = _nice_date_and_days(created)
				# Map type: only "Urgent" or "Info"
				notif_type = r.get("type") or "Info"
				if notif_type.lower() != "urgent":
					notif_type = "Info"
				out.append(
					{
						"type": notif_type,
						"title": r.get("title") or "(no title)",
						"msg": r.get("msg") or "",
						"date": human,
						"days": days,
					}
				)

		cursor.close()
		conn.close()
		return out
	except Exception:
		traceback.print_exc()
		return []

def mark_notification_read(notification_id: int) -> bool:
	"""Mark a notification read if notifications table exists. Returns True on success or False."""
	try:
		conn = get_db_connection()
		cursor = conn.cursor()
		try:
			cursor.execute("UPDATE broadcasts SET status = 'read' WHERE broadcast_id = %s", (notification_id,))
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