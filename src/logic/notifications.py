# logic/notifications.py
import flet as ft
from datetime import datetime

def send_notification(dash, user_id, title, message):
    """
    Logic cốt lõi để gửi thông báo.
    user_id: Số phòng hoặc ID của cư dân nhận tin.
    """
    try:
        # Lấy thời gian thực tại
        timestamp = datetime.now().strftime("%H:%M")
        
        # --- BƯỚC 1: LƯU VÀO DATABASE ---
        # Sau này bạn sẽ dùng code SQL ở đây:
        # db.execute("INSERT INTO notifications (user_id, title, msg, time, status)
        #            VALUES (?, ?, ?, ?, 'unread')", (user_id, title, message, timestamp))
        
        # --- BƯỚC 2: LOG KIỂM TRA ---
        print(f"DEBUG: Notification sent to {user_id} | {title}")
        
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False