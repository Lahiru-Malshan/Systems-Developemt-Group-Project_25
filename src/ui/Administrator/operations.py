# Elena Ho - 25044389

import sys
import os
from turtle import color
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *
from logic.search import *

# --- MOCK DATA ---
ops_tasks = [
    {"id": "OP-101", "task": "Fire Extinguisher Check", "assigned": "Security Team", "priority": "High", "status": "Pending"},
    {"id": "OP-102", "task": "Garden Watering", "assigned": "Maintenance", "priority": "Low", "status": "Completed"},
    {"id": "OP-103", "task": "CCTV System Audit", "assigned": "IT Support", "priority": "Medium", "status": "In Progress"},
]

def show_operations(dash, *args):
    dash.content_column.controls.clear()

    search_term = getattr(dash, "ops_search_input", ft.TextField()).value or ""
    filtered_data = SearchEngine.apply_logic(ops_tasks, search_term=search_term)

    current_rows = []
    for op in filtered_data:
        status_color = ft.Colors.GREEN if op["status"] == "Completed" else \
                    ft.Colors.ORANGE if op["status"] == "In Progress" else ft.Colors.RED_ACCENT
        
        current_rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(op["id"], color=TEXT_DARK, weight="bold")),
                ft.DataCell(ft.Text(op["task"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(op["assigned"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(op["priority"], color=TEXT_DARK)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(op["status"], color="white", size=12, weight="bold"),
                        bgcolor=status_color, padding=5, border_radius=5
                    )
                ),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(ft.Icons.CHECK_CIRCLE_OUTLINE, icon_color="green", icon_size=18),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", icon_size=18),
                    ])
                ),
            ])
        )

    dash.ops_search_input = ft.TextField(
        label="Search operations...", prefix_icon=ft.Icons.SEARCH, value=search_term,
        expand=True, color=TEXT_DARK, border_color=ACCENT_BLUE,
        on_submit=lambda _: show_operations(dash)
    )

    header = ft.Row([
        ft.Column([
            ft.Text("Building Operations", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Daily tasks and personnel assignment", color=TEXT_DARK, size=14),
        ]),
        ft.Button(
            "Add Task", icon=ft.Icons.ADD_TASK,
            bgcolor=ACCENT_BLUE, color="white",
            on_click=lambda _: open_ops_modal(dash)
        )
    ], alignment="spaceBetween")

    main_container = ft.Container(
        content=ft.Column([
            header,
            ft.Divider(height=20, color="transparent"),
            ft.Row([
                dash.ops_search_input,
                ft.Button("Apply", bgcolor=ACCENT_BLUE, color="white", on_click=lambda _: show_operations(dash)),
                ft.IconButton(ft.Icons.REFRESH, icon_color=ACCENT_BLUE, on_click=lambda _: (setattr(dash.ops_search_input, "value", ""), show_operations(dash)))
            ], spacing=10),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Task Name", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Assigned To", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Priority", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Manage", weight="bold", color=TEXT_DARK)),
                ],
                rows=current_rows, expand=True
            )
        ], scroll=ft.ScrollMode.AUTO),
        padding=30, bgcolor=CARD_BG, border_radius=15, expand=True
    )

    dash.content_column.controls.append(main_container)
    dash.page.update()

def open_ops_modal(dash):
    task_field = ft.TextField(label="Task Name", border_color=ACCENT_BLUE, color=TEXT_WHITE)
    assigned_field = ft.Dropdown(
        label="Assign To",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Maintenance Team"),
            ft.dropdown.Option("Security Team"),
            ft.dropdown.Option("Cleaning Crew")
        ],
        value="All", color=TEXT_WHITE, border_color=ACCENT_BLUE
    )
    priority_field = ft.Dropdown(
        label="Priority",
        options=[
            ft.dropdown.Option("Low"),
            ft.dropdown.Option("Medium"),
            ft.dropdown.Option("High")
        ],
        value="Medium", color=TEXT_WHITE, border_color=ACCENT_BLUE
    )

    def submit_task(e):
        if not task_field.value:
            dash.show_message("Error: Task name is required!")
            return

        ops_tasks.insert(0, {
            "id": f"OP-{len(ops_tasks) + 1}",
            "task": task_field.value,
            "assigned": assigned_field.value,
            "priority": priority_field.value,
            "status": "Pending"
        })

        dash.close_dialog()
        dash.show_message("New operational task added!")
        show_operations(dash)

    modal_content = ft.Column([
        ft.Text("Create a new operational duty.", size=14),
        task_field,
        assigned_field,
        priority_field
    ], tight=True, spacing=15, width=450)

    actions = [
        ft.TextButton("Cancel", on_click=lambda _: dash.close_dialog()),
        ft.Button("CREATE TASK", bgcolor=ACCENT_BLUE, color="white", on_click=submit_task)
    ]

    dash.show_custom_modal("New Operation Task", modal_content, actions)