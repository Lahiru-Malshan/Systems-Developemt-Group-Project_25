
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from base_dashboard import *
from .work_orders import *
from settingsStaff import *
from backend.Maintance.maintenance_process import MaintenanceProcessBackend
import flet as ft

class MaintenanceDashboard(BaseDashboard):
    def __init__(self, page: ft.Page, username: str, role_name: str = "Maintenance Staff"):
        super().__init__(page, username, role_name=role_name)

        self.create_nav_btn(
            "Dashboard",ft.Icons.DASHBOARD_ROUNDED,lambda _: self.switch_page("Dashboard", "Welcome back to your overview", self.show_dashboard)
        )

        self.create_nav_btn(
            "Work Orders",ft.Icons.HANDYMAN_ROUNDED,lambda _: self.switch_page("Work Orders", "View and manage work orders", show_work_orders)
        )

        self.create_nav_btn(
            "Settings",ft.Icons.SETTINGS_ROUNDED,lambda _: self.switch_page("Settings", "Manage your account and preferences", show_settings)
        )

        self.switch_page("Dashboard", "Welcome back to your overview", self.show_dashboard)
    
# FUNCTIONS TO DISPLAY CONTENT
    def show_dashboard(self, *args):

        backend = MaintenanceProcessBackend(user_id=getattr(self, "user_id", None), username=self.username)
        stats = backend.get_dashboard_stats()
        urgent_requests = backend.get_urgent_tasks(limit=3)

        self.content_column.controls.clear()

        # --- 1. WELCOME HEADER ---
        header = ft.Container(
            content=ft.Column([
                ft.Text("Maintenance Overview", size=24, weight="bold", color=TEXT_DARK),
                ft.Text("Quick glance at your tasks and building status", size=14, color=TEXT_MUTED)
            ], spacing=5)
        )

        # --- 2. QUICK STATS ---
        stats_row = ft.Row([
            self.create_stat_card("New Requests", str(stats["new_requests"]), ft.Icons.FIBER_NEW_ROUNDED),
            self.create_stat_card("On-Going", str(stats["ongoing"]), ft.Icons.HANDYMAN_ROUNDED),
            self.create_stat_card("Resolved", str(stats["resolved"]), ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED),
        ], spacing=20)

        # --- 3. URGENT TASKS SECTION ---
        urgent_label = ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_700, size=20),
            ft.Text("Urgent Attention Required", weight="bold", size=16, color=TEXT_DARK),
        ], spacing=10)

        urgent_list = ft.Column(spacing=10)
        if urgent_requests:
            for item in urgent_requests:
                urgent_list.controls.append(self._create_urgent_card(item["room"], item["issue"], item["reportedDate"], item["status"]))
        else:
            urgent_list.controls.append(
                ft.Container(
                    bgcolor=CARD_BG,
                    padding=15,
                    border_radius=10,
                    content=ft.Text("No assigned work orders require attention right now.", color=TEXT_MUTED)
                )
            )

        # --- 4. MAIN LAYOUT  ---
        main_content = ft.Row([
            ft.Column([
                urgent_label,
                urgent_list,
                ft.TextButton(
                    "View all work orders",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=lambda _: show_work_orders(self)
                )
            ], expand=2, spacing=15),
            
            ft.Column([
                ft.Text("System Status", weight="bold", size=16, color=TEXT_DARK),
                self._create_infrastructure_status()
            ], expand=1, spacing=15)
        ], alignment="start", vertical_alignment="start", spacing=30)

        self.content_column.controls.extend([
            header,
            ft.Divider(height=10, color="transparent"),
            stats_row,
            ft.Divider(height=20, color="transparent"),
            main_content
        ])
        self.page.update()

    def _create_urgent_card(self, room, issue, time, label):
        return ft.Container(
            bgcolor=CARD_BG,
            padding=15,
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.RED_100),
            content=ft.Row([
                ft.Icon(ft.Icons.REPORT_PROBLEM_ROUNDED, color=ft.Colors.RED_700),
                ft.Column([
                    ft.Text(f"Unit {room}", weight="bold", color=TEXT_DARK),
                    ft.Text(issue, color=TEXT_MUTED, size=13),
                ], expand=True, spacing=2),
                ft.Text(label, size=11, weight="bold", color=ft.Colors.RED_700),
            ])
        )

    def _create_infrastructure_status(self):
        return ft.Container(
            bgcolor=CARD_BG,
            padding=20,
            border_radius=12,
            content=ft.Column([
                self._status_row("Elevator Block A", "Active", ft.Colors.GREEN_700),
                self._status_row("Water Pump", "Warning", ft.Colors.ORANGE_700),
                self._status_row("Backup Gen", "Offline", ft.Colors.RED_700),
            ], spacing=10)
        )

    def _status_row(self, name, status, color):
        return ft.Row([
            ft.Text(name, color=TEXT_DARK, size=13, expand=True),
            ft.Container(
                content=ft.Text(status, size=10, color="white", weight="bold"),
                bgcolor=color, padding=ft.Padding.symmetric(horizontal=8, vertical=2), border_radius=5
            )
        ])

#Test case
def main(page: ft.Page):
    dashboard = MaintenanceDashboard(page, "Sara", "Maintenance Staff")

    page.add(dashboard)
    dashboard.switch_page("Dashboard", "Welcome back to your overview", dashboard.show_dashboard)
            
if __name__ == "__main__":
    ft.run(main)