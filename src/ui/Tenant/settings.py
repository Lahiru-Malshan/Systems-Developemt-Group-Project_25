# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from base_dashboard import *
import flet as ft

# --- TAB: MY PROFILE (Personal & Lease Info) ---
def draw_my_profile_tab(dash, *args):
    dash.detail_area.controls.clear()
    profile = dash.backend.get_profile() if hasattr(dash, "backend") else {}
    
    # Section 1: Personal Information
    ref_occupation = ft.TextField(
        label="Occupation", value=profile.get("occupation", "Tenant"), expand=True,
        border_color=ACCENT_BLUE, text_style=ft.TextStyle(color=TEXT_DARK)
    )
    ref_dob = ft.TextField(
        label="Date of Birth", value=profile.get("dob", ""), expand=True,
        border_color=ACCENT_BLUE, text_style=ft.TextStyle(color=TEXT_DARK)
    )
    ref_phone = ft.TextField(
        label="Phone", value=profile.get("phone", ""), expand=True,
        border_color=ACCENT_BLUE, text_style=ft.TextStyle(color=TEXT_DARK)
    )
    ref_email = ft.TextField(
        label="Email", value=profile.get("email", ""), expand=True,
        border_color=ACCENT_BLUE, text_style=ft.TextStyle(color=TEXT_DARK)
    )
    
    # Section 2: Lease Details (Read Only)
    ref_start_date = ft.TextField(
        label="Start Date", value="2026-01-01", read_only=True,
        expand=True, bgcolor=ft.Colors.GREY_50, text_style=ft.TextStyle(color=TEXT_DARK)
    )
    ref_end_date = ft.TextField(
        label="End Date", value="2027-01-01", read_only=True,
        expand=True, bgcolor=ft.Colors.GREY_50, text_style=ft.TextStyle(color=TEXT_DARK)
    )

    def handle_update_profile(e):
        data_to_update = {
            "occupation": ref_occupation.value,
            "dob": ref_dob.value,
            "phone": ref_phone.value,
            "email": ref_email.value
        }
        
        try:
            if hasattr(dash, "backend"):
                success, msg = dash.backend.update_profile(data_to_update)
                if not success:
                    raise Exception(msg)
            print(f"Updating DB with: {data_to_update}")
            dash.show_message("Profile updated successfully!")
            dash.page.update()
            
        except Exception as ex:
            dash.show_message(f"Update failed: {str(ex)}")
    # LAYOUT
    personal_section = ft.Column([
        ft.Text("Personal Information", size=18, weight="bold", color=TEXT_DARK),
        ft.Row([ref_occupation, ref_dob], spacing=20),
        ft.Row([ref_phone, ref_email], spacing=20),
    ], spacing=15)
    lease_section = ft.Column([
        ft.Text("Lease Details (System Only)", size=18, weight="bold", color=TEXT_DARK),
        ft.Row([ref_start_date, ref_end_date], spacing=20),
    ], spacing=15)
    
    update_btn_row = ft.Row([
        ft.Button(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE_ROUNDED, color="white"),
                ft.Text("Update Profile", weight="bold", color="white"),
            ], tight=True, spacing=10),
            height=45,
            bgcolor=ACCENT_BLUE,
            on_click=handle_update_profile # Gán hàm xử lý
        )
    ], alignment=ft.MainAxisAlignment.END)

    dash.detail_area.controls.extend([
        personal_section,
        ft.Divider(height=30, color="transparent"),
        lease_section,
        ft.Divider(height=20, color="transparent"),
        update_btn_row
    ])
    dash.page.update()

