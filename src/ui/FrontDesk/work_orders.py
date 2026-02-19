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
from logic.notifications import *

# Mock data để test (Sau này sẽ thay bằng SQL SELECT)
# Cấu trúc: [ID, Room, Category, Description, Priority, Status, Date]
test_work_orders = [
    ["WO-001", "302", "Plumbing", "Kitchen sink leaking", "High", "In Progress", "2026-02-15"],
    ["WO-002", "105", "Electrical", "AC not cooling", "Medium", "Pending", "2026-02-16"],
    ["WO-003", "B-704", "Carpentry", "Broken wardrobe door", "Low", "Completed", "2026-02-14"],
]

def show_work_orders(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    
    status_order = {"Pending": 0, "In Progress": 1, "Assigned": 2, "Completed": 3}
    test_work_orders.sort(key=lambda x: (status_order.get(x[5], 99), x[6]), reverse=False)

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
    pending_cnt = len([o for o in test_work_orders if o[5] == "Pending"])
    progress_cnt = len([o for o in test_work_orders if o[5] in ["In Progress", "Assigned"]])
    completed_cnt = len([o for o in test_work_orders if o[5] == "Completed"])
    
    order_stats = ft.Row([
        dash.create_stat_card("Pending", str(pending_cnt), ft.Icons.PENDING_ACTIONS_ROUNDED),
        dash.create_stat_card("In Progress", str(progress_cnt), ft.Icons.HANDYMAN_ROUNDED),
        dash.create_stat_card("Completed", str(completed_cnt), ft.Icons.TASK_ALT_ROUNDED),
    ], spacing=20)

    # --- 3. LIST VIEW ---
    order_items = []
    for order in test_work_orders:
        order_items.append(_create_work_order_item(dash, *order))

    orders_list = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.TextField(label="Search by Room or Category", prefix_icon=ft.Icons.SEARCH, border_radius=10, color=TEXT_DARK, on_change=lambda e: print("Searching...")),
            ft.Divider(height=10, color="transparent"),
            ft.ListView(controls=order_items, expand=True, spacing=10)
        ])
    )

    dash.content_column.controls.extend([header, order_stats, orders_list])
    dash.page.update()

def open_create_order_modal(dash):
    # --- 1. REFS TO COLLECT DATA ---
    ref_room = ft.TextField(label="Room Number", hint_text="e.g. 302 or Common Area", border_color=ACCENT_BLUE)
    ref_category = ft.Dropdown(
        label="Category",
        options=[ft.dropdown.Option(x) for x in ["Plumbing", "Electrical", "General", "Elevator"]],
        border_color=ACCENT_BLUE
    )
    ref_desc = ft.TextField(label="Issue Description", multiline=True, min_lines=3, border_color=ACCENT_BLUE)

    # --- 2. SUBMIT LOGIC ---
    def handle_submit_order(e):
        if not ref_room.value or not ref_desc.value:
            dash.show_message("Please fill in all required fields!")
            return
        
        # Add to our global test list (Mock DB)
        global test_work_orders
        current_date = datetime.now().strftime("%Y-%m-%d")

        try:
            ids = [int(o[0].split('-')[1]) for o in test_work_orders if '-' in o[0]]
            next_id = max(ids) + 1 if ids else 1
        except:
            next_id = len(test_work_orders) + 1

        new_id = f"WO-{next_id:03d}"
        
        test_work_orders.insert(0, [
            new_id, ref_room.value, ref_category.value if ref_category.value else "General", ref_desc.value, "Medium", "Pending", current_date
        ])

        dash.close_dialog()
        show_work_orders(dash)
        dash.show_message(f"Work Order {new_id} created successfully!")

    # --- 3. MODAL UI ---
    content = ft.Column([
        ref_room,
        ref_category,
        ref_desc,
    ], spacing=15, tight=True, width=400)

    actions = [
        ft.Button("Cancel", on_click=dash.close_dialog),
        ft.Button(
            content=ft.Text("CREATE ORDER", color="white", weight="bold"),
            bgcolor=ACCENT_BLUE,
            on_click=handle_submit_order
        ),
    ]

    dash.show_custom_modal("Create New Work Order", content, actions)
    
def _create_work_order_item(dash, wo_id, room, cat, desc, priority, status, date):
    status_colors = {
        "Pending": ft.Colors.ORANGE_700,
        "Assigned": ft.Colors.BLUE_700,
        "Completed": ft.Colors.GREEN_700
    }
    s_color = status_colors.get(status, ft.Colors.GREY_400)

    # FD just "Assign" not "Complete"
    if status == "Pending":
        action_button = ft.Button(
            content=ft.Text("Assign Tech", size=11, color="white", weight="bold"),
            bgcolor=ACCENT_BLUE,
            height=30,
            on_click=lambda _: handle_assign_order(dash, wo_id, room)
        )
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
                    ft.Text(cat, weight="bold", size=14, color=TEXT_DARK),
                    ft.Text(f"• {wo_id}", size=11, color=TEXT_MUTED),
                ], spacing=10),
                ft.Text(desc, size=13, color=TEXT_MUTED, max_lines=1, overflow="ellipsis"),
            ], expand=True),
            ft.Column([
                ft.Text(date, size=11, color=TEXT_MUTED),
                action_button
            ], horizontal_alignment="end")
        ])
    )
    
def handle_assign_order(dash, wo_id, room):
    global test_work_orders
    
    try:
        for order in test_work_orders:
            if order[0] == wo_id:
                order[5] = "Assigned"
                break

        send_notification(
            dash,
            user_id=room,
            title="Maintenance Update",
            message=f"Your request {wo_id} has been assigned to a technician."
        )
        
        dash.show_message(f"Work order {wo_id} assigned.")
        show_work_orders(dash)
        
    except Exception as e:
        dash.show_message(f"Error: {str(e)}")