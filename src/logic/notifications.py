# logic/notifications.py
import flet as ft
from datetime import datetime

def send_notification(dash, user_id, title, message):

    try:
        # Take current timestamp for record-keeping
        timestamp = datetime.now().strftime("%H:%M")
        
        # --- Step 1: Save to Database ---

        # db.execute("INSERT INTO notifications (user_id, title, msg, time, status)
        #            VALUES (?, ?, ?, ?, 'unread')", (user_id, title, message, timestamp))
        
        # --- Step 2: Log Verification ---
        print(f"DEBUG: Notification sent to {user_id} | {title}")
        
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False