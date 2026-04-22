
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from datetime import datetime
from base_dashboard import *
from logic.search import *

invoices_data = [
    {"id": "INV-2001", "room": "A-101", "desc": "Monthly Rent - Feb", "net": 1000.00, "vat": 200.00, "status": "Paid", "date": "2026-02-05"},
    {"id": "INV-2002", "room": "B-302", "desc": "Service Charge - Q1", "net": 450.00, "vat": 90.00, "status": "Overdue", "date": "2026-02-15"},
    {"id": "INV-2003", "room": "C-204", "desc": "Utility Repair", "net": 75.00, "vat": 15.00, "status": "Unpaid", "date": "2026-02-25"},
]

def show_invoices(dash, *args):
    if not dash:
        return
    dash.content_column.controls.clear()
    dash.invoice_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.ALWAYS)

    header = ft.Row([
        ft.Column([
            ft.Text("Invoice Management", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Manage, issue and track resident billings", size=14, color=TEXT_MUTED),
        ]),
        ft.Button(
            content=ft.Text("CREATE INVOICE", weight="bold", color="white"),
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            bgcolor=ACCENT_BLUE,
            on_click=lambda _: open_invoice_form(dash)
        ),
    ], alignment="spaceBetween")

    dash.status_filter = ft.SegmentedButton(
        selected=["ALL"],
        allow_multiple_selection=False,
        on_change=lambda _: apply_invoice_filters(dash),
        segments=[
            ft.Segment(value="ALL", label=ft.Text("All", color=ACCENT_BLUE_LIGHT), icon=ft.Icon(ft.Icons.LIST_ROUNDED, color=ACCENT_BLUE_LIGHT)),
            ft.Segment(value="Paid", label=ft.Text("Paid", color=ACCENT_BLUE_LIGHT), icon=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, ft.Colors.GREEN_700)),
            ft.Segment(value="Unpaid", label=ft.Text("Unpaid", color=ACCENT_BLUE_LIGHT), icon=ft.Icon(ft.Icons.PENDING_OUTLINED, ft.Colors.ORANGE_700)),
            ft.Segment(value="Overdue", label=ft.Text("Overdue", color=ACCENT_BLUE_LIGHT), icon=ft.Icon(ft.Icons.REPORT_GMAILERRORRED_OUTLINED, ft.Colors.RED_700)),
        ],
    )
    dash.inv_search = ft.TextField(
        label="Search Unit or Invoice ID",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        bgcolor="white",
        color=TEXT_DARK,
        expand=True
    )
    apply_btn = ft.Button(
        "Apply",
        icon=ft.Icons.SEARCH_ROUNDED,
        bgcolor=ACCENT_BLUE,
        color="white",
        height=45,
        on_click=lambda _: apply_invoice_filters(dash)
    )
    filter_row = ft.Column([
        ft.Row([dash.inv_search,
                apply_btn], spacing=10),
        ft.Row([ft.Text("Status:", weight="bold", color=ACCENT_BLUE), dash.status_filter], spacing=10)
    ], spacing=15)

    list_container = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        content=ft.Column([
            filter_row,
            ft.Divider(height=10, color="transparent"),
            ft.Container(content=dash.invoice_list_column, expand=True)
        ])
    )

    dash.content_column.controls.extend([header, list_container])
    apply_invoice_filters(dash)
    dash.page.update()

def apply_invoice_filters(dash):
    if not hasattr(dash, "invoice_list_column"):
        return
    
    search_term = (dash.inv_search.value or "").upper()
    sel = dash.status_filter.selected
    selected_status = list(sel)[0] if sel else "ALL"
    current_filters = {}
    if selected_status != "ALL":
        current_filters["status"] = selected_status
    
    final_list = SearchEngine.apply_logic(
        data_list=invoices_data,
        search_term=search_term,
        filters=current_filters
    )
    dash.invoice_list_column.controls.clear()
    if not final_list:
        dash.invoice_list_column.controls.append(
            ft.Container(
                content=ft.Text("No invoices match your filters.", italic=True),
                padding=20
            )
        )
    else:
        for inv in final_list:
            dash.invoice_list_column.controls.append(_create_invoice_item(dash, inv))
    
    dash.page.update()

def _create_invoice_item(dash, inv):
    total = inv["net"] + inv["vat"]
    s_color = ft.Colors.GREEN_700 if inv["status"] == "Paid" else ft.Colors.RED_700 if inv["status"] == "Overdue" else ft.Colors.ORANGE_700
    return ft.Container(
        padding=15,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=10,
        bgcolor="white",
        content=ft.Row([
            ft.Text(inv["id"], weight="bold", width=100, color=TEXT_DARK),
            ft.Text(inv["room"], weight="bold", width=80, color=TEXT_DARK),
            ft.Text(inv["desc"], expand=True, color=TEXT_DARK),
            ft.Text(f"£{total:,.2f}", width=100, weight="bold", color=TEXT_DARK),
            ft.Container(
                content=ft.Text(inv["status"].upper(), size=10, weight="bold", color="white"),
                bgcolor=s_color,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=15,
                width=100,
                alignment=ft.Alignment(0.5, 0.5)
            ),
        ])
    )

def open_invoice_form(dash):
    current_date = datetime.now().strftime("%Y-%m-%d")

    ref_block = ft.Dropdown(
        label="Block",
        border_color=ACCENT_BLUE,
        options=[
            ft.dropdown.Option("A"),
            ft.dropdown.Option("B"),
            ft.dropdown.Option("C"),
            ft.dropdown.Option("D"),
        ],
        width=120
    )
    ref_unit_number = ft.TextField(label="Unit Number", border_color=ACCENT_BLUE, hint_text="e.g. 101", width=165)
    ref_desc = ft.TextField(label="Description", border_color=ACCENT_BLUE)
    ref_net = ft.TextField(label="Net Amount (£)", border_color=ACCENT_BLUE)

    def handle_submit(e):
        if not ref_block.value or not ref_unit_number.value or not ref_net.value:
            dash.show_message("Please fill in Block, Unit Number and Amount!")
            return
        try:
            global invoices_data
            net_val = float(ref_net.value)
            vat_val = net_val * 0.20  # 20% VAT UK
            unit_display = f"{ref_block.value}-{ref_unit_number.value}"
            new_inv = {
                "id": f"INV-{len(invoices_data) + 1}",
                "room": unit_display,
                "desc": ref_desc.value if ref_desc.value else "Manual Entry",
                "net": net_val,
                "vat": vat_val,
                "status": "Unpaid",
                "date": current_date
            }
            invoices_data.insert(0, new_inv)
            dash.close_dialog(e)
            dash.show_message(f"Invoice {new_inv['id']} issued for {unit_display}!")
            show_invoices(dash)
        except ValueError:
            dash.show_message("Please enter a valid amount!")

    content = ft.Column([
        ft.Row([ref_block, ref_unit_number], spacing=15),
        ref_desc, ref_net,
        ft.Text("Standard UK VAT (20%) will be added automatically.", size=11, italic=True)
    ], tight=True, spacing=15, width=400)
    actions = [
        ft.TextButton(content=ft.Text("Cancel"), on_click=lambda e: dash.close_dialog(e)),
        ft.Button(content=ft.Text("ISSUE INVOICE", color="white"), bgcolor=ACCENT_BLUE, on_click=handle_submit)
    ]
    dash.show_custom_modal("New Invoice", content, actions)
