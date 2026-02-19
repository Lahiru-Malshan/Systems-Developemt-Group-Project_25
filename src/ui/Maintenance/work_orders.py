from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)
# Đoạn code trên đang thêm thư mục cha của file hiện tại vào sys.path để có thể import các module từ thư mục đó để chạy test. Điều này giúp tránh lỗi ImportError khi import các module khác trong dự án. Sau này sẽ sửa lại, dùng .. để import trực tiếp thay vì sửa sys.path như này.

import flet as ft
from base_dashboard import *

# Mock data để test (Sau này sẽ thay bằng SQL SELECT)
test_work_orders = [
    {"id": "WO-101", "room": "A-1204", "issue": "Water Pipe Burst", "category": "Plumbing", "priority": "Emergency", "status": "Pending", "reportedDate": "2026-02-18", "scheduledDate": "2026-02-19", "completionDate": "-"},
    {"id": "WO-102", "room": "B-302", "issue": "Power Outage", "category": "Electrical", "priority": "High", "status": "Pending", "reportedDate": "2026-02-19", "scheduledDate": "2026-02-19", "completionDate": "-"},
    {"id": "WO-103", "room": "C-501", "issue": "AC not cooling", "category": "HVAC", "priority": "Medium", "status": "In Progress", "reportedDate": "2026-02-17", "scheduledDate": "2026-02-18", "completionDate": "-"},
    {"id": "WO-002", "room": "Lobby", "issue": "Main door glass cracked", "category": "Security", "priority": "Medium", "status": "Pending", "reportedDate": "2026-02-19", "scheduledDate": "TBD", "completionDate": "-"},
]

def get_all_work_orders():
    """Bây giờ hàm này chỉ trả về biến Global đã khai báo ở trên"""
    global test_work_orders
    return test_work_orders

def update_work_order_status(wo_id, new_status):
    """Hàm cập nhật - Sau này gửi lệnh UPDATE vào Database ở đây"""
    print(f"Executing: UPDATE work_orders SET status='{new_status}' WHERE id='{wo_id}'")
    return True

def show_work_orders(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    work_orders = sorted(get_all_work_orders(), key=lambda x: x['reportedDate'], reverse=True)
    
    # --- 1. HEADER ---
    header = ft.Row([
        ft.Text("Work Order Directory", size=24, weight="bold", color=TEXT_DARK),
        ft.Container(expand=True),
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, color="white", size=20),
                ft.Text("NEW REQUEST", weight="bold", color="white"),
            ], tight=True),
            bgcolor=ACCENT_BLUE,
            on_click=lambda _: open_new_request_form(dash)
        ),
        ft.VerticalDivider(width=10),
        ft.SegmentedButton(
            selected=["all"],
            segments=[
                ft.Segment(value="all", label=ft.Text("All Tasks")),
                ft.Segment(value="pending", label=ft.Text("Pending")),
            ],
        )
    ], alignment="spaceBetween")

    # --- 2. TABLE DATA ---
    rows = []
    for wo in work_orders:
        p_color = ft.Colors.RED_700 if wo["priority"] in ["Emergency", "High"] else TEXT_DARK

        if wo["status"] == "Pending":
            action_btn = ft.Button("Start Work", bgcolor=ACCENT_BLUE, color="white",on_click=lambda e, w_id=wo["id"]: handle_status_change(dash, w_id))
        elif wo["status"] == "In Progress":
            action_btn = ft.Row([
                ft.IconButton(icon=ft.Icons.REPLAY_CIRCLE_FILLED_ROUNDED, icon_color=ft.Colors.ORANGE_700,on_click=lambda e, w_id=wo["id"]: handle_status_change(dash, w_id)),
                ft.Button("Finish", bgcolor=ft.Colors.GREEN_700, color="white",on_click=lambda e, w_id=wo["id"]: open_completion_report(dash, w_id))
            ], spacing=5, tight=True)
        else:
            action_btn = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400)

        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(wo["id"], weight="bold", color=TEXT_DARK)),
                ft.DataCell(ft.Text(wo["room"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(wo["issue"], color=TEXT_DARK)),
                ft.DataCell(_create_priority_tag(wo["priority"], p_color)),
                ft.DataCell(_create_status_badge(wo["status"])),
                ft.DataCell(ft.Text(wo.get("completionDate", "-"), color=TEXT_DARK)),
                ft.DataCell(action_btn),
            ])
        )

    table_container = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.DataTable(
                expand=True,
                column_spacing=45,
                heading_row_color=ft.Colors.BLUE_GREY_50,
                heading_row_height=50,
                columns=[
                    ft.DataColumn(ft.Text("ID",weight="bold", color=ACCENT_BLUE)),
                    ft.DataColumn(ft.Text("Room", weight="bold", color=ACCENT_BLUE)),
                    ft.DataColumn(ft.Text("Issue", weight="bold", color=ACCENT_BLUE)),
                    ft.DataColumn(ft.Text("Priority", weight="bold", color=ACCENT_BLUE)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=ACCENT_BLUE)),
                    ft.DataColumn(ft.Text("Completed", weight="bold", color=ACCENT_BLUE)),
                    ft.DataColumn(ft.Text("Action", weight="bold", color=ACCENT_BLUE)),
                ],
                rows=rows,
            )
        ], scroll=ft.ScrollMode.AUTO)
    )

    dash.content_column.controls.extend([header, ft.Divider(height=10, color="transparent"), table_container])
    dash.page.update()

