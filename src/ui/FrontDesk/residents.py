# Elena Ho - 25044389

import sys
import os
from datetime import datetime, timedelta
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
    pending_accounts = backend.get_pending_account_requests()
    pending_rentals = backend.get_pending_rental_requests()
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
                    ft.VerticalDivider(width=10, color="transparent"),
                    ft.Text("Residents:", size=13, weight="w500", color=TEXT_MUTED),
                    ft.Text(str(resident_stats["resident_count"]), size=13, weight="bold", color=TEXT_DARK),
                    ft.VerticalDivider(width=10, color="transparent"),
                    ft.Text("Account Approvals:", size=13, weight="w500", color=TEXT_MUTED),
                    ft.Text(str(len(pending_accounts)), size=13, weight="bold", color=ft.Colors.GREEN_700),
                    ft.VerticalDivider(width=10, color="transparent"),
                    ft.Text("Rental Approvals:", size=13, weight="w500", color=TEXT_MUTED),
                    ft.Text(str(len(pending_rentals)), size=13, weight="bold", color=ft.Colors.BLUE_700),
                ], spacing=5)
            ], spacing=15),
            ft.Button("Refresh Directory", icon=ft.Icons.REFRESH, bgcolor=ACCENT_BLUE, color="white",on_click=lambda _: show_residents(dash))
        ], alignment="spaceBetween")
    )

    approval_row = ft.Row(
        spacing=20,
        vertical_alignment="start",
        controls=[
            _build_pending_accounts_card(dash, pending_accounts),
            _build_pending_rentals_card(dash, pending_rentals),
        ],
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

    dash.content_column.controls.extend([header, approval_row, filter_bar, main_layout])
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

def open_account_approval_modal(dash, request):
    backend = _get_frontdesk_backend(dash)
    ni_input = ft.TextField(
        label="NI Number",
        border_color=ACCENT_BLUE,
        value="",
    )
    occupation_input = ft.TextField(
        label="Occupation",
        border_color=ACCENT_BLUE,
        value="",
    )

    def handle_submit(e):
        success, message = backend.approve_tenant_account(
            request["user_id"],
            ni_input.value,
            occupation_input.value,
        )
        dash.show_message(message)
        if success:
            dash.close_dialog()
            show_residents(dash)

    content = ft.Column(
        [
            ft.Text(f"Approve account for {request['name']}.", color=TEXT_DARK),
            ft.Text(request.get("approval_stage", "Pending account approval"), size=12, color=TEXT_MUTED),
            ni_input,
            occupation_input,
        ],
        tight=True,
        spacing=15,
        width=420,
    )

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("APPROVE ACCOUNT", bgcolor=ft.Colors.GREEN_700, color="white", on_click=handle_submit),
    ]
    dash.show_custom_modal("Approve Tenant Account", content, actions)

def handle_account_reject(dash, user_id):
    backend = _get_frontdesk_backend(dash)
    success, message = backend.reject_tenant_account(user_id)
    dash.show_message(message)
    if success:
        show_residents(dash)

