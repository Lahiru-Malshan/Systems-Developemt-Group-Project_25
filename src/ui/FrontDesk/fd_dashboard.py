
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic.notifications import *
from base_dashboard import *
from .residents import *
from .work_orders import *
from .parcel_mgr import *
from settingsStaff import *
from backend.FrontDesk.frontdesk import FrontDeskBackend

import flet as ft

class FrontDeskDashboard(BaseDashboard):
    def __init__(self, page: ft.Page, username: str, role_name: str = "Front Desk Staff"):
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

        self.switch_page("Overview", "Building Status Summary", self.show_overview)
    
    def show_overview(self, *args):
        backend = FrontDeskBackend(user_id=getattr(self, "user_id", None), username=self.username)
        stats = backend.get_dashboard_stats()
        recent_orders = backend.get_recent_open_orders(limit=3)
        recent_parcels = backend.get_recent_parcels(limit=3)

        self.detail_area = ft.Column(expand=True, spacing=15)

        stats_row = ft.Row(
            spacing=20,
            controls=[
                self.create_stat_card("Occupied Units", stats["occupied_units_label"], ft.Icons.APARTMENT),
                self.create_stat_card("Pending Parcels", str(stats["pending_parcels"]), ft.Icons.INVENTORY_2_ROUNDED, highlight=True),
                self.create_stat_card("Open Orders", str(stats["open_orders"]), ft.Icons.BUILD_CIRCLE),
            ]
        )

        # MAIN LAYOUT
        main_layout = ft.Row(
            expand=True,
            vertical_alignment="start",
            controls=[
                # LEFT COLUMN
                ft.Column(
                    expand=6,
                    controls=[
                        ft.Text("Urgent Work Orders", size=18, weight="bold", color=TEXT_DARK),
                        ft.Container(
                            bgcolor="white", padding=20, border_radius=12,
                            content=ft.Column(
                                [
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.BUILD_CIRCLE, color=ACCENT_BLUE),
                                        title=ft.Text(f"Unit {item['apartment_number']} - {item['resident_name']}", color=TEXT_DARK),
                                        subtitle=ft.Text(item["description"], color=TEXT_MUTED),
                                    )
                                    for item in recent_orders
                                ]
                                or [ft.Text("No open repair requests at the moment.", italic=True, color=TEXT_DARK)]
                            )
                        )
                    ]
                ),
                # RIGHT COLUMN
                ft.Column(
                    expand=4,
                    controls=[
                        ft.Text("Recent Parcels", size=18, weight="bold", color=TEXT_DARK),
                        ft.Container(
                            bgcolor="white", padding=20, border_radius=12,
                            content=ft.Column([
                                *[
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.LOCAL_SHIPPING, color=ACCENT_BLUE),
                                        title=ft.Text(f"Unit {item['room']} - {item['carrier']}", color=TEXT_DARK),
                                        subtitle=ft.Text(f"Recipient: {item['display_recipient']}", color=TEXT_MUTED),
                                    )
                                    for item in recent_parcels
                                ]
                            ] or [ft.Text("No parcels logged yet.", italic=True, color=TEXT_DARK)])
                        )
                    ]
                )
            ]
        )

        self.content_column.controls = [stats_row, main_layout]
        self.page.update()

# #Test case
# def main(page: ft.Page):
#     dashboard = FrontDeskDashboard(page, "Sara", "Front Desk")

#     page.add(dashboard)
#     dashboard.switch_page("Dashboard", "Welcome back to your overview", dashboard.show_overview)
            
# if __name__ == "__main__":
#     ft.run(main)
