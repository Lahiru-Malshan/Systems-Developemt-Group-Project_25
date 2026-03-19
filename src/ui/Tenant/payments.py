# Elena Ho - 25044389

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from base_dashboard import *
import flet as ft

transactions_data = [
    ["2025-10-01", "Monthly Rent - October", 1200.00, "Pending"],
    ["2025-09-05", "Monthly Rent - September", 1200.00, "Paid"],
    ["2025-08-28", "Water Bill - August", 50.00, "Paid"],
]

def show_payments(dash, *args):
    if not dash:
        return
    
    invoices = []
    transactions = []
    if hasattr(dash, "backend"):
        invoices = dash.backend.get_invoices() if hasattr(dash.backend, "get_invoices") else []
        transactions = dash.backend.get_payments() if hasattr(dash.backend, "get_payments") else []
    else:
        transactions = transactions_data
    dash.content_column.controls.clear()
    
    outstanding = sum(inv.get("amount", 0) for inv in invoices if inv.get("status") != "Paid")
    last_paid = next((t for t in transactions if t.get("status") == "Paid"), None)
    last_paid_label = f"£{last_paid['amount']:,.2f} ({last_paid['date']})" if last_paid else "£0.00"

    # 1. Balance Overview (Cards)
    balance_cards = ft.Row(
        spacing=20,
        controls=[
            dash.create_stat_card("Total Outstanding", f"£{outstanding:,.2f}", ft.Icons.MONEY_OFF_ROUNDED, highlight=True),
            dash.create_stat_card("Last Paid", last_paid_label, ft.Icons.CHECK_CIRCLE_ROUNDED),
            dash.create_stat_card("Open Invoices", str(len([i for i in invoices if i.get("status") != "Paid"])), ft.Icons.RECEIPT_LONG_ROUNDED),
        ]
    )
    
    # 2. Invoice Rows & Transaction History
    # Invoice Rows
    invoice_rows = []
    for inv in sorted(invoices, key=lambda x: x.get("invoice_id", 0)):
        status = inv.get("status", "Unpaid")
        color = ft.Colors.GREEN_700 if status == "Paid" else ft.Colors.RED_700 if status == "Late" else ft.Colors.ORANGE_700
        invoice_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(inv.get("invoice_id", "")), weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(str(inv.get("issue_date", "")), weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                    ft.DataCell(ft.Text(str(inv.get("due_date", "")), weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                    ft.DataCell(ft.Text(f"£{inv.get('amount', 0):,.2f}", weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                    ft.DataCell(ft.Container(content=ft.Text(status, color="white", size=10, weight="bold"), bgcolor=color, padding=ft.padding.symmetric(vertical=4, horizontal=10), border_radius=15)),
                ]
            )
        )
    
    invoice_table = ft.Container(
        bgcolor=CARD_BG,
        padding=25,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.Text("My Invoices", size=18, weight="bold", color=TEXT_DARK),
            ft.DataTable(
                expand=True,
                columns=[
                    ft.DataColumn(ft.Text("Invoice #", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Issue Date", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Due Date", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Amount", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                ],
                rows=invoice_rows,
            )
        ], scroll=ft.ScrollMode.AUTO)
    )
    
    payment_rows = []
    for t in transactions:
        payment_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(t.get("date", ""), weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                    ft.DataCell(ft.Text(t.get("description", ""), weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                    ft.DataCell(ft.Text(f"£{t.get('amount', 0):,.2f}", weight=ft.FontWeight.BOLD, color=TEXT_DARK)),
                    ft.DataCell(ft.Text(t.get("status", ""), weight=ft.FontWeight.W_500, color=TEXT_DARK)),
                ]
            )
        )
        
    history_table = ft.Container(
        bgcolor=CARD_BG,
        padding=25,
        border_radius=12,
        expand=True,
        content=ft.Column([
            ft.Text("Transaction History", size=18, weight="bold", color=TEXT_DARK),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Date", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Description", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Amount", weight="bold", color=TEXT_DARK)),
                    ft.DataColumn(ft.Text("Status", weight="bold", color=TEXT_DARK)),
                ],
                rows=payment_rows,
            )
        ], scroll=ft.ScrollMode.AUTO)
    )

    # 3. Pay Action
    action_card = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        width=320,
        content=ft.Column([
            ft.Text("Make Payment", size=16, weight="bold", color=TEXT_DARK),
            ft.Text(f"Outstanding: £{outstanding:,.2f}", size=18, weight="bold", color=TEXT_DARK),
            ft.Divider(),
            ft.Button("Pay Now", icon=ft.Icons.PAYMENT_ROUNDED, bgcolor=ACCENT_BLUE, color="white", height=50, on_click=lambda _: open_payment_modal(dash, invoices)),
            ft.Text("Payment updates invoice status and history.", size=11, color=TEXT_MUTED, italic=True),
        ], horizontal_alignment="center")
    )
    
    left_column = ft.Column(
        [invoice_table, history_table],
        expand=True,
        spacing=25,
        scroll=ft.ScrollMode.AUTO
    )
    
    main_row = ft.Row(
        [left_column, action_card],
        expand=True,
        alignment="start",
        vertical_alignment="start",
        spacing=20
    )
    
    dash.content_column.controls = [
        balance_cards,
        main_row,
    ]
    dash.page.update()
    
