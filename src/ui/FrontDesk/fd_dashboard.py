import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)
# Đoạn code trên đang thêm thư mục cha của file hiện tại vào sys.path để có thể import các module từ thư mục đó để chạy test. Điều này giúp tránh lỗi ImportError khi import các module khác trong dự án. Sau này sẽ sửa lại, dùng .. để import trực tiếp thay vì sửa sys.path như này.

from logic.notifications import *
from base_dashboard import *
from residents import *
from work_orders import *
from parcel_mgr import *
from settingsStaff import *

import flet as ft

class FrontDeskDashboard(BaseDashboard):
    def __init__(self, page: ft.Page, username: str, role_name: str = "Front Desk"):
        super().__init__(page, username, role_name=role_name)
        
        self.create_nav_btn(
            "Overview",
            ft.Icons.DASHBOARD_ROUNDED,
            lambda _: self.switch_page("Overview", "Building Status Summary", self.show_overview)
        )
        self.create_nav_btn(
            "Residents",
            ft.Icons.PEOPLE_ALT_ROUNDED,
            lambda _: self.switch_page("Resident Directory", "Search and manage apartment occupants", show_residents)
        )
        self.create_nav_btn(
            "Parcel Management",
            ft.Icons.INVENTORY_2_ROUNDED,
            lambda _: self.switch_page("Parcel Management", "Track and deliver incoming packages", show_parcel)
        )
        self.create_nav_btn(
            "Work Orders",
            ft.Icons.HANDYMAN_ROUNDED,
            lambda _: self.switch_page("Work Orders", "Handle maintenance requests from residents", show_work_orders)
        )
        self.create_nav_btn(
            "Settings",
            ft.Icons.SETTINGS_ROUNDED,
            lambda _: self.switch_page("Settings", "Account and system preferences", show_settings)
        )
    
    def show_overview(self, *args):
        self.detail_area = ft.Column(expand=True, spacing=15)

        stats_row = ft.Row(
            spacing=20,
            controls=[
                self.create_stat_card("Occupied Units", "185/200", ft.Icons.APARTMENT),
                self.create_stat_card("Pending Parcels", "24", ft.Icons.INVENTORY_2_ROUNDED, highlight=True),
                self.create_stat_card("Open Orders", "8", ft.Icons.BUILD_CIRCLE),
            ]
        )

        # MAIN LAYOUT
        main_layout = ft.Row(
            expand=True,
            vertical_alignment="start",
            controls=[
                # Cột trái: Thông báo khẩn & Công việc (60%)
                ft.Column(
                    expand=6,
                    controls=[
                        ft.Text("Urgent Work Orders", size=18, weight="bold", color=TEXT_DARK),
                        ft.Container(
                            bgcolor="white", padding=20, border_radius=12,
                            content=ft.Text("No urgent repair requests at the moment.", italic=True, color=TEXT_DARK)
                        )
                    ]
                ),
                # Cột phải: Log bưu phẩm gần đây (40%)
                ft.Column(
                    expand=4,
                    controls=[
                        ft.Text("Recent Parcels", size=18, weight="bold", color=TEXT_DARK),
                        ft.Container(
                            bgcolor="white", padding=20, border_radius=12,
                            content=ft.Column([
                                ft.ListTile(leading=ft.Icon(ft.Icons.LOCAL_SHIPPING, color= ACCENT_BLUE), title=ft.Text("Room 302 - SPX", color=TEXT_DARK), subtitle=ft.Text("10 mins ago")),
                                ft.ListTile(leading=ft.Icon(ft.Icons.LOCAL_SHIPPING, color=ACCENT_BLUE), title=ft.Text("Room 105 - GrabFood", color=TEXT_DARK), subtitle=ft.Text("25 mins ago")),
                            ])
                        )
                    ]
                )
            ]
        )

        self.content_column.controls = [stats_row, main_layout]
        self.page.update()
        
def main(page: ft.Page):
    dashboard = FrontDeskDashboard(page, "Sara", "Front Desk")

    page.add(dashboard)
    dashboard.switch_page("Dashboard", "Welcome back to your overview", dashboard.show_overview)
            
if __name__ == "__main__":
    ft.run(main)
