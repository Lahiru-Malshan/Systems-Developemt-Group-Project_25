import sys
import os
from turtle import color
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Đoạn code trên đang thêm thư mục cha của file hiện tại vào sys.path để có thể import các module từ thư mục đó để chạy test. Điều này giúp tránh lỗi ImportError khi import các module khác trong dự án. Sau này sẽ sửa lại, dùng .. để import trực tiếp thay vì sửa sys.path như này.

import flet as ft
from base_dashboard import *
from logic.search import *

# Mock Database for Residents
test_residents_data = [
    {"room": "A-302", "name": "Nguyen Van A", "type": "Owner", "contact": "0901234567", "block": "A"},
    {"room": "B-105", "name": "Tran Thi B", "type": "Tenant", "contact": "0987654321", "block": "B"},
    {"room": "A-1204", "name": "Le Van C", "type": "Owner", "contact": "0912334455", "block": "A"},
]

def show_residents(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    if not hasattr(dash, "resident_table_area"):
        dash.resident_table_area = ft.Column(expand=True)
    
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
                    ft.Text("185", size=13, weight="bold", color=ACCENT_BLUE),
                    ft.VerticalDivider(width=10, color="transparent"),
                    ft.Text("Vacant:", size=13, weight="w500", color=TEXT_MUTED),
                    ft.Text("15", size=13, weight="bold", color=ft.Colors.ORANGE_700),
                ], spacing=5)
            ], spacing=15),
            ft.Button("Add Resident", icon=ft.Icons.ADD, bgcolor=ACCENT_BLUE, color="white",on_click=lambda _: draw_resident_registration(dash))
        ], alignment="spaceBetween")
    )

    # --- 2. SEARCH & FILTER SECTION ---
    dash.res_search_box = ft.TextField(
        label="Search by Name or Room...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True, border_radius=10, bgcolor="white", color=TEXT_DARK,
    )
    
    dash.res_block_filter = ft.Dropdown(
        width=150,
        label="Block",
        color=TEXT_DARK,
        options=[ft.dropdown.Option("All Blocks"), ft.dropdown.Option("A"), ft.dropdown.Option("B")],
        value="All Blocks"
    )
    apply_btn = ft.ElevatedButton(
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
                    subtitle=ft.Text(f"Room {r['room']}", size=11, color=TEXT_MUTED),
                    dense=True
                ) for r in test_residents_data[:3]
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
        data_list=test_residents_data,
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
                ft.DataColumn(ft.Text("Room", weight="bold", color=TEXT_DARK)),
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
    dash.content_column.controls.clear()

    ref_block = ft.TextField(label="Block", expand=True, border_radius=8, color=TEXT_DARK, hint_text="e.g. A")
    ref_room = ft.TextField(label="Room Number", expand=True, border_radius=8, color=TEXT_DARK)
    ref_name = ft.TextField(label="Full Name", expand=True, border_radius=8, color=TEXT_DARK)
    ref_email = ft.TextField(label="Email Address", expand=True, border_radius=8, color=TEXT_DARK)
    ref_phone = ft.TextField(label="Phone Number", expand=True, border_radius=8, color=TEXT_DARK)
    ref_dob = ft.TextField(label="Date of Birth", expand=True, border_radius=8, hint_text="DD/MM/YYYY", color=TEXT_DARK)
    ref_id = ft.TextField(label="ID / Passport Number", expand=True, border_radius=8, color=TEXT_DARK)
    ref_type = ft.Dropdown(
        label="Resident Type",
        expand=True,
        border_radius=8,
        color=TEXT_DARK,
        options=[
            ft.dropdown.Option("Owner"),
            ft.dropdown.Option("Tenant"),
            ft.dropdown.Option("Family Member"),
        ]
    )
    
    back_btn = ft.Button(
        content=ft.Row([
            ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, color=NAVY_SECOND, size=16),
            ft.Text("Back to Directory", color=NAVY_SECOND, weight="bold"),
        ], tight=True),
        bgcolor="transparent",
        on_click=lambda _: show_residents(dash)
    )

    registration_card = ft.Container(
        bgcolor=CARD_BG,
        padding=30,
        border_radius=12,
        content=ft.Column([
            ft.Text("Register New Resident", size=20, weight="bold", color=TEXT_DARK),
            ft.Divider(height=20),
            
            # Apartment Info
            ft.Row([ref_block, ref_room], spacing=20),

            # Personal Info
            ft.Row([ref_name, ref_email], spacing=20),
            ft.Row([ref_phone, ref_dob], spacing=20),
            ft.Row([ref_type, ref_id], spacing=20),
            ft.Divider(height=20),
            
            # Action Buttons
            ft.Row([
                ft.Button(
                    content=ft.Text("Confirm Registration", color="white", weight="bold"),
                    bgcolor=ACCENT_BLUE,
                    width=200,
                    on_click=lambda _: handle_save_resident(
                        dash,
                        ref_block.value,
                        ref_room.value,
                        ref_name.value,
                        ref_phone.value,
                        ref_type.value
                    )
                ),
            ], alignment="end")
        ], spacing=15)
    )

    dash.content_column.controls.extend([back_btn, registration_card])
    dash.page.update()

def handle_save_resident(dash, block, room, name, phone, res_type):
    if not room or not name or not phone:
        dash.show_message("Error: Room, Name and Phone are required!")
        return

    try:
        global test_residents_data
        full_room = f"{block}-{room}" if block else room

        test_residents_data.insert(0, {
            "room": full_room,
            "name": name,
            "type": res_type,
            "contact": phone,
            "block": block
        })

        dash.show_message(f"Resident {name} registered successfully!")
        show_residents(dash)
        
    except Exception as e:
        dash.show_message(f"Registration failed: {str(e)}")

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