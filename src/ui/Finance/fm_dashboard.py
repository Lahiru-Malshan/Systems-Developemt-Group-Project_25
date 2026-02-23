import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

import flet as ft
import flet.canvas as cv
from flet_charts import LineChart, LineChartData, LineChartDataPoint, ChartAxis, ChartAxisLabel, ChartGridLines
from datetime import datetime
from base_dashboard import *
from settingsStaff import *
from invoices import *
from transactions import *
from reports import *

class FinanceDashboard(BaseDashboard):
    def __init__(self, page: ft.Page, username: str, role_name: str = "Finance Manager"):
        super().__init__(page, username, role_name=role_name)

        self.create_nav_btn(
            "Financial Overview",
            ft.Icons.DASHBOARD_ROUNDED,
            lambda _: self.switch_page("Financial Overview", "Summary of financial metrics and trends", self.show_overview)
        )
        self.create_nav_btn(
            "Invoices",
            ft.Icons.RECEIPT_LONG_ROUNDED,
            lambda _: self.switch_page("Invoice Management", "Manage and track all invoices", show_invoices)
        )
        self.create_nav_btn(
            "Transactions",
            ft.Icons.PAYMENT_ROUNDED,
            lambda _: self.switch_page("Transactions", "View and manage all financial transactions", show_transactions)
        )
        self.create_nav_btn(
            "Financial Reports",
            ft.Icons.ASSESSMENT_ROUNDED,
            lambda _: self.switch_page("Financial Reports", "Generate and view detailed financial reports", show_reports)
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
                self.create_stat_card("Monthly Revenue", "£45,200.00", ft.Icons.ATTACH_MONEY_ROUNDED, highlight=True),
                self.create_stat_card("Outstanding", "£3,150.00", ft.Icons.MONEY_OFF_ROUNDED),
                self.create_stat_card("VAT (20%)", "£9,040.00", ft.Icons.ACCOUNT_BALANCE_ROUNDED),
                self.create_stat_card("Overdue Accounts", "12", ft.Icons.REPORT_PROBLEM_ROUNDED),
            ]
        )
        quick_actions = ft.Container(
            bgcolor=ft.Colors.with_opacity(0.05, ACCENT_BLUE),
            padding=15, border_radius=12,
            content=ft.Row([
                ft.Text("Quick Actions:", weight="bold", color=TEXT_DARK),
                ft.Button("Run Monthly Billing", icon=ft.Icons.PLAY_CIRCLE_FILL, bgcolor=ACCENT_BLUE,
                on_click=self.handle_run_monthly_billing),
                ft.Button("VAT Report", icon=ft.Icons.FILE_DOWNLOAD, bgcolor=ACCENT_BLUE,
                on_click=self.handle_vat_report),
                ft.Button("Manual Entry", icon=ft.Icons.EDIT_SQUARE, bgcolor=ACCENT_BLUE,
                on_click=lambda _: open_invoice_form(self)),
            ], spacing=15)
        )
        
        chart_card = ft.Container(
            bgcolor=CARD_BG, padding=20, border_radius=12, expand=5,
            height=300,
            content=ft.Column([
                ft.Text("Revenue vs Expenses", size=16, weight="bold", color=TEXT_DARK),
                LineChart(
                    data_series=[
                        # Revenue
                        LineChartData(
                            points=[
                                LineChartDataPoint(0, 30), LineChartDataPoint(1, 35),
                                LineChartDataPoint(2, 45), LineChartDataPoint(3, 42),
                            ],
                            color=ACCENT_BLUE, stroke_width=4,
                        ),
                        # Expenses
                        LineChartData(
                            points=[
                                LineChartDataPoint(0, 10), LineChartDataPoint(1, 15),
                                LineChartDataPoint(2, 12), LineChartDataPoint(3, 14),
                            ],
                            color=ft.Colors.ORANGE_700, stroke_width=4,
                        ),
                    ],
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
                    horizontal_grid_lines=ChartGridLines(interval=10, color=ft.Colors.with_opacity(0.05, TEXT_DARK)),
                    bottom_axis=ChartAxis(
                        labels=[
                            ChartAxisLabel(value=0, label=ft.Text("Nov", color=TEXT_DARK)),
                            ChartAxisLabel(value=1, label=ft.Text("Dec", color=TEXT_DARK)),
                            ChartAxisLabel(value=2, label=ft.Text("Jan", color=TEXT_DARK)),
                            ChartAxisLabel(value=3, label=ft.Text("Feb", color=TEXT_DARK)),
                        ]
                    ),
                    expand=True,
                ),
                ft.Row([
                    ft.Row([ft.Container(width=10, height=10, bgcolor=ACCENT_BLUE), ft.Text("Revenue", size=10, color=ACCENT_BLUE)]),
                    ft.Row([ft.Container(width=10, height=10, bgcolor=ft.Colors.ORANGE_700), ft.Text("Expenses", size=10, color=ft.Colors.ORANGE_700)]),
                ], spacing=20, alignment="center")
            ])
        )
        
        recent_data = [
            ["2026-02-20", "A-101", "Rent - Feb", "£1,200.00", "Paid"],
            ["2026-02-20", "B-302", "Service Fee", "£150.00", "Pending"],
            ["2026-02-19", "C-204", "Utility Bill", "£85.20", "Paid"],
        ]
        rows = []
        for date, unit, desc, amt, status in recent_data:
            s_color = ft.Colors.GREEN_600 if status == "Paid" else ft.Colors.ORANGE_600
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(date, color=TEXT_DARK)),
                    ft.DataCell(ft.Text(unit, weight="bold", color=TEXT_DARK)),
                    ft.DataCell(ft.Text(desc, color=TEXT_DARK)),
                    ft.DataCell(ft.Text(amt, weight="bold", color=ACCENT_BLUE)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status, color="white", size=10, weight="bold"),
                            bgcolor=s_color, padding=ft.Padding.symmetric(horizontal=10, vertical=4), border_radius=10
                        )
                    ),
                ])
            )
            
        table_card = ft.Container(
            bgcolor=CARD_BG, padding=20, border_radius=12, expand=5,
            height=500,
            content=ft.Column([
                ft.Row([
                    ft.Text("Recent Financial Activity", size=18, weight="bold", color=TEXT_DARK),
                    ft.TextButton("View all transactions", icon=ft.Icons.ARROW_FORWARD, on_click=lambda _: show_transactions(self))
                ], alignment="spaceBetween"),
                ft.Column([
                    ft.DataTable(
                        column_spacing=15,
                        heading_row_color=ft.Colors.BLUE_GREY_50,
                        columns=[
                            ft.DataColumn(ft.Text("Date", color=TEXT_DARK)),
                            ft.DataColumn(ft.Text("Unit", color=TEXT_DARK)),
                            ft.DataColumn(ft.Text("Description", color=TEXT_DARK)),
                            ft.DataColumn(ft.Text("Amount", color=TEXT_DARK)),
                            ft.DataColumn(ft.Text("Status", color=TEXT_DARK)),
                        ],
                        rows=rows
                    )
                ], scroll=ft.ScrollMode.AUTO, expand=True)
            ])
        )
        chart_table_row = ft.Row(
            controls=[chart_card, table_card],
            spacing=20,
            vertical_alignment="stretch"
        )
        
        self.content_column.controls = [
            stats_row,
            ft.Divider(height=10, color="transparent"),
            quick_actions,
            ft.Divider(height=10, color="transparent"),
            ft.Container(content=chart_table_row, height=300)
        ]
        self.page.update()
        
    def handle_run_monthly_billing(self, e):
        """Automatically generate monthly rent invoices for all units that don't have an invoice for the current month yet"""
        
        units_to_bill = ["A-101", "B-302", "C-204", "D-505"]
        current_month = datetime.now().strftime("%b")
        count = 0
        
        for unit in units_to_bill:
            # Check if an invoice for this unit and month already exists
            exists = any(inv["room"] == unit and current_month in inv["desc"] for inv in invoices_data)
            if not exists:
                new_inv = {
                    "id": f"INV-{len(invoices_data) + 2001}",
                    "room": unit,
                    "desc": f"Monthly Rent - {current_month}",
                    "net": 1200.0,
                    "vat": 240.0, # 20% VAT
                    "status": "Unpaid",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
                invoices_data.insert(0, new_inv)
                count += 1
        
        if count > 0:
            self.show_message(f"Success: {count} monthly invoices generated for {current_month}!")
            show_invoices(self)
        else:
            self.show_message("Billing already processed for this month.")

    def handle_vat_report(self, e):
        """Calculate total VAT collected for the current period and show in a modal"""
        total_vat = sum(inv["vat"] for inv in invoices_data)
        self.show_custom_modal(
            "VAT Summary Report",
            ft.Column([
                ft.Text(f"Total VAT Collected (Current Period):", size=14),
                ft.Text(f"£{total_vat:,.2f}", size=30, weight="bold", color=ACCENT_BLUE),
                ft.Text("This data is ready for HMRC submission.", size=12, italic=True)
            ], tight=True),
            [ft.Button("Close", on_click=lambda _: self.close_dialog())]
        )
    
def main(page: ft.Page):
    dashboard = FinanceDashboard(page, "Mr. Sterling", "Finance Manager")
    page.add(dashboard)
    dashboard.switch_page("Financial Overview", "System financial health at a glance", dashboard.show_overview)

if __name__ == "__main__":
    ft.run(main)
