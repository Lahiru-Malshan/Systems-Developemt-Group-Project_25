import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *
from db import get_db_connection


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
def show_assets(dash, *args):
    dash.content_column.controls.clear()

    def get_assets_view():
        rows = []
        assets_data = fetch_assets()

        for ast in assets_data:
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
                ])
            )

        return ft.Column([
            ft.Row([
                ft.Text("Asset Inventory", size=18, weight="bold"),
                ft.ElevatedButton(
                    "Add Asset",
                    icon=ft.Icons.ADD,
                    bgcolor=ACCENT_BLUE,
                    color="white",
                    on_click=lambda _: register_asset(dash)
                )
            ], alignment="spaceBetween"),

            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Name")),
                    ft.DataColumn(ft.Text("Type")),
                    ft.DataColumn(ft.Text("Status")),
                    ft.DataColumn(ft.Text("Last Service")),
                ],
                rows=rows
            )
        ])

    dash.content_column.controls.append(get_assets_view())
    dash.page.update()


# -------- REGISTER ASSET FORM --------
def register_asset(dash):
    id_input = ft.TextField(label="Asset ID")
    name_input = ft.TextField(label="Asset Name")

    type_input = ft.Dropdown(
        label="Type",
        options=[
            ft.dropdown.Option("Machinery"),
            ft.dropdown.Option("Electrical"),
            ft.dropdown.Option("HVAC"),
            ft.dropdown.Option("Plumbing"),
        ],
        value="Machinery"
    )

    def handle_submit(e):
        print("Add Asset button clicked")

        if not id_input.value or not name_input.value:
            dash.show_message("Fill all fields!")
            return

        try:
            print("Trying insert:", id_input.value)

            create_asset(
                asset_id=id_input.value.upper(),
                asset_name=name_input.value,
                asset_type=type_input.value,
                status="Operational",
                last_service=datetime.now().strftime("%Y-%m-%d")
            )

            dash.close_dialog()
            dash.show_message("Asset added!")

            show_assets(dash)
            dash.page.update()

        except Exception as ex:
            print("ERROR:", ex)
            dash.show_message(str(ex))

    dash.show_custom_modal(
        "Add Asset",
        ft.Column([id_input, name_input, type_input]),
        [
            ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
            ft.ElevatedButton("Save", on_click=handle_submit)
        ]
    )









































