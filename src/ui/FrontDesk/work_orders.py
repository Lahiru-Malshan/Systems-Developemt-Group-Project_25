# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from base_dashboard import *
from logic.search import *
from backend.FrontDesk.frontdesk import FrontDeskBackend



def _get_frontdesk_backend(dash):
    return FrontDeskBackend(user_id=getattr(dash, "user_id", None), username=getattr(dash, "username", None))

def show_work_orders(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    if not hasattr(dash, "order_list_column"):
        dash.order_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)

    backend = _get_frontdesk_backend(dash)
    dash.work_order_data = backend.get_maintenance_requests()
    
    # --- 1. HEADER ---
    header = ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        content=ft.Row([
            ft.Text("Maintenance Work Orders", size=20, weight="bold", color=TEXT_DARK),
            ft.Button(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD_TASK_ROUNDED, color="white", size=20),
                    ft.Text("Create Order", weight="bold", color="white"),
                ], tight=True),
                bgcolor=ACCENT_BLUE,
                on_click=lambda _: open_create_order_modal(dash)
            )
        ], alignment="spaceBetween")
    )

    # --- 2. STATS ---
    pending_cnt = len([o for o in dash.work_order_data if o["status"] == "Pending"])
    progress_cnt = len([o for o in dash.work_order_data if o["status"] == "In Progress"])
    completed_cnt = len([o for o in dash.work_order_data if o["status"] == "Resolved"])
    
    order_stats = ft.Row([
        dash.create_stat_card("Pending", str(pending_cnt), ft.Icons.PENDING_ACTIONS_ROUNDED),
        dash.create_stat_card("In Progress", str(progress_cnt), ft.Icons.HANDYMAN_ROUNDED),
        dash.create_stat_card("Completed", str(completed_cnt), ft.Icons.TASK_ALT_ROUNDED),
    ], spacing=20)
    
    # --- 3. FILTER BAR ---
    dash.wo_search = ft.TextField(
        label="Search by Unit or Category",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        color=TEXT_DARK,
        expand=True
    )
    apply_btn = ft.Button(
        "Apply",
        icon=ft.Icons.SEARCH_ROUNDED,
        bgcolor=ACCENT_BLUE,
        color="white",
        height=40,
        on_click=lambda _: apply_work_order_filters(dash)
    )

    # --- 4. LIST VIEW ---
    orders_list_container = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.Row([dash.wo_search, apply_btn], spacing=10),
            ft.Divider(height=10, color="transparent"),
            ft.Container(content=dash.order_list_column, expand=True)
        ])
    )

    dash.content_column.controls.extend([header, order_stats, orders_list_container])
    apply_work_order_filters(dash)
    dash.page.update()

def apply_work_order_filters(dash):
    if not hasattr(dash, "order_list_column"): return

    filtered = SearchEngine.apply_logic(
        data_list=getattr(dash, "work_order_data", []),
        search_term=dash.wo_search.value
    )

    status_order = {"Pending": 0, "In Progress": 1, "Resolved": 2}
    
    final_list = sorted(
        filtered,
        key=lambda x: (
            status_order.get(x["status"], 99),
            x["date"]
        )
    )

    dash.order_list_column.controls.clear()
    for order in final_list:
        dash.order_list_column.controls.append(
            _create_work_order_item(dash, order)
        )
    dash.page.update()
    
def open_create_order_modal(dash):
    backend = _get_frontdesk_backend(dash)
    apartment_options = backend.get_apartment_options()

    # --- 1. REFS TO COLLECT DATA ---
    ref_room = ft.Dropdown(
        label="Apartment Number",
        options=[ft.dropdown.Option(x) for x in apartment_options],
        border_color=ACCENT_BLUE,
    )
    ref_resident = ft.Dropdown(label="Requested By", border_color=ACCENT_BLUE, disabled=True, options=[])
    resident_lookup = {}
    ref_desc = ft.TextField(label="Issue Description", multiline=True, min_lines=3, border_color=ACCENT_BLUE)

    def load_residents(e):
        nonlocal resident_lookup
        residents = backend.get_apartment_residents(ref_room.value) if ref_room.value else []
        resident_lookup = {resident["name"]: resident["tenant_id"] for resident in residents}
        ref_resident.options = [ft.dropdown.Option(resident["name"]) for resident in residents]
        ref_resident.value = residents[0]["name"] if len(residents) == 1 else None
        ref_resident.disabled = len(residents) == 0
        dash.page.update()

    ref_room.on_change = load_residents

    # --- 2. SUBMIT LOGIC ---
    def handle_submit_order(e):
        if not ref_room.value or not ref_resident.value or not ref_desc.value:
            dash.show_message("Please fill in all required fields!")
            return

        success, message = backend.create_maintenance_request(
            apartment_number=ref_room.value,
            tenant_id=resident_lookup.get(ref_resident.value),
            description=ref_desc.value,
        )
        if not success:
            dash.show_message(f"Error: {message}")
            return

        dash.close_dialog()
        show_work_orders(dash)
        dash.show_message(message)

    # --- 3. MODAL UI ---
    dash.show_custom_modal(
        "Create New Work Order",
        ft.Column([ref_room, ref_resident, ref_desc], spacing=15, tight=True, width=400),
        [
            ft.Button("Cancel", on_click=dash.close_dialog),
            ft.Button("CREATE", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit_order)
        ]
    )
    
