import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

import flet as ft
from datetime import datetime
from base_dashboard import *
from flet_charts import BarChart, BarChartGroup, BarChartRod, ChartAxis, ChartAxisLabel, ChartGridLines

def show_occupancy(dash):
    if not dash:
        return
    dash.content_column.controls.clear()
    
    if not hasattr(dash, "occupancy_chart"):
        dash.occupancy_chart = ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            height=350,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
            content=ft.Column([
                ft.Text("Occupancy Levels by City (Total Units)", size=16, weight="bold", color=TEXT_DARK),
                ft.Container(expand=True)
            ])
        )
    if not hasattr(dash, "occupancy_table"):
        dash.occupancy_table = ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
            content=ft.Column([
                ft.Text("Live Apartment Inventory Status", size=16, weight="bold", color=TEXT_DARK),
                ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
            ])
        )

    # 1. HEADER: Strategic Insights
    header = ft.Row([
        ft.Column([
            ft.Text("Occupancy & Inventory Analytics", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Live tracking of apartment occupancy across multi-city locations", size=14, color=TEXT_MUTED),
        ]),
        ft.Row([
            ft.Button(
                "GENERATE PDF REPORT",
                icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
                bgcolor=ACCENT_BLUE,
                color=TEXT_WHITE,
                on_click=lambda _: dash.show_message("Generating occupancy report... ")
            )
        ])
    ], alignment="spaceBetween")

    # 2. ANALYTICS AREA: Capacity vs Occupied
    dash.occupancy_chart = ft.Container(
        bgcolor=CARD_BG,
        border_radius=12,
        padding=20,
        height=350,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
        content=ft.Column([
            ft.Text("Occupancy Levels by City (Total Units)", size=16, weight="bold", color=TEXT_DARK),
            ft.Container(expand=True)
        ])
    )

    # 3. DETAILED INVENTORY STATUS
    dash.occupancy_table = ft.Container(
        bgcolor=CARD_BG,
        border_radius=12,
        padding=20,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
        content=ft.Column([
            ft.Text("Live Apartment Inventory Status ", size=16, weight="bold", color=TEXT_DARK),
            ft.Column(spacing=10) # DataTable injected here
        ])
    )
    
    dash.content_column.controls.extend([
        header,
        ft.Divider(height=10, color="transparent"),
        dash.occupancy_chart,
        ft.Divider(height=10, color="transparent"),
        dash.occupancy_table
    ])

    render_occupancy_data(dash)
    dash.page.update()

def render_occupancy_data(dash):
    """Populates the occupancy chart and table based on UK location."""
    chart_target = dash.occupancy_chart.content.controls[1]
    table_target = dash.occupancy_table.content.controls[1]
    # MOCK DATA: Based on PAMS city requirements
    occupancy_data = [
        {"city": "London", "total": 120, "occupied": 112},
        {"city": "Manchester", "total": 85, "occupied": 75},
        {"city": "Bristol", "total": 60, "occupied": 48},
        {"city": "Cardiff", "total": 50, "occupied": 40},
    ]

    # Calculate Max Y with buffer
    max_units = max([item["total"] for item in occupancy_data])
    calculated_max_y = max_units * 1.15

    bar_groups = []
    chart_labels = []

    for i, item in enumerate(occupancy_data):
        chart_labels.append(ChartAxisLabel(value=i, label=ft.Text(item["city"], size=14, weight="bold", color=TEXT_DARK)))
        
        bar_groups.append(
            BarChartGroup(
                x=i,
                rods=[
                    BarChartRod(from_y=0, to_y=item["total"], color=NAVY_SECOND, width=22, border_radius=4),
                    BarChartRod(from_y=0, to_y=item["occupied"], color=ACCENT_BLUE_LIGHT, width=22, border_radius=4),
                ]
            )
        )

    # Legend for clarity
    chart_target.content = ft.Column([
        ft.Row([
            ft.Row([ft.Container(width=12, height=12, bgcolor=NAVY_SECOND, border_radius=3), ft.Text("Total Capacity", size=11, color=TEXT_DARK)]),
            ft.Row([ft.Container(width=12, height=12, bgcolor=ACCENT_BLUE_LIGHT, border_radius=3), ft.Text("Occupied Units", size=11, color=TEXT_DARK)]),
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
            horizontal_grid_lines=ChartGridLines(interval=20, color=ft.Colors.with_opacity(0.05, TEXT_DARK)),
            expand=True
        )
    ], spacing=10, expand=True)

    # Detailed Table of Occupancy
    rows = []
    for item in occupancy_data:
        vacant = item["total"] - item["occupied"]
        rate = (item["occupied"] / item["total"]) * 100
        
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["city"], weight="bold", color=TEXT_DARK)),
                ft.DataCell(ft.Text(str(item["total"]), color=NAVY_SECOND)),
                ft.DataCell(ft.Text(str(item["occupied"]), color=ACCENT_BLUE, weight="bold")),
                ft.DataCell(ft.Text(str(vacant), color=ft.Colors.ORANGE_700)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(f"{rate:.1f}%", color="white", size=11, weight="bold"),
                        bgcolor=ft.Colors.GREEN_700 if rate > 90 else ft.Colors.BLUE_600,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=15
                    )
                ),
            ])
        )

    table_target.controls = [
        ft.DataTable(
            heading_row_color=ft.Colors.BLUE_GREY_50,
            columns=[
                ft.DataColumn(ft.Text("Branch Location", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Total Units", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Occupied Units", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Vacant Units", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Occupancy Rate", weight="bold", color=TEXT_DARK)),
            ],
            rows=rows
        )
    ]
    dash.page.update()
