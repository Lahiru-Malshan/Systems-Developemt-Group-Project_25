import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../../"))
if src_path not in sys.path:
    sys.path.append(src_path)
    
from base_dashboard import *
from logic.search import *
import flet as ft

def show_notifications(dash, *args):
    if not dash: return
    dash.content_column.controls.clear()
    
    dash.type_filter = ft.Dropdown(
        label="Type",
        value="All Types",
        width=150,
        text_style=ft.TextStyle(color=TEXT_DARK),
        options=[ft.dropdown.Option(x) for x in ["All Types", "Billing", "Maintenance", "Security", "General"]],
    )

    dash.time_filter = ft.Dropdown(
        label="Time",
        value="All Time",
        width=180,
        text_style=ft.TextStyle(color=TEXT_DARK),
        options=[ft.dropdown.Option(x) for x in ["All Time", "Last 1 Week", "Last 2 Weeks", "Last 1 Month", "Last 3 Months"]],
    )

    filter_bar = ft.Container(
        bgcolor=CARD_BG,
        padding=15,
        border_radius=12,
        content=ft.Row([
            ft.Icon(ft.Icons.FILTER_LIST_ROUNDED, color=ACCENT_BLUE),
            ft.Text("Filters:", weight="bold", color=TEXT_DARK),
            dash.type_filter,
            dash.time_filter,
            ft.Button(
                "Apply",
                icon=ft.Icons.SEARCH_ROUNDED,
                on_click=lambda e: apply_notification_filters(dash),
                style=ft.ButtonStyle(bgcolor=ACCENT_BLUE, color="white")
            ),
            ft.Container(expand=True),
            ft.TextButton(
                "Clear All",
                icon=ft.Icons.REFRESH_ROUNDED,
                on_click=lambda e: reset_filters(dash)
            )
        ], spacing=20)
    )

    dash.notif_list_area = ft.Column(spacing=10, expand=True)
    
    notif_container = ft.Container(
        bgcolor=CARD_BG,
        padding=25,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.Text("Alert History", size=18, weight="bold", color=TEXT_DARK),
            dash.notif_list_area
        ], scroll=ft.ScrollMode.AUTO)
    )

    dash.content_column.controls = [filter_bar, notif_container]
    apply_notification_filters(dash)

def apply_notification_filters(dash, e=None):
    if not hasattr(dash, "notif_list_area") or dash.notif_list_area is None:
        return

    # --- KẾT NỐI DỮ LIỆU (DẠNG DICTIONARY) ---
    # Sau này dòng này sẽ là: raw_data = db.fetch_all_as_dict("SELECT * FROM notifications")
    
    raw_data = [
        {"type": "Security", "title": "Parking Update", "msg": "New guest parking rules.", "date": "4 days ago", "days": 4, "unread": False},
        {"type": "Billing", "title": "Rent Invoice Generated", "msg": "Your rent invoice for February is ready.", "date": "Today", "days": 0, "unread": True},
        {"type": "General", "title": "Spring BBQ Party", "msg": "Join us for a BBQ party.", "date": "20 days ago", "days": 20, "unread": False},
        {"type": "Maintenance", "title": "Elevator Repair", "msg": "Elevator maintenance in Block B.", "date": "Yesterday", "days": 1, "unread": True},
        {"type": "Maintenance", "title": "Water Leak Fixed", "msg": "The leak in 3rd floor is fixed.", "date": "45 days ago", "days": 45, "unread": False},
        {"type": "Billing", "title": "Payment Received", "msg": "Received payment for January.", "date": "10 days ago", "days": 10, "unread": False},
    ]

    filtered = SearchEngine.apply_logic(raw_data, filters={"type": dash.type_filter.value})

    time_map = {"Last 1 Week": 7, "Last 2 Weeks": 14, "Last 1 Month": 30, "Last 3 Months": 90}
    if dash.time_filter.value != "All Time":
        max_days = time_map.get(dash.time_filter.value, 999)
        filtered = [n for n in filtered if n["days"] <= max_days]

    final_list = sorted(filtered, key=lambda x: (not x["unread"], x["days"]))

    dash.notif_list_area.controls.clear()

    if not final_list:
        dash.notif_list_area.controls.append(
            ft.Container(content=ft.Text("No results.", weight="bold"), padding=50, alignment=ft.Alignment(0,0))
        )
    else:
        shown_recent = shown_last_week = shown_older = False
        badge_colors = {"Billing": ft.Colors.ORANGE_700, "Maintenance": ft.Colors.RED_700, "Security": ft.Colors.BLUE_GREY_900, "General": ft.Colors.BLUE_700}

        for item in final_list:
            # Header logic
            header_text = ""
            if item["days"] <= 7 and not shown_recent:
                header_text = "RECENT (THIS WEEK)"; shown_recent = True
            elif 7 < item["days"] <= 14 and not shown_last_week:
                header_text = "LAST WEEK"; shown_last_week = True
            elif item["days"] > 14 and not shown_older:
                header_text = "OLDER NOTIFICATIONS"; shown_older = True

            if header_text:
                dash.notif_list_area.controls.append(
                    ft.Row([ft.Divider(expand=True), ft.Text(header_text, size=11, weight="bold", color=ft.Colors.GREY_400)], spacing=10)
                )

            # Notification Item
            dash.notif_list_area.controls.append(
                ft.Container(
                    padding=ft.Padding(15, 12, 15, 12),
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_50 if item["unread"] else ft.Colors.TRANSPARENT,
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(item["type"].upper(), size=9, weight="bold", color="white"),
                            bgcolor=badge_colors.get(item["type"], ft.Colors.GREY_500),
                            padding=ft.Padding(10, 4, 10, 4), border_radius=5, width=90, alignment=ft.Alignment(0, 0)
                        ),
                        ft.Column([
                            ft.Text(item["title"], weight="bold", size=15, color=TEXT_DARK),
                            ft.Text(item["msg"], size=13, weight="bold", color=ft.Colors.GREY_600, width=500),
                        ], expand=True, spacing=2),
                        ft.Column([
                            ft.Text(item["date"], size=12, weight="bold", color=ft.Colors.GREY_400),
                            ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.BLUE_600, size=12) if item["unread"] else ft.Container()
                        ], horizontal_alignment=ft.CrossAxisAlignment.END)
                    ])
                )
            )
    dash.page.update()

def reset_filters(dash, e=None):
    dash.type_filter.value = "All Types"
    dash.time_filter.value = "All Time"
    apply_notification_filters(dash)