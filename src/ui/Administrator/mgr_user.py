
import sys
import os
from turtle import color
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from base_dashboard import *
from logic.search import *
import db # Connects to your database


STAFF_ROLE_OPTIONS = [
    "Administrator",
    "Manager",
    "Front Desk",
    "Maintenance",
    "Finance Manager",
]

def show_user(dash, tab_index=0, *args):
    dash.content_column.controls.clear()
    
    # TAB 1: STAFF MANAGEMENT
    def get_staff_view():
        search_val = getattr(dash, "staff_search", ft.TextField()).value or ""
        
        # Fetch from database
        staff_data = db.get_all_staff()
        
        current_rows = []
        for staff in staff_data:
            username = staff.get("ni") or staff.get("username") or ""
            if search_val.lower() in staff["name"].lower() or search_val.lower() in username.lower():
                current_rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(username, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(staff["name"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(staff["role"], color=TEXT_DARK)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(staff["status"], size=12, color="green" if staff["status"] == "Active" else "red"),
                                bgcolor=ft.Colors.with_opacity(0.1, "green" if staff["status"] == "Active" else "red"),
                                padding=5,
                                border_radius=5
                            )
                        ),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.EDIT, icon_size=18, icon_color=TEXT_DARK,
                                    on_click=lambda e, s=staff: edit_staff(dash, s)
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE, icon_color="red", icon_size=18,
                                    on_click=lambda e, username=username: delete_staff_record(dash, username)
                                )
                            ])
                        ),
                    ])
                )
        dash.staff_search = ft.TextField(
            label="Search Staff (Name/Username)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
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
                    ft.DataColumn(ft.Text("Username", weight="bold", color=TEXT_DARK)),
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
        
        # Fetch pending residents from database
        pending_residents = db.get_pending_residents()
        
        rows = []
        for r in pending_residents:
            if search_val.lower() in r["name"].lower():
                # Clean up the date display
                req_date = str(r["created_at"]).split()[0] if r.get("created_at") else "Unknown"
                
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(r["name"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text("Unassigned", color=TEXT_DARK, italic=True)), 
                        ft.DataCell(ft.Text("Tenant", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(req_date, color=TEXT_DARK)),
                        ft.DataCell(ft.Row([
                            ft.IconButton(
                                ft.Icons.CHECK, icon_color="green", tooltip="Approve",
                                on_click=lambda e, uid=r["user_id"]: handle_approve(dash, uid)
                            ),
                            ft.IconButton(
                                ft.Icons.CLOSE, icon_color="red", tooltip="Reject",
                                on_click=lambda e, uid=r["user_id"]: handle_reject(dash, uid)
                            )
                        ])),
                    ])
                )

        dash.res_search = ft.TextField(
            label="Search Residents (Name)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
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
                        ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[get_staff_view()]),
                        ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[get_resident_view()]),
                        ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[get_logs_view()]),
                    ]
                )
            ]
        )
    )

    dash.content_column.controls.append(tabs)
    dash.page.update()

# --- DATABASE ACTIONS: STAFF ---
def delete_staff_record(dash, username):
    db.delete_staff(username)
    dash.show_message(f"Staff record {username} deleted.")
    show_user(dash, tab_index=0)

def edit_staff(dash, staff):
    username = staff.get("ni") or staff.get("username") or ""
    name_input = ft.TextField(label="Full Name", value=staff["name"], border_color=ACCENT_BLUE)
    role_input = ft.Dropdown(
        label="Role",
        border_color=ACCENT_BLUE,
        options=[ft.dropdown.Option(role_name) for role_name in STAFF_ROLE_OPTIONS],
        value=staff["role"]
    )
    status_input = ft.Dropdown(
        label="Status",
        border_color=ACCENT_BLUE,
        options=[ft.dropdown.Option("Active"), ft.dropdown.Option("Inactive")],
        value=staff["status"]
    )

    def handle_update(e):
        if not name_input.value:
            dash.show_message("Name cannot be empty!")
            return
        
        db.update_staff(username, name_input.value, role_input.value, status_input.value)
        dash.close_dialog()
        dash.show_message("Staff updated successfully!")
        show_user(dash, tab_index=0) 

    content = ft.Column([
        ft.Text(f"Editing record for Username: {username}", weight="bold"),
        name_input,
        role_input,
        status_input
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("UPDATE", bgcolor=ACCENT_BLUE, color="white", on_click=handle_update)
    ]
    dash.show_custom_modal("Edit Staff", content, actions)

def register_staff(dash, *args):
    username_input = ft.TextField(
        label="Username",
        hint_text="e.g. jsmith",
        border_color=ACCENT_BLUE,
    )
    name_input = ft.TextField(
        label="Full Name",
        hint_text="Enter staff full name",
        border_color=ACCENT_BLUE
    )
    role_input = ft.Dropdown(
        label="Role",
        border_color=ACCENT_BLUE,
        options=[ft.dropdown.Option(role_name) for role_name in STAFF_ROLE_OPTIONS],
        value="Front Desk"
    )

    def handle_submit(e):
        if not username_input.value or not name_input.value:
            dash.show_message("Please fill in all required fields!")
            return

        # pass the username value to existing add_staff API (it expects an "ni" string)
        result = db.add_staff(username_input.value.upper(), name_input.value, role_input.value)
        
        if result["success"]:
            dash.close_dialog()
            dash.show_message(
                f"Staff {name_input.value} registered. Username: {result['username']} | Temporary password: {result['password']}"
            )
            show_user(dash, tab_index=0)
        else:
            dash.show_message(f"Error: Could not save staff record. {result.get('error', '')}")

    content = ft.Column([
        ft.Text("Register a new staff member for this branch."),
        username_input,
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

# --- DATABASE ACTIONS: RESIDENTS ---
def handle_approve(dash, user_id):
    db.approve_resident(user_id)
    dash.show_message("Resident approved successfully!")
    show_user(dash, tab_index=1)

def handle_reject(dash, user_id):
    db.reject_resident(user_id)
    dash.show_message("Resident request rejected and deleted.")
    show_user(dash, tab_index=1)