# --- TAB: SECURITY (Password Management) ---
def draw_security_tab(dash):
    dash.detail_area.controls.clear()
    
    ref_current_pw = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        border_color=ACCENT_BLUE,
        text_style=ft.TextStyle(color=TEXT_DARK)
    )
    ref_new_pw = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        border_color=ACCENT_BLUE,
        text_style=ft.TextStyle(color=TEXT_DARK)
    )
    ref_confirm_pw = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        border_color=ACCENT_BLUE,
        text_style=ft.TextStyle(color=TEXT_DARK)
    )
    
    def handle_update_password(e):
        if not ref_current_pw.value or not ref_new_pw.value:
            dash.show_message("Please fill in all password fields!")
            return
        
        if ref_new_pw.value != ref_confirm_pw.value:
            dash.show_message("New passwords do not match!")
            return

        if len(ref_new_pw.value) < 6:
            dash.show_message("Password must be at least 6 characters long!")
            return

        try:
            if hasattr(dash, "backend"):
                success, message = dash.backend.update_password(ref_current_pw.value, ref_new_pw.value)
                if not success:
                    dash.show_message(f"Update failed: {message}")
                    return
            dash.show_message("Password updated successfully!")
            ref_current_pw.value = ""
            ref_new_pw.value = ""
            ref_confirm_pw.value = ""
            dash.page.update()
            
        except Exception as ex:
            dash.show_message(f"Update failed: {str(ex)}")
    # LAYOUT
    header_text = ft.Column([
        ft.Text("Change Password", size=18, weight="bold", color=TEXT_DARK),
        ft.Text("Use a strong, unique password to keep your account safe.", color=TEXT_MUTED, size=13),
    ], spacing=5)
    password_fields = ft.Column([
        ref_current_pw,
        ref_new_pw,
        ref_confirm_pw,
    ], spacing=15, width=450)
    save_btn_row = ft.Row([
        ft.Button(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCK_ROUNDED, color="white"),
                ft.Text("Update Password", weight="bold", color="white"),
            ], tight=True, spacing=10),
            bgcolor=ACCENT_BLUE,
            height=45,
            on_click=handle_update_password
        )
    ], alignment=ft.MainAxisAlignment.END)

    dash.detail_area.controls.extend([
        header_text,
        ft.Divider(height=30, color="transparent"),
        password_fields,
        ft.Divider(height=20, color="transparent"),
        save_btn_row
    ])
    
    dash.page.update()
# --- TAB: PAYMENT (Payment Methods Management) ---
def draw_payment_tab(dash, *args):
    dash.detail_area.controls.clear()

    # 1. SECTION: SAVED PAYMENT METHODS
    dash.detail_area.controls.append(
        ft.Text("Saved Payment Methods", size=18, weight="bold", color=TEXT_DARK)
    )

    # Mock data for saved cards
    saved_cards = [
        {"type": "VISA", "number": "**** **** **** 4242", "exp": "12/28", "color": ft.Colors.BLUE_900},
        {"type": "MASTERCARD", "number": "**** **** **** 8888", "exp": "05/27", "color": ft.Colors.DEEP_ORANGE_900},
    ]

    card_list = ft.Row(spacing=20, scroll=ft.ScrollMode.AUTO)
    
    for card in saved_cards:
        card_list.controls.append(
            ft.Container(
                width=320, height=180,
                bgcolor=card["color"],
                border_radius=15,
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Text(card["type"], size=18, weight="bold", italic=True, color="white"),
                        ft.Icon(ft.Icons.CONTACTLESS_ROUNDED, color="white", size=24),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(expand=True),
                    ft.Text(card["number"], size=18, weight="bold", color="white", font_family="monospace"),
                    ft.Container(expand=True),
                    ft.Row([
                        ft.Column([
                            ft.Text("CARD HOLDER", size=9, color=ft.Colors.BLUE_GREY_100, weight="bold"),
                            ft.Text("JOHNATHAN DOE", size=12, color="white", weight="bold"),
                        ], spacing=2),
                        ft.Column([
                            ft.Text("EXPIRES", size=9, color=ft.Colors.BLUE_GREY_100, weight="bold"),
                            ft.Text(card["exp"], size=12, color="white", weight="bold"),
                        ], spacing=2),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
            )
        )

    # 2. SECTION: ADD NEW METHOD
    dash.detail_area.controls.extend([
        card_list,
        ft.Divider(height=40, color=ft.Colors.GREY_300),
        ft.Text("Add New Payment Method", size=18, weight="bold", color=TEXT_DARK)
    ])
    
    add_method_options = ft.Row([
        # Option: Card
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ADD_CARD_ROUNDED, size=30, color=ACCENT_BLUE),
                ft.Text("Credit/Debit Card", weight="bold", color=TEXT_DARK, size=13)
            ], alignment="center", horizontal_alignment="center"),
            width=170, height=110,
            bgcolor=CARD_BG,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=12,
            ink=True,
            on_click=lambda e: open_add_card_dialog(dash)
        ),
        # Option: E-Wallet
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, size=30, color=ft.Colors.GREEN_800),
                ft.Text("E-Wallet", weight="bold", color=TEXT_DARK, size=13)
            ], alignment="center", horizontal_alignment="center"),
            width=170, height=110,
            bgcolor=CARD_BG,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=12,
            ink=True,
            on_click=lambda e: open_ewallet_dialog(dash, e)
        ),
    ], spacing=20)

    dash.detail_area.controls.append(add_method_options)
    dash.page.update()
    if dash.page:
        dash.page.update()

