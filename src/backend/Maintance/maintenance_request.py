from datetime import datetime
from db import get_db_connection


def create_maintenance_request(tenant_id, apartment_id, description):
    if not tenant_id:
        raise ValueError("tenant_id is required")
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO maintenance_requests
        (tenant_id, apartment_id, description, status, reported_at)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            tenant_id,
            apartment_id,
            description,
            "Pending",
            datetime.now()
        )

        cursor.execute(query, values)
        conn.commit()

        print("Maintenance request created successfully!")

    except Exception as e:
        print("Error creating maintenance request:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
