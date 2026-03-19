# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from datetime import datetime
import flet as ft
from logic.notifications import *
from logic.search import *
from base_dashboard import *

parcels_data = [
    {"room": "302", "carrier": "SPX Express", "time": "10:30 AM", "type": "Standard", "status": "Delivered", "days": 0},
    {"room": "105", "carrier": "UberEat", "time": "11:45 AM", "type": "Cold Storage", "status": "Pending", "days": 1},
    {"room": "105", "carrier": "Amazon", "time": "12:45 AM", "type": "Standard", "status": "Pending", "days": 2},
]
def show_parcel(dash, *args):
    if not dash: return
    if not hasattr(dash, "parcel_list_column"):
        dash.parcel_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)
    dash.content_column.controls.clear()
    
    dash.parcel_search = ft.TextField(
        label="Search Unit or Carrier",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        bgcolor="white",
        color=TEXT_DARK,
        value="",
        expand=True,
    )
    filter_btn = ft.Button(
        "Apply",icon=ft.Icons.SEARCH_ROUNDED,
        on_click=lambda _: apply_parcel_filters(dash),
        bgcolor=ACCENT_BLUE,
        color="white",
        height=40
    )
    
    # --- 1. HEADER / ACTION BAR ---
    header = ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LIGHTBULB_OUTLINED, size=16, color=ACCENT_BLUE),
                        ft.Text("Quick Actions", weight="w500", color=TEXT_DARK, size=13),
                    ], tight=True),
                    bgcolor=ft.Colors.with_opacity(0.1, ACCENT_BLUE),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=20,
                ),
                ft.Text("Log deliveries and manage pickups", color=TEXT_MUTED, size=12, italic=True),
            ], spacing=15),

            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_BOX_ROUNDED, color="white", size=20),
                    ft.Text("Receive New Parcel", weight="bold", color="white"),
                ], tight=True),
                bgcolor=ACCENT_BLUE,
                on_click=lambda _: draw_add_parcel_form(dash)
            )
        ], alignment="spaceBetween")
    )

    # --- 2. STATS CARDS ---
    parcel_stats = ft.Row([
        dash.create_stat_card("Waiting Pickup", "18", ft.Icons.HOURGLASS_EMPTY_ROUNDED),
        dash.create_stat_card("Today Received", "42", ft.Icons.MOVE_TO_INBOX_ROUNDED),
        dash.create_stat_card("Overdue (3+ days)", "5", ft.Icons.WARNING_AMBER_ROUNDED, highlight=True),
    ], spacing=20)

    # --- 3. PARCEL LIST DATA  ---
    dash.parcel_list_column.controls.clear()
    for p in parcels_data:
        dash.parcel_list_column.controls.append(_create_parcel_item(dash, p))
    
    parcel_table = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.Row([dash.parcel_search, filter_btn], spacing=10),
            ft.Divider(height=10, color="transparent"),
            ft.Text("Recent Parcels List", weight="bold", color=TEXT_DARK),
            ft.Container(content=dash.parcel_list_column, expand=True)
        ])
    )

    dash.content_column.controls.extend([header, parcel_stats, parcel_table])
    apply_parcel_filters(dash)
    dash.page.update()


def apply_parcel_filters(dash):
    if not hasattr(dash, "parcel_list_column") or dash.parcel_list_column is None:
        return

    dash.parcel_list_column.controls.clear()
    filtered = SearchEngine.apply_logic(
        data_list=parcels_data,
        search_term=dash.parcel_search.value
    )

    final_list = sorted(filtered, key=lambda x: (x["status"] == "Delivered", x["days"]), reverse=False)

    dash.parcel_list_column.controls.clear()
    for p in final_list:
        dash.parcel_list_column.controls.append(
            _create_parcel_item(dash, p)
        )
    
    dash.page.update()

