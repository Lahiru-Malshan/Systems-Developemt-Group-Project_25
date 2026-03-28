import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from pwhash import hash_password


load_dotenv(Path(__file__).resolve().parent.parent / ".env")


ROLE_LABEL_TO_DB = {
    "Administrator": "Administrator",
    "Manager": "Manager",
    "Front Desk": "FrontDeskStaff",
    "Maintenance": "MaintenanceStaff",
    "Finance Manager": "FinancialManager",
}

ROLE_DB_TO_LABEL = {value: key for key, value in ROLE_LABEL_TO_DB.items()}
DEFAULT_STAFF_LOCATION_ID = int(os.getenv("DEFAULT_STAFF_LOCATION_ID", "1"))


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


def _normalize_staff_role(role: str) -> str:
    normalized_role = ROLE_LABEL_TO_DB.get(role, role)
    if normalized_role not in ROLE_DB_TO_LABEL:
        raise ValueError(f"Unsupported staff role: {role}")
    return normalized_role


def _format_staff_role(role_name: str) -> str:
    return ROLE_DB_TO_LABEL.get(role_name, role_name)


def _split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        raise ValueError("Staff name is required")
    if len(parts) == 1:
        return parts[0], "Staff"
    return parts[0], " ".join(parts[1:])


def _build_staff_username(ni: str) -> str:
    return "".join(character for character in ni.lower().strip() if character.isalnum())


def _generate_staff_email(username: str) -> str:
    return f"{username}@staff.local"


def _generate_staff_password(ni: str) -> str:
    return f"Paragon@{ni[-4:]}"


def _remove_staff_assignment(cursor, user_id: int):
    cursor.execute("DELETE FROM administrators WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM managers WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM frontdesk_staff WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM maintenance_staff WHERE user_id = %s", (user_id,))
    cursor.execute("DELETE FROM financial_managers WHERE user_id = %s", (user_id,))


def _assign_staff_role(cursor, user_id: int, role_id: int):
    _remove_staff_assignment(cursor, user_id)

    if role_id == 1:
        cursor.execute(
            "INSERT INTO administrators (user_id, location_id) VALUES (%s, %s)",
            (user_id, DEFAULT_STAFF_LOCATION_ID),
        )
    elif role_id == 2:
        cursor.execute(
            "INSERT INTO managers (user_id, location_id) VALUES (%s, %s)",
            (user_id, DEFAULT_STAFF_LOCATION_ID),
        )
    elif role_id == 3:
        cursor.execute(
            "INSERT INTO frontdesk_staff (user_id, location_id, hire_date) VALUES (%s, %s, CURRENT_DATE)",
            (user_id, DEFAULT_STAFF_LOCATION_ID),
        )
    elif role_id == 4:
        cursor.execute(
            "INSERT INTO maintenance_staff (user_id, location_id, hire_date) VALUES (%s, %s, CURRENT_DATE)",
            (user_id, DEFAULT_STAFF_LOCATION_ID),
        )
    elif role_id == 5:
        cursor.execute(
            "INSERT INTO financial_managers (user_id, location_id, hire_date) VALUES (%s, %s, CURRENT_DATE)",
            (user_id, DEFAULT_STAFF_LOCATION_ID),
        )
    else:
        raise ValueError(f"Unsupported role id for staff assignment: {role_id}")


def _get_staff_user_by_ni(cursor, ni: str):
    cursor.execute(
        """
        SELECT user_id, role_id
        FROM users
        WHERE role_id IN (1, 2, 3, 4, 5)
          AND UPPER(COALESCE(NULLIF(nickname, ''), username)) = %s
        """,
        (ni.upper(),),
    )
    return cursor.fetchone()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=_get_required_env("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "paragon_db")
    )

# ==========================================
# --- STAFF MANAGEMENT QUERIES ---
# ==========================================

