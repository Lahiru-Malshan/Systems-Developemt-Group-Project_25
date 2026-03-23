import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

import flet as ft
from logic.notifications import *
from base_dashboard import *
import db
from pwhash import hash_password, verify_password  # <-- Imports both functions

def show_settings(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()

    # --- FETCHING USER DATA (Lahiru_Malshan) ---
    try:
        current_user_id = dash.user_id
    except AttributeError:
        current_user_id = 1  # Failsafe by Lahiru_Malshan

    user_data = db.get_user_profile(current_user_id)
    if user_data:
        full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        current_email = user_data.get('email', "")
        current_phone = user_data.get('phone_number', "")
        current_hash = user_data.get('password_hash', "")
    else:
        full_name, current_email, current_phone, current_hash = "", "", "", ""

    
    header = ft.Text("Settings & Account", size=24, weight="bold", color=TEXT_DARK)

    
    ref_name = ft.TextField(label="Full Name", value=full_name, border_radius=8, color=TEXT_DARK, expand=True)
    ref_phone = ft.TextField(label="Phone Number", value=current_phone, border_radius=8, color=TEXT_DARK, expand=True)
    ref_email = ft.TextField(label="Email Address", value=current_email, border_radius=8, color=TEXT_DARK, expand=True)

    def handle_profile_update(e):
        if not ref_name.value or not ref_email.value:
            dash.show_message("Name and Email cannot be empty!")
            return
            
        # Split full name back into first and last name safely
        name_parts = ref_name.value.strip().split(" ", 1)
        first = name_parts[0]
        last = name_parts[1] if len(name_parts) > 1 else ""

        if db.update_user_profile(current_user_id, first, last, ref_email.value, ref_phone.value):
            dash.show_message("Profile information updated successfully!")
        else:
            dash.show_message("Database Error: Could not update profile.")

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
                    on_click=handle_profile_update
                )
            ], alignment="end")
        ], spacing=15)
    )

    # CHANGE PASSWORD
    ref_old_pass = ft.TextField(label="Current Password", password=True, can_reveal_password=True, border_radius=8, color=TEXT_DARK)
    ref_new_pass = ft.TextField(label="New Password", password=True, can_reveal_password=True, border_radius=8, color=TEXT_DARK)
    ref_confirm_pass = ft.TextField(label="Confirm New Password", password=True, can_reveal_password=True, border_radius=8, color=TEXT_DARK)

    def handle_password_change(e):
        nonlocal current_hash  # Fixed the SyntaxError!

        if not ref_old_pass.value or not ref_new_pass.value or not ref_confirm_pass.value:
            dash.show_message("Please fill out all password fields.")
            return
        
        if ref_new_pass.value != ref_confirm_pass.value:
            dash.show_message("Error: New passwords do not match!")
            return

        # Uses verify_password to properly check the database hash
        if not verify_password(ref_old_pass.value, current_hash):
            dash.show_message("Error: Current password is incorrect!")
            return

        # Hash new password and save to DB
        new_hash = hash_password(ref_new_pass.value)
        if db.update_user_password(current_user_id, new_hash):
            dash.show_message("Password has been changed successfully!")
            ref_old_pass.value = ""
            ref_new_pass.value = ""
            ref_confirm_pass.value = ""
            
            # Immediately update the hash in memory 
            current_hash = new_hash
            
            dash.page.update()
        else:
            dash.show_message("Database Error: Could not update password.")

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
                    on_click=handle_password_change
                )
            ], alignment="end")
        ], spacing=15)
    )

    #LOGOUT ZONE
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