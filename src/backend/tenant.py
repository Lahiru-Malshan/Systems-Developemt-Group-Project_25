import bcrypt
from datetime import datetime
from db import get_db_connection


class TenantBackend:
    # Fallback mock data for environments without full schema
    _mock_payments = [
        {"date": "2025-10-01", "description": "Monthly Rent - October", "amount": 1200.00, "status": "Pending", "method": "Bank Transfer"},
        {"date": "2025-09-05", "description": "Monthly Rent - September", "amount": 1200.00, "status": "Paid", "method": "Card"},
        {"date": "2025-08-28", "description": "Water Bill - August", "amount": 50.00, "status": "Paid", "method": "Card"},
    ]

    _mock_maintenance = [
        {"id": 101, "category": "Plumbing", "description": "Kitchen sink leaking", "priority": "High", "status": "In Progress", "created_date": "2026-02-15", "completed_date": None},
        {"id": 102, "category": "Electrical", "description": "AC Filter Cleaning", "priority": "Low", "status": "Completed", "created_date": "2026-01-22", "completed_date": "2026-01-23"},
        {"id": 103, "category": "Furniture", "description": "Broken door handle", "priority": "Medium", "status": "Pending", "created_date": "2026-02-10", "completed_date": None},
    ]

    _mock_notifications = [
        {"id": 1, "type": "Security", "title": "Parking Update", "msg": "New guest parking rules.", "date": "4 days ago", "days": 4, "unread": False},
        {"id": 2, "type": "Billing", "title": "Rent Invoice Generated", "msg": "Your rent invoice for February is ready.", "date": "Today", "days": 0, "unread": True},
        {"id": 3, "type": "General", "title": "Spring BBQ Party", "msg": "Join us for a BBQ party.", "date": "20 days ago", "days": 20, "unread": False},
        {"id": 4, "type": "Maintenance", "title": "Elevator Repair", "msg": "Elevator maintenance in Block B.", "date": "Yesterday", "days": 1, "unread": True},
    ]

    def __init__(self, user_id=None, username=None):
        self.user_id = user_id
        self.username = username

    def _db(self):
        return get_db_connection()

    def _safe_query(self, query, params=(), fetch_one=False):
        try:
            conn = self._db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Exception:
            return None

    def get_profile(self):
        if self.user_id is None:
            return {
                "username": self.username or "Tenant",
                "email": "tenant@example.com",
                "phone": "N/A",
                "occupation": "N/A",
                "dob": "N/A",
                "lease_start": "2026-01-01",
                "lease_end": "2027-01-01",
            }
        user = self._safe_query("SELECT username, email, phone_number, first_name, last_name FROM users WHERE user_id = %s", (self.user_id,), fetch_one=True)
        if not user:
            return {
                "username": self.username or "Tenant",
                "email": "tenant@example.com",
                "phone": "N/A",
                "occupation": "N/A",
                "dob": "N/A",
                "lease_start": "2026-01-01",
                "lease_end": "2027-01-01",
            }
        return {
            "username": user.get("username"),
            "first_name": user.get("first_name", ""),
            "last_name": user.get("last_name", ""),
            "email": user.get("email", ""),
            "phone": user.get("phone_number", ""),
            "occupation": user.get("occupation", "Tenant"),
            "dob": user.get("dob", "N/A"),
            "lease_start": user.get("lease_start", "2026-01-01"),
            "lease_end": user.get("lease_end", "2027-01-01"),
        }

    def update_profile(self, updates):
        if self.user_id is None:
            return False, "No user ID set"
        allowed = {"occupation", "dob", "phone", "email", "first_name", "last_name"}
        data = {k: v for k, v in updates.items() if k in allowed and v is not None}
        if not data:
            return False, "No valid fields"

        col_map = {"phone": "phone_number", "dob": "dob"}
        query_data = {}
        for k, v in data.items():
            col = col_map.get(k, k)
            query_data[col] = v

        try:
            conn = self._db()
            cursor = conn.cursor()
            set_clause = ", ".join([f"{k} = %s" for k in query_data.keys()])
            params = list(query_data.values())
            params.append(self.user_id)
            cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = %s", tuple(params))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Profile updated"
        except Exception as ex:
            return False, str(ex)

    def update_password(self, current_password: str, new_password: str):
        if self.user_id is None:
            return False, "User not authenticated"
        try:
            conn = self._db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT password_hash FROM users WHERE user_id = %s", (self.user_id,))
            user = cursor.fetchone()
            if not user:
                cursor.close()
                conn.close()
                return False, "User not found"
            if not bcrypt.checkpw(current_password.encode("utf-8"), user["password_hash"].encode("utf-8")):
                cursor.close()
                conn.close()
                return False, "Current password is incorrect"
            new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_hash, self.user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Password updated"
        except Exception as ex:
            return False, str(ex)

    def get_dashboard_stats(self):
        payments = self.get_payments()
        next_due = "£1,200"
        payment_status = "On Time"
        unread = sum(1 for p in self.get_notifications() if p.get("unread"))
        if payments:
            pending_count = sum(1 for p in payments if p.get("status") == "Pending")
            if pending_count > 0:
                next_due = f"£{sum(p['amount'] for p in payments if p['status'] == 'Pending'):.2f}"
                payment_status = "Overdue" if pending_count > 1 else "Pending"
        return {
            "next_rent_due": next_due,
            "payment_status": payment_status,
            "unread_notifications": unread,
        }

    def get_payments(self):
        if self.user_id is None:
            return self._mock_payments
        records = self._safe_query("SELECT date, description, amount, status, method FROM payments WHERE user_id = %s ORDER BY date DESC", (self.user_id,))
        if not records:
            return self._mock_payments
        return [
            {
                "date": str(r.get("date")) if r.get("date") else "",
                "description": r.get("description", ""),
                "amount": float(r.get("amount", 0.0)),
                "status": r.get("status", "Pending"),
                "method": r.get("method", "Unknown"),
            }
            for r in records
        ]

    def add_payment(self, amount: float, method: str, description: str):
        if self.user_id is None:
            self._mock_payments.insert(0, {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
                "amount": float(amount),
                "status": "Paid",
                "method": method,
            })
            return True, "Payment added"
        try:
            conn = self._db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO payments (user_id, date, description, amount, status, method) VALUES (%s, %s, %s, %s, %s, %s)", (
                self.user_id,
                datetime.now().strftime("%Y-%m-%d"),
                description,
                amount,
                "Paid",
                method,
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Payment added"
        except Exception:
            self._mock_payments.insert(0, {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
                "amount": float(amount),
                "status": "Paid",
                "method": method,
            })
            return True, "Payment added (fallback)"

    def get_maintenance_requests(self):
        if self.user_id is None:
            return self._mock_maintenance
        records = self._safe_query("SELECT id, category, description, priority, status, created_date, completed_date FROM maintenance_requests WHERE user_id = %s ORDER BY created_date DESC", (self.user_id,))
        if not records:
            return self._mock_maintenance
        return [
            {
                "id": r.get("id"),
                "category": r.get("category", "General"),
                "description": r.get("description", ""),
                "priority": r.get("priority", "Medium"),
                "status": r.get("status", "Pending"),
                "created_date": str(r.get("created_date", "")),
                "completed_date": str(r.get("completed_date", "-")) if r.get("completed_date") else "-",
            }
            for r in records
        ]

    def create_maintenance_request(self, category: str, description: str, priority: str):
        if self.user_id is None:
            new_id = max((r["id"] for r in self._mock_maintenance), default=100) + 1
            self._mock_maintenance.insert(0, {
                "id": new_id,
                "category": category,
                "description": description,
                "priority": priority,
                "status": "Pending",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "completed_date": None,
            })
            return True, "Request submitted"
        try:
            conn = self._db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO maintenance_requests (user_id, category, description, priority, status, created_date) VALUES (%s, %s, %s, %s, %s, %s)", (
                self.user_id,
                category,
                description,
                priority,
                "Pending",
                datetime.now().strftime("%Y-%m-%d"),
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Request submitted"
        except Exception:
            new_id = max((r["id"] for r in self._mock_maintenance), default=100) + 1
            self._mock_maintenance.insert(0, {
                "id": new_id,
                "category": category,
                "description": description,
                "priority": priority,
                "status": "Pending",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "completed_date": None,
            })
            return True, "Request submitted (fallback)"

    def get_notifications(self):
        if self.user_id is None:
            return self._mock_notifications
        records = self._safe_query("SELECT id, type, title, msg, date, unread FROM notifications WHERE user_id = %s ORDER BY date DESC", (self.user_id,))
        if not records:
            return self._mock_notifications
        return [
            {
                "id": r.get("id"),
                "type": r.get("type", "General"),
                "title": r.get("title", ""),
                "msg": r.get("msg", ""),
                "date": str(r.get("date", "")),
                "days": 0,
                "unread": bool(r.get("unread", 0)),
            }
            for r in records
        ]

    def mark_notification_read(self, notification_id):
        if self.user_id is None:
            for note in self._mock_notifications:
                if note["id"] == notification_id:
                    note["unread"] = False
                    return True
            return False
        try:
            conn = self._db()
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET unread = 0 WHERE id = %s AND user_id = %s", (notification_id, self.user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            return False