def get_all_staff():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            UPPER(COALESCE(NULLIF(u.nickname, ''), u.username)) AS ni,
            CONCAT(u.first_name, ' ', u.last_name) AS name,
            r.role_name AS role,
            u.account_status AS status
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.role_id IN (1, 2, 3, 4, 5)
        ORDER BY u.first_name, u.last_name
        """
    )
    staff = cursor.fetchall()
    conn.close()
    for item in staff:
        item["role"] = _format_staff_role(item["role"])
    return staff

def add_staff(ni, name, role, status="Active"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        normalized_role = _normalize_staff_role(role)
        first_name, last_name = _split_full_name(name)
        username = _build_staff_username(ni)
        if not username:
            raise ValueError("NI number must contain letters or digits")

        email = _generate_staff_email(username)
        temp_password = _generate_staff_password(ni.upper())

        cursor.execute("SELECT role_id FROM roles WHERE role_name = %s", (normalized_role,))
        role_row = cursor.fetchone()
        if not role_row:
            raise ValueError(f"Role not found: {normalized_role}")

        cursor.execute(
            """
            INSERT INTO users (
                role_id, username, password_hash, first_name, last_name, email, account_status, nickname
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (role_row[0], username, hash_password(temp_password), first_name, last_name, email, status, ni.upper()),
        )
        user_id = cursor.lastrowid
        _assign_staff_role(cursor, user_id, role_row[0])
        conn.commit()
        return {"success": True, "username": username, "password": temp_password}
    except Exception as e:
        conn.rollback()
        print(f"DATABASE ERROR (Add Staff): {e}")
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def delete_staff(ni):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        staff_user = _get_staff_user_by_ni(cursor, ni)
        if not staff_user:
            return False

        user_id = staff_user[0]
        _remove_staff_assignment(cursor, user_id)
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def update_staff(ni, new_name, new_role, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        staff_user = _get_staff_user_by_ni(cursor, ni)
        if not staff_user:
            return False

        normalized_role = _normalize_staff_role(new_role)
        first_name, last_name = _split_full_name(new_name)

        cursor.execute("SELECT role_id FROM roles WHERE role_name = %s", (normalized_role,))
        role_row = cursor.fetchone()
        if not role_row:
            raise ValueError(f"Role not found: {normalized_role}")

        user_id = staff_user[0]
        role_id = role_row[0]
        cursor.execute(
            """
            UPDATE users
            SET first_name = %s, last_name = %s, role_id = %s, account_status = %s
            WHERE user_id = %s
            """,
            (first_name, last_name, role_id, new_status, user_id),
        )
        _assign_staff_role(cursor, user_id, role_id)
        conn.commit()
        return True
    finally:
        conn.close()

# ==========================================
# --- RESIDENT APPROVAL QUERIES ---
# ==========================================

def get_pending_residents():
    """Fetches Tenants (role 6) whose accounts are Inactive."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT user_id, CONCAT(first_name, ' ', last_name) AS name, created_at 
        FROM users 
        WHERE role_id = 6 AND account_status = 'Inactive'
    """
    cursor.execute(query)
    pending_users = cursor.fetchall()
    conn.close()
    return pending_users

def approve_resident(user_id):
    """Changes a user's status to Active."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET account_status = 'Active' WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()

def reject_resident(user_id):
    """Deletes the rejected user from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()

# ==========================================
# --- ASSETS (APARTMENTS) QUERIES ---
# ==========================================

def get_all_apartments():
    """Fetches all apartments and their current status."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT a.apartment_id, a.apartment_number, a.bedrooms, a.bathrooms, a.rent, a.status, l.city 
        FROM apartments a
        LEFT JOIN locations l ON a.location_id = l.location_id
    """
    cursor.execute(query)
    apartments = cursor.fetchall()
    conn.close()
    return apartments

def add_apartment(location_id, apartment_number, bedrooms, bathrooms, rent, status="Available"):
    """Adds a new apartment to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO apartments (location_id, apartment_number, bedrooms, bathrooms, rent, status) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (location_id, apartment_number, bedrooms, bathrooms, rent, status))
        conn.commit()
        success = True
    except Exception as e:
        print(f"DATABASE ERROR (Add Apartment): {e}")
        success = False 
    finally:
        conn.close()
    return success

def update_apartment_status(apartment_id, new_status):
    """Updates an apartment to Available, Occupied, or Maintenance."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE apartments SET status = %s WHERE apartment_id = %s", (new_status, apartment_id))
    conn.commit()
    conn.close()

def delete_apartment(apartment_id):
    """Removes an apartment from the system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM apartments WHERE apartment_id = %s", (apartment_id,))
    conn.commit()
    conn.close()

# ==========================================
# --- LEASE AGREEMENTS QUERIES ---
# ==========================================

def get_all_leases():
    """Fetches all leases, linking the apartment number and tenant name."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT l.lease_id, a.apartment_number, u.first_name, u.last_name, 
               l.start_date, l.end_date, l.monthly_rent, l.status
        FROM lease_agreements l
        JOIN apartments a ON l.apartment_id = a.apartment_id
        JOIN tenants t ON l.tenant_id = t.tenant_id
        JOIN users u ON t.user_id = u.user_id
    """
    cursor.execute(query)
    leases = cursor.fetchall()
    conn.close()
    return leases

def add_lease(tenant_id, apartment_id, start_date, end_date, monthly_rent, status="Active"):
    """Creates a new lease agreement and marks the apartment as Occupied."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO lease_agreements (tenant_id, apartment_id, start_date, end_date, monthly_rent, status) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (tenant_id, apartment_id, start_date, end_date, monthly_rent, status))
        
        # Automatically update the apartment status to Occupied
        cursor.execute("UPDATE apartments SET status = 'Occupied' WHERE apartment_id = %s", (apartment_id,))
        
        conn.commit()
        success = True
    except Exception as e:
        print(f"DATABASE ERROR (Add Lease): {e}")
        success = False 
    finally:
        conn.close()
    return success

# ==========================================
# --- BROADCAST QUERIES ---
# ==========================================

def get_all_broadcasts():
    """Fetches all past broadcasts from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT broadcast_id, title, target_audience, urgency, DATE(created_at) as send_date 
        FROM broadcasts 
        ORDER BY created_at DESC
    """)
    broadcasts = cursor.fetchall()
    conn.close()
    return broadcasts

