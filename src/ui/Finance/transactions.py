# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import flet as ft
from base_dashboard import *
from logic.search import *

payments_data = [
    {"date": "2026-02-20", "unit": "A-101", "ref": "RENT-FEB-101", "amount": 1200.00, "method": "Bank Transfer", "status": "Reconciled"},
    {"date": "2026-02-19", "unit": "B-302", "ref": "SVC-302-Q1", "amount": 540.00, "method": "Stripe", "status": "Pending"},
    {"date": "2026-02-18", "unit": "C-204", "ref": "UTIL-FEB-204", "amount": 90.00, "method": "Direct Debit", "status": "Paid"},
    {"date": "2026-02-17", "unit": "D-505", "ref": "PARK-FEB-505", "amount": 50.00, "method": "Bank Transfer", "status": "Pending"},
    {"date": "2026-02-16", "unit": "A-205", "ref": "RENT-FEB-205", "amount": 950.00, "method": "Direct Debit", "status": "Paid"},
]

def show_transactions(dash, *args):
    if not dash:
        return
    dash.content_column.controls.clear()
    if not hasattr(dash, "transaction_table_area"):
        dash.transaction_table_area = ft.Column(expand=True)

    header = ft.Row([
        ft.Column([
            ft.Text("Payment Transactions", size=24, weight="bold", color=TEXT_DARK),
            ft.Text("Track and reconcile incoming payments", size=14, color=TEXT_MUTED),
        ]),
        ft.Button(
            "IMPORT STATEMENT (CSV)",
            icon=ft.Icons.UPLOAD_FILE_ROUNDED,
            bgcolor=ft.Colors.BLUE_GREY_800,
            color="white",
            on_click=lambda _: dash.show_message("Importing bank statement...")
        )
    ], alignment="spaceBetween")

    dash.trans_search = ft.TextField(
        label="Search Unit or Reference",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        bgcolor="white",
        color=TEXT_DARK,
        border_radius=10,
        on_submit=lambda _: apply_transaction_filters(dash)
    )
    dash.trans_status_filter = ft.Dropdown(
        label="Status",
        width=220,
        value="All",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Reconciled"),
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("Paid"),
        ],
        bgcolor="white",
        color=TEXT_DARK
    )
    filter_bar = ft.Container(
        padding=15,
        bgcolor=ft.Colors.with_opacity(0.05, ACCENT_BLUE),
        border_radius=10,
        content=ft.Row([
            dash.trans_search,
            dash.trans_status_filter,
            ft.Button(
                "APPLY",
                icon=ft.Icons.FILTER_ALT_ROUNDED,
                bgcolor=ACCENT_BLUE,
                color="white",
                on_click=lambda _: apply_transaction_filters(dash)
            ),
            ft.Button(
                "RECONCILE ALL PAID",
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
                bgcolor=ft.Colors.GREEN_700,
                color="white",
                on_click=lambda _: handle_reconcile_all_paid(dash)
            ),
            ft.IconButton(
                icon=ft.Icons.RESTART_ALT_ROUNDED,
                tooltip="Reset Filters",
                on_click=lambda _: show_transactions(dash)
            )
        ], spacing=15)
    )

    table_card = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        expand=True,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, TEXT_DARK)),
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.05, "black")),
        content=ft.Column([
            ft.Row([
                ft.Text("Transaction List", weight="bold", size=16, color=TEXT_DARK),
                ft.Text(f"Showing {len(payments_data)} records", size=12, color=TEXT_MUTED)
            ], alignment="spaceBetween"),
            ft.Divider(height=1),
            ft.Row([dash.transaction_table_area], scroll=ft.ScrollMode.ALWAYS)
        ])
    )

    dash.content_column.controls.extend([header, filter_bar, table_card])
    apply_transaction_filters(dash)
    dash.page.update()