def draw_add_parcel_form(dash, *args):
    dash.content_column.controls.clear()
    
    ref_room = ft.TextField(label="Unit Number", expand=True, hint_text="e.g. 302", border_radius=8, color=TEXT_DARK)
    ref_recipient = ft.TextField(label="Recipient Name (Optional)", expand=True, border_radius=8, color=TEXT_DARK)
    ref_carrier = ft.Dropdown(
        label="Carrier",
        expand=True,
        border_radius=8,
        color=TEXT_DARK,
        options=[ft.dropdown.Option(x) for x in ["Royal Mail", "DHL", "Evri", "Parcelforce", "Other"]]
    )
    ref_storage = ft.Dropdown(
        label="Storage Type",
        expand=True,
        border_radius=8,
        color=TEXT_DARK,
        options=[ft.dropdown.Option(x) for x in ["Standard", "Cold/Food", "Fragile/Large"]]
    )
    ref_note = ft.TextField(label="Note / Description", multiline=True, min_lines=2, border_radius=8, color=TEXT_DARK)
    
    back_btn = ft.Button(
        content=ft.Row([
            ft.Icon(ft.Icons.ARROW_BACK, color=NAVY_SECOND, size=18),
            ft.Text("Back to List", color=NAVY_SECOND, weight="bold"),
        ], tight=True),
        bgcolor="transparent",
        on_click=lambda _: show_parcel(dash)
    )
    
    def handle_save_parcel(e):
        if not ref_room.value or not ref_carrier.value:
            dash.show_message("Error: Unit and Carrier are required!")
            return
        
        parcels_data.insert(0, {
            "room": ref_room.value,
            "carrier": ref_carrier.value,
            "time": datetime.now().strftime("%I:%M %p"),
            "type": ref_storage.value,
            "status": "Pending",
            "days": 0
        })
        dash.show_message("Parcel logged!")
        show_parcel(dash)

    form_card = ft.Container(
        bgcolor=CARD_BG,
        padding=30,
        border_radius=12,
        content=ft.Column([
            ft.Text("Log New Incoming Parcel", size=20, weight="bold", color=TEXT_DARK),
            ft.Divider(),
            ft.Row([ref_room, ref_recipient], spacing=20),
            ft.Row([ref_carrier, ref_storage], spacing=20),
            ref_note,
            ft.Row([
                ft.Button(
                    content=ft.Text("Confirm", color="white", weight="bold"),
                    bgcolor=ACCENT_BLUE,
                    width=200,
                    on_click=handle_save_parcel
                )
            ], alignment="end")
        ], spacing=20)
    )

    dash.content_column.controls.extend([back_btn, form_card])
    dash.page.update()

def _create_parcel_item(dash, item):
    status = item["status"]
    room = item["room"]
    carrier = item["carrier"]
    
    action_area = None
    if status == "Delivered":
        action_area = ft.Container(
            content=ft.Text("Picked Up", size=11, color="white", weight="bold"),
            bgcolor=ft.Colors.RED_ACCENT_400,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=15
        )
    else:
        action_area = ft.Button(
            content=ft.Text("Mark Delivered", size=12, color="white", weight="bold"),
            bgcolor="#10B981",
            height=35,
            on_click=lambda _: handle_mark_delivered(dash, room, carrier)
        )
        
    return ft.Container(
        padding=15,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=10,
        content=ft.Row([
            ft.Icon(ft.Icons.INVENTORY_2_ROUNDED, color=ACCENT_BLUE),
            ft.Column([
                ft.Text(f"Unit {room}", weight="bold", size=15, color=TEXT_DARK),
                ft.Text(f"{carrier} • {item['type']}", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
            ], spacing=2, expand=True),
            ft.Text(item["time"], size=13, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
            action_area
        ])
    )
def handle_mark_delivered(dash, room, carrier):
    for parcel in parcels_data:
        if parcel["room"] == room and parcel["carrier"] == carrier:
            parcel["status"] = "Delivered"
            break
    
    dash.show_message(f"Unit {room} picked up.")
    apply_parcel_filters(dash)