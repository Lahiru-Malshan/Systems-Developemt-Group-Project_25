# Elena Ho - 25044389

import sys
import os
from turtle import color
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import flet as ft
from base_dashboard import *
from logic.search import *
from backend.FrontDesk.frontdesk import FrontDeskBackend


def _get_frontdesk_backend(dash):
    return FrontDeskBackend(user_id=getattr(dash, "user_id", None), username=getattr(dash, "username", None))

def show_residents(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    if not hasattr(dash, "resident_table_area"):
        dash.resident_table_area = ft.Column(expand=True)

    backend = _get_frontdesk_backend(dash)
    resident_data = backend.get_resident_directory()
    resident_stats = backend.get_resident_stats()
    dash.resident_data = resident_data

    block_options = sorted({resident.get("block", "N/A") for resident in resident_data if resident.get("block")})
    dropdown_options = [ft.dropdown.Option("All Blocks")] + [ft.dropdown.Option(block) for block in block_options]
    
    # --- 1. HEADER SECTION ---
    header = ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.APARTMENT_ROUNDED, size=18, color=ACCENT_BLUE),
                        ft.Text("Quick Stats", weight="bold", size=13,color=TEXT_DARK),], tight=True),
                    bgcolor=ft.Colors.with_opacity(0.1, ACCENT_BLUE),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=20,
                ),
                ft.Row([
                    ft.Text("Occupied:", size=13, weight="w500", color=TEXT_MUTED),
                    ft.Text(str(resident_stats["occupied_units"]), size=13, weight="bold", color=ACCENT_BLUE),
                    ft.VerticalDivider(width=10, color="transparent"),
                    ft.Text("Vacant:", size=13, weight="w500", color=TEXT_MUTED),
                    ft.Text(str(resident_stats["vacant_units"]), size=13, weight="bold", color=ft.Colors.ORANGE_700),
                ], spacing=5)
            ], spacing=15),
            ft.Button("Refresh Directory", icon=ft.Icons.REFRESH, bgcolor=ACCENT_BLUE, color="white",on_click=lambda _: show_residents(dash))
        ], alignment="spaceBetween")
    )

    # --- 2. SEARCH & FILTER SECTION ---
    dash.res_search_box = ft.TextField(
        label="Search by Name or Unit...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True, border_radius=10, bgcolor="white", color=TEXT_DARK,
    )
    
    dash.res_block_filter = ft.Dropdown(
        width=150,
        label="Block",
        color=TEXT_DARK,
        options=dropdown_options,
        value="All Blocks"
    )
    apply_btn = ft.Button(
        "Apply",
        icon=ft.Icons.SEARCH_ROUNDED,
        bgcolor=ACCENT_BLUE,
        color="white",
        height=45,
        on_click=lambda _: apply_resident_filters(dash)
    )

    filter_bar = ft.Container(
        padding=ft.padding.only(bottom=15),
        content=ft.Row([
            dash.res_search_box,
            dash.res_block_filter,
            apply_btn
        ], spacing=15)
    )
    
    # --- 3. RESIDENT TABLE ---
    table_card = ft.Container(
        bgcolor=CARD_BG, padding=20, border_radius=12, expand=7,
        content=ft.Column([
            ft.Text("Resident List", weight="bold", size=16, color=TEXT_DARK),
            dash.resident_table_area
        ])
    )
    
    side_panel = ft.Container(
        bgcolor=CARD_BG, padding=20, border_radius=12, expand=3,
        content=ft.Column([
            ft.Text("Demographics", size=18, weight="bold", color=TEXT_DARK),
            ft.Divider(),
            ft.Container(
                height=150, bgcolor=ft.Colors.BLUE_GREY_50, border_radius=10,
                alignment=ft.Alignment(0, 0),
                content=ft.Text("Chart Area", color=TEXT_MUTED)
            ),
            ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.PERSON_OUTLINE, color=ACCENT_BLUE),
                    title=ft.Text(r["name"], size=13, weight="bold", color=TEXT_DARK),
                    subtitle=ft.Text(f"Unit {r['room']}", size=11, color=TEXT_MUTED),
                    dense=True
                ) for r in resident_stats["recent_residents"]
            ])
        ], spacing=15)
    )
    
    main_layout = ft.Row([table_card, side_panel], spacing=20, expand=True,vertical_alignment="start",)

    dash.content_column.controls.extend([header, filter_bar, main_layout])
    apply_resident_filters(dash)

def apply_resident_filters(dash):
    if not hasattr(dash, "resident_table_area"): return

    block_filter = dash.res_block_filter.value
    filtered = SearchEngine.apply_logic(
        data_list=getattr(dash, "resident_data", []),
        search_term=dash.res_search_box.value,
        filters={"block": block_filter} if block_filter != "All Blocks" else None
    )

    rows = [_create_resident_row(dash, r) for r in filtered]

    dash.resident_table_area.controls = [
        ft.DataTable(
            expand=True,
            column_spacing=30,
            heading_row_color=ft.Colors.BLUE_GREY_50,
            columns=[
                ft.DataColumn(ft.Text("Unit", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Full Name", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Type", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Contact", weight="bold", color=TEXT_DARK)),
                ft.DataColumn(ft.Text("Actions", weight="bold", color=TEXT_DARK)),
            ],
            rows=rows
        )
    ]
    dash.page.update()

def draw_resident_registration(dash, *args):
    dash.show_message("Resident creation should go through tenant onboarding and lease management.")

def handle_save_resident(dash, block, room, name, phone, res_type):
    dash.show_message("Resident creation is not available from the front desk screen yet.")

def _create_resident_row(dash, item):
    type_color = ACCENT_BLUE if item["type"] == "Owner" else ft.Colors.ORANGE_700
    contact = item.get("contact", "")
    masked = f"{contact[:2]}****{contact[-3:]}" if len(contact) > 5 else contact

    return ft.DataRow(
        cells=[
            ft.DataCell(ft.Text(item["room"], color=TEXT_DARK, weight="bold")),
            ft.DataCell(ft.Text(item["name"], color=TEXT_DARK)),
            ft.DataCell(
                ft.Container(
                    content=ft.Text(item["type"].upper(), size=10, weight="bold", color="white"),
                    bgcolor=type_color,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    border_radius=15
                )
            ),
            ft.DataCell(ft.Text(masked, color=TEXT_DARK)),
            ft.DataCell(
                ft.Row([
                    ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_color=ACCENT_BLUE, icon_size=18),
                    ft.IconButton(ft.Icons.CONTACT_PHONE, icon_color=TEXT_MUTED, icon_size=18),
                ])
            ),
        ]
    )