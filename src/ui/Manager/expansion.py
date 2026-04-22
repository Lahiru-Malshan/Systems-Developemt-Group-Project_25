
import sys
import os
from weakref import ref
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *

test_regional_admins = [
    {
        "city": "London",
        "admin_name": "Sarah Jenkins",
        "ni_number": "QQ123456C",
        "email": "sarah.j@paragon.uk",
        "phone": "077 0090 0123",
        "assigned_date": "2025-10-01",
        "status": "Active"
    },
    {
        "city": "Manchester",
        "admin_name": "Michael Scott",
        "ni_number": "AB987654D",
        "email": "m.scott@paragon.uk",
        "phone": "077 0090 0456",
        "assigned_date": "2025-11-15",
        "status": "Active"
    },
    {
        "city": "Bristol",
        "admin_name": "John Doe",
        "ni_number": "XY112233Z",
        "email": "j.doe@paragon.uk",
        "phone": "077 0090 0789",
        "assigned_date": "2026-01-10",
        "status": "Active"
    },
    {
        "city": "Cardiff",
        "admin_name": "Emma Wilson",
        "ni_number": "ZZ556677A",
        "email": "e.wilson@paragon.uk",
        "phone": "077 0090 0111",
        "assigned_date": "2026-02-05",
        "status": "On Leave"
    }
]

def show_expansion(dash):
    if not dash:
        return
    dash.content_column.controls.clear()
    if not hasattr(dash, "branch_table_area"):
        dash.branch_table_area = ft.Column(expand=True)

    # 1. HEADER: Strategic Growth
    header = ft.Row([
        ft.Column([
            ft.Text("Business Expansion & Growth", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Register new branch locations to scale multi-city operations ", size=14, color=TEXT_MUTED),
        ]),
        ft.Button(
            "Add New Branch",
            icon=ft.Icons.ADD_LOCATION_ALT_ROUNDED,
            bgcolor=ACCENT_BLUE,
            color=TEXT_WHITE,
            on_click=lambda _: draw_expansion_form(dash)
        )
    ], alignment="spaceBetween")
    
    dash.exp_name_search = ft.TextField(
        label="Search by  Admin Name",
        prefix_icon=ft.Icons.SEARCH,
        color=TEXT_DARK,
        expand=True, border_radius=10, bgcolor="white",
    )
    dash.exp_city_search = ft.Dropdown(
        width=150,
        label="City",
        color=TEXT_DARK,
        options=[ft.dropdown.Option("All Cities"), ft.dropdown.Option("London"), ft.dropdown.Option("Manchester"), ft.dropdown.Option("Bristol"), ft.dropdown.Option("Cardiff")],
        value="All Cities"
    )
    apply_btn = ft.Button(
        "Apply",
        icon=ft.Icons.SEARCH_ROUNDED,
        bgcolor=ACCENT_BLUE,
        color="white",
        height=45,
        on_click=lambda _: apply_expansion_filters(dash)
    )
    filter_bar = ft.Container(
        padding=ft.padding.only(bottom=15),
        content=ft.Row([
            dash.exp_name_search,
            dash.exp_city_search,
            apply_btn
        ], spacing=15)
    )
        
    table_card = ft.Container(
        bgcolor=CARD_BG, padding=20, border_radius=12,
        content=ft.Column([
            ft.Text("Regional Administration Directory", weight="bold", size=16, color=TEXT_DARK),
            dash.branch_table_area
        ])
    )
    dash.content_column.controls.extend([
        header,
        ft.Divider(height=10, color="transparent"),
        filter_bar,
        table_card
    ])
    refresh_branch_table(dash)
    dash.page.update()

def apply_expansion_filters(dash):
    name_query = dash.exp_name_search.value.lower() if dash.exp_name_search.value else ""
    city_query = dash.exp_city_search.value

    filtered_data = []
    for item in test_regional_admins:
        match_name = not name_query or name_query in item["admin_name"].lower()
        match_city = (city_query == "All Cities") or (item["city"] == city_query)
        if match_name and match_city:
            filtered_data.append(item)

    rows = []
    for item in filtered_data:
        phone = item["phone"]
        masked = f"{phone[:2]}****{phone[-3:]}" if len(phone) > 5 else phone

        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["city"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["admin_name"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["email"], color=ACCENT_BLUE)),
                ft.DataCell(ft.Text(masked, color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["ni_number"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["assigned_date"], color=TEXT_DARK)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(item["status"], color="white", size=10, weight="bold"),
                        bgcolor=ft.Colors.GREEN_700 if item["status"] == "Active" else ft.Colors.ORANGE_700,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=12
                    )
                ),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_size=18, icon_color=TEXT_MUTED),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_size=18, icon_color=ft.Colors.RED_300),
                    ], spacing=0)
                ),
            ])
        )

    dash.branch_table_area.controls = [
        ft.DataTable(
            expand=True,
            column_spacing=15,
            heading_row_color=ft.Colors.BLUE_GREY_50,
            columns=[
                ft.DataColumn(ft.Text("City Location", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Admin Name", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Admin Email", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Contact", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("NI Number", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Status", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Assigned Date", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Actions", color=TEXT_DARK)),
            ],
            rows=rows
        )
    ]
    dash.page.update()
    
