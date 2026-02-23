import sys
import os
from turtle import color
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from base_dashboard import *
from logic.search import *

staff_data = [
    {"ni": "AB123456C", "name": "John Wick", "role": "Front Desk", "status": "Active"},
]

def show_user(dash, tab_index=0, *args):
    dash.content_column.controls.clear()
    
    # TAB 1: STAFF MANAGEMENT
    def get_staff_view():
        search_val = getattr(dash, "staff_search", ft.TextField()).value or ""
        
        current_rows = []
        for staff in staff_data:
            if search_val.lower() in staff["name"].lower() or search_val.lower() in staff["ni"].lower():
                current_rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(staff["ni"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(staff["name"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(staff["role"], color=TEXT_DARK)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(staff["status"], size=12, color="green"),
                                bgcolor=ft.Colors.with_opacity(0.1, "green"),
                                padding=5,
                                border_radius=5
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT, icon_size=18, icon_color=TEXT_DARK),
                                ft.IconButton(ft.Icons.DELETE, icon_color="red", icon_size=18)
                            ])
                        ),
                    ])
                )
        dash.staff_search = ft.TextField(
            label="Search Staff (Name/NI)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
            expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
            on_submit=lambda _: show_user(dash, tab_index=0)
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Branch Staff Directory", size=18, weight="bold", color=TEXT_DARK),
                ft.Button(
                    "Register New Staff",
                    icon=ft.Icons.ADD,
                    bgcolor=ACCENT_BLUE,
                    color="white",
                    on_click=lambda _: register_staff(dash)
                )
            ], alignment="spaceBetween"),
            ft.Row([
                dash.staff_search,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_user(dash, tab_index=0)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.staff_search, "value", ""), show_user(dash, tab_index=0)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("NI Number", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Full Name", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Role", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Actions", weight="bold", color=TEXT_DARK)),
                ],
                rows=current_rows,
                expand=True
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
    # TAB 2: RESIDENTS APPROVALS
    def get_resident_view():
        search_val = getattr(dash, "res_search", ft.TextField()).value or ""
        
        residents = [{"name": "Alice Smith", "unit": "A-101", "type": "Tenant", "date": "2026-02-22"}]
        
        rows = []
        for r in residents:
            if search_val.lower() in r["name"].lower() or search_val.lower() in r["unit"].lower():
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(r["name"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(r["unit"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(r["type"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(r["date"], color=TEXT_DARK)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(ft.Icons.CHECK, icon_color="green"),
                            ft.IconButton(ft.Icons.CLOSE, icon_color="red")
                        ])),
                    ])
                )

        dash.res_search = ft.TextField(
            label="Search Residents (Name/Unit)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
            expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
            on_submit=lambda _: show_user(dash, tab_index=1)
        )
        
        return ft.Column([
            ft.Text("Pending Verification Requests", size=18, weight="bold", color=TEXT_DARK),
            ft.Row([
                dash.res_search,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_user(dash, tab_index=1)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.res_search, "value", ""), show_user(dash, tab_index=1)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Name", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Unit", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Type", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Requested At", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Approval", color=TEXT_DARK, weight="bold")),
                ],rows=rows, expand=True
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
    # TAB 3: SECURITY LOGS
    def get_logs_view():
        logs_list = ft.ListView(expand=True, spacing=10)
        logs = [
            {"time": "18:45:02", "event": "Failed login attempt", "color": "orange"},
            {"time": "16:20:11", "event": "Admin JohnW changed permissions", "color": "blue"},
        ]
        for log in logs:
            logs_list.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SHIELD_OUTLINED, color=log["color"]),
                    title=ft.Text(log["event"], size=14, color=TEXT_DARK),
                    subtitle=ft.Text(f"Timestamp: {log['time']}", size=12),
                    bgcolor=ft.Colors.with_opacity(0.02, TEXT_DARK),
                )
            )
        return ft.Column([
            ft.Text("System Security Audit Trail", size=18, weight="bold", color=TEXT_DARK),
            logs_list
        ], expand=True)
        
    # --- 3. MAIN LAYOUT  ---
    tabs =ft.Tabs(
        selected_index=tab_index,
        length=3,
        animation_duration=300,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Staff Management", icon=ft.Icons.PEOPLE),
                        ft.Tab(label="Resident Approvals", icon=ft.Icons.PERSON_SEARCH),
                        ft.Tab(label="Security Logs", icon=ft.Icons.LOCK_CLOCK),
                    ],
                    label_color=ACCENT_BLUE,
                    unselected_label_color=TEXT_DARK,
                    indicator_color=ACCENT_BLUE,
                    expand=True,
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        # TAB 1
                        ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[get_staff_view()]
                        ),
                        # TAB 2
                        ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[get_resident_view()]
                        ),
                        # TAB 3
                        ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[get_logs_view()]
                        ),
                    ]
                )
            ]
        )
    )

    dash.content_column.controls.append(tabs)
    dash.page.update()

def register_staff(dash, *args):
    ni_input = ft.TextField(
        label="National Insurance (NI) Number",
        hint_text="e.g. QQ123456C",
        border_color=ACCENT_BLUE,
        capitalization=ft.TextCapitalization.CHARACTERS
    )
    name_input = ft.TextField(
        label="Full Name",
        hint_text="Enter staff full name",
        border_color=ACCENT_BLUE
    )
    role_input = ft.Dropdown(
        label="Role",
        border_color=ACCENT_BLUE,
        options=[
            ft.dropdown.Option("Front Desk"),
            ft.dropdown.Option("Maintenance"),
            ft.dropdown.Option("Security"),
            ft.dropdown.Option("Manager"),
        ],
        value="Front Desk"
    )

    def handle_submit(e):
        if not ni_input.value or not name_input.value:
            dash.show_message("Please fill in all required fields!")
            return

        staff_data.insert(0, {
            "ni": ni_input.value.upper(),
            "name": name_input.value,
            "role": role_input.value,
            "status": "Active"
        })
        
        dash.close_dialog()
        dash.show_message(f"Staff {name_input.value} registered!")
        show_user(dash)
        
    content = ft.Column([
        ft.Text("Register a new staff member for this branch."),
        ni_input,
        name_input,
        role_input,
        ft.Text("Note: Default status will be set to 'Active'.", size=11, italic=True)
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton(
            "REGISTER STAFF",
            bgcolor=ACCENT_BLUE,
            color="white",
            on_click=handle_submit
        )
    ]

    dash.show_custom_modal("New Staff Registration", content, actions)