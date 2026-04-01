#Duc Trung Nguyen - 25036440
from db import get_db_connection
from pwhash import verify_password

def login(username, password):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        user_val = username
        pass_val = password

        if not user_val or not pass_val:
            return "informationError"

        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (user_val,))
        user = cursor.fetchone()

        if not user:
            return "Invalid"

        if user.get('account_status') != 'Active':
            if user.get('role_id') == 6:
                return "PendingApproval"
            return "Inactive"

        if verify_password(pass_val, user['password_hash']):
            return user
        else:
            return "Invalid"
    except Exception as e:
        return str(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()