def refresh_branch_table(dash):
    rows = []
    for item in test_regional_admins:
        phone = item["phone"]
        masked = f"{phone[:2]}****{phone[-3:]}" if len(phone) > 5 else phone

        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["city"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["admin_name"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["email"], color=ACCENT_BLUE)),
                ft.DataCell(ft.Text(masked, color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["ni_number"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(item["assigned_date"], color=TEXT_DARK)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(item["status"], color="white", size=10, weight="bold"),
                        bgcolor=ft.Colors.GREEN_700 if item["status"] == "Active" else ft.Colors.ORANGE_700,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=12
                    )
                ),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_size=18, icon_color=TEXT_MUTED),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_size=18, icon_color=ft.Colors.RED_300),
                    ], spacing=0)
                ),
            ])
        )

    dash.branch_table_area.controls = [
        ft.DataTable(
            expand=True,
            column_spacing=15,
            heading_row_color=ft.Colors.BLUE_GREY_50,
            columns=[
                ft.DataColumn(ft.Text("City Location", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Admin Name", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Admin Email", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Contact", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("NI Number", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Status", color=TEXT_DARK, weight="bold")),
                ft.DataColumn(ft.Text("Assigned Date", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Actions", color=TEXT_DARK)),
            ],
            rows=rows
        )
    ]

def draw_expansion_form(dash):
    dash.content_column.controls.clear()
    
    ref_city = ft.TextField(label="Branch City", expand=True, hint_text="e.g. Birmingham", color=TEXT_DARK)
    ref_address = ft.TextField(label="Regional Office Address", hint_text="Street, Postcode", expand=True, color=TEXT_DARK)
    
    ref_admin = ft.TextField(label="Full Name of Administrator", expand=True, color=TEXT_DARK)
    ref_ni = ft.TextField(label="National Insurance Number", expand=True, hint_text="e.g. QQ123456C", color=TEXT_DARK)
    
    ref_email = ft.TextField(label="Admin Email Address", expand=True, color=TEXT_DARK)
    ref_phone = ft.TextField(label="Contact Number", expand=True, color=TEXT_DARK)

    back_btn = ft.Button(
        content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16), ft.Text("Back to Directory")], tight=True),
        on_click=lambda _: show_expansion(dash)
    )
    registration_card = ft.Container(
        bgcolor=CARD_BG, padding=30, border_radius=12,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
        content=ft.Column([
            ft.Text("Strategic Branch Expansion", size=20, weight="bold", color=TEXT_DARK),
            ft.Text("Registering a new city will trigger the automated deployment of local infrastructure.", size=12, color=TEXT_MUTED),
            ft.Divider(),
            
            ft.Text("Location Details", weight="bold", size=14, color=TEXT_DARK),
            ft.Row([ref_city, ref_address], spacing=20),
            
            ft.Text("Administrator Identity (NI Required)", weight="bold", size=14, color=TEXT_DARK),
            ft.Row([ref_admin, ref_ni], spacing=20),
            
            ft.Text("Contact & System Access", weight="bold", size=14, color=TEXT_DARK),
            ft.Row([ref_email, ref_phone], spacing=20),
            
            ft.Divider(height=20),
            ft.Row([
                ft.Button(
                    "LAUNCH NEW BRANCH",
                    bgcolor=ACCENT_BLUE,
                    color="white",
                    icon=ft.Icons.SEND_ROUNDED,
                    height=50,
                    on_click=lambda _: handle_save_branch(
                        dash,
                        ref_city.value,
                        ref_address.value,
                        ref_admin.value,
                        ref_ni.value,
                        ref_email.value,
                        ref_phone.value
                    )
                )
            ], alignment="end")
        ], spacing=15)
    )

    dash.content_column.controls.extend([back_btn, registration_card])
    dash.page.update()
    
def handle_save_branch(dash, city, address, admin, ni, email, phone):
    if not city or not admin:
        dash.show_message("Error: City and Admin name are required!")
        return

    # temp_password = secrets.token_hex(4).upper() # Ví dụ: 4A2B9C1D
    
    dash.show_message(f"Initiating infrastructure for {city} and sending activation email...")
    
    global test_regional_admins
    test_regional_admins.insert(0, {
        "city": city,
        "admin_name": admin,
        "ni_number": ni.upper(),
        "email": email,
        "phone": phone,
        "assigned_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "Active"
    })
    
    # 4. Gửi Email (Chạy ngầm hoặc gọi hàm)
    # email_sent = send_activation_email(email, admin, city, temp_password)

    dash.show_message(f"Successfully expanded to {city}!")
    show_expansion(dash)