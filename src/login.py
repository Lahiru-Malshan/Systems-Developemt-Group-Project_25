from db import get_db_connection
import bcrypt

def login(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        user_val = username
        pass_val = password

        if not user_val or not pass_val:
            return "informationError"
        # Retrieve User
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (user_val,))
        user = cursor.fetchone()

        if user_val and bcrypt.checkpw(pass_val.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Login Successfully
            return "Success"
            
            # Can be redirect to Dashboard HERE
            # e.g., page.go("/dashboard")
        else:
            return "Invalid"
        
    except Exception as e:
        return str(e)
    finally:
        cursor.close()
        conn.close()