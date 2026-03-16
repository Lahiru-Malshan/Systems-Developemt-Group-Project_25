from unittest import result

import flet as ft
from flet import Icon
from login import login
# --- DATABASE CONFIGURATION ---

def main(page: ft.Page):
    page.title = "PAMS - Login"
    page.window_width = 1400  
    page.window_height = 900
    page.update()
    # page.window.center() # deprecated await form in newer flet versions
    page.update()
    
    page.window.resizable = True
    page.padding = 40
    page.bgcolor = "#F2F4F7"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- UI ---
    username_field = ft.TextField(
        label="Username", prefix_icon=ft.Icons.PERSON_OUTLINED,
        border_color="#1D4ED8", color="#0B0E11", height=50, width=370
    )
    
    password_field = ft.TextField(
        label="Password", password=True, can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINED, border_color="#1D4ED8",
        color="#0B0E11", height=50, width=370
    )
    
    error_text = ft.Text(value="", color="red", size=12)

    # --- 2. FUNCTIONS ---
    def go_register(e):
        page.controls.clear()
        import ui.register_dashboard as register_dashboard
        register_dashboard.register_main(page)
    
    def redirect_by_role(user_data):
        role = user_data.get("role_id")
        full_name = user_data.get("full_name", user_data.get("username"))
        page.controls.clear()

        # Điều hướng dựa trên 6 Roles
        if role == 1:
            from ui.Administrator.admin_dashboard import AdminDashboard
            page.add(AdminDashboard(page, full_name, "Administrator"))
        elif role == 2:
            from ui.Manager.mgr_dashboard import ManagerDashboard
            page.add(ManagerDashboard(page, full_name, "Manager"))
        elif role == 3:
            from ui.FrontDesk.fd_dashboard import FrontDeskDashboard
            page.add(FrontDeskDashboard(page, full_name, "Front Desk Staff"))
        elif role == 4:
            from ui.Maintenance.ms_dashboard import MaintenanceDashboard
            page.add(MaintenanceDashboard(page, full_name, "Maintenance Staff"))
        elif role == 5:
            from ui.Finance.fm_dashboard import FinanceDashboard
            page.add(FinanceDashboard(page, full_name, "Finance Manager"))
        elif role == 6:
            from ui.Tenant.tenant_dashboard import TenantDashboard
            page.add(TenantDashboard(page, full_name, "Tenant", user_data=user_data))
     
        page.update()

    # --- EXECUTED LOGIN LOGIC ---
    def login_click(e):
        if not username_field.value or not password_field.value:
            error_text.value = "Please fill all the information"
            page.update()
            return
        result = login(username_field.value, password_field.value)
        
        if isinstance(result, dict):
            page.snack_bar = ft.SnackBar(ft.Text(f"Welcome back, {result.get('username')}!"))
            page.snack_bar.open = True
            redirect_by_role(result)
        elif result == "informationError":
            error_text.value = "Information is missing"
        else:
            error_text.value = "Invalid username or password"
        page.update()
        if result == "informationError":
            error_text.value = "Please fill all the information"
            page.update()
    
    # --- 3. ASSIGN EVENTS ---
    password_field.on_submit = login_click
    
    page.controls.clear()
    page.add(
        ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
            controls=[
                ft.Icon(ft.Icons.APARTMENT_ROUNDED, size=60, color="#1D4ED8"),
                ft.Column([
                    ft.Text("PAMS LOGIN", size=28, weight="bold", color="#0A1A2F"),
                    ft.Text("Paragon Apartment Management System", size=14, color="#515358"),
                ], horizontal_alignment="center", spacing=0),
                
                ft.Divider(height=10, color="transparent"),
                username_field,
                password_field,
                error_text,
                
                ft.Button(
                    "LOGIN SYSTEM", bgcolor="#1D4ED8", color="white",
                    width=300, height=50, on_click=login_click,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                ),
                
                ft.Row([
                    ft.Text("Don't you have an account?", size=13, color="#515358"),
                    ft.TextButton("Create Account", on_click=go_register)
                ], alignment="center")
            ]
        )
    )
    page.update()
