from db import get_db_connection
import bcrypt

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

        if bcrypt.checkpw(pass_val.encode('utf-8'), user['password_hash'].encode('utf-8')):
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