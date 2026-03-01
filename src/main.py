import flet as ft
import ui.login_dashboard as login_dashboard

def main(page: ft.Page):
    login_dashboard.main(page)

if __name__ == "__main__":
    ft.app(target=main)