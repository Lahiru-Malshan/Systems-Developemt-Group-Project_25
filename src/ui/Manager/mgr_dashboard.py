import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

import flet as ft
import flet.canvas as cv
from flet_charts import BarChart, BarChartGroup, BarChartRod, ChartAxis, ChartAxisLabel, ChartGridLines
from datetime import datetime
from base_dashboard import *
from settingsStaff import *
from occupancy import *
from fn_reports import *
from expansion import *

class ManagerDashboard(BaseDashboard):
    def __init__(self, page: ft.Page, username: str, role_name: str = "Manager"):
        super().__init__(page, username, role_name=role_name)
        
        self.create_nav_btn(
            "Dashboard",ft.Icons.DASHBOARD_ROUNDED,lambda _: self.switch_page("Dashboard", "Welcome back to your overview", self.show_overview)
        )
        self.create_nav_btn(
            "Occupancy",ft.Icons.APARTMENT_ROUNDED,lambda _: self.switch_page("Occupancy", "Track unit occupancy and turnover rates",show_occupancy)
        )
        self.create_nav_btn(
            "Finance Reports",ft.Icons.BAR_CHART_ROUNDED,lambda _: self.switch_page("Financial Reports", "View revenue, expenses, and profit trends", show_financials)
        )
        self.create_nav_btn(
            "Expansion",ft.Icons.ADD_LOCATION_ALT_ROUNDED,lambda _: self.switch_page("Expansion Planning", "Analyze growth opportunities and market trends", show_expansion)
        )
        self.create_nav_btn(
            "Settings",ft.Icons.SETTINGS_ROUNDED,lambda _: self.switch_page("Settings", "Manage your account and preferences", show_settings)
        )
    
    def show_overview(self, *args):
        self.content_column.controls.clear()
        
        header = ft.Row([
        ft.Column([
            ft.Text("Executive Analytics Overview", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Consolidated performance across Bristol, Cardiff, London, and Manchester", size=14, color=TEXT_MUTED),
        ]),
        ft.Button(
            "EXPAND BUSINESS",
            icon=ft.Icons.ADD_LOCATION_ALT_ROUNDED,
            bgcolor=ACCENT_BLUE,
            color=TEXT_WHITE,
            on_click=lambda _: show_expansion(self)
        )
    ], alignment="spaceBetween")
        
        kpi_row = ft.Row([
            self.create_stat_card("Group Occupancy", "88.2%", ft.Icons.HOUSE_ROUNDED, highlight=True),
            self.create_stat_card("Total Revenue", "£1,420,500", ft.Icons.MONETIZATION_ON_ROUNDED),
            self.create_stat_card("Operating Costs", "£52,400", ft.Icons.PAYMENT_ROUNDED),
        ], spacing=20)
        
        self.city_chart_container = ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            height=380,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
            content=ft.Column([
                ft.Text("Financial Performance by City (k£)", size=18, weight="bold", color=TEXT_DARK),
                ft.Container(expand=True)
            ])
        )
        self.city_table_container = ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
            content=ft.Column([
                ft.Row([
                    ft.Text("Regional Branch Performance", size=18, weight="bold", color=TEXT_DARK),
                    ft.TextButton("Export Global Report", icon=ft.Icons.DOWNLOAD_ROUNDED)
                ], alignment="spaceBetween"),
                ft.Column(spacing=10) # Regional DataTable will be injected here
            ])
        )
        
        self.content_column.controls.extend([
            header,
            ft.Divider(height=10, color="transparent"),
            kpi_row,
            ft.Divider(height=15, color="transparent"),
            self.city_chart_container,
            ft.Divider(height=15, color="transparent"),
            self.city_table_container
        ])
        render_manager_data(self)
        self.page.update()
        