def open_payment_modal(dash, invoices=None):
    unpaid = [inv for inv in (invoices or []) if inv.get("status") != "Paid"]
    invoice_options = [ft.dropdown.Option(str(inv.get("invoice_id"))) for inv in unpaid] if unpaid else [ft.dropdown.Option("0")]
    
    initial_invoice_id = str(unpaid[0].get("invoice_id")) if unpaid else "0"
    initial_amount = str(unpaid[0].get("amount", 0)) if unpaid else "0"
    
    invoice_dropdown = ft.Dropdown(label="Invoice", value=initial_invoice_id, options=invoice_options, border_color=ACCENT_BLUE)
    ref_amount = ft.TextField(label="Amount", prefix=ft.Text("£ "), value=initial_amount, keyboard_type=ft.KeyboardType.NUMBER, border_color=ACCENT_BLUE)
    ref_method = ft.Dropdown(label="Method", value="Visa / Mastercard", options=[ft.dropdown.Option("Visa / Mastercard"), ft.dropdown.Option("PayPal"), ft.dropdown.Option("Google Pay"), ft.dropdown.Option("Apple Pay")], border_color=ACCENT_BLUE)

    def handle_confirm_payment(e):
        amount_str = ref_amount.value or "0"
        try:
            amt = float(amount_str)
            if amt <= 0:
                raise ValueError("Amount must be greater than 0")
        except (ValueError, TypeError) as ex:
            dash.show_message(f"Please enter a valid amount.")
            return

        invoice_id_str = invoice_dropdown.value or "0"
        invoice_id = None
        try:
            if invoice_id_str and invoice_id_str.isdigit():
                inv_id = int(invoice_id_str)
                if inv_id != 0:
                    invoice_id = inv_id
        except (ValueError, TypeError):
            pass

        method = ref_method.value or "Visa / Mastercard"
        description = f"Payment on invoice {invoice_id}" if invoice_id else "Payment"

        if hasattr(dash, "backend") and hasattr(dash.backend, "make_payment"):
            success, msg = dash.backend.make_payment(amt, method, description, invoice_id=invoice_id)
        elif hasattr(dash, "backend") and hasattr(dash.backend, "add_payment"):
            success, msg = dash.backend.add_payment(amt, method, description)
        else:
            success, msg = False, "No backend available"

        if success:
            dash.show_message("Payment recorded successfully.")
        else:
            dash.show_message(f"Payment failed: {msg}")
        dash.close_dialog()
        show_payments(dash)

    content = ft.Column([ft.Text("Complete payment details"), invoice_dropdown, ref_amount, ref_method], spacing=10)
    
    dash.show_custom_modal("Make Payment", content, [ft.TextButton("Cancel", on_click=dash.close_dialog), ft.Button("Confirm", bgcolor=ACCENT_BLUE, color="white", on_click=handle_confirm_payment)])
