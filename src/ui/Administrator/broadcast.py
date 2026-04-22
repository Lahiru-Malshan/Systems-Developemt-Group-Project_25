
import sys
import os
from turtle import color
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *
from logic.search import *
from logic.notifications import *
import db # IMPORTANT: Connects to MySQL

def show_broadcast(dash, *args):
    dash.content_column.controls.clear()

    search_term = getattr(dash, "bc_search_input", ft.TextField()).value or ""
    
    # 1. FETCH FROM DATABASE
    raw_db_data = db.get_all_broadcasts()
    
    # Map DB data to the format your UI and SearchEngine expects
    broadcast_history = []
    for b in raw_db_data:
        broadcast_history.append({
            "id": f"BC-{b['broadcast_id']}",
            "title": b["title"],
            "target": b["target_audience"],
            "date": str(b["send_date"]),
            "type": b["urgency"]
        })

    filtered_data = SearchEngine.apply_logic(broadcast_history, search_term=search_term)

    current_rows = []
    for bc in filtered_data:
        type_color = ft.Colors.RED_ACCENT if bc["type"] == "Urgent" else ft.Colors.BLUE_ACCENT
        current_rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(bc["id"], color=TEXT_DARK, weight="bold")),
                ft.DataCell(ft.Text(bc["title"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(bc["target"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(bc["date"], color=TEXT_DARK)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(bc["type"], color="white", size=12, weight="bold"),
                        bgcolor=type_color, padding=5, border_radius=5
                    )
                ),
            ])
        )

    # --- UI COMPONENTS ---
    dash.bc_search_input = ft.TextField(
        label="Search history...", prefix_icon=ft.Icons.SEARCH, value=search_term,
        expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
        on_submit=lambda _: show_broadcast(dash)
    )

    header = ft.Row([
        ft.Column([
            ft.Text("Communication Center", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Broadcast system connected to Resident App", color=TEXT_DARK, size=14),
        ]),
        ft.Button(
            "New Announcement", icon=ft.Icons.ADD_COMMENT,
            bgcolor=ACCENT_BLUE, color="white",
            on_click=lambda _: open_broadcast_modal(dash)
        )
    ], alignment="spaceBetween")

    main_container = ft.Container(
        content=ft.Column([
            header,
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                dash.bc_search_input,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_broadcast(dash)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.bc_search_input, "value", ""), show_broadcast(dash)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Title", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Target", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Date Sent", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Urgency", weight="bold", color=TEXT_DARK)),
                ],
                rows=current_rows, expand=True
            )
        ], scroll=ft.ScrollMode.AUTO),
        padding=30, bgcolor=CARD_BG, border_radius=15, expand=True
    )

    dash.content_column.controls.append(main_container)
    dash.page.update()

def open_broadcast_modal(dash):
    title_field = ft.TextField(label="Message Title", border_color=ACCENT_BLUE)
    target_field = ft.Dropdown(
        label="Target Audience",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("All Residents"),
            ft.dropdown.Option("All Staff")
        ],
        value="All",
        border_color=ACCENT_BLUE
    )
    content_field = ft.TextField(label="Content", multiline=True, min_lines=3,border_color=ACCENT_BLUE)
    type_field = ft.Dropdown(
        label="Type",
        options=[
            ft.dropdown.Option("Info"),
            ft.dropdown.Option("Urgent"),
        ],
        value="Info",
        border_color=ACCENT_BLUE
    )

    def submit_broadcast(e):
        if not title_field.value or not content_field.value:
            dash.show_message("Error: Please fill all fields!")
            return
        
        selected_type = type_field.value

        # Normalize selected_type: Dropdown may return a set/list in some configs
        if isinstance(selected_type, (set, list, tuple)):
            try:
                selected_type = next(iter(selected_type))
            except StopIteration:
                selected_type = 'Info'

        # Validate and restrict to allowed values only
        if selected_type not in ('Info', 'Urgent'):
            selected_type = 'Info'

        # 1. SEND REAL NOTIFICATION
        try:
            # Convert target dropdown to proper recipients
            recipients_raw = []
            if target_field.value == "All":
                recipients_raw = db.get_all_users()
            elif target_field.value == "All Staff":
                recipients_raw = db.get_all_staff()
            elif target_field.value == "All Residents":
                recipients_raw = db.get_all_residents()

            # Normalize to list of user_id integers
            recipients = []
            for r in recipients_raw:
                if isinstance(r, dict):
                    uid = r.get('user_id') or r.get('userId') or r.get('id')
                    if uid is not None:
                        recipients.append(uid)
                else:
                    recipients.append(r)

            for user_id in recipients:
                send_notification(
                    dash,
                    user_id=user_id,
                    title=title_field.value,
                    message=content_field.value
                )
        except Exception as err:
            print(f"Notification Error: {err}")

        # 2. SAVE TO MYSQL DATABASE
        # Only send 'Info' or 'Urgent' to the DB (no mapping needed)
        db_urgency = selected_type

        success = db.add_broadcast(
            title=title_field.value,
            target_audience=target_field.value,
            content=content_field.value,
            urgency=db_urgency
        )

        if success:
            dash.close_dialog()
            dash.show_message("Announcement broadcasted successfully!")
            show_broadcast(dash) # Refresh UI to show the new broadcast
        else:
            dash.show_message("Database Error: Could not save broadcast history.")

    dash.show_custom_modal(
        "Compose Broadcast",
        ft.Column([title_field, target_field, type_field, content_field], tight=True, spacing=15, width=450),
        [
            ft.TextButton("Discard", on_click=lambda _: dash.close_dialog()),
            ft.Button("SEND NOW", bgcolor=ACCENT_BLUE, color="white", on_click=submit_broadcast)
        ]
    )