def render_manager_data(self):
    """
    Logic to populate multi-city analytics.
    Focuses on Bristol, Cardiff, London, and Manchester.
    """
    # 1. MOCK DATA: Performance by City
    # Requirements: Financial summaries comparing collected vs pending
    regional_data = [
        {"city": "London", "revenue": 450, "expenses": 120, "occupancy": "94%"},
        {"city": "Manchester", "revenue": 320, "expenses": 95, "occupancy": "88%"},
        {"city": "Bristol", "revenue": 210, "expenses": 65, "occupancy": "82%"},
        {"city": "Cardiff", "revenue": 185, "expenses": 55, "occupancy": "79%"},
    ]

    # 2. GENERATE BAR CHART (City Comparison)
    # Requirement: Generate performance reports according to location
    all_values = []
    for item in regional_data:
        all_values.extend([item.get("revenue", 0), item.get("expenses", 0)])
    
    max_val_k = max(all_values) * 1.1 if all_values else 100
    
    
    bar_groups = []
    chart_labels = []

    for i, item in enumerate(regional_data):
        # Labels for X-Axis (City Names)
        chart_labels.append(
            ChartAxisLabel(
                value=i,
                label=ft.Text(item["city"], size=14, weight="bold", color=TEXT_DARK)
            )
        )

        bar_groups.append(
            BarChartGroup(
                x=i,
                rods=[
                    BarChartRod(from_y=0, to_y=item["revenue"], color=ACCENT_BLUE, width=20, border_radius=4),
                    BarChartRod(from_y=0, to_y=item["expenses"], color=ft.Colors.ORANGE_500, width=20, border_radius=4),
                ]
            )
        )

    # Injecting BarChart into the container
    self.city_chart_container.content.controls[1].content = ft.Column([
        ft.Row([
            ft.Row([
                ft.Container(width=12, height=12, bgcolor=ACCENT_BLUE, border_radius=3),
                ft.Text("Revenue (£k)", size=12, color=ACCENT_BLUE, weight=ft.FontWeight.W_500)
            ], spacing=8),
            ft.Row([
                ft.Container(width=12, height=12, bgcolor=ft.Colors.ORANGE_500, border_radius=3),
                ft.Text("Maint. Expenses (£k)", size=12, color=ft.Colors.ORANGE_500, weight=ft.FontWeight.W_500)
            ], spacing=8),
        ], alignment=ft.MainAxisAlignment.END, spacing=25),
        BarChart(
            groups=bar_groups,
            bottom_axis=ChartAxis(labels=chart_labels),
            left_axis=ChartAxis(
                    label_size=50,
                    labels=[
                        ChartAxisLabel(
                            value=v,
                            label=ft.Text(str(v), color=TEXT_DARK, size=14)
                        ) for v in range(0, int(max_val_k) + 50, 50)
                    ]
                ),
            max_y=max_val_k,
            min_y=0,
            horizontal_grid_lines=ChartGridLines(interval=50, color=ft.Colors.with_opacity(0.1, TEXT_DARK)),
            expand=True,
            interactive=True
        )
    ], spacing=10, expand=True)

    # 3. GENERATE REGIONAL TABLE
    # Requirement: Insight into occupancy and financial performance
    rows = []
    for item in regional_data:
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["city"], weight="bold", color=ft.Colors.BLUE_900)),
                ft.DataCell(ft.Text(f"£{item['revenue']}k", color=ACCENT_BLUE)),
                ft.DataCell(ft.Text(f"£{item['expenses']}k", color=ft.Colors.RED_400)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(item["occupancy"], color="white", size=11, weight="bold"),
                        bgcolor=ft.Colors.GREEN_700 if int(item["occupancy"].strip('%')) > 85 else ft.Colors.BLUE_600,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=15
                    )
                ),
                ft.DataCell(ft.IconButton(ft.Icons.ANALYTICS_OUTLINED, icon_color=ACCENT_BLUE)),
            ])
        )

    self.city_table_container.content.controls[1].controls = [
        ft.DataTable(
            heading_row_color=ft.Colors.BLUE_GREY_50,
            columns=[
                ft.DataColumn(ft.Text("Branch Location", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Total Revenue", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Maint. Costs", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Occupancy Rate", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Details", weight="bold", color=TEXT_DARK)),
            ],
            rows=rows
        )
    ]
    
    self.page.update()
    
def main(page: ft.Page):
    dashboard = ManagerDashboard(page, "Sara", "Manager")

    page.add(dashboard)
    dashboard.switch_page("Dashboard", "Welcome back to your overview", dashboard.show_overview)
            
if __name__ == "__main__":
    ft.run(main)