def open_rental_approval_modal(dash, request):
    backend = _get_frontdesk_backend(dash)
    apartments = backend.get_available_apartments_for_rental()
    if not apartments:
        dash.show_message("No available apartments found for this branch.")
        return

    apartment_lookup = {apartment["apartment_number"]: apartment for apartment in apartments}
    default_apartment = apartments[0]

    apartment_input = ft.Dropdown(
        label="Apartment",
        border_color=ACCENT_BLUE,
        options=[ft.dropdown.Option(apartment["apartment_number"]) for apartment in apartments],
        value=default_apartment["apartment_number"],
    )
    rent_input = ft.TextField(
        label="Monthly Rent",
        border_color=ACCENT_BLUE,
        keyboard_type=ft.KeyboardType.NUMBER,
        value=f"{float(default_apartment['rent']):.2f}",
    )
    start_input = ft.TextField(
        label="Start Date (YYYY-MM-DD)",
        border_color=ACCENT_BLUE,
        value=datetime.now().strftime("%Y-%m-%d"),
    )
    end_input = ft.TextField(
        label="End Date (YYYY-MM-DD)",
        border_color=ACCENT_BLUE,
        value=(datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
    )

    def sync_selected_apartment(e):
        selected = apartment_lookup.get(apartment_input.value)
        if not selected:
            return
        rent_input.value = f"{float(selected['rent']):.2f}"
        dash.page.update()

    apartment_input.on_change = sync_selected_apartment

    def handle_submit(e):
        selected = apartment_lookup.get(apartment_input.value)
        if not selected or not rent_input.value or not start_input.value or not end_input.value:
            dash.show_message("Apartment, lease dates, and rent are required.")
            return

        success, message = backend.approve_rental_request(
            request["tenant_id"],
            selected["apartment_id"],
            start_input.value,
            end_input.value,
            rent_input.value,
        )
        dash.show_message(message)
        if success:
            dash.close_dialog()
            show_residents(dash)

    content = ft.Column(
        [
            ft.Text(f"Approve apartment rental for {request['name']}.", color=TEXT_DARK),
            apartment_input,
            rent_input,
            start_input,
            end_input,
        ],
        tight=True,
        spacing=15,
        width=420,
    )

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.ElevatedButton("APPROVE RENTAL", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit),
    ]
    dash.show_custom_modal("Approve Rental", content, actions)

def _build_pending_accounts_card(dash, pending_accounts):
    body = [ft.Text("Pending tenant accounts", size=18, weight="bold", color=TEXT_DARK)]
    if pending_accounts:
        body.extend(_create_account_request_row(dash, item) for item in pending_accounts)
    else:
        body.append(ft.Text("No tenant account approvals are waiting.", color=TEXT_MUTED, italic=True))

    return ft.Container(
        expand=True,
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        content=ft.Column(body, spacing=12),
    )

def _build_pending_rentals_card(dash, pending_rentals):
    body = [ft.Text("Pending apartment rentals", size=18, weight="bold", color=TEXT_DARK)]
    if pending_rentals:
        body.extend(_create_rental_request_row(dash, item) for item in pending_rentals)
    else:
        body.append(ft.Text("No eligible tenants are waiting for apartment approval.", color=TEXT_MUTED, italic=True))

    return ft.Container(
        expand=True,
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        content=ft.Column(body, spacing=12),
    )

def _create_account_request_row(dash, item):
    return ft.Container(
        padding=15,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=10,
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(item["name"], size=14, weight="bold", color=TEXT_DARK),
                        ft.Text(item.get("email") or "No email provided", size=12, color=TEXT_MUTED),
                        ft.Text(item.get("approval_stage") or "Pending account approval", size=11, color=TEXT_MUTED),
                        ft.Text(f"Requested: {item['requested_label']}", size=11, color=TEXT_MUTED),
                    ],
                    expand=True,
                    spacing=4,
                ),
                ft.Row(
                    [
                        ft.Button(
                            "Approve",
                            icon=ft.Icons.CHECK,
                            bgcolor=ft.Colors.GREEN_700,
                            color="white",
                            on_click=lambda _, request=item: open_account_approval_modal(dash, request),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            icon_color=ft.Colors.RED_700,
                            tooltip="Reject",
                            on_click=lambda _, uid=item["user_id"]: handle_account_reject(dash, uid),
                        ),
                    ],
                    spacing=5,
                ),
            ],
            alignment="spaceBetween",
            vertical_alignment="center",
        ),
    )

def _create_rental_request_row(dash, item):
    note = item.get("additional_notes") or "No additional notes"
    return ft.Container(
        padding=15,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=10,
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(item["name"], size=14, weight="bold", color=TEXT_DARK),
                        ft.Text(item["requirements_label"], size=12, color=TEXT_MUTED),
                        ft.Text(f"Budget: {item['max_rent_label']}", size=12, color=TEXT_MUTED),
                        ft.Text(note, size=11, color=TEXT_MUTED, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    expand=True,
                    spacing=4,
                ),
                ft.Button(
                    "Approve Rental",
                    icon=ft.Icons.KEY,
                    bgcolor=ACCENT_BLUE,
                    color="white",
                    on_click=lambda _, request=item: open_rental_approval_modal(dash, request),
                ),
            ],
            alignment="spaceBetween",
            vertical_alignment="center",
        ),
    )

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