import flet as ft
from register import register_user

def main(page: ft.Page):
    page.title = "Register"
    page.window_width = 400
    page.window_height = 500
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True)
    first_name = ft.TextField(label="First Name")
    last_name = ft.TextField(label="Last Name")
    email = ft.TextField(label="Email")

    def submit(e):
        result = register_user(
            username.value,
            password.value,
            first_name.value,
            last_name.value,
            email.value
        )

        if result == "Success":
            page.snack_bar = ft.SnackBar(ft.Text("Registration successful!"))
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error: {result}"))

        page.snack_bar.open = True
        page.update()

    page.add(
        ft.Column([
            username,
            password,
            first_name,
            last_name,
            email,
            ft.ElevatedButton("Register", on_click=submit)
        ])
    )

ft.app(target=main)
