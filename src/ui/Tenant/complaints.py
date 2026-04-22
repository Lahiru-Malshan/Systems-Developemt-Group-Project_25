# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from base_dashboard import *
import flet as ft

def show_complaints(dash, *args):
    if not dash:
        return

    complaints = dash.backend.get_complaints()
    
    dash.content_column.controls.clear()

    # Header with action button
    header = ft.Row([
        ft.Text("My Complaints", size=20, weight="bold", color=TEXT_DARK),
        ft.Container(expand=True),
        ft.Button(
            "File New Complaint",
            icon=ft.Icons.ADD_ROUNDED,
            bgcolor=ACCENT_BLUE,
            color="white",
            on_click=lambda _: open_complaint_form(dash)
        )
    ])

    # Stats cards
    total_complaints = len(complaints)
    open_complaints = len([c for c in complaints if c.get("status", "").lower() == "open"])
    resolved_complaints = len([c for c in complaints if c.get("status", "").lower() == "resolved"])

    stats_row = ft.Row([
        dash.create_stat_card("Total Complaints", str(total_complaints), ft.Icons.LIST_ALT_ROUNDED),
        dash.create_stat_card("Open", str(open_complaints), ft.Icons.PRIORITY_HIGH_ROUNDED, highlight=True),
        dash.create_stat_card("Resolved", str(resolved_complaints), ft.Icons.CHECK_CIRCLE_ROUNDED),
    ], spacing=20)

    # Complaints table
    complaint_rows = []
    for comp in sorted(complaints, key=lambda x: x.get("created_at", ""), reverse=True):
        status = comp.get("status", "Open")
        color = ft.Colors.GREEN_700 if status.lower() == "resolved" else ft.Colors.ORANGE_700
        complaint_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(comp.get("complaint_id", "")), weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(comp.get("description", ""), weight=ft.FontWeight.W_500, color=TEXT_DARK, overflow=ft.TextOverflow.ELLIPSIS),
                        width=400
                    )),
                    ft.DataCell(ft.Text(str(comp.get("created_at", "")).split(" ")[0] if comp.get("created_at") else "-", weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                    ft.DataCell(ft.Container(
                        content=ft.Text(status, color="white", size=10, weight="bold"),
                        bgcolor=color,
                        padding=ft.padding.symmetric(vertical=4, horizontal=10),
                        border_radius=15
                    )),
                ]
            )
        )

    complaints_table = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.Text("Complaint History", size=18, weight="bold", color=TEXT_DARK),
            ft.DataTable(
                expand=True,
                column_spacing=30,
                heading_row_color=ft.Colors.BLUE_GREY_50,
                columns=[
                    ft.DataColumn(ft.Text("ID", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Description", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Date Filed", weight="bold", color=ft.Colors.BLUE_900)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=ft.Colors.BLUE_900)),
                ],
                rows=complaint_rows if complaint_rows else [],
            )
        ], scroll=ft.ScrollMode.AUTO)
    )

    if not complaint_rows:
        complaints_table = ft.Container(
            bgcolor=CARD_BG,
            padding=50,
            border_radius=12,
            alignment=ft.Alignment(0, 0),
            content=ft.Text("No complaints filed yet.", weight="bold", size=14, color=TEXT_MUTED)
        )

    dash.content_column.controls = [header, stats_row, complaints_table]
    dash.page.update()


def open_complaint_form(dash):
    ref_description = ft.TextField(
        label="Complaint Description",
        hint_text="Please describe your issue in detail...",
        multiline=True,
        min_lines=5,
        border_color=ACCENT_BLUE
    )

    def handle_submit(e):
        if not ref_description.value or ref_description.value.strip() == "":
            dash.show_message("Please provide a description of your complaint.")
            return

        success, msg = dash.backend.submit_complaint(ref_description.value)
        
        if success:
            dash.show_message("Complaint submitted successfully!")
            dash.close_dialog()
            show_complaints(dash)
        else:
            dash.show_message(f"Error submitting complaint: {msg}")

    form_content = ft.Column([
        ft.Text("Please provide details about your complaint below", color=TEXT_MUTED),
        ref_description,
    ], spacing=15, tight=True, width=500)

    dash.show_custom_modal(
        "File a Complaint",
        form_content,
        [
            ft.TextButton("Cancel", on_click=dash.close_dialog),
            ft.Button("SUBMIT", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit)
        ]
    )
