#Lahiru_Malshan - 25044389

import sys
import os
from turtle import color
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *
import db # IMPORTANT: Connects to MySQL

def show_assets(dash, tab_index=0, *args):
    dash.content_column.controls.clear()

    # --- 1. VIEW: APARTMENTS (ASSETS) ---
    def get_assets_view():
        search_val = getattr(dash, "asset_search", ft.TextField()).value or ""
        
        # Fetch actual apartments from MySQL
        apartments_data = db.get_all_apartments()
        
        rows = []
        for apt in apartments_data:
            apt_num = str(apt["apartment_number"])
            if search_val.lower() in apt_num.lower():
                status_color = ft.Colors.GREEN if apt["status"] == "Available" else ft.Colors.ORANGE_700 if apt["status"] == "Maintenance" else ft.Colors.BLUE_500
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"APT-{apt['apartment_id']}", weight="bold", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(apt_num, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(f"{apt['bedrooms']} Bed / {apt['bathrooms']} Bath", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(f"£{apt['rent']}", color=TEXT_DARK, weight="bold")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(apt["status"], size=12, color="white", weight="bold"),
                                bgcolor=status_color, padding=5, border_radius=5
                            )
                        ),
                        ft.DataCell(ft.IconButton(ft.Icons.SETTINGS_OUTLINED, icon_color=TEXT_DARK, icon_size=18)),
                    ])
                )
        dash.asset_search = ft.TextField(
            label="Search Apartments (Unit #)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
            expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
            on_submit=lambda _: show_assets(dash, tab_index=0)
        )
        
        return ft.Column([
            ft.Row([
                ft.Text("Property Assets (Apartments)", size=18, weight="bold", color=TEXT_DARK),
                ft.Button(
                    "Add Apartment",
                    icon=ft.Icons.ADD,
                    bgcolor=ACCENT_BLUE,
                    color="white",
                    on_click=lambda _: register_apartment(dash)
                )
            ], alignment="spaceBetween"),
            ft.Row([
                dash.asset_search,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_assets(dash, tab_index=0)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.asset_search, "value", ""), show_assets(dash, tab_index=0)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Unit Number", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Layout", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Monthly Rent", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Action", weight="bold", color=TEXT_DARK)),
                ],
                rows=rows, expand=True
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    # --- 2. VIEW: LEASE MANAGEMENT ---
    def get_leases_view():
        search_val = getattr(dash, "lease_search", ft.TextField()).value or ""
        
        # Fetch actual leases from MySQL
        leases_data = db.get_all_leases()
        
        rows = []
        for l in leases_data:
            tenant_name = f"{l['first_name']} {l['last_name']}"
            if search_val.lower() in tenant_name.lower() or search_val.lower() in str(l["apartment_number"]).lower():
                l_color = ft.Colors.RED_400 if l["status"] == "Expired" else ft.Colors.BLUE_400
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(l["apartment_number"]), weight="bold", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(tenant_name, color=TEXT_DARK)),
                        ft.DataCell(ft.Text(str(l["start_date"]), color=TEXT_DARK)),
                        ft.DataCell(ft.Text(str(l["end_date"]), color=TEXT_DARK)),
                        ft.DataCell(ft.Text(f"£{l['monthly_rent']}", color=ft.Colors.GREEN_700, weight="bold")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(l["status"], size=11, color="white", weight="bold"),
                                bgcolor=l_color, padding=ft.Padding.symmetric(horizontal=8, vertical=2), border_radius=5
                            )
                        ),
                    ])
                )
        dash.lease_search = ft.TextField(
            label="Search Leases (Tenant or Unit)...", prefix_icon=ft.Icons.SEARCH, value=search_val,
            expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
            on_submit=lambda _: show_assets(dash, tab_index=1)
        )

        return ft.Column([
            ft.Row([
                ft.Text("Active Lease Agreements", size=18, weight="bold", color=TEXT_DARK),
                ft.Button(
                    "New Lease",
                    icon=ft.Icons.KEY,
                    bgcolor=ACCENT_BLUE,
                    color="white",
                    on_click=lambda _: register_lease(dash)
                    )
            ], alignment="spaceBetween"),
            ft.Row([
                dash.lease_search,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_assets(dash, tab_index=1)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.lease_search, "value", ""), show_assets(dash, tab_index=1)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Unit", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Tenant Name", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Start Date", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("End Date", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Rent", color=TEXT_DARK, weight="bold")),
                    ft.DataColumn(ft.Text("Status", color=TEXT_DARK, weight="bold")),
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
                        ft.Tab(label="Property Assets", icon=ft.Icons.APARTMENT),
                        ft.Tab(label="Lease Management", icon=ft.Icons.ASSIGNMENT_OUTLINED),
                    ],
                    label_color=ACCENT_BLUE,
                    unselected_label_color=TEXT_DARK,
                    indicator_color=ACCENT_BLUE,
                    expand=True,
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[get_assets_view()]),
                        ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[get_leases_view()]),
                    ]
                )
            ]
        )
    )

    dash.content_column.controls.append(tabs)
    dash.page.update()

