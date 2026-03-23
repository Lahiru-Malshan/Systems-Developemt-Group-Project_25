# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from logic.notifications import *
from base_dashboard import *
from logic.search import *

# Mock data
# Structure: [ID, Unit, Category, Description, Priority, Status, Date]
test_work_orders = [
    {"id": "WO-001", "room": "302", "category": "Plumbing", "desc": "Kitchen sink leaking", "priority": "High", "status": "In Progress", "date": "2026-02-15", "days": 5},
    {"id": "WO-002", "room": "105", "category": "Electrical", "desc": "AC not cooling", "priority": "Medium", "status": "Pending", "date": "2026-02-16", "days": 4},
    {"id": "WO-003", "room": "B-704", "category": "Carpentry", "desc": "Broken wardrobe door", "priority": "Low", "status": "Completed", "date": "2026-02-14", "days": 6},
]

def show_work_orders(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    if not hasattr(dash, "order_list_column"):
        dash.order_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)
    
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
    pending_cnt = len([o for o in test_work_orders if o["status"] == "Pending"])
    progress_cnt = len([o for o in test_work_orders if o["status"] in ["In Progress", "Assigned"]])
    completed_cnt = len([o for o in test_work_orders if o["status"] == "Completed"])
    
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
        data_list=test_work_orders,
        search_term=dash.wo_search.value
    )

    status_order = {"Pending": 0, "In Progress": 1, "Assigned": 2, "Completed": 3}
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    
    final_list = sorted(
        filtered,
        key=lambda x: (
            status_order.get(x["status"], 99),
            priority_order.get(x["priority"], 99),
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
    # --- 1. REFS TO COLLECT DATA ---
    ref_room = ft.TextField(label="Unit Number", hint_text="e.g. 302 or Common Area", border_color=ACCENT_BLUE)
    ref_category = ft.Dropdown(
        label="Category",
        options=[ft.dropdown.Option(x) for x in ["Plumbing", "Electrical", "General", "Elevator"]],
        border_color=ACCENT_BLUE
    )
    ref_priority = ft.Dropdown(
        label="Priority Level",
        options=[ft.dropdown.Option(x) for x in ["High", "Medium", "Low"]],
        value="Medium",
        border_color=ACCENT_BLUE,
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
        new_id = f"WO-{len(test_work_orders) + 1}"
        
        test_work_orders.insert(0, {
            "id": new_id,
            "room": ref_room.value,
            "category": ref_category.value if ref_category.value else "General",
            "desc": ref_desc.value,
            "priority": ref_priority.value,
            "status": "Pending",
            "date": current_date,
            "days": 0
        })

        dash.close_dialog()
        show_work_orders(dash)
        dash.show_message(f"Work Order {new_id} created successfully!")

    # --- 3. MODAL UI ---
    dash.show_custom_modal(
        "Create New Work Order",
        ft.Column([ref_room, ref_category, ref_priority, ref_desc], spacing=15, tight=True, width=400),
        [
            ft.Button("Cancel", on_click=dash.close_dialog),
            ft.Button("CREATE", bgcolor=ACCENT_BLUE, color="white", on_click=handle_submit_order)
        ]
    )
    
def _create_work_order_item(dash, order):
    wo_id = order["id"]
    room = order["room"]
    cat = order["category"]
    desc = order["desc"]
    priority = order["priority"]
    status = order["status"]
    date = order["date"]
    
    status_colors = {
        "Pending": ft.Colors.ORANGE_700,
        "Assigned": ft.Colors.BLUE_700,
        "Completed": ft.Colors.GREEN_700
    }
    s_color = status_colors.get(status, ft.Colors.GREY_400)
    
    priority = order.get("priority", "Low")
    priority_colors = {
        "High": ft.Colors.RED_700,
        "Medium": ft.Colors.ORANGE_700,
        "Low": ft.Colors.BLUE_GREY_400
    }
    p_color = priority_colors.get(priority, ft.Colors.GREY_400)

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
                    ft.Container(
                        content=ft.Text(priority, size=10, color="white", weight="bold"),
                        bgcolor=p_color,
                        padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        border_radius=5
                    ),
                    ft.Text(f"• {wo_id}", size=11, color=TEXT_MUTED),
                ], spacing=10),
                ft.Text(f"Unit: {room}", size=12, color=TEXT_MUTED, weight=ft.FontWeight.W_500),
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
            if order["id"] == wo_id:
                order["status"] = "Assigned"
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