def _create_work_order_item(dash, order):
    wo_id = order["id"]
    room = order["room"]
    resident_name = order["resident_name"]
    desc = order["description"]
    status = order["status"]
    date = order["date"]
    assigned_name = order.get("assigned_name", "Unassigned")
    
    status_colors = {
        "Pending": ft.Colors.ORANGE_700,
        "In Progress": ft.Colors.BLUE_700,
        "Resolved": ft.Colors.GREEN_700
    }
    s_color = status_colors.get(status, ft.Colors.GREY_400)

    if status == "Pending":
        action_button = ft.Row([
            ft.Button(
                content=ft.Text("Assign Tech", size=11, color="white", weight="bold"),
                bgcolor=ACCENT_BLUE,
                height=30,
                on_click=lambda _: handle_assign_order(dash, order)
            )
        ])
    elif status == "In Progress":
        action_button = ft.Row([
            ft.Button(
                content=ft.Text("Resolve", size=11, color="white", weight="bold"),
                bgcolor=ft.Colors.GREEN_700,
                height=30,
                on_click=lambda _: handle_resolve_order(dash, order["request_id"])
            )
        ])
    else:
        action_button = ft.Container(
            content=ft.Text(status, size=11, color="white", weight="bold"),
            bgcolor=s_color,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=15
        )

    return ft.Container(
        padding=15,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=10,
        content=ft.Row([
            ft.Column([
                ft.Row([
                    ft.Text(f"• {wo_id}", size=11, color=TEXT_MUTED),
                    ft.Container(
                        content=ft.Text(status, size=10, color="white", weight="bold"),
                        bgcolor=s_color,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        border_radius=5
                    ),
                ], spacing=10),
                ft.Text(f"Unit: {room} • Requested by: {resident_name}", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
                ft.Text(desc, size=13, color=TEXT_MUTED, max_lines=1, overflow="ellipsis"),
                ft.Text(f"Assigned to: {assigned_name}", size=12, color=TEXT_MUTED),
            ], expand=True),
            ft.Column([
                ft.Text(date, size=11, color=TEXT_MUTED),
                action_button
            ], horizontal_alignment="end")
        ])
    )
    
def handle_assign_order(dash, order):
    backend = _get_frontdesk_backend(dash)
    staff_options = backend.get_maintenance_staff_options()
    if not staff_options:
        dash.show_message("No active maintenance staff found for this location.")
        return

    staff_dropdown = ft.Dropdown(
        label="Assign To",
        border_color=ACCENT_BLUE,
        options=[ft.dropdown.Option(staff["name"]) for staff in staff_options],
        value=staff_options[0]["name"],
    )
    staff_lookup = {staff["name"]: staff["maintenance_staff_id"] for staff in staff_options}

    def save_assignment(e):
        success, message = backend.assign_maintenance_request(
            order["request_id"],
            staff_lookup.get(staff_dropdown.value),
        )
        dash.close_dialog()
        dash.show_message(message)
        if success:
            show_work_orders(dash)

    dash.show_custom_modal(
        f"Assign {order['id']}",
        ft.Column([staff_dropdown], spacing=15, tight=True, width=400),
        [
            ft.Button("Cancel", on_click=dash.close_dialog),
            ft.Button("ASSIGN", bgcolor=ACCENT_BLUE, color="white", on_click=save_assignment),
        ],
    )


def handle_resolve_order(dash, request_id):
    backend = _get_frontdesk_backend(dash)
    success, message = backend.update_maintenance_request_status(request_id, "Resolved")
    dash.show_message(message)
    if success:
        show_work_orders(dash)