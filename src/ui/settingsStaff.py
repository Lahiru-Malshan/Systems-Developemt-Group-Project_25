import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)
# Đoạn code trên đang thêm thư mục cha của file hiện tại vào sys.path để có thể import các module từ thư mục đó để chạy test. Điều này giúp tránh lỗi ImportError khi import các module khác trong dự án. Sau này sẽ sửa lại, dùng .. để import trực tiếp thay vì sửa sys.path như này.

import flet as ft
from logic.notifications import *
from base_dashboard import *

def show_settings(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()

    # --- HEADER ---
    header = ft.Text("Settings & Account", size=24, weight="bold", color=TEXT_DARK)

    # --- 1. EDIT PROFILE SECTION ---
    ref_name = ft.TextField(label="Full Name", value=" ", border_radius=8, color=TEXT_DARK, expand=True)
    ref_phone = ft.TextField(label="Phone Number", value=" ", border_radius=8, color=TEXT_DARK, expand=True)
    ref_email = ft.TextField(label="Email Address", value=" ", border_radius=8, color=TEXT_DARK, expand=True)

    profile_card = ft.Container(
        bgcolor=CARD_BG,
        padding=25,
        border_radius=12,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, color=ACCENT_BLUE),
                ft.Text("Personal Information", weight="bold", size=18, color=TEXT_DARK),
            ]),
            ft.Divider(height=10),
            ft.Row([ref_name, ref_phone], spacing=20),
            ref_email,
            ft.Row([
                ft.Button(
                    content=ft.Text("Update Profile", color="white", weight="bold"),
                    bgcolor=ACCENT_BLUE,
                    on_click=lambda _: dash.show_message("Profile information updated!")
                )
            ], alignment="end")
        ], spacing=15)
    )

    # --- 2. CHANGE PASSWORD SECTION ---
    ref_old_pass = ft.TextField(label="Current Password", password=True, can_reveal_password=True, border_radius=8, color=TEXT_DARK)
    ref_new_pass = ft.TextField(label="New Password", password=True, can_reveal_password=True, border_radius=8, color=TEXT_DARK)
    ref_confirm_pass = ft.TextField(label="Confirm New Password", password=True, can_reveal_password=True, border_radius=8, color=TEXT_DARK)

    password_card = ft.Container(
        bgcolor=CARD_BG,
        padding=25,
        border_radius=12,
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LOCK_RESET_ROUNDED, color=ACCENT_BLUE),
                ft.Text("Security & Password", weight="bold", size=18, color=TEXT_DARK),
            ]),
            ft.Divider(height=10),
            ref_old_pass,
            ref_new_pass,
            ref_confirm_pass,
            
            ft.Row([
                ft.Button(
                    content=ft.Text("Change Password", color="white", weight="bold"),
                    bgcolor=NAVY_SECOND,
                    on_click=lambda _: dash.show_message("Password has been changed successfully!")
                )
            ], alignment="end")
        ], spacing=15)
    )

    # --- 3. LOGOUT / DANGER ZONE ---
    danger_card = ft.Container(
        bgcolor=ft.Colors.RED_50,
        padding=20,
        border_radius=12,
        border=ft.border.all(1, ft.Colors.RED_100),
        content=ft.Row([
            ft.Column([
                ft.Text("Session Management", weight="bold", color=ft.Colors.RED_700),
                ft.Text("Sign out of the system to protect your data.", color=ft.Colors.RED_400, size=12),
            ], expand=True),
            ft.Button(
                content=ft.Text("Logout", color="white", weight="bold"),
                bgcolor=ft.Colors.RED_700,
                on_click=dash.logout
            )
        ])
    )

    dash.content_column.controls.extend([
        header,
        ft.Divider(height=10, color="transparent"),
        profile_card,
        ft.Divider(height=10, color="transparent"),
        password_card,
        ft.Divider(height=10, color="transparent"),
        danger_card
    ])
    
    dash.page.update()