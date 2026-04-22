
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from datetime import datetime
import flet as ft
from logic.notifications import *
from logic.search import *
from base_dashboard import *
from backend.FrontDesk.frontdesk import FrontDeskBackend


def _get_frontdesk_backend(dash):
    return FrontDeskBackend(user_id=getattr(dash, "user_id", None), username=getattr(dash, "username", None))

def show_parcel(dash, *args):
    if not dash: return
    if not hasattr(dash, "parcel_list_column"):
        dash.parcel_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)
    dash.content_column.controls.clear()

    backend = _get_frontdesk_backend(dash)
    dash.parcel_data = backend.get_parcels()
    parcel_stats_data = backend.get_parcel_stats()
    
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
        dash.create_stat_card("Waiting Pickup", str(parcel_stats_data["pending_count"]), ft.Icons.HOURGLASS_EMPTY_ROUNDED),
        dash.create_stat_card("Today Received", str(parcel_stats_data["received_today"]), ft.Icons.MOVE_TO_INBOX_ROUNDED),
        dash.create_stat_card("Overdue (3+ days)", str(parcel_stats_data["overdue_count"]), ft.Icons.WARNING_AMBER_ROUNDED, highlight=True),
    ], spacing=20)
    
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

    filtered = SearchEngine.apply_logic(
        data_list=getattr(dash, "parcel_data", []),
        search_term=dash.parcel_search.value
    )

    final_list = sorted(filtered, key=lambda x: (x["status"] == "Picked Up", x["days"], x["room"]), reverse=False)

    dash.parcel_list_column.controls.clear()
    for p in final_list:
        dash.parcel_list_column.controls.append(
            _create_parcel_item(dash, p)
        )
    
    dash.page.update()

def draw_add_parcel_form(dash, *args):
    dash.content_column.controls.clear()
    backend = _get_frontdesk_backend(dash)
    apartment_options = backend.get_apartment_options()
    resident_lookup = {}
    
    ref_room = ft.Dropdown(
        label="Apartment Number",
        expand=True,
        border_radius=8,
        color=TEXT_DARK,
        options=[ft.dropdown.Option(number) for number in apartment_options],
    )
    ref_recipient = ft.Dropdown(
        label="Recipient",
        expand=True,
        border_radius=8,
        color=TEXT_DARK,
        disabled=True,
        options=[],
    )
    recipient_hint = ft.Text("Select an apartment to load active tenants.", size=11, color=TEXT_MUTED)
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

    def handle_apartment_change(e):
        nonlocal resident_lookup
        residents = backend.get_apartment_residents(ref_room.value) if ref_room.value else []
        resident_lookup = {resident["name"]: resident["tenant_id"] for resident in residents}
        ref_recipient.options = [ft.dropdown.Option(resident["name"]) for resident in residents]
        ref_recipient.value = residents[0]["name"] if len(residents) == 1 else None
        ref_recipient.disabled = len(residents) == 0
        if len(residents) > 1:
            recipient_hint.value = "This apartment has multiple active tenants. Select the parcel recipient."
        elif len(residents) == 1:
            recipient_hint.value = f"Recipient auto-selected: {residents[0]['name']}"
        else:
            recipient_hint.value = "No active tenants found for this apartment."
        dash.page.update()

    ref_room.on_change = handle_apartment_change
    
    def handle_save_parcel(e):
        if not ref_room.value or not ref_carrier.value:
            dash.show_message("Error: Unit and Carrier are required!")
            return
        success, message = backend.create_parcel(
            apartment_number=ref_room.value,
            carrier=ref_carrier.value,
            storage_type=ref_storage.value or "Standard",
            note=ref_note.value,
            tenant_id=resident_lookup.get(ref_recipient.value),
            recipient_name=ref_recipient.value,
        )
        if not success:
            dash.show_message(f"Error: {message}")
            return

        dash.show_message(message)
        show_parcel(dash)

    form_card = ft.Container(
        bgcolor=CARD_BG,
        padding=30,
        border_radius=12,
        content=ft.Column([
            ft.Text("Log New Incoming Parcel", size=20, weight="bold", color=TEXT_DARK),
            ft.Divider(),
            ft.Row([ref_room, ref_recipient], spacing=20),
            recipient_hint,
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
    if status == "Picked Up":
        action_area = ft.Container(
            content=ft.Text("Picked Up", size=11, color="white", weight="bold"),
            bgcolor=ft.Colors.RED_ACCENT_400,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=15
        )
    else:
        action_area = ft.Button(
            content=ft.Text("Mark Picked Up", size=12, color="white", weight="bold"),
            bgcolor="#10B981",
            height=35,
            on_click=lambda _: handle_mark_delivered(dash, item["parcel_id"])
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
                ft.Text(f"Recipient: {item['display_recipient']}", size=11, color=TEXT_MUTED),
            ], spacing=2, expand=True),
            ft.Text(item["time"], size=13, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
            action_area
        ])
    )
def handle_mark_delivered(dash, parcel_id):
    backend = _get_frontdesk_backend(dash)
    success, message = backend.mark_parcel_picked_up(parcel_id)
    dash.show_message(message)
    if success:
        show_parcel(dash)