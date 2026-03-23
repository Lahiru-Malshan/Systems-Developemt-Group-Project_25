import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *
import db # IMPORTANT: Connects to your MySQL database

def show_operations(dash, tab_index=0, *args):
    dash.content_column.controls.clear()

    # --- 1. VIEW: MAINTENANCE REQUESTS ---
    def get_maintenance_view():
        search_val = getattr(dash, "maint_search", ft.TextField()).value or ""
        
        # Fetch from MySQL
        maintenance_data = db.get_maintenance_requests()
        
        rows = []
        for req in maintenance_data:
            tenant_name = f"{req['first_name']} {req['last_name']}"
            unit = str(req["apartment_number"])
            
            if search_val.lower() in tenant_name.lower() or search_val.lower() in unit.lower():
                status_color = ft.Colors.RED_400 if req["status"] == "Pending" else ft.Colors.ORANGE_500 if req["status"] == "In Progress" else ft.Colors.GREEN_600
                
                # Truncate long descriptions for the table view
                desc = req["description"]
                short_desc = desc[:35] + "..." if len(desc) > 35 else desc

                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"MR-{req['request_id']}", weight="bold", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(unit, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(tenant_name, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(short_desc, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(str(req["reported_date"]), color=TEXT_DARK)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(req["status"], size=11, color="white", weight="bold"),
                                bgcolor=status_color, padding=5, border_radius=5
                            )
                        ),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.EDIT_DOCUMENT, icon_color=TEXT_DARK, icon_size=18, tooltip="Update Status",
                                on_click=lambda e, r=req: open_update_maintenance(dash, r)
                            )
                        ),
                    ])
                )

        dash.maint_search = ft.TextField(
            label="Search Requests (Unit or Tenant)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
            expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
            on_submit=lambda _: show_operations(dash, tab_index=0)
        )

        return ft.Column([
            ft.Row([
                ft.Text("Maintenance & Repairs", size=18, weight="bold", color=TEXT_DARK),
            ], alignment="spaceBetween"),
            ft.Row([
                dash.maint_search,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_operations(dash, tab_index=0)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.maint_search, "value", ""), show_operations(dash, tab_index=0)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Ticket ID", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Unit", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Tenant", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Issue", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Date", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Manage", weight="bold", color=TEXT_DARK)),
                ],
                rows=rows, expand=True
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    # --- 2. VIEW: TENANT COMPLAINTS ---
    def get_complaints_view():
        search_val = getattr(dash, "comp_search", ft.TextField()).value or ""
        
        # Fetch from MySQL
        complaints_data = db.get_all_complaints()
        
        rows = []
        for comp in complaints_data:
            tenant_name = f"{comp['first_name']} {comp['last_name']}"
            
            if search_val.lower() in tenant_name.lower():
                status_color = ft.Colors.RED_400 if comp["status"] == "Open" else ft.Colors.GREEN_600
                
                desc = comp["description"]
                short_desc = desc[:45] + "..." if len(desc) > 45 else desc

                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"FB-{comp['complaint_id']}", weight="bold", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(tenant_name, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(short_desc, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(str(comp["reported_date"]), color=TEXT_DARK)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(comp["status"], size=11, color="white", weight="bold"),
                                bgcolor=status_color, padding=5, border_radius=5
                            )
                        ),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.CHECK_CIRCLE_OUTLINE if comp["status"] == "Open" else ft.Icons.REPLAY, 
                                icon_color=TEXT_DARK, icon_size=18, tooltip="Toggle Status",
                                on_click=lambda e, c=comp: open_update_complaint(dash, c)
                            )
                        ),
                    ])
                )

        dash.comp_search = ft.TextField(
            label="Search Complaints (Tenant Name)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
            expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
            on_submit=lambda _: show_operations(dash, tab_index=1)
        )

        return ft.Column([
            ft.Row([
                ft.Text("Tenant Feedback & Complaints", size=18, weight="bold", color=TEXT_DARK),
            ], alignment="spaceBetween"),
            ft.Row([
                dash.comp_search,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_operations(dash, tab_index=1)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.comp_search, "value", ""), show_operations(dash, tab_index=1)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Tenant", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Details", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Date", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Action", weight="bold", color=TEXT_DARK)),
                ],
                rows=rows, expand=True
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    # --- 3. MAIN LAYOUT ---
    tabs = ft.Tabs(
        selected_index=tab_index,
        length=2,
        animation_duration=300,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Maintenance", icon=ft.Icons.HOME_REPAIR_SERVICE),
                        ft.Tab(label="Complaints", icon=ft.Icons.REPORT_PROBLEM),
                    ],
                    label_color=ACCENT_BLUE,
                    unselected_label_color=TEXT_DARK,
                    indicator_color=ACCENT_BLUE,
                    expand=True,
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[get_maintenance_view()]),
                        ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[get_complaints_view()]),
                    ]
                )
            ]
        )
    )

    dash.content_column.controls.append(tabs)
    dash.page.update()


# --- ACTION: UPDATE MAINTENANCE STATUS ---
def open_update_maintenance(dash, req):
    status_dropdown = ft.Dropdown(
        label="Current Status",
        options=[
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("In Progress"),
            ft.dropdown.Option("Resolved"),
        ],
        value=req["status"],
        border_color=ACCENT_BLUE
    )

    def save_maintenance(e):
        db.update_maintenance_status(req["request_id"], status_dropdown.value)
        dash.close_dialog()
        dash.show_message("Maintenance ticket updated!")
        show_operations(dash, tab_index=0)

    content = ft.Column([
        ft.Text(f"Ticket: MR-{req['request_id']} (Unit {req['apartment_number']})", weight="bold"),
        ft.Text(f"Issue: {req['description']}", italic=True, size=13),
        ft.Divider(),
        status_dropdown
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("SAVE", bgcolor=ACCENT_BLUE, color="white", on_click=save_maintenance)
    ]
    dash.show_custom_modal("Update Maintenance Ticket", content, actions)


# --- ACTION: UPDATE COMPLAINT STATUS ---
def open_update_complaint(dash, comp):
    new_status = "Closed" if comp["status"] == "Open" else "Open"
    
    def save_complaint(e):
        db.update_complaint_status(comp["complaint_id"], new_status)
        dash.close_dialog()
        dash.show_message(f"Complaint marked as {new_status}!")
        show_operations(dash, tab_index=1)

    content = ft.Column([
        ft.Text(f"Are you sure you want to mark Ticket FB-{comp['complaint_id']} as {new_status}?", size=14)
    ], tight=True)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("CONFIRM", bgcolor=ACCENT_BLUE, color="white", on_click=save_complaint)
    ]
    dash.show_custom_modal("Update Complaint", content, actions)