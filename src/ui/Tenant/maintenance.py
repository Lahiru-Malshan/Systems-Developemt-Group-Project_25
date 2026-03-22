# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from base_dashboard import ACCENT_BLUE, ACCENT_BLUE_LIGHT, CARD_BG, TEXT_DARK, TEXT_MUTED, BaseDashboard
from flet_charts import PieChart, PieChartSection
from db import get_db_connection
from backend.Maintance.maintenance_request import create_maintenance_request

import flet as ft


def fetch_maintenance_requests(dash):
    # Use tenant backend if available to filter by tenant and sort by request_id
    if hasattr(dash, "backend") and hasattr(dash.backend, "get_maintenance_requests"):
        raw = dash.backend.get_maintenance_requests()
        ordered = sorted(raw, key=lambda r: r.get("id", 0), reverse=False)
        formatted = []
        for idx, r in enumerate(ordered, start=1):
            formatted.append([
                idx,
                f"Apt {r.get('apartment_id', '-')}",
                r.get("description", ""),
                "Medium",
                r.get("status", "Pending"),
                str(r.get("reported_at", "")).split(" ")[0] if r.get("reported_at") else "-",
                str(r.get("resolved_at", "")).split(" ")[0] if r.get("resolved_at") else "-",
            ])
        return formatted

    # Fallback: query global maintenance requests (not tenant scoped)
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT request_id, description, status, reported_at, resolved_at
            FROM maintenance_requests
            ORDER BY request_id ASC
        """)

        records = cursor.fetchall()
        formatted_records = []

        for idx, row in enumerate(records, start=1):
            formatted_records.append([
                idx,
                "General",
                row["description"],
                "Medium",
                row["status"],
                str(row["reported_at"]).split(" ")[0] if row["reported_at"] else "-",
                str(row["resolved_at"]).split(" ")[0] if row["resolved_at"] else "-"
            ])

        return formatted_records

    except Exception as e:
        print("Error fetching maintenance requests:", e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def show_maintenance(dash, *args):
    if not dash:
        return

    dash.content_column.controls.clear()

    maintenance_data = fetch_maintenance_requests(dash)

    action_bar = ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        content=ft.Row([
            ft.Text("Maintenance Records", size=18, weight="bold", color=TEXT_DARK),
            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_ROUNDED, color="white", size=20),
                    ft.Text("NEW REQUEST", weight="bold", color="white"),
                ], tight=True),
                bgcolor=ACCENT_BLUE,
                on_click=lambda _: open_maintenance_form(dash)
            )
        ], alignment="spaceBetween")
    )

    rows = []
    for m in maintenance_data:
        p_color = ft.Colors.RED_700 if m[3] == "High" else ft.Colors.ORANGE_700 if m[3] == "Medium" else ft.Colors.BLUE_GREY_400
        s_color = ft.Colors.BLUE_700 if m[4] == "In Progress" else ft.Colors.GREEN_700 if m[4] == "Completed" else ft.Colors.GREY_600

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(f"#{m[0]}", weight="w500", color=TEXT_DARK)),
                    ft.DataCell(ft.Text(m[1], weight="w500", color=TEXT_DARK)),
                    ft.DataCell(ft.Container(content=ft.Text(m[2], weight="w500", color=TEXT_DARK, overflow=ft.TextOverflow.ELLIPSIS), width=200)),
                    ft.DataCell(ft.Text(m[3], color=p_color, weight="bold")),
                    ft.DataCell(ft.Container(content=ft.Text(m[4], color="white", size=10, weight="bold"), bgcolor=s_color, padding=ft.padding.symmetric(vertical=4, horizontal=10), border_radius=15)),
                    ft.DataCell(ft.Text(m[5], weight="w500", color=TEXT_DARK)),
                    ft.DataCell(ft.Text(m[6], weight="w500", color=TEXT_DARK)),
                ]
            )
        )

    table_container = ft.Container(
        bgcolor=CARD_BG, padding=20, border_radius=12, expand=True,
        content=ft.Column([
            ft.DataTable(
                expand=True,
                column_spacing=45,
                heading_row_color=ft.Colors.BLUE_GREY_50,
                columns=[
                    ft.DataColumn(ft.Text("ID", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Category", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Description", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Priority", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Reported", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Completed", weight="bold", color=ft.Colors.BLUE_900)),
                ],
                rows=rows,
            )
        ], scroll=ft.ScrollMode.AUTO)
    )

    status_counts = {"Pending": 0, "In Progress": 0, "Completed": 0}
    for m in maintenance_data:
        st = m[4]
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts["Pending"] += 1

    total = sum(status_counts.values()) or 1
    sections = []
    if status_counts["In Progress"] > 0:
        sections.append(PieChartSection(int(status_counts["In Progress"] / total * 100), title=f"{int(status_counts["In Progress"] / total * 100)}%", color=ft.Colors.BLUE_700, radius=40, title_style=ft.TextStyle(size=12, weight="bold", color="white")))
    if status_counts["Completed"] > 0:
        sections.append(PieChartSection(int(status_counts["Completed"] / total * 100), title=f"{int(status_counts["Completed"] / total * 100)}%", color=ft.Colors.GREEN_700, radius=40, title_style=ft.TextStyle(size=12, weight="bold", color="white")))
    if status_counts["Pending"] > 0:
        sections.append(PieChartSection(int(status_counts["Pending"] / total * 100), title=f"{int(status_counts["Pending"] / total * 100)}%", color=ft.Colors.GREY_600, radius=40, title_style=ft.TextStyle(size=12, weight="bold", color="white")))
    if not sections:
        sections = [PieChartSection(100, title="100%", color=ft.Colors.GREY_400, radius=40, title_style=ft.TextStyle(size=12, weight="bold", color="white"))]

    pie_chart = PieChart(
        sections=sections,
        sections_space=2,
        center_space_radius=40,
        expand=True,
    )

    chart_card = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.Text("Status Overview", size=18, weight="bold", color=TEXT_DARK),
            ft.Container(content=pie_chart, height=200),
            ft.Column([
                ft.Row([ft.Container(width=12, height=12, bgcolor=ft.Colors.BLUE_700, border_radius=3), ft.Text("In Progress", weight="bold", size=12, color=ft.Colors.BLUE_700)]),
                ft.Row([ft.Container(width=12, height=12, bgcolor=ft.Colors.GREEN_700, border_radius=3), ft.Text("Completed", weight="bold", size=12, color=ft.Colors.GREEN_700)]),
                ft.Row([ft.Container(width=12, height=12, bgcolor=ft.Colors.GREY_600, border_radius=3), ft.Text("Pending", weight="bold", size=12, color=ft.Colors.GREY_600)]),
            ], spacing=10)
        ])
    )

    sent_card = ft.Container(
        bgcolor=CARD_BG, padding=20, border_radius=12, width=320,
        content=ft.Column([
            ft.Text("Recent History", size=18, weight="bold", color=TEXT_DARK),
            ft.Divider(),
            ft.ListView(
                spacing=10,
                height=300,
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.BUILD_CIRCLE_ROUNDED, color=ACCENT_BLUE),
                        title=ft.Text(f"Request #{m[0]}", weight="bold", color=TEXT_DARK),
                        subtitle=ft.Text(f"{m[1]} - {m[5]}"),
                    )
                    for m in maintenance_data[:5]
                ]
            )
        ])
    )

    dash.content_column.controls = [
        action_bar,
        ft.Row([table_container]),
        ft.Row([chart_card, sent_card], spacing=20, vertical_alignment="start")
    ]
    dash.page.update()


def open_maintenance_form(dash):
    current_date = datetime.now().strftime("%Y-%m-%d")

    ref_category = ft.Dropdown(
        label="Category", value="Plumbing",
        options=[ft.dropdown.Option(x) for x in ["Plumbing", "Electrical", "Furniture", "Others"]],
        border_color=ACCENT_BLUE
    )

    ref_priority = ft.Dropdown(
        label="Priority Level", value="Medium",
        options=[ft.dropdown.Option(x) for x in ["Low", "Medium", "High"]],
        border_color=ACCENT_BLUE
    )

    ref_desc = ft.TextField(
        label="Issue Description", hint_text="Tell us what needs fixing...", multiline=True, min_lines=3, border_color=ACCENT_BLUE
    )

    def handle_submit(e):
        if not ref_desc.value:
            dash.show_message("Please provide a description of the issue!")
            return

        tenant = None
        if hasattr(dash, 'backend') and hasattr(dash.backend, 'get_tenant_record'):
            tenant = dash.backend.get_tenant_record()
        if not tenant or not tenant.get('tenant_id'):
            dash.show_message("Tenant not found. Cannot submit request.")
            return

        apartment_id = 1
        tenant_id = tenant.get('tenant_id')
        try:
            create_maintenance_request(
                tenant_id=tenant_id,
                apartment_id=apartment_id,
                description=ref_desc.value
            )

            dash.show_message("Success! Request submitted successfully!")
            dash.close_dialog()
            show_maintenance(dash)

        except Exception as ex:
            dash.show_message(f"Submit error: {str(ex)}")

    form_content = ft.Column([
        ft.Text("Please fill out the details below", color=TEXT_MUTED),
        ref_category,
        ref_priority,
        ref_desc,
        ft.Row([
            ft.Icon(ft.Icons.CALENDAR_MONTH, size=16, color=TEXT_MUTED),
            ft.Text(f"Reported Date: {current_date}", size=12, color=TEXT_MUTED, weight="bold"),
        ]),
    ], spacing=20, width=450)

    actions = [
        ft.Button(
            ft.TextButton("Cancel", on_click=dash.close_dialog),
        ),
        ft.Button(
            content=ft.Text("SUBMIT REQUEST", color="white", weight="bold"),
            bgcolor=ACCENT_BLUE,
            on_click=handle_submit
        ),
    ]

    dash.show_custom_modal("New Maintenance Request", form_content, actions)