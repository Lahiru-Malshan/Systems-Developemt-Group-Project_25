import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)

import flet as ft
from datetime import datetime
from logic.search import *
from base_dashboard import *
from flet_charts import BarChart, BarChartGroup, BarChartRod, ChartAxis, ChartAxisLabel, ChartGridLines

report_db = {
    "2024": [
        {"month": "Apr", "revenue": 45000, "expenses": 13000},
        {"month": "May", "revenue": 42000, "expenses": 16000},
        {"month": "Jun", "revenue": 35000, "expenses": 18000},
    ],
    "2025": [
        {"month": "Jan", "revenue": 40000, "expenses": 15000},
        {"month": "Feb", "revenue": 42000, "expenses": 14000},
        {"month": "Mar", "revenue": 38000, "expenses": 18000},
    ],
    "2026": [
        {"month": "Jan", "revenue": 45000, "expenses": 12000},
        {"month": "Feb", "revenue": 48000, "expenses": 11000},
    ]
}
def show_reports(dash, *args):
    if not dash:
        return
    dash.content_column.controls.clear()
    if not hasattr(dash, "report_table_area"):
        dash.report_table_area = ft.Column(expand=True)
    if not hasattr(dash, "chart_area"):
        dash.chart_area = ft.Container(
        height=350,
        bgcolor=CARD_BG,
        border_radius=12,
        padding=20,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        content=ft.Text("Click GENERATE to view analytics", color=ft.Colors.GREY_400)
        )

    header = ft.Row([
        ft.Column([
            ft.Text("Financial Reporting", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Generate tax-ready statements and profit/loss reports", size=14, color=TEXT_MUTED),
        ]),
        ft.Row([
            ft.Button(
                "EXPORT EXCEL",
                icon=ft.Icons.TABLE_CHART_ROUNDED,
                bgcolor=ft.Colors.GREEN_800,
                color="white",
                on_click=lambda _: dash.show_message("Exporting report...")
            ),
            ft.Button(
                "VAT STATEMENT",
                icon=ft.Icons.RECEIPT_LONG_ROUNDED,
                bgcolor=ACCENT_BLUE,
                color="white",
                on_click=lambda _: dash.show_message("Generating VAT Report...")
            ),
        ], spacing=10)
    ], alignment="spaceBetween")
    
    dash.year_input = ft.TextField(
        label="Enter Year",
        value="2026",
        color=TEXT_DARK,
        width=120,
        text_align="center",
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]"),
        bgcolor="white"
    )
    dash.report_type_filter = ft.Dropdown(
        label="Report Type",
        width=250,
        value="Profit & Loss",
        color=TEXT_DARK,
        options=[
            ft.dropdown.Option("Profit & Loss",),
            ft.dropdown.Option("Revenue Only",),
            ft.dropdown.Option("Expenses Only",)
        ],
        bgcolor="white"
    )

    filter_bar = ft.Container(
        padding=15,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
        border_radius=10,
        content=ft.Row([
            dash.year_input,
            dash.report_type_filter,
            ft.Button(
                "GENERATE",
                icon=ft.Icons.REFRESH_ROUNDED,
                bgcolor=ft.Colors.BLUE,
                color="white",
                on_click=lambda _: handle_generate_logic(dash)
            )
        ], spacing=20)
    )
    
    dash.content_column.controls.extend([
        header,
        filter_bar,
        ft.Divider(height=5, color="transparent"),
        ft.Text("Financial Analytics Visualization", size=16, weight="bold", color=TEXT_DARK),
        dash.chart_area,
        ft.Divider(height=5, color="transparent"),
        dash.report_table_area
    ])
    handle_generate_logic(dash)
    dash.page.update()