def apply_transaction_filters(dash):
    if not hasattr(dash, "transaction_table_area"):
        return
    search_val = (dash.trans_search.value or "")
    status_val = dash.trans_status_filter.value or "All"
    
    filtered = SearchEngine.apply_logic(
        data_list=payments_data,
        search_term=search_val,
        filters={"status": status_val}
    )
    filtered = sorted(filtered, key=lambda x: x["date"], reverse=True)
    
    rows = []
    for p in filtered:
        if p["status"] == "Reconciled":
            s_color = ft.Colors.GREEN_700
        elif p["status"] == "Paid":
            s_color = ft.Colors.BLUE_700
        else:
            s_color = ft.Colors.ORANGE_700
        ref_val = p["ref"]
        if p["status"] == "Paid":
            action_control = ft.IconButton(
                ft.Icons.CHECK_CIRCLE_OUTLINE,
                icon_color=ft.Colors.GREEN_700,
                tooltip="Mark as Reconciled",
                on_click=lambda e, r=ref_val: handle_reconcile(dash, r)
            )
        elif p["status"] == "Pending":
            action_control = ft.Icon(ft.Icons.LOCK_ROUNDED, color=ft.Colors.ORANGE_600, size=20)
        else:
            action_control = ft.Icon(ft.Icons.VERIFIED_ROUNDED, color=ft.Colors.BLUE_400, size=20)
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(p["date"], color=TEXT_DARK)),
                ft.DataCell(ft.Text(p["unit"], weight="bold", color=TEXT_DARK)),
                ft.DataCell(ft.Text(p["ref"], font_family="monospace", color=ft.Colors.BLUE_GREY_700)),
                ft.DataCell(ft.Text("£{:,.2f}".format(p["amount"]), weight="bold", color=ACCENT_BLUE)),
                ft.DataCell(ft.Text(p["method"], color=TEXT_DARK)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(p["status"].upper(), size=10, weight="bold", color="white"),
                        bgcolor=s_color,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=15
                    )
                ),
                ft.DataCell(action_control),
            ])
        )

    dash.transaction_table_area.controls = [
        ft.DataTable(
            expand=True,
            column_spacing=35,
            heading_row_color=ft.Colors.BLUE_GREY_50,
            columns=[
                ft.DataColumn(ft.Text("Date", color=ft.Colors.BLUE_900, weight="bold")),
                ft.DataColumn(ft.Text("Unit", color=ft.Colors.BLUE_900, weight="bold")),
                ft.DataColumn(ft.Text("Reference", color=ft.Colors.BLUE_900, weight="bold")),
                ft.DataColumn(ft.Text("Amount", color=ft.Colors.BLUE_900, weight="bold")),
                ft.DataColumn(ft.Text("Method", color=ft.Colors.BLUE_900, weight="bold")),
                ft.DataColumn(ft.Text("Status", color=ft.Colors.BLUE_900, weight="bold")),
                ft.DataColumn(ft.Text("Action", color=ft.Colors.BLUE_900, weight="bold")),
            ],
            rows=rows
        )
    ]
    dash.page.update()

def _get_filtered_list(dash):
    search_val = (dash.trans_search.value or "").lower()
    status_val = dash.trans_status_filter.value or "All"
    filtered = [
        p for p in payments_data
        if (search_val in p["unit"].lower() or search_val in p["ref"].lower())
        and (status_val == "All" or p["status"] == status_val)
    ]
    return filtered

def handle_reconcile_all_paid(dash):
    global payments_data
    filtered = _get_filtered_list(dash)
    paid_refs = [p["ref"] for p in filtered if p["status"] == "Paid"]
    count = 0
    for p in payments_data:
        if p["ref"] in paid_refs:
            p["status"] = "Reconciled"
            count += 1
    if count > 0:
        dash.show_message(f"Successfully reconciled {count} Paid transaction(s).")
    else:
        dash.show_message("No Paid transactions in current filter to reconcile.")
    apply_transaction_filters(dash)

def handle_reconcile(dash, reference):
    global payments_data
    for p in payments_data:
        if p["ref"] == reference:
            p["status"] = "Reconciled"
            break
    dash.show_message("Transaction " + reference + " successfully reconciled.")
    apply_transaction_filters(dash)
