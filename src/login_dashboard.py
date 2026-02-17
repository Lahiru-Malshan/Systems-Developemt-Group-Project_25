import flet as ft
from flet import Icon
from login import login
# --- DATABASE CONFIGURATION ---

def main(page: ft.Page):
    page.title = "Paragon PAMS - Login"
    page.window_width = 400
    page.window_height = 500
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- EXECUTED LOGIN LOGIC ---
    def login_click(e):
        user_val = username_field.value
        pass_val = password_field.value
        result = login(user_val, pass_val)
        if result == "informationError":
            error_text.value = "Please fill all the information"
            page.update()
        elif result == "Success":
            page.snack_bar = ft.SnackBar(ft.Text("Registration successful!"))
        else:
            error_text.value = "Invalid username or password"
        page.update()

    # --- UI ---
    username_field = ft.TextField(label="username", prefix_icon="person_outline")
    password_field = ft.TextField(label="password", password=True, can_reveal_password=True, prefix_icon="lock_outline")
    error_text = ft.Text(value="", color="red")

    login_card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Text("PARAGON PAMS", size=25, weight=ft.FontWeight.BOLD, color="blue800"),
                    ft.Text("Apartment Manager System"),
                    ft.Divider(),
                    username_field,
                    password_field,
                    error_text,
                    ft.ElevatedButton(
                        "Login", 
                        on_click=login_click,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                        width=200
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=30,
        )
    )

    page.add(login_card)

ft.run(main)