def handle_generate_logic(dash):
    year = dash.year_input.value
    report_type = dash.report_type_filter.value
    data = report_db.get(year, [])
    
    if not data:
        dash.show_message(f"No data for {year}")
        return

    all_values = []
    for item in data:
        all_values.extend([item.get("revenue", 0), item.get("expenses", 0)])
    
    max_val_k = (max(all_values) / 1000) * 1.1 if all_values else 100
    
    bar_groups = []
    chart_labels = []

    for i, item in enumerate(data):
        chart_labels.append(
            ChartAxisLabel(value=i, label=ft.Text(item.get("month"), size=10, weight="bold", color=TEXT_DARK))
        )

        rods = []
        if report_type in ["Profit & Loss", "Revenue Only"]:
            rods.append(BarChartRod(from_y=0, to_y=item.get("revenue", 0)/1000, color=ft.Colors.BLUE_600, width=16))
        if report_type in ["Profit & Loss", "Expenses Only"]:
            rods.append(BarChartRod(from_y=0, to_y=item.get("expenses", 0)/1000, color=ft.Colors.ORANGE_500, width=16))
        
        bar_groups.append(BarChartGroup(x=i, rods=rods))
    
    # Update chart area with new data
    dash.chart_area.content = ft.Column([
        # Legend
        ft.Row([
            ft.Row([ft.Container(width=12, height=12, bgcolor=ft.Colors.BLUE_600, border_radius=3), ft.Text("Revenue (£k)", size=12, color=ft.Colors.BLUE_600)]),
            ft.Row([ft.Container(width=12, height=12, bgcolor=ft.Colors.ORANGE_500, border_radius=3), ft.Text("Expenses (£k)", size=12, color=ft.Colors.ORANGE_500)]),
        ], alignment="end", spacing=20),
        
        BarChart(
            groups=bar_groups,
            bottom_axis=ChartAxis(labels=chart_labels),
            left_axis=ChartAxis(
                label_size=50,
                labels=[
                    ChartAxisLabel(
                        value=v,
                        label=ft.Text(str(v), color=TEXT_DARK, size=14)
                    ) for v in range(0, int(max_val_k) + 10, 10)
                ]
            ),
            max_y=max_val_k,
            min_y=0,
            horizontal_grid_lines=ChartGridLines(
                interval=10,
                color=ft.Colors.with_opacity(0.05, "black")
            ),
            expand=True,
        )
    ], spacing=10)

    apply_report_filters(dash)
    dash.page.update()
    
def handle_export_action(dash, type):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"Financial_Report_{timestamp}.xlsx" if type == "Excel" else f"VAT_Statement_{timestamp}.pdf"
    dash.show_message(f"Preparing {type} file: {filename}... Download starting soon.")

def apply_report_filters(dash):
    year_selected = dash.year_input.value
    raw_data = report_db.get(year_selected, [])
    
    search_term = getattr(dash, "report_search_field", None)
    search_value = search_term.value if search_term else ""
    
    filtered_data = SearchEngine.apply_logic(
        data_list=raw_data,
        search_term=search_value
    )

    rows = []
    for r in filtered_data:
        if isinstance(r, str):
            continue
        
        month_with_year = f"{r.get('month', 'N/A')} {year_selected}"
        
        rev = r.get("revenue", 0)
        exp = r.get("expenses", 0)
        vat_val = rev * 0.2
        profit_val = rev - exp - vat_val
        
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(month_with_year, weight="bold", color=TEXT_DARK)),
                ft.DataCell(ft.Text(f"£{rev:,.2f}", color=TEXT_DARK)),
                ft.DataCell(ft.Text(f"£{vat_val:,.2f}", color=ft.Colors.BLUE_700)),
                ft.DataCell(ft.Text(f"£{exp:,.2f}", color=ft.Colors.RED_600)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(f"£{profit_val:,.2f}", weight="bold", color="white"),
                        bgcolor=ft.Colors.GREEN_700 if profit_val > 0 else ft.Colors.RED_700,
                        padding=ft.Padding.symmetric(horizontal=12, vertical=4),
                        border_radius=8
                    )
                ),
                ft.DataCell(ft.IconButton(ft.Icons.FILE_DOWNLOAD_OUTLINED, icon_color=ACCENT_BLUE)),
            ])
        )

    dash.report_table_area.controls = [
        ft.Container(
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, TEXT_DARK)),
            content=ft.Column([
                ft.Text("Financial Transaction List", size=18, weight="bold", color=TEXT_DARK),
                ft.Divider(height=10, color="transparent"),
                ft.DataTable(
                    heading_row_color=ft.Colors.BLUE_GREY_50,
                    heading_row_height=50,
                    data_row_min_height=60,
                    column_spacing=30,
                    divider_thickness=1,
                    columns=[
                        ft.DataColumn(ft.Text("Period", weight="bold", color=ft.Colors.BLUE_900)),
                        ft.DataColumn(ft.Text("Revenue", weight="bold", color=ft.Colors.BLUE_900)),
                        ft.DataColumn(ft.Text("VAT (20%)", weight="bold", color=ft.Colors.BLUE_900)),
                        ft.DataColumn(ft.Text("Expenses", weight="bold", color=ft.Colors.BLUE_900)),
                        ft.DataColumn(ft.Text("Status", weight="bold", color=ft.Colors.BLUE_900)),
                        ft.DataColumn(ft.Text("Action", weight="bold", color=ft.Colors.BLUE_900)),
                    ],
                    rows=rows
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
    ]
    dash.page.update()