def add_broadcast(title, target_audience, content, urgency):
    """Saves a new broadcast to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO broadcasts (title, target_audience, content, urgency) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (title, target_audience, content, urgency))
        conn.commit()
        success = True
    except Exception as e:
        print(f"DATABASE ERROR (Add Broadcast): {e}")
        success = False 
    finally:
        conn.close()
    return success

# ==========================================
# --- OPERATIONS: MAINTENANCE & COMPLAINTS ---
# ==========================================

def get_maintenance_requests():
    """Fetches all maintenance requests with the tenant's name and unit number."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT m.request_id, a.apartment_number, u.first_name, u.last_name, 
               m.description, m.status, DATE(m.reported_at) as reported_date
        FROM maintenance_requests m
        JOIN apartments a ON m.apartment_id = a.apartment_id
        JOIN tenants t ON m.tenant_id = t.tenant_id
        JOIN users u ON t.user_id = u.user_id
        ORDER BY m.reported_at DESC
    """
    cursor.execute(query)
    requests = cursor.fetchall()
    conn.close()
    return requests

def update_maintenance_status(request_id, new_status):
    """Updates a maintenance ticket to Pending, In Progress, or Resolved."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE maintenance_requests SET status = %s WHERE request_id = %s", (new_status, request_id))
    conn.commit()
    conn.close()

def get_all_complaints():
    """Fetches all tenant complaints."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT c.complaint_id, u.first_name, u.last_name, 
               c.description, c.status, DATE(c.created_at) as reported_date
        FROM complaints c
        JOIN tenants t ON c.tenant_id = t.tenant_id
        JOIN users u ON t.user_id = u.user_id
        ORDER BY c.created_at DESC
    """
    cursor.execute(query)
    complaints = cursor.fetchall()
    conn.close()
    return complaints

def update_complaint_status(complaint_id, new_status):
    """Updates a complaint ticket to Open or Closed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status = %s WHERE complaint_id = %s", (new_status, complaint_id))
    conn.commit()
    conn.close()

# ==========================================
# --- SETTINGS & PROFILE QUERIES ---
# ==========================================

def get_user_profile(user_id):
    """Fetches the user's current profile data."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # I added phone_number to this SELECT query!
    cursor.execute("SELECT first_name, last_name, email, phone_number, password_hash FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_profile(user_id, first_name, last_name, email, phone_number):
    """Updates the user's name, email, and phone."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # I added phone_number to this UPDATE query!
        cursor.execute("""
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, phone_number = %s
            WHERE user_id = %s
        """, (first_name, last_name, email, phone_number, user_id))
        conn.commit()
        success = True
    except Exception as e:
        print(f"DATABASE ERROR (Update Profile): {e}")
        success = False
    finally:
        conn.close()
    return success

def update_user_password(user_id, new_password_hash):
    """Updates the user's password."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_password_hash, user_id))
        conn.commit()
        success = True
    except Exception as e:
        print(f"DATABASE ERROR (Update Password): {e}")
        success = False
    finally:
        conn.close()
    return success

# ==========================================
# --- SECURITY LOGS QUERIES ---
# ==========================================

def get_security_logs():
    """Fetches the latest security logs."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT event_description as event, severity_color as color, 
               DATE_FORMAT(created_at, '%H:%i:%s') as time 
        FROM security_logs 
        ORDER BY created_at DESC 
        LIMIT 50
    """)
    logs = cursor.fetchall()
    conn.close()
    return logs

def add_security_log(event_description, severity_color="blue"):
    """Saves a new security event to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO security_logs (event_description, severity_color) VALUES (%s, %s)", 
                       (event_description, severity_color))
        conn.commit()
    except Exception as e:
        print(f"DATABASE ERROR (Add Log): {e}")
    finally:
        conn.close()


def get_manager_city_analytics():
    """Fetches live occupancy and invoice analytics grouped by city."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT
            l.city,
            COALESCE(unit_stats.total_units, 0) AS total_units,
            COALESCE(unit_stats.occupied_units, 0) AS occupied_units,
            COALESCE(financials.collected_revenue, 0) AS collected_revenue,
            COALESCE(financials.pending_revenue, 0) AS pending_revenue
        FROM locations l
        LEFT JOIN (
            SELECT
                a.location_id,
                COUNT(*) AS total_units,
                SUM(CASE WHEN a.status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_units
            FROM apartments a
            GROUP BY a.location_id
        ) AS unit_stats ON unit_stats.location_id = l.location_id
        LEFT JOIN (
            SELECT
                a.location_id,
                SUM(CASE WHEN i.status = 'Paid' THEN i.amount ELSE 0 END) AS collected_revenue,
                SUM(CASE WHEN i.status IN ('Unpaid', 'Late') THEN i.amount ELSE 0 END) AS pending_revenue
            FROM apartments a
            LEFT JOIN lease_agreements la ON la.apartment_id = a.apartment_id
            LEFT JOIN invoices i ON i.lease_id = la.lease_id
            GROUP BY a.location_id
        ) AS financials ON financials.location_id = l.location_id
        ORDER BY l.city
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows