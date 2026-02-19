import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)
# Đoạn code trên đang thêm thư mục cha của file hiện tại vào sys.path để có thể import các module từ thư mục đó để chạy test. Điều này giúp tránh lỗi ImportError khi import các module khác trong dự án. Sau này sẽ sửa lại, dùng .. để import trực tiếp thay vì sửa sys.path như này.

import flet as ft
from logic.notifications import *
from base_dashboard import *

parcels_data = [
    ["302", "SPX Express", "10:30 AM", "Standard", "Delivered"],
    ["105", "UberEat", "11:45 AM", "Cold Storage", "Pending"],
    ["105", "Amazon", "11:45 AM", "Standard", "Pending"],
]
def show_parcel(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    
    parcels_data.sort(key=lambda x: x[4], reverse=True)
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
                ft.Text("Select a resident to log a delivery", color=TEXT_MUTED, size=12, italic=True),
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
    parcel_items = []
    for room, carrier, time, p_type, status in parcels_data:
        parcel_items.append(_create_parcel_item(dash, room, carrier, time, p_type, status))
        
    parcel_table = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.TextField(
                label="Search by Room or Carrier",
                prefix_icon=ft.Icons.SEARCH,
                border_radius=10,
                bgcolor="white",
                color=TEXT_DARK,
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Text("Recent Parcels List", weight="bold", color=TEXT_DARK),
            ft.ListView(
                expand=True,
                spacing=10,
                controls=parcel_items
            )
        ])
    )

    dash.content_column.controls.extend([header, parcel_stats, parcel_table])
    dash.page.update()

def draw_add_parcel_form(dash, *args):
    dash.content_column.controls.clear()
    
    ref_room = ft.TextField(label="Room Number", expand=True, hint_text="e.g. 302", border_radius=8, color=TEXT_DARK)
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
            dash.show_message("Error: Room and Carrier are required!")
            return
        
        global parcels_data
        current_time = datetime.now().strftime("%I:%M %p")
        
        parcels_data.insert(0, [
            ref_room.value,
            ref_carrier.value,
            current_time,
            ref_storage.value if ref_storage.value else "Standard",
            "Pending"
        ])

        dash.show_message(f"Parcel for Room {ref_room.value} logged successfully!")
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
                    content=ft.Text("Confirm Receipt", color="white", weight="bold"),
                    bgcolor=ACCENT_BLUE,
                    width=200,
                    on_click=handle_save_parcel
                )
            ], alignment="end")
        ], spacing=20)
    )

    dash.content_column.controls.extend([back_btn, form_card])
    dash.page.update()

def _create_parcel_item(dash, room, carrier, time, p_type, status="Pending"):
    action_area = None
    if status == "Delivered":
        action_area = ft.Container(
            content=ft.Text("Delivered", size=11, color="white", weight="bold"),
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
                ft.Text(f"Room {room}", weight="bold", size=15, color=TEXT_DARK),
                ft.Text(f"{carrier} • {p_type}", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
            ], spacing=2, expand=True),
            ft.Text(time, size=13, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
            action_area
        ])
    )
def handle_mark_delivered(dash, room, carrier):
    global parcels_data
    for p in parcels_data:
        if p[0] == room and p[1] == carrier and p[4] == "Pending":
            p[4] = "Delivered"
            break
            
        # 1. LOGIC DATABASE:
        # db.update_parcel_status(room=room, carrier=carrier, status="Delivered")
        print(f"Updating Database: Parcel for {room} delivered.")

        send_notification(
            dash,
            user_id=room,
            title="Parcel Picked Up",
            message=f"The package from {carrier} has been marked as picked up at the Front Desk."
        )
    dash.show_message(f"Room {room} picked up their parcel.")
    show_parcel(dash)