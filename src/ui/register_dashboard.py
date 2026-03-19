import flet as ft
from register import register_user

def register_main(page: ft.Page):
    page.title = "Register"
    
    page.window.width = 1400
    page.window.height = 900
    page.update()
    page.window.center()
    page.update()
    
    page.window.resizable = False
    
    page.padding = 40
    page.bgcolor = "#F2F4F7"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    FIELD_WIDTH = 400
    HALF_WIDTH = 195
    
    username = ft.TextField(label="Username", prefix_icon=ft.Icons.PERSON_OUTLINED, border_color="#1D4ED8", color="#0B0E11", width=FIELD_WIDTH)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINED, border_color="#1D4ED8", color="#0B0E11", width=FIELD_WIDTH)
    first_name = ft.TextField(label="First Name", border_color="#1D4ED8", width=HALF_WIDTH)
    last_name = ft.TextField(label="Last Name", border_color="#1D4ED8", width=HALF_WIDTH)
    email = ft.TextField(label="Email", prefix_icon=ft.Icons.EMAIL_OUTLINED, border_color="#1D4ED8", color="#0B0E11", width=FIELD_WIDTH)
    
    def go_login(e):
        page.controls.clear()
        import ui.login_dashboard as login_dashboard
        login_dashboard.main(page)

    def submit(e):
        if not username.value or not password.value or not email.value:
            page.snack_bar = ft.SnackBar(ft.Text("Please fill in required fields"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        result = register_user(
            username.value,
            password.value,
            first_name.value,
            last_name.value,
            email.value
        )

        if result == "Success":
            page.snack_bar = ft.SnackBar(ft.Text("Registration successful! Redirecting to login..."), bgcolor="green")
            page.snack_bar.open = True
            page.update()
            import time
            time.sleep(1.5)
            go_login(None)
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {result}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    page.controls.clear()
    page.add(
        ft.Column(
            horizontal_alignment="center",
            spacing=18,
            controls=[
                ft.Icon(ft.Icons.PERSON_ADD_ROUNDED, size=60, color="#1D4ED8"),
                ft.Text("JOIN PAMS", size=28, weight="bold", color="#0A1A2F"),
                
                ft.Divider(height=10, color="transparent"),
                username,
                password,
                ft.Row([first_name, last_name], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                email,
                
                ft.Container(height=10),
                
                ft.Button(
                    "CREATE ACCOUNT", bgcolor="#1D4ED8", color="white",
                    width=300, height=50, on_click=submit,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                ),
                
                ft.TextButton("Already have an account? Login", on_click=go_login)
            ]
        )
    )
    page.update()