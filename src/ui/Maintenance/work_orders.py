
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from base_dashboard import *
from backend.Maintance.maintenance_process import MaintenanceProcessBackend


def _get_maintenance_backend(dash):
    return MaintenanceProcessBackend(user_id=getattr(dash, "user_id", None), username=getattr(dash, "username", None))

def show_work_orders(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    backend = _get_maintenance_backend(dash)
    dash.assigned_work_orders = backend.get_assigned_work_orders()
    
    dash.wo_status_tab = ft.SegmentedButton(
        selected=["all"],
        segments=[
            ft.Segment(value="all", label=ft.Text("All Tasks", color=ACCENT_BLUE_LIGHT)),
            ft.Segment(value="Pending", label=ft.Text("Pending", color= ACCENT_BLUE_LIGHT)),
            ft.Segment(value="In Progress", label=ft.Text("In Progress", color=ACCENT_BLUE_LIGHT)),
            ft.Segment(value="Resolved", label=ft.Text("Resolved", color=ACCENT_BLUE_LIGHT)),
        ],
    )
    dash.wo_status_tab.on_change = lambda _: apply_wo_filters(dash)
    
    # --- 1. HEADER ---
    header = ft.Row([
        ft.Column([
            ft.Text("Work Order Directory", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Tasks assigned to your maintenance account", color=TEXT_MUTED, size=13),
        ]),
        ft.Container(expand=True),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.REFRESH, color="white", size=20),
                ft.Text("REFRESH", weight="bold", color="white"),
            ], tight=True),
            bgcolor=ACCENT_BLUE,
            on_click=lambda _: show_work_orders(dash)
        ),
    ], alignment="spaceBetween")
    dash.wo_table_area = ft.Column(scroll=ft.ScrollMode.AUTO)
    
    table_container = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=dash.wo_table_area
    )
    dash.content_column.controls.extend([
        header,
        ft.Divider(height=10, color="transparent"),
        dash.wo_status_tab,
        ft.Divider(height=10, color="transparent"),
        table_container
    ])
    
    apply_wo_filters(dash)
    
def apply_wo_filters(dash):
    if not hasattr(dash, "wo_table_area"): return
    work_orders = getattr(dash, "assigned_work_orders", [])
    status_val = list(dash.wo_status_tab.selected)[0]
    
    if status_val == "all":
        filtered_list = work_orders
    else:
        filtered_list = [wo for wo in work_orders if wo["status"] == status_val]

    final_list = sorted(filtered_list, key=lambda x: x['reportedDate'], reverse=True)
    
    rows = []
    for wo in final_list:
        if wo["status"] == "Pending":
            action_btn = ft.Button(
                "Start Work",
                bgcolor=ACCENT_BLUE,
                color="white",
                on_click=lambda e, request_id=wo["request_id"]: handle_status_change(dash, request_id, "In Progress")
            )
        elif wo["status"] == "In Progress":
            action_btn = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.REPLAY_CIRCLE_FILLED_ROUNDED,
                    icon_color=ft.Colors.ORANGE_700,
                    on_click=lambda e, request_id=wo["request_id"]: handle_status_change(dash, request_id, "Pending")
                ),
                ft.Button(
                    "Finish",
                    bgcolor=ft.Colors.GREEN_700,
                    color="white",
                    on_click=lambda e, request_id=wo["request_id"], work_order_id=wo["id"]: open_completion_report(dash, request_id, work_order_id)
                )
            ], spacing=5, tight=True)
        else:
            action_btn = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400)

        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(wo["id"], weight="bold", color=TEXT_DARK)),
                ft.DataCell(ft.Text(wo["room"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(wo["issue"], color=TEXT_DARK)),
                ft.DataCell(_create_status_badge(wo["status"])),
                ft.DataCell(ft.Text(wo.get("completionDate", "-"), color=TEXT_DARK)),
                ft.DataCell(action_btn),
            ])
        )

    dash.wo_table_area.controls = [
        ft.DataTable(
            expand=True,
            column_spacing=45,
            heading_row_color=ft.Colors.BLUE_GREY_50,
            heading_row_height=50,
            columns=[
                ft.DataColumn(ft.Text("ID", weight="bold", color=ACCENT_BLUE)),
                ft.DataColumn(ft.Text("Unit", weight="bold", color=ACCENT_BLUE)),
                ft.DataColumn(ft.Text("Issue", weight="bold", color=ACCENT_BLUE)),
                ft.DataColumn(ft.Text("Status", weight="bold", color=ACCENT_BLUE)),
                ft.DataColumn(ft.Text("Completed", weight="bold", color=ACCENT_BLUE)),
                ft.DataColumn(ft.Text("Action", weight="bold", color=ACCENT_BLUE)),
            ],
            rows=rows
        )
    ]

    dash.page.update()

def handle_status_change(dash, request_id, new_status):
    backend = _get_maintenance_backend(dash)
    success, message = backend.update_work_order_status(request_id, new_status)
    dash.show_message(message)
    if success:
        show_work_orders(dash)

def open_completion_report(dash, request_id, wo_id):
    date_input = ft.TextField(
        label="Completion Date",
        value="Auto-set to today when resolved",
        width=250,
        prefix_icon=ft.Icons.CALENDAR_TODAY,
        disabled=True,
    )
    report_input = ft.TextField(
        label="Maintenance Report",
        multiline=True,
        min_lines=3,
        hint_text="Describe the fix or parts replaced...",
        border_radius=10,
        autofocus=True,
    )

    def submit_resolve(e):
        if not report_input.value.strip():
            dash.show_message("Please provide a resolution report!")
            return

        backend = _get_maintenance_backend(dash)
        success, message = backend.update_work_order_status(request_id, "Resolved")
        if not success:
            dash.show_message(message)
            return
        
        dash.close_dialog()
        dash.show_message(f"Task {wo_id} has been resolved.")
        show_work_orders(dash)
        
    dash.show_custom_modal(
        title=f"Complete Task: {wo_id}",
        content=ft.Column([
            ft.Text("Enter the work details and verify completion date:", color=TEXT_MUTED),
            date_input, report_input,
        ], tight=True, spacing=15),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
            ft.Button("Submit & Resolve", bgcolor=ft.Colors.GREEN_700, color="white", on_click=submit_resolve)
        ]
    )

def _create_status_badge(status):
    colors = {"Pending": ft.Colors.RED_100, "In Progress": ft.Colors.ORANGE_100, "Resolved": ft.Colors.GREEN_100}
    text_colors = {"Pending": ft.Colors.RED_700, "In Progress": ft.Colors.ORANGE_700, "Resolved": ft.Colors.GREEN_700}
    return ft.Container(
        content=ft.Text(status, size=11, weight="bold", color=text_colors.get(status, ft.Colors.BLACK)),
        bgcolor=colors.get(status, ft.Colors.GREY_100),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=5
    )