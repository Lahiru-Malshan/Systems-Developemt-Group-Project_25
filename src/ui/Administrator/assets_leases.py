import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *
from db import get_db_connection


# -------- LEASE MOCK DATA (keep for now) --------
leases_data = [
    {"unit": "A-101", "tenant": "Alice Smith", "start": "2025-01-01", "end": "2026-01-01", "rent": "£1,200", "status": "Active"},
    {"unit": "B-205", "tenant": "Bob Johnson", "start": "2025-06-01", "end": "2026-06-01", "rent": "£1,500", "status": "Expiring Soon"},
]


# -------- FETCH ASSETS FROM DATABASE --------
def fetch_assets():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT asset_id, asset_name, asset_type, status, last_service
            FROM assets
            ORDER BY asset_id
        """)

        return cursor.fetchall()

    except Exception as e:
        print("Error fetching assets:", e)
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -------- INSERT ASSET INTO DATABASE --------
def create_asset(asset_id, asset_name, asset_type, status="Operational", last_service=None):
    conn = None
    cursor = None

    try:
        print("create_asset() started")
        conn = get_db_connection()
        print("DB connected")

        cursor = conn.cursor()

        query = """
        INSERT INTO assets (asset_id, asset_name, asset_type, status, last_service)
        VALUES (%s, %s, %s, %s, %s)
        """

        print("Running insert:", asset_id)
        cursor.execute(query, (asset_id, asset_name, asset_type, status, last_service))
        conn.commit()
        print("Insert successful!")

    except Exception as e:
        print("Error creating asset:", e)
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Connection closed")


# -------- MAIN VIEW --------
def show_assets(dash, tab_index=0, *args):
    dash.content_column.controls.clear()

    def get_assets_view():
        search_val = getattr(dash, "asset_search", ft.TextField()).value or ""
        rows = []
        assets_data = fetch_assets()

        for ast in assets_data:
            if search_val.lower() in ast["asset_name"].lower() or search_val.lower() in ast["asset_id"].lower():
                status_color = ft.Colors.GREEN if ast["status"] == "Operational" else ft.Colors.ORANGE_700

                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(ast["asset_id"], weight="bold", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(ast["asset_name"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(ast["asset_type"], color=TEXT_DARK)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(ast["status"], size=12, color="white", weight="bold"),
                                bgcolor=status_color,
                                padding=5,
                                border_radius=5
                            )
                        ),
                        ft.DataCell(ft.Text(str(ast["last_service"]), color=TEXT_DARK)),
                        ft.DataCell(ft.IconButton(ft.Icons.SETTINGS_OUTLINED, icon_color=TEXT_DARK, icon_size=18)),
                    ])
                )

        dash.asset_search = ft.TextField(
            label="Search Assets...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            color=TEXT_DARK,
            border_color=ACCENT_BLUE,
            on_submit=lambda _: show_assets(dash, tab_index=0)
        )

        return ft.Column([
            ft.Row([
                ft.Text("Building Asset Registry", size=18, weight="bold", color=TEXT_DARK),
                ft.Button(
                    "Add Asset",
                    icon=ft.Icons.ADD,
                    bgcolor=ACCENT_BLUE,
                    color="white",
                    on_click=lambda _: register_asset(dash)
                )
            ], alignment="spaceBetween"),
            ft.Row([
                dash.asset_search,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_assets(dash, tab_index=0)),
                ft.IconButton(
                    ft.Icons.REFRESH,
                    icon_color=ACCENT_BLUE,
                    on_click=lambda _: (setattr(dash.asset_search, "value", ""), show_assets(dash, tab_index=0))
                )
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Asset Name", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Type", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Last Service", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Action", weight="bold", color=TEXT_DARK)),
                ],
                rows=rows,
                expand=True
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

    def get_leases_view():
        search_val = getattr(dash, "lease_search", ft.TextField()).value or ""

        rows = []
        for l in leases_data:
            if search_val.lower() in l["tenant"].lower() or search_val.lower() in l["unit"].lower():
                l_color = ft.Colors.RED_400 if l["status"] == "Expiring Soon" else ft.Colors.BLUE_400
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(l["unit"], weight="bold", color=TEXT_DARK)),
                        ft.DataCell(ft.Text(l["tenant"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(l["start"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(l["end"], color=TEXT_DARK)),
                        ft.DataCell(ft.Text(l["rent"], color=ft.Colors.GREEN_700, weight="bold")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(l["status"], size=11, color="white", weight="bold"),
                                bgcolor=l_color,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                                border_radius=5
                            )
                        ),
                    ])
                )

        dash.lease_search = ft.TextField(
            label="Search Leases...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            color=TEXT_DARK,
            border_color=ACCENT_BLUE,
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
                ft.IconButton(
                    ft.Icons.REFRESH,
                    icon_color=ACCENT_BLUE,
                    on_click=lambda _: (setattr(dash.lease_search, "value", ""), show_assets(dash, tab_index=1))
                )
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
                rows=rows,
                expand=True
            )
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

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
                        ft.Tab(label="Asset Inventory", icon=ft.Icons.INVENTORY_2_OUTLINED),
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
                        ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[get_assets_view()]
                        ),
                        ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[get_leases_view()]
                        ),
                    ]
                )
            ]
        )
    )

    dash.content_column.controls.append(tabs)
    dash.page.update()


# -------- REGISTER ASSET FORM --------
def register_asset(dash, *args):
    id_input = ft.TextField(label="Asset ID", hint_text="e.g. AST-004", border_color=ACCENT_BLUE)
    name_input = ft.TextField(label="Asset Name", border_color=ACCENT_BLUE)
    type_input = ft.Dropdown(
        label="Type",
        border_color=ACCENT_BLUE,
        options=[
            ft.dropdown.Option("Machinery"),
            ft.dropdown.Option("Electrical"),
            ft.dropdown.Option("HVAC"),
            ft.dropdown.Option("Plumbing"),
        ],
        value="Machinery"
    )

    def handle_submit(e):
        print("Add Asset button submitted")

        if not id_input.value or not name_input.value:
            dash.show_message("Please fill in all required fields!")
            return

        try:
            print("Trying to insert:", id_input.value, name_input.value, type_input.value)

            create_asset(
                asset_id=id_input.value.upper(),
                asset_name=name_input.value,
                asset_type=type_input.value,
                status="Operational",
                last_service=datetime.now().strftime("%Y-%m-%d")
            )

            dash.close_dialog()
            dash.show_message(f"Asset {name_input.value} registered!")
            show_assets(dash, tab_index=0)
            dash.page.update()

        except Exception as ex:
            dash.show_message(f"Error: {str(ex)}")
            print("Insert error:", ex)

    content = ft.Column([
        ft.Text("Register a new building asset."),
        id_input,
        name_input,
        type_input,
        ft.Text("Note: Default status will be set to 'Operational'.", size=11, italic=True)
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("REGISTER", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit)
    ]

    dash.show_custom_modal("New Asset Registration", content, actions)


def register_lease(dash, *args):
    unit_input = ft.TextField(label="Unit Number", hint_text="e.g. C-302", border_color=ACCENT_BLUE)
    tenant_input = ft.TextField(label="Tenant Full Name", border_color=ACCENT_BLUE)
    rent_input = ft.TextField(label="Monthly Rent", hint_text="e.g. £1,500", border_color=ACCENT_BLUE)

    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = "2027-02-23"

    def handle_submit(e):
        if not unit_input.value or not tenant_input.value or not rent_input.value:
            dash.show_message("Please fill in all fields!")
            return

        leases_data.insert(0, {
            "unit": unit_input.value.upper(),
            "tenant": tenant_input.value,
            "start": start_date,
            "end": end_date,
            "rent": rent_input.value if "£" in rent_input.value else f"£{rent_input.value}",
            "status": "Active"
        })

        dash.close_dialog()
        dash.show_message(f"Lease for {unit_input.value} created!")
        show_assets(dash, tab_index=1)

    content = ft.Column([
        ft.Text("Create a new lease agreement.", color=TEXT_DARK, weight="bold"),
        unit_input,
        tenant_input,
        rent_input,
        ft.Row([
            ft.Icon(ft.Icons.CALENDAR_MONTH, size=16, color=TEXT_DARK),
            ft.Text(f"Term: {start_date} to {end_date}", size=12, color=TEXT_DARK)
        ], spacing=5)
    ], tight=True, spacing=15, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("CREATE LEASE", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit)
    ]

    dash.show_custom_modal("New Lease Agreement", content, actions)





































