import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Đoạn code trên đang thêm thư mục cha của file hiện tại vào sys.path để có thể import các module từ thư mục đó để chạy test. Điều này giúp tránh lỗi ImportError khi import các module khác trong dự án. Sau này sẽ sửa lại, dùng .. để import trực tiếp thay vì sửa sys.path như này.

from base_dashboard import *
from payments import *
from maintenance import *
from settings import *
from notifications import *
from flet_charts import PieChart, PieChartSection
import flet as ft

class TenantDashboard(BaseDashboard):
    def __init__(self, page: ft.Page, username: str, role_name: str = "Tenant"):
        super().__init__(page, username, role_name=role_name)
        
        self.create_nav_btn(
            "Dashboard",ft.Icons.DASHBOARD_ROUNDED,lambda _: self.switch_page("Dashboard", "Welcome back to your overview", self.show_dashboard)
        )

        self.create_nav_btn(
            "My Payments",ft.Icons.PAYMENTS_ROUNDED,lambda _: self.switch_page("My Payments", "Manage your rent and history", show_payments)
        )

        self.create_nav_btn(
            "Maintenance",ft.Icons.HANDYMAN_ROUNDED,lambda _: self.switch_page("Maintenance", "Request repairs and tracking", show_maintenance)
        )

        self.create_nav_btn(
            "Notifications",ft.Icons.NOTIFICATIONS_ROUNDED,lambda _: self.switch_page("Notifications", "Stay updated with latest news", show_notifications)
        )

        self.create_nav_btn(
            "Settings",ft.Icons.SETTINGS_ROUNDED,lambda _: self.switch_page("Settings", "Manage your account and preferences", self.show_settings)
        )
        
# FUNCTIONS TO DISPLAY CONTENT
    def show_dashboard(self):
        # STAT CARDS
        stat_cards = ft.Row(
            spacing=20,
            controls=[
                self.create_stat_card("Next Rent Due", "£1,200", ft.Icons.CALENDAR_MONTH_ROUNDED),
                self.create_stat_card("Payment Status", "On Time", ft.Icons.CHECK_CIRCLE_ROUNDED),
                self.create_stat_card("Unread Notifs", "3 New", ft.Icons.ERROR_OUTLINE_ROUNDED, highlight=True),
            ]
        )
        
        # CHART + TABLE AREA
        chart_table_row = ft.Row(
            spacing=20,
            controls=[
                ft.Container(
                    bgcolor=CARD_BG,
                    padding=25,
                    border_radius=12,
                    width=600,
                    height=350,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text("Payments History", size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            ft.Container(
                                expand=True,
                                bgcolor="#F9FAFB",
                                border=ft.Border.all(1, "#E5E7EB"),
                                border_radius=8,
                                alignment=ft.alignment.center if hasattr(ft.alignment, "center") else "center",
                                content=ft.Text("Chart Placeholder", color=TEXT_MUTED)
                            )
                        ]
                    )
                ),

                ft.Container(
                    bgcolor=CARD_BG,
                    padding=25,
                    border_radius=12,
                    expand=True,
                    height=350,
                    content=ft.Column(
                        controls=[
                            ft.Text("Announcements", size=16, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            ft.Divider(height=1, color="#F3F4F6"),
                            # Example announcements (replace with dynamic content later)
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.INFO_OUTLINE, color=ACCENT_BLUE),
                                title=ft.Text("Hệ thống bảo trì điện", weight=ft.FontWeight.BOLD, color=TEXT_DARK, size=14),
                                subtitle=ft.Text("Vào chủ nhật tuần này, từ 8:00 đến 12:00.",
                                color=ft.Colors.BLACK87,weight=ft.FontWeight.W_500),
                            ),
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.CAMPAIGN_OUTLINED, color=ACCENT_BLUE),
                                title=ft.Text("Thu gom rác"),
                                subtitle=ft.Text("Vui lòng để rác đúng nơi quy định trước 7:00 sáng."),
                            ),
                        ]
                    )
                )
                
            ]
        )
        self.content_column.controls = [
            stat_cards,chart_table_row
        ]

    def show_settings(self, active_tab="My Profile"):
        if not isinstance(active_tab, str):
            active_tab = "My Profile"
        self.detail_area = ft.Column(expand=True, spacing=20)
        
        # Routing to specific tab content
        if active_tab == "My Profile":
            draw_my_profile_tab(self)
        elif active_tab == "Security":
            draw_security_tab(self)
        elif active_tab == "Support":
            draw_support_tab(self)
        elif active_tab == "Payment Method":
            draw_payment_tab(self)
        else:
            self.detail_area.controls.append(
                ft.Container(
                    content=ft.Text(f"Settings for {active_tab} will be available soon.",italic=True, weight="bold", color=TEXT_MUTED),
                    padding=30
                )
            )
            
        # PROFILE HEADER SECTION
        header_container = ft.Container(
            bgcolor=CARD_BG,
            padding=30,
            border_radius=12,
            content=ft.Row([
                # Avatar Container
                ft.Container(
                    width=100, height=100,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    border_radius=50,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text("👤", size=50)
                ),
                ft.VerticalDivider(width=20, color="transparent"),
                # Main Profile Information
                ft.Column([
                    ft.Text(self.username, size=24, weight="bold", color=TEXT_DARK),
                    ft.Text(f"Role: {self.role_name}", size=14, weight="bold", color=TEXT_MUTED),
                    ft.Text("Apartment: Block B - Unit 302", size=14, weight="bold", color=ACCENT_BLUE),
                ], spacing=5, expand=True),
                # Control Buttons
                ft.Column([
                    ft.OutlinedButton(
                        "Logout",
                        icon=ft.Icons.LOGOUT_ROUNDED,
                        style=ft.ButtonStyle(color=ft.Colors.GREY_700),
                        width=160,
                        # CONNECTED: Link to logout function in base_dashboard
                        on_click=self.logout
                    ),
                    ft.OutlinedButton(
                        "Delete Account",
                        icon=ft.Icons.DELETE_FOREVER_ROUNDED,
                        style=ft.ButtonStyle(color=ft.Colors.RED_700),
                        width=200,
                        on_click=lambda _: self.show_message("Request to delete account sent!")
                    ),
                ], spacing=10, alignment=ft.MainAxisAlignment.START)
            ])
        )

        # SUB-MENU NAVIGATION (Tab Bar)
        tabs = ["My Profile", "Security", "Payment Method", "Support", "Terms & FAQ"]
        tab_buttons = []
        for tab_name in tabs:
            is_active = (tab_name == active_tab)
            
            # Create tab item container
            tab_item = ft.Container(
                content=ft.Text(
                    tab_name,
                    weight="bold",
                    color=ACCENT_BLUE if is_active else ft.Colors.GREY_600
                ),
                padding=ft.Padding(20, 15, 20, 15),
                border=ft.Border(bottom=ft.BorderSide(3, ACCENT_BLUE)) if is_active else None,
                on_click=lambda e, t=tab_name: self.show_settings(t),
            )
            
            # Safely assign cursor for Python 3.14/Flet latest
            try:
                tab_item.mouse_cursor = "hand"
            except:
                pass
                
            tab_buttons.append(tab_item)

        sub_menu = ft.Row(tab_buttons, spacing=0)

        # 3. DYNAMIC CONTENT AREA
        content_card = ft.Container(
            bgcolor=CARD_BG,
            padding=30,
            border_radius=12,
            expand=True,
            content=ft.Column([
                sub_menu,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                ft.Container(height=10),
                self.detail_area
            ], scroll=ft.ScrollMode.AUTO)
        )

        self.content_column.controls = [header_container, content_card]
        if self.page:
            self.page.update()
    
def main(page: ft.Page):
    dashboard = TenantDashboard(page, "Sara", "Tenant")

    page.add(dashboard)
    dashboard.switch_page("Dashboard", "Welcome back to your overview", dashboard.show_dashboard)
            
if __name__ == "__main__":
    ft.run(main)