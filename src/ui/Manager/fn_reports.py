
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from flet_charts import BarChart, BarChartGroup, BarChartRod, ChartAxis, ChartAxisLabel, ChartGridLines
from base_dashboard import *

def show_financials(dash):
    dash.content_column.controls.clear()

    # 1. HEADER: Financial Oversight
    header = ft.Row([
        ft.Column([
            ft.Text("Global Financial Performance", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Comparative analysis of revenue and maintenance budgets across locations ", size=14, color=TEXT_MUTED),
        ]),
        ft.Row([
            ft.Button(
                "EXPORT SUMMARY",
                icon=ft.Icons.FILE_DOWNLOAD_ROUNDED,
                bgcolor=ACCENT_BLUE,
                color=TEXT_WHITE,
                on_click=lambda _: dash.show_message("Exporting consolidated financial summary...")
            )
        ])
    ], alignment="spaceBetween")

    # 2. CHART AREA: Collected vs Pending vs Costs
    dash.fn_chart_container = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=20,
        height=400,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
        content=ft.Column([
            ft.Text("Revenue Status vs. Maintenance Costs (k£) ", size=16, weight="bold", color=TEXT_DARK),
            ft.Container(expand=True)
        ])
    )

    # 4. DATA TABLE AREA
    dash.fn_table_container = ft.Container(
        bgcolor="white",
        border_radius=12,
        padding=20,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
        content=ft.Column([
            ft.Text("Regional Financial Breakdown", size=16, weight="bold", color=TEXT_DARK),
            ft.Column(spacing=10)
        ])
    )

    dash.content_column.controls.extend([
        header,
        ft.Divider(height=10, color="transparent"),
        dash.fn_chart_container,
        ft.Divider(height=10, color="transparent"),
        dash.fn_table_container
    ])

    render_financial_data(dash)
    dash.page.update()

def render_financial_data(dash):
    """Calculates and renders comparative financial bars for the Manager."""
    chart_target = dash.fn_chart_container.content.controls[1]
    table_target = dash.fn_table_container.content.controls[1]

    # MOCK DATA: Strategic financial overview per city
    # 'collected' vs 'pending' vs 'maint_costs'
    fn_data = [
        {"city": "London", "collected": 420, "pending": 30, "costs": 45},
        {"city": "Manchester", "collected": 280, "pending": 40, "costs": 32},
        {"city": "Bristol", "collected": 195, "pending": 15, "costs": 22},
        {"city": "Cardiff", "collected": 170, "pending": 15, "costs": 18},
    ]
    max_units = max([item["collected"] + item["pending"] for item in fn_data])
    calculated_max_y = max_units * 1.15

    # Color Scheme
    COLOR_COLLECTED = ACCENT_BLUE
    COLOR_PENDING = ft.Colors.AMBER_600
    COLOR_COSTS = ft.Colors.RED_400

    bar_groups = []
    chart_labels = []

    for i, item in enumerate(fn_data):
        chart_labels.append(ChartAxisLabel(value=i, label=ft.Text(item["city"], size=14, weight="bold", color=TEXT_DARK)))
        
        bar_groups.append(
            BarChartGroup(
                x=i,
                rods=[
                    BarChartRod(from_y=0, to_y=item["collected"], color=COLOR_COLLECTED, width=18),
                    BarChartRod(from_y=0, to_y=item["pending"], color=COLOR_PENDING, width=18),
                    BarChartRod(from_y=0, to_y=item["costs"], color=COLOR_COSTS, width=18),
                ]
            )
        )

    # Dynamic Legend & Chart
    chart_target.content = ft.Column([
        ft.Row([
            ft.Row([ft.Container(width=10, height=10, bgcolor=COLOR_COLLECTED), ft.Text("Collected", size=10, color=COLOR_COLLECTED)]),
            ft.Row([ft.Container(width=10, height=10, bgcolor=COLOR_PENDING), ft.Text("Pending", size=10, color=COLOR_PENDING)]),
            ft.Row([ft.Container(width=10, height=10, bgcolor=COLOR_COSTS), ft.Text("Maint. Costs", size=10, color=COLOR_COSTS)]),
        ], alignment=ft.MainAxisAlignment.END, spacing=20),
        BarChart(
            groups=bar_groups,
            bottom_axis=ChartAxis(labels=chart_labels),
            left_axis=ChartAxis(
                label_size=40,
                labels=[
                    ChartAxisLabel(
                        value=v,
                        label=ft.Text(str(v), color=TEXT_DARK, size=14)
                    ) for v in range(0, int(calculated_max_y) + 10, 10)
                ]
            ),
            max_y=calculated_max_y,
            horizontal_grid_lines=ChartGridLines(interval=100, color=ft.Colors.with_opacity(0.05, TEXT_DARK)),
            expand=True
        )
    ], expand=True)

    # Financial Summary Table
    rows = []
    for item in fn_data:
        total_rent = item["collected"] + item["pending"]
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["city"], weight="bold", color=TEXT_DARK)),
                ft.DataCell(ft.Text(f"£{item['collected']}k", color=COLOR_COLLECTED)),
                ft.DataCell(ft.Text(f"£{item['pending']}k", color=COLOR_PENDING)),
                ft.DataCell(ft.Text(f"£{item['costs']}k", color=COLOR_COSTS)),
                ft.DataCell(ft.Text(f"£{total_rent - item['costs']}k", weight="bold", color=TEXT_DARK)),
            ])
        )

    table_target.controls = [
        ft.DataTable(
            heading_row_color=ft.Colors.BLUE_GREY_50,
            columns=[
                ft.DataColumn(ft.Text("Branch Location", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Collected Rent", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Pending Rent", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Maint. Budget", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Net Performance", weight="bold", color=TEXT_DARK)),
            ],
            rows=rows
        )
    ]
    dash.page.update()