def open_add_card_dialog(dash):
    
    ref_card_num = ft.TextField(label="Card Number", hint_text="0000 0000 0000 0000", border_color=ACCENT_BLUE)
    ref_holder = ft.TextField(label="Card Holder", hint_text="MR J SMITH", border_color=ACCENT_BLUE)
    ref_exp = ft.TextField(label="Expiry", hint_text="MM/YY", expand=True, border_color=ACCENT_BLUE)
    ref_cvv = ft.TextField(label="CVV", hint_text="***", expand=True, password=True, border_color=ACCENT_BLUE)
    ref_postcode = ft.TextField(label="Postcode", hint_text="BS1 5TY", border_color=ACCENT_BLUE)
    
    def handle_save_card(e):
        if not ref_card_num.value or not ref_holder.value:
            dash.show_message("Please fill in card details!")
            return
        # LOGIC SAVE DATABASE
        print(f"Linking Card: {ref_card_num.value} for {ref_holder.value}")
        
        dash.close_dialog()
        dash.show_message("Card linked successfully!")
        draw_payment_tab(dash)
        
    card_form = ft.Column([
        ft.Text("Enter Debit/Credit Card Details", color=TEXT_MUTED, size=13),
        ref_card_num,
        ref_holder,
        ft.Row([ref_exp, ref_cvv], spacing=20),
        ref_postcode,
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton(
            content=ft.Text("Cancel", weight="bold", color=ACCENT_BLUE),
            on_click=lambda _: dash.close_dialog()
        ),
        ft.Button(
            content=ft.Text("Link Card", weight="bold", color="white"),
            bgcolor=ACCENT_BLUE,
            on_click=handle_save_card
        ),
    ]
    
    dash.show_custom_modal("Add Payment Method", card_form, actions)

def open_ewallet_dialog(dash, e):
    def handle_wallet_click(wallet_name):
        dash.close_dialog()

        if wallet_name == "PayPal":
            dash.page.launch_url("https://www.paypal.com/uk/signin")
            dash.show_message("Redirecting to PayPal...")
        elif wallet_name == "Apple Pay":
            dash.show_message("Apple Pay is only available on supported iOS/macOS devices.")
        elif wallet_name == "Google Pay":
            dash.page.launch_url("https://pay.google.com/")
            dash.show_message("Redirecting to Google Pay...")
            
    wallet_content = ft.Column([
        ft.Text("Select your Digital Wallet", weight="bold"),
        ft.ListTile(
            leading=ft.Icon(ft.Icons.PAYPAL_ROUNDED, color="#003087", size=28),
            title=ft.Text("PayPal", weight="bold", color=TEXT_WHITE),
            subtitle=ft.Text("Secure online payments", size=11),
            on_click=lambda _: handle_wallet_click("PayPal")
        ),
        ft.ListTile(
            leading=ft.Icon(ft.Icons.APPLE_ROUNDED, color="black", size=28),
            title=ft.Text("Apple Pay", weight="bold", color=TEXT_WHITE),
            subtitle=ft.Text("Pay with Touch ID or Face ID", size=11),
            on_click=lambda _: handle_wallet_click("Apple Pay")
        ),
        ft.ListTile(
            leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, color="#4285F4", size=28),
            title=ft.Text("Google Pay", weight="bold", color=TEXT_WHITE),
            subtitle=ft.Text("Fast, simple way to pay", size=11),
            on_click=lambda _: handle_wallet_click("Google Pay")
        )
    ], tight=True, spacing=5, width=400)
    
    actions = [
        ft.TextButton("Cancel", on_click=dash.close_dialog),
        
    ]
    dash.show_custom_modal("Digital Wallet", wallet_content)

# --- TAB: SUPPORT (Contact Info) ---
def draw_support_tab(dash):
    dash.detail_area.controls.clear()
    
    support_card = ft.Container(
        border=ft.border.all(1, ft.Colors.GREY_200),
        border_radius=12,
        padding=25,
        content=ft.Column([
            ft.Text("Property Manager Contact", size=16, weight="bold", color=ACCENT_BLUE),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PHONE_ROUNDED, color=ACCENT_BLUE),
                title=ft.Text("Phone: +84 123 456 789", weight="bold", color=TEXT_DARK),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.EMAIL_ROUNDED, color=ACCENT_BLUE),
                title=ft.Text("Email: manager.paragon@gmail.com", weight="bold", color=TEXT_DARK),
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.BUSINESS_ROUNDED, color=ACCENT_BLUE),
                title=ft.Text("Office Hours: 08:00 AM - 05:00 PM", weight="bold", color=TEXT_DARK),
            ),
        ])
    )
    dash.detail_area.controls.append(support_card)