def register_apartment(dash, *args):
    unit_input = ft.TextField(label="Apartment Number", hint_text="e.g. A-101", border_color=ACCENT_BLUE)
    bed_input = ft.TextField(label="Bedrooms", hint_text="e.g. 2", border_color=ACCENT_BLUE, keyboard_type=ft.KeyboardType.NUMBER)
    bath_input = ft.TextField(label="Bathrooms", hint_text="e.g. 1", border_color=ACCENT_BLUE, keyboard_type=ft.KeyboardType.NUMBER)
    rent_input = ft.TextField(label="Monthly Rent (£)", hint_text="e.g. 1500.00", border_color=ACCENT_BLUE, keyboard_type=ft.KeyboardType.NUMBER)

    def handle_submit(e):
        if not unit_input.value or not bed_input.value or not rent_input.value:
            dash.show_message("Please fill in all required fields!")
            return

        # Note: Hardcoding location_id=1. You must have at least one location in your DB!
        success = db.add_apartment(1, unit_input.value, int(bed_input.value), int(bath_input.value), float(rent_input.value))
        
        if success:
            dash.close_dialog()
            dash.show_message(f"Apartment {unit_input.value} added!")
            show_assets(dash, tab_index=0)
        else:
            dash.show_message("Database Error: Could not add apartment.")
        
    content = ft.Column([
        ft.Text("Register a new apartment to the building."),
        unit_input,
        bed_input,
        bath_input,
        rent_input,
        ft.Text("Note: Default status will be set to 'Available'.", size=11, italic=True)
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("ADD APARTMENT", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit)
    ]

    dash.show_custom_modal("New Apartment Registration", content, actions)

def register_lease(dash, *args):
    # Using Database IDs for simplicity. In a real app, these would be Dropdowns fetching from DB!
    tenant_id_input = ft.TextField(label="Tenant ID (from Tenants table)", border_color=ACCENT_BLUE, keyboard_type=ft.KeyboardType.NUMBER)
    apt_id_input = ft.TextField(label="Apartment ID", border_color=ACCENT_BLUE, keyboard_type=ft.KeyboardType.NUMBER)
    rent_input = ft.TextField(label="Agreed Monthly Rent (£)", hint_text="e.g. 1500.00", border_color=ACCENT_BLUE, keyboard_type=ft.KeyboardType.NUMBER)
    start_input = ft.TextField(label="Start Date (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"), border_color=ACCENT_BLUE)
    end_input = ft.TextField(label="End Date (YYYY-MM-DD)", hint_text="e.g. 2027-01-01", border_color=ACCENT_BLUE)

    def handle_submit(e):
        if not tenant_id_input.value or not apt_id_input.value or not rent_input.value:
            dash.show_message("Please fill in all fields!")
            return

        success = db.add_lease(
            int(tenant_id_input.value),
            int(apt_id_input.value),
            start_input.value,
            end_input.value,
            float(rent_input.value)
        )
        
        if success:
            dash.close_dialog()
            dash.show_message("Lease created successfully! Apartment is now Occupied.")
            show_assets(dash, tab_index=1)
        else:
            dash.show_message("Error: Check if Tenant ID and Apartment ID are valid.")

    content = ft.Column([
        ft.Text("Create a new lease agreement.", ),
        tenant_id_input,
        apt_id_input,
        rent_input,
        start_input,
        end_input,
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("CREATE LEASE", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit)
    ]

    dash.show_custom_modal("New Lease Agreement", content, actions)