import bcrypt
from datetime import datetime
from db import get_db_connection

class TenantBackend:
    # Fallback mock data for environments without full schema

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
        user = self._safe_query("SELECT username, email, phone_number, first_name, last_name, nickname, dob FROM users WHERE user_id = %s", (self.user_id,), fetch_one=True)
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
            "nickname": user.get("nickname") or f"{user.get('first_name','')} {user.get('last_name','')}".strip() or "Tenant",
            "dob": user.get("dob", "N/A"),
            "lease_start": user.get("lease_start", "2026-01-01"),
            "lease_end": user.get("lease_end", "2027-01-01"),
        }

    def update_profile(self, updates):
        if self.user_id is None:
            return False, "No user ID set"
        allowed = {"nickname", "dob", "phone", "email", "first_name", "last_name"}
        data = {k: v for k, v in updates.items() if k in allowed and v is not None}
        if not data:
            return False, "No valid fields"

        col_map = {"nickname": "nickname", "phone": "phone_number", "dob": "dob", "first_name": "first_name", "last_name": "last_name", "email": "email"}
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
            return []
        tenant = self.get_tenant_record()
        if not tenant:
            return []
        records = self._safe_query("SELECT payment_id, invoice_id, amount, payment_date, method, description, status FROM payments WHERE tenant_id = %s ORDER BY payment_date DESC", (tenant["tenant_id"],))
        if not records:
            return []
        return [
            {
                "date": str(r.get("payment_date", "")),
                "description": r.get("description") or f"Payment #{r.get('payment_id')}",
                "amount": float(r.get("amount", 0.0)),
                "status": r.get("status", "Paid"),
                "method": r.get("method", "Unknown"),
            }
            for r in records
        ]

    def add_payment(self, amount: float, method: str, description: str):
        # Keep compatibility as a simple alias for make_payment
        return self.make_payment(amount=amount, method=method, description=description)

    def make_payment(self, amount: float, method: str, description: str, invoice_id: int = None):
        if self.user_id is None:
            return False, "User not authenticated"
        tenant = self.get_tenant_record()
        if not tenant:
            return False, "Tenant record not found"
        if amount <= 0:
            return False, "Amount must be greater than zero"

        try:
            conn = self._db()
            cursor = conn.cursor()
            invoice_amount = 0

            if invoice_id is None:
                invoice_row = self._safe_query(
                    "SELECT i.invoice_id, i.amount FROM invoices i WHERE i.tenant_id = %s AND i.status <> 'Paid' ORDER BY i.due_date ASC LIMIT 1",
                    (tenant["tenant_id"],),
                    fetch_one=True,
                )
                if invoice_row:
                    invoice_id = invoice_row.get("invoice_id")
                    invoice_amount = float(invoice_row.get("amount", 0))
                else:
                    lease = self.get_lease_agreement()
                    if not lease:
                        cursor.close()
                        conn.close()
                        return False, "No active lease found to create invoice"
                    invoice_amount = float(lease.get("monthly_rent", amount))
                    issue_date = datetime.now().date()
                    due_date = issue_date
                    cursor.execute(
                        "INSERT INTO invoices (tenant_id, lease_id, amount, issue_date, due_date, status) VALUES (%s, %s, %s, %s, %s, %s)",
                        (
                            tenant["tenant_id"],
                            lease["lease_id"],
                            invoice_amount,
                            issue_date,
                            due_date,
                            "Unpaid",
                        ),
                    )
                    invoice_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO payments (tenant_id, invoice_id, processed_by, amount, payment_date, method, description, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    tenant["tenant_id"],
                    invoice_id or 0,
                    1,
                    amount,
                    datetime.now().strftime("%Y-%m-%d"),
                    method,
                    description,
                    "Paid",
                ),
            )

            if invoice_id is not None:
                if not invoice_amount:
                    invoice_row = self._safe_query("SELECT amount FROM invoices WHERE invoice_id = %s", (invoice_id,), fetch_one=True)
                    invoice_amount = float(invoice_row.get("amount", 0)) if invoice_row else 0
                if amount >= invoice_amount:
                    cursor.execute("UPDATE invoices SET status = 'Paid' WHERE invoice_id = %s", (invoice_id,))
                else:
                    cursor.execute("UPDATE invoices SET status = 'Late' WHERE invoice_id = %s", (invoice_id,))

            conn.commit()
            cursor.close()
            conn.close()
            return True, "Payment processed and saved"
        except Exception as ex:
            return False, str(ex)


    def get_maintenance_requests(self):
        if self.user_id is None:
            return []
        tenant = self.get_tenant_record()
        if not tenant:
            return []
        records = self._safe_query("SELECT request_id, apartment_id, description, status, reported_at, resolved_at FROM maintenance_requests WHERE tenant_id = %s ORDER BY request_id DESC", (tenant["tenant_id"],))
        if not records:
            return []
        return [
            {
                "id": r.get("request_id"),
                "apartment_id": r.get("apartment_id"),
                "description": r.get("description", ""),
                "status": r.get("status", "Pending"),
                "reported_at": str(r.get("reported_at", "")),
                "resolved_at": str(r.get("resolved_at", "-")) if r.get("resolved_at") else "-",
            }
            for r in records
        ]

    def create_maintenance_request(self, category: str, description: str, priority: str):
        if self.user_id is None:
            return False, "User not authenticated"
        tenant = self.get_tenant_record()
        if not tenant:
            return False, "Tenant record not found"

        lease = self._safe_query("SELECT apartment_id FROM lease_agreements WHERE tenant_id = %s ORDER BY start_date DESC LIMIT 1", (tenant["tenant_id"],), fetch_one=True)
        apartment_id = lease.get("apartment_id") if lease else None

        try:
            conn = self._db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO maintenance_requests (tenant_id, apartment_id, description, status, reported_at) VALUES (%s, %s, %s, %s, %s)", (
                tenant["tenant_id"],
                apartment_id or 0,
                description,
                "Pending",
                datetime.now(),
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Request submitted"
        except Exception as ex:
            return False, str(ex)


    def get_notifications(self):
        return []

    def mark_notification_read(self, notification_id):
        return False

    def get_tenant_record(self):
        if self.user_id is None:
            return None
        row = self._safe_query("SELECT tenant_id, ni_number, occupation FROM tenants WHERE user_id = %s", (self.user_id,), fetch_one=True)
        return row

    def get_lease_agreement(self):
        tenant = self.get_tenant_record()
        if not tenant:
            return None
        row = self._safe_query("SELECT l.lease_id, l.start_date, l.end_date, l.monthly_rent, a.apartment_number FROM lease_agreements l JOIN apartments a ON l.apartment_id = a.apartment_id WHERE l.tenant_id = %s ORDER BY l.start_date DESC LIMIT 1", (tenant["tenant_id"],), fetch_one=True)
        return row

    def get_invoices(self):
        if self.user_id is None:
            return []
        tenant = self.get_tenant_record()
        if not tenant:
            return []
        rows = self._safe_query("SELECT i.invoice_id, i.issue_date, i.due_date, i.amount, i.status FROM invoices i JOIN lease_agreements l ON i.lease_id = l.lease_id WHERE l.tenant_id = %s ORDER BY issue_date DESC", (tenant["tenant_id"],))
        if not rows:
            return []
        return [{
            "invoice_id": r.get("invoice_id"),
            "issue_date": str(r.get("issue_date", "")),
            "due_date": str(r.get("due_date", "")),
            "amount": float(r.get("amount", 0.0)),
            "status": r.get("status", "Unpaid")
        } for r in rows]

    def get_complaints(self):
        if self.user_id is None:
            return []
        tenant = self.get_tenant_record()
        if not tenant:
            return []
        rows = self._safe_query("SELECT c.complaint_id, c.description, c.status, c.created_at FROM complaints c WHERE c.tenant_id = %s ORDER BY c.created_at DESC", (tenant["tenant_id"],))
        if not rows:
            return []
        return [{
            "complaint_id": r.get("complaint_id"),
            "description": r.get("description", ""),
            "status": r.get("status", "Open"),
            "created_at": str(r.get("created_at", ""))
        } for r in rows]

    def submit_complaint(self, description: str):
        if self.user_id is None:
            return False, "User not authenticated"
        tenant = self.get_tenant_record()
        if not tenant:
            return False, "Tenant record not found"
        try:
            conn = self._db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO complaints (tenant_id, description, status, created_at) VALUES (%s, %s, %s, %s)", (
                tenant["tenant_id"],
                description,
                "Open",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Complaint submitted"
        except Exception as err:
            return False, str(err)
