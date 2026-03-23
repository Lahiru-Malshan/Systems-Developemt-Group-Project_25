# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from flet_charts import BarChart, BarChartGroup, BarChartRod, ChartAxis, ChartAxisLabel, ChartGridLines
from datetime import datetime
from logic.search import *
from base_dashboard import *
from settingsStaff import *
from .mgr_user import *
from .assets_leases import *
from .broadcast import *
from .operations import *

class AdminDashboard(BaseDashboard):
    def __init__(self, page: ft.Page, username: str = "Admin_User", role_name: str = "Administrator"):
        super().__init__(page, username, role_name)
        
        self.create_nav_btn("Dashboard", ft.Icons.DASHBOARD_ROUNDED, lambda _: self.switch_page("Dashboard", "Branch Operational Lead", self.show_dashboard))
        
        self.create_nav_btn("Manage User", ft.Icons.SUPERVISED_USER_CIRCLE_ROUNDED, lambda _: self.switch_page("Manage User", "Manage Staff & Residents", show_user))
        
        self.create_nav_btn("Assets & Leases", ft.Icons.HOME_WORK_ROUNDED,lambda _: self.switch_page("Assets & Leases", "Units and Contract Oversight", show_assets))
        
        self.create_nav_btn("Broadcast", ft.Icons.CAMPAIGN_ROUNDED, lambda _: self.switch_page("Broadcast", "Send Branch-wide Alerts", show_broadcast))
        
        self.create_nav_btn( "Operations", ft.Icons.ANALYTICS_ROUNDED, lambda _: self.switch_page("Operations", "Building Maintenance & Tasks", show_operations)
        )
        
        self.create_nav_btn("Settings", ft.Icons.SETTINGS_ROUNDED, lambda _: self.switch_page("Settings", "Manage your account and preferences", show_settings))

        self.switch_page("Dashboard", "Branch Operational Lead", self.show_dashboard)

    def show_dashboard(self, *args):

        self.content_column.controls.clear()

        # --- SECTION 1: STAT CARDS ---
        stats_row = ft.Row([
            self.create_stat_card("Local Staff", "12", ft.Icons.BADGE_ROUNDED, highlight=True),
            self.create_stat_card("Active Residents", "142", ft.Icons.HOUSE_ROUNDED),
            self.create_stat_card("Pending Approvals", "05", ft.Icons.MARK_EMAIL_UNREAD_ROUNDED),
            self.create_stat_card("Vacant Units", "08", ft.Icons.EVENT_AVAILABLE_ROUNDED),
        ], spacing=20)

        # --- SECTION 2: OPERATIONAL AREAS ---
        performance_chart = ft.Container(
            bgcolor=CARD_BG, padding=25, border_radius=12, expand=7,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black")),
            content=ft.Column([
                ft.Row([
                    ft.Text("Weekly Staff Performance", size=18, weight="bold", color=TEXT_DARK),
                    ft.Row([
                        self._create_legend("Front Desk", ACCENT_BLUE),
                        self._create_legend("Maintenance", ft.Colors.ORANGE_400),
                    ], spacing=15)
                ], alignment="spaceBetween"),
                ft.Container(height=20),
                self._build_bar_chart()
            ], expand=True)
        )
        system_alerts = ft.Container(
            bgcolor=CARD_BG, padding=25, border_radius=12, expand=3,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black")),
            content=ft.Column([
                ft.Text("System Alerts", size=18, weight="bold", color=TEXT_DARK),
                ft.Divider(),
                self._create_alert_item("Unverified NI", "Unit B-202 - Missing docs", "High", ft.Colors.RED_400),
                self._create_alert_item("Login Attempt", "Multiple fails from IP: 192...", "Med", ft.Colors.AMBER_600),
                self._create_alert_item("Contract Gap", "Unit A-105 expired today", "Low", ft.Colors.BLUE_400),
                ft.TextButton(
                    "View Security Logs",
                    icon=ft.Icons.SHIELD_OUTLINED,
                    icon_color=TEXT_MUTED,
                    on_click=lambda _: self.switch_page(
                        "Manage User",
                        "Manage Staff & Residents", show_user
                    )
                )
            ], spacing=15)
        )
        
        performance_row = ft.Row(
            controls=[performance_chart, system_alerts],
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
        
        main_layout = ft.Row([
            ft.Container(
                bgcolor=CARD_BG, padding=25, border_radius=12, expand=6,
                content=ft.Column([
                    ft.Text("Registration Requests", size=18, weight="bold", color=TEXT_DARK),
                    ft.Divider(),
                    self._create_approval_card("Alice Smith", "Unit A-101", "Tenant", "10:30 AM"),
                    self._create_approval_card("Bob Brown", "Unit B-205", "Owner", "11:15 AM"),
                ])
            ),
            ft.Container(
                bgcolor=CARD_BG, padding=25, border_radius=12, expand=4,
                content=ft.Column([
                    ft.Text("Staff Activity Feed", size=18, weight="bold", color=TEXT_DARK),
                    ft.Divider(),
                    self._create_activity_row("Front Desk", "Signed Lease for A-202", "2m ago", ft.Icons.GAVEL_ROUNDED),
                    self._create_activity_row("Maintenance", "Fixed leak in B-105", "15m ago", ft.Icons.BUILD_CIRCLE_ROUNDED),
                ], spacing=20)
            )
        ],spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START)

        self.content_column.controls.extend([
            stats_row,
            ft.Divider(height=10, color="transparent"),
            performance_row,
            ft.Divider(height=10, color="transparent"),
            main_layout])

        self.page.update()
    
    def _build_bar_chart(self):
        data = [
            {"day": "Mon", "fd": 15, "mt": 12},
            {"day": "Tue", "fd": 18, "mt": 10},
            {"day": "Wed", "fd": 22, "mt": 15},
            {"day": "Thu", "fd": 14, "mt": 20},
            {"day": "Fri", "fd": 25, "mt": 18},
            {"day": "Sat", "fd": 10, "mt": 8},
        ]
        all_values = []
        for item in data:
            all_values.extend([item["fd"], item["mt"]])
        
        raw_max = max(all_values) if all_values else 20
        max_val = ((raw_max // 5) + 1) * 5
        
        bar_groups = []
        chart_labels = []
        for i, item in enumerate(data):
            chart_labels.append(
                ChartAxisLabel(value=i, label=ft.Text(item["day"], size=12, weight="bold", color=TEXT_DARK))
            )
            
            bar_groups.append(
                BarChartGroup(
                    x=i,
                    rods=[
                        BarChartRod(from_y=0, to_y=item["fd"], color=ACCENT_BLUE, width=12, border_radius=3),
                        BarChartRod(from_y=0, to_y=item["mt"], color=ft.Colors.ORANGE_400, width=12, border_radius=3),
                    ]
                )
            )
            
        return BarChart(
            groups=bar_groups,
            border=ft.Border.all(0, "transparent"),
            left_axis=ChartAxis(
                label_size=40,
                labels=[
                    ChartAxisLabel(
                        value=v,
                        label=ft.Text(str(v), color=TEXT_DARK, size=14)
                    ) for v in range(0, int(max_val) + 5, 5)
                ]
            ),
            bottom_axis=ChartAxis(labels=chart_labels,label_size=30),
            max_y=max_val,
            min_y=0,
            horizontal_grid_lines=ChartGridLines(
                interval=5,
                color=ft.Colors.with_opacity(0.05, TEXT_DARK),
                width=1
            ),
            expand=True,
        )

    def _create_bar_group(self, x, val1, val2):
        """Tạo 1 nhóm cột (Front Desk vs Maintenance)"""
        return BarChartGroup(
            x=x,
            rods=[
                BarChartRod(from_y=0, to_y=val1, color=ACCENT_BLUE, width=15, border_radius=4),
                BarChartRod(from_y=0, to_y=val2, color=ft.Colors.ORANGE_400, width=15, border_radius=4),
            ],
        )

    def _create_legend(self, text, color):
        return ft.Row([
            ft.Container(width=10, height=10, bgcolor=color, border_radius=2),
            ft.Text(text, size=12, color=TEXT_DARK, weight="bold")
        ], spacing=5)

    def _create_alert_item(self, title, subtitle, level, color):
        return ft.Row([
            ft.Container(width=4, height=35, bgcolor=color, border_radius=2),
            ft.Column([
                ft.Text(title, size=14, weight="bold", color=TEXT_DARK),
                ft.Text(subtitle, size=11, color=TEXT_MUTED),
            ], spacing=0, expand=True),
            ft.Container(
                content=ft.Text(level, size=10, color=color, weight="bold"),
                border=ft.Border.all(1, color),
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=5
            )
        ], spacing=10)

    # --- UI HELPERS CHO DASHBOARD ---
    def _create_approval_card(self, name, unit, res_type, time):
        card = ft.Container(
            padding=12,
            bgcolor="#F8FAFC",
            border_radius=10,
            border=ft.Border.all(1, "#F1F5F9"),
            content=ft.Row([
                ft.CircleAvatar(content=ft.Text(name[0]), bgcolor=ACCENT_BLUE, color="white", radius=18),
                ft.Column([
                    ft.Text(name, weight="bold", size=14, color=TEXT_DARK),
                    ft.Text(f"{unit} • {res_type}", size=12, color=TEXT_MUTED),
                ], expand=True, spacing=0),
                ft.Text(time, size=11, color=TEXT_MUTED),

                ft.IconButton(
                    icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                    icon_color="green",
                    icon_size=20,
                    tooltip="Approve & Send Credentials",
                    on_click=lambda _: self.handle_approval(name, True, card)
                ),

                ft.IconButton(
                    icon=ft.Icons.HIGHLIGHT_OFF_ROUNDED,
                    icon_color="red",
                    icon_size=20,
                    tooltip="Reject Request",
                    on_click=lambda _: self.handle_approval(name, False, card)
                ),
            ])
        )
        return card
    
    def handle_approval(self, name, is_approved, card_control):
        if is_approved:
            self.show_message(f"APPROVED: Credentials sent to {name}'s email.")
        else:
            self.show_message(f"REJECTED: Registration for {name} has been cancelled.")
        
        card_control.visible = False
        self.page.update()
        
    def _create_activity_row(self, role, action, time, icon):
        return ft.Row([
            ft.Container(
                content=ft.Icon(icon, color=ACCENT_BLUE, size=18),
                bgcolor=ft.Colors.with_opacity(0.1, ACCENT_BLUE),
                padding=8, border_radius=8
            ),
            ft.Column([
                ft.Text(f"{role}: {action}", size=13, color=TEXT_DARK, weight=ft.FontWeight.BOLD),
                ft.Text(time, size=11, color=TEXT_MUTED),
            ], spacing=0, expand=True)
        ], spacing=15)
        
# --- Test Script ---
# def main(page: ft.Page):
#     dashboard = AdminDashboard(page, "Sara", "Administrator")
#     page.add(dashboard)
#     dashboard.switch_page("Dashboard", "Welcome back to your overview", dashboard.show_dashboard)

# if __name__ == "__main__":
#     ft.run(main)