def handle_status_change(dash, wo_id):
    global test_work_orders
    for wo in test_work_orders:
        if wo["id"] == wo_id:
            new_status = "In Progress" if wo["status"] == "Pending" else "Pending"
            wo["status"] = new_status
            
            update_work_order_status(wo_id, new_status)
            dash.show_message(f"Task {wo_id} is now {new_status}")
            break
    show_work_orders(dash)

def open_new_request_form(dash):
    """Form để Tenant hoặc Staff báo cáo lỗi mới"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    room_input = ft.TextField(label="Room / Common Area", hint_text="e.g. A-1204 or Lobby", border_color=ACCENT_BLUE)
    category_input = ft.Dropdown(
        label="Category", value="General", border_color=ACCENT_BLUE,
        options=[ft.dropdown.Option(x) for x in ["Plumbing", "Electrical", "HVAC", "Security", "General"]]
    )
    priority_input = ft.Dropdown(
        label="Priority", value="Medium", border_color=ACCENT_BLUE,
        options=[ft.dropdown.Option(x) for x in ["Low", "Medium", "High", "Emergency"]]
    )
    issue_input = ft.TextField(label="Description", multiline=True, min_lines=3, border_color=ACCENT_BLUE)

    def submit_new_request(e):
        if not room_input.value or not issue_input.value:
            dash.show_message("Please fill in Room and Description!")
            return
        
        global test_work_orders
        existing_ids = [int(wo['id'].split('-')[1]) for wo in test_work_orders if '-' in wo['id']]
        next_id_num = max(existing_ids) + 1 if existing_ids else 101
        new_id = f"WO-{next_id_num}"
        
        test_work_orders.insert(0, {
            "id": new_id,
            "room": room_input.value,
            "issue": issue_input.value,
            "category": category_input.value,
            "priority": priority_input.value,
            "status": "Pending",
            "reportedDate": current_date,
            "scheduledDate": "TBD",
            "completionDate": "-"
        })
        
        dash.close_dialog()
        dash.show_message(f"Request {new_id} submitted successfully!")
        show_work_orders(dash)

    dash.show_custom_modal(
        title="Submit New Maintenance Request",
        content=ft.Column([
            ft.Text("Provide details for the maintenance issue below:", color=TEXT_MUTED),
            room_input, ft.Row([category_input, priority_input]), issue_input,
            ft.Text(f"Date: {current_date}", size=12, color=TEXT_MUTED, weight="bold")
        ], tight=True, spacing=15),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
            ft.ElevatedButton("Submit Request", bgcolor=ACCENT_BLUE, color="white", on_click=submit_new_request)
        ]
    )

def open_completion_report(dash, wo_id):
    date_input = ft.TextField(
        label="Completion Date",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=250,
        prefix_icon=ft.Icons.CALENDAR_TODAY
    )
    report_input = ft.TextField(label="Maintenance Report",multiline=True,min_lines=3,hint_text="Describe the fix or parts replaced...",border_radius=10,autofocus=True
    )
    def submit_resolve(e):
        if not report_input.value.strip():
            dash.show_message("Please provide a resolution report!")
            return
        global test_work_orders
        for wo in test_work_orders:
            if wo["id"] == wo_id:
                wo["status"] = "Resolved"
                wo["completionDate"] = date_input.value
                wo["description"] = report_input.value
                break
        
        dash.close_dialog()
        dash.show_message(f"Task {wo_id} has been resolved.")
        show_work_orders(dash)
        
    dash.show_custom_modal(
        title=f"Complete Task: {wo_id}",
        content=ft.Column([
            ft.Text("Enter the work details and verify completion date:", color=TEXT_MUTED),
            date_input, report_input,
        ], tight=True, spacing=15),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
            ft.Button("Submit & Resolve", bgcolor=ft.Colors.GREEN_700, color="white", on_click=submit_resolve)
        ]
    )
    
def _create_priority_tag(text, color):
    return ft.Container(
        content=ft.Text(text, size=11, color="white", weight="bold"),
        bgcolor=color, padding=ft.Padding.symmetric(horizontal=8, vertical=2), border_radius=5
    )
def _create_status_badge(status):
    colors = {"Pending": ft.Colors.RED_100, "In Progress": ft.Colors.ORANGE_100, "Resolved": ft.Colors.GREEN_100}
    text_colors = {"Pending": ft.Colors.RED_700, "In Progress": ft.Colors.ORANGE_700, "Resolved": ft.Colors.GREEN_700}
    return ft.Container(
        content=ft.Text(status, size=11, weight="bold", color=text_colors.get(status, ft.Colors.BLACK)),
        bgcolor=colors.get(status, ft.Colors.GREY_100),
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=5
    )