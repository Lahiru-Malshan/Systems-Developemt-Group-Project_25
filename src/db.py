import mysql.connector
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # Database Username
        password="asdf1234", # Database password
        database="paragon_db"
    )



def get_all_staff():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ni, name, role, status FROM staff")
    staff = cursor.fetchall()
    conn.close()
    return staff

def add_staff(ni, name, role, status="Active"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO staff (ni, name, role, status) VALUES (%s, %s, %s, %s)", 
                       (ni, name, role, status))
        conn.commit()
        success = True
    except:
        success = False # e.g. NI number already exists
    finally:
        conn.close()
    return success

def delete_staff(ni):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE ni = %s", (ni,))
    conn.commit()
    conn.close()

def update_staff(ni, new_name, new_role, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE staff SET name = %s, role = %s, status = %s WHERE ni = %s", 
                   (new_name, new_role, new_status, ni))
    conn.commit()
    conn.close()