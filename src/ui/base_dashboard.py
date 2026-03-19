# Elena Ho - 25044389

from time import sleep
import flet as ft
from matplotlib.pyplot import title

# -------------------------------
# COLOR PALETTE
# -------------------------------
NAVY_PRIMARY = "#0A1A2F"
NAVY_SECOND = "#1C3557"
ACCENT_BLUE = "#1D4ED8"
ACCENT_BLUE_LIGHT = "#3B82F6"
MAIN_BG = "#F2F4F7"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#0B0E11"
TEXT_MUTED = "#515358"
TEXT_WHITE = "#FFFFFF"

# BASE DASHBOARD LAYOUT FOR ALL ROLES
class BaseDashboard(ft.Container):
    def __init__(self, page: ft.Page, username: str, role_name: str):
        super().__init__()
        page.window_width = 1400
        page.window_height = 900
        page.window_resizable = True
        
        page.padding = 0
        self.username = username
        self.role_name = role_name

        page.title = f"PAMS – {role_name} Dashboard"
        page.bgcolor = MAIN_BG
        self.expand = True
        self.sidebar_width = 270
        self.nav_container = ft.Column(spacing=5)

        # Header
        self.header_title = ft.Text("Dashboard", size=24, weight="bold", color=TEXT_DARK)
        self.header_subtitle = ft.Text("", size=13, color=TEXT_MUTED, weight="w500")
        
        self.common_header = ft.Container(
            height=80,
            bgcolor=CARD_BG,
            border=ft.border.only(bottom=ft.BorderSide(1, "#E5E7EB")),
            padding=ft.Padding(20, 0, 20, 0),
            content=ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.Column(
                        spacing=0,
                        alignment="center",
                        controls=[self.header_title, self.header_subtitle]
                    ),
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.IconButton(ft.Icons.HELP_OUTLINE, icon_color=TEXT_DARK),
                        ]
                    )
                ]
            )
        )
        
        # Content area container
        self.content_column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
        )
        self.detail_area = ft.Column(expand=True, spacing=15)
        
        self.main_area = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                self.common_header,
                ft.Container(content=self.content_column, expand=True, padding=ft.Padding(20, 20, 20, 20))
            ]
        )
        
        self.content = ft.Row(
            [
                self._build_sidebar(),
                ft.Container(content=self.main_area, expand=True, bgcolor=MAIN_BG)
            ],
            expand=True,
            spacing=0
        )
        self.content = self.content

    # SIDEBAR DESIGN
    def _build_sidebar(self):
        return ft.Container(
            width=self.sidebar_width,
            bgcolor=NAVY_PRIMARY,
            padding=20,
            content=ft.Column(
                controls=[
                    # ----- LOGO -----
                    ft.Icon(ft.Icons.APARTMENT_ROUNDED, size=30, color=ACCENT_BLUE),
                    ft.Text("PAMS", size=30, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Divider(thickness=1, color=NAVY_SECOND),
                    self.nav_container,
                    
                    ft.Container(expand=True),

                    # ----- AVATAR + USERNAME -----
                    ft.Container(
                        padding=ft.padding.only(bottom=10),
                        content=ft.Row(
                            spacing=10,
                            controls=[
                                ft.CircleAvatar(
                                    radius=30,
                                    #foreground_image_url=""
                                ),
                                ft.Column(
                                    spacing=0,
                                    controls=[
                                        ft.Text(self.username, size=16, weight="bold", color="white"),
                                        ft.Text(self.role_name, size=14, color=ACCENT_BLUE_LIGHT),
                                    ]
                                )
                            ]
                        )
                    ),

                    # ----- LOGOUT BUTTON -----
                    ft.Container(
                        on_click=self.logout,
                        padding=15,
                        border_radius=8,
                        ink=True,
                        content=ft.Row([
                            ft.Icon(ft.Icons.LOGOUT, color="white", size=20),
                            ft.Text("Logout", size=14, color="white"),
                        ])
                    )
                ]
            )
        )
        
    # ADD NAVIGATION BUTTON
    def create_nav_btn(self, text, icon, on_click):
        btn = ft.Container(
            padding=15,
            border_radius=8,
            ink=True,
            content=ft.Row([
                ft.Icon(icon, color="white", size=20),
                ft.Text(text, size=14, color="white")
            ]),
            on_click=on_click,
        )
        self.nav_container.controls.append(btn)
        return btn

    def switch_page(self, title, subtitle, page_content_func):
        self.header_title.value = title
        self.header_subtitle.value = subtitle
        self.content_column.controls.clear()
        try:
            try:
                page_content_func(self)
            except TypeError:
                page_content_func()
        except RuntimeError as ex:
            if "Control must be added to the page first" not in str(ex):
                raise

        if self.parent:
            self.page.update()
            
    # LOGOUT ACTION (Updated)
    def logout(self, e):
        # 1. Show confirmation toast
        self.show_message("Logging out...")
        
        if self.page:
            # 2. Clear current dashboard interface
            self.page.controls.clear()
            
            self.page.window_width = 450
            self.page.window_height = 650
            self.page.window_resizable = False
            try:
                # Thử cách mới của Flet 0.21+
                self.page.window.center()
            except:
                # Cách cũ hơn hoặc dự phòng
                self.page.window_center = True
            
            import login_dashboard
            login_dashboard.main(self.page)
            
            self.page.update()

    async def close_app_task(self):
        from asyncio import sleep as async_sleep
        await async_sleep(0.5)
        await self.page.window.close()
    
    # COMPONENT: Stat card
    def create_stat_card(self, title, value, icon, highlight=False):
        return ft.Container(
            bgcolor=CARD_BG, padding=20,border_radius=12, expand=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            ),
            content=ft.Row(
                controls=[
                    ft.Container(
                        bgcolor=ACCENT_BLUE_LIGHT if highlight else "#F3F4F6",
                        padding=12,
                        border_radius=10,
                        content=ft.Icon(
                            icon, color="white" if highlight else ACCENT_BLUE,size=26
                        ),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(title, size=12, color="#4B5563"),
                            ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ]
                    )
                ]
            )
        )
    
    # SHOW POPUP DIALOG
    def show_popup(self, title: str, content=None, width=600, height=600, actions=None):
        self.page.dialog = None
        
        display_actions = actions
        if display_actions is None:
            display_actions = [
                ft.TextButton(
                    content=ft.Text("Close", weight="bold"),
                    on_click=lambda _: self.close_dialog()
                )
            ]
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight="bold", color=TEXT_DARK),
            content=ft.Container(
                content=content,
                width=width,
                height=height,
                padding=10
            ),
            actions=display_actions
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_custom_modal(self, title, content, actions=None):
        self.page.overlay.clear()
        self.active_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight="bold", color=ft.Colors.BLUE_ACCENT_200),
            content=ft.Container(content=content, width=450, padding=10),
            actions=actions if actions else [
                ft.TextButton(
                    content=ft.Text("Close", weight="bold"),
                    on_click=lambda _: self.close_dialog()
                )
            ],
        )
        self.page.overlay.append(self.active_dialog)
        self.active_dialog.open = True
        self.page.update()

    def close_dialog(self, e=None):
        if hasattr(self, "active_dialog"):
            self.active_dialog.open = False
            self.page.update()

    # SHOW MESSAGE (info / warning / error)
    def show_message(self, message: str):
        if self.page:
            snack = ft.SnackBar(ft.Text(message), bgcolor=ACCENT_BLUE)
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()

# # ====================================================
# # SAMPLE MAIN (run this file alone to test)
# # ====================================================
# def main(page: ft.Page):

#     dashboard = BaseDashboard(page, "Sara", "Admin")

#     # Example nav button
#     dashboard.create_nav_btn("My Profile", ft.Icons.PERSON, lambda e: dashboard.show_message("Profile Clicked"))
#     dashboard.create_nav_btn("Payment Method", ft.Icons.PAYMENT, lambda e: dashboard.show_message("Payment Clicked"))
#     dashboard.create_nav_btn("Terms & Conditions", ft.Icons.DESCRIPTION, lambda e: dashboard.show_message("Terms Clicked"))
#     dashboard.create_nav_btn("Support", ft.Icons.CONTACT_SUPPORT, lambda e: dashboard.show_message("Support Clicked"))

#     page.add(dashboard)

# if __name__ == "__main__":
#     ft.run(main)
