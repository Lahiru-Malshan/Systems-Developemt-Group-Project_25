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
    if hasattr(dash, "backend"):
        transactions = dash.backend.get_payments()
    else:
        transactions = transactions_data
    dash.content_column.controls.clear()
    
    transactions = sorted(transactions, key=lambda x: x["date"] if isinstance(x, dict) else x[0], reverse=True)
    
    total_outstanding = sum((t["amount"] if isinstance(t, dict) else t[2]) for t in transactions if (t["status"] if isinstance(t, dict) else t[3]) == "Pending")
    last_paid_entry = next((t for t in transactions if (t["status"] if isinstance(t, dict) else t[3]) == "Paid"), None)
    if last_paid_entry:
        amount = last_paid_entry["amount"] if isinstance(last_paid_entry, dict) else last_paid_entry[2]
        date = last_paid_entry["date"] if isinstance(last_paid_entry, dict) else last_paid_entry[0]
        last_paid = f"£{amount:,.2f} ({date})"
    else:
        last_paid = "£0.00"
    
    # 1. Balance Overview (Cards)
    balance_cards = ft.Row(
        spacing=20,
        controls=[
            dash.create_stat_card("Total Outstanding", f"£{total_outstanding:,.2f}", ft.Icons.MONEY_OFF_ROUNDED, highlight=True),
            dash.create_stat_card("Last Paid", last_paid, ft.Icons.CHECK_CIRCLE_ROUNDED),
            dash.create_stat_card("Next Due", "£1,200.00 (Nov 05)", ft.Icons.CALENDAR_MONTH_ROUNDED),
        ]
    )
    
    # 2. Transaction History
    rows = []
    for t in transactions:
        date = t["date"] if isinstance(t, dict) else t[0]
        desc = t["description"] if isinstance(t, dict) else t[1]
        amt = t["amount"] if isinstance(t, dict) else t[2]
        status = t["status"] if isinstance(t, dict) else t[3]
        status_color = ft.Colors.ORANGE_700 if status == "Pending" else ft.Colors.GREEN_700
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(date, color=TEXT_DARK, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(desc, color=TEXT_DARK, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(f"£{amt:,.2f}", weight=ft.FontWeight.BOLD, color=TEXT_DARK)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status, color="white", size=10, weight="bold"),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(vertical=4, horizontal=10),
                            border_radius=15
                        )
                    ),
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
                rows=rows,
            )
        ], scroll=ft.ScrollMode.AUTO)
    )

    # 3. Pay Action
    current_invoice = f"£{total_outstanding:,.2f}" if total_outstanding else "£0.00"
    action_card = ft.Container(
        bgcolor=CARD_BG,
        padding=20,
        border_radius=12,
        width=300,
        content=ft.Column([
            ft.Text("Current Invoice", size=16, weight="bold",color=TEXT_DARK),
            ft.Text(current_invoice, size=28, weight="bold", color=TEXT_DARK),
            ft.Divider(),
            ft.Button(
                "Make a Payment",
                icon=ft.Icons.PAYMENT_ROUNDED,
                bgcolor=ACCENT_BLUE,
                color="white",
                height=50,
                on_click=lambda _: open_payment_modal(dash)
            ),
            ft.Text("* Secured by Paragon Pay", size=10, color=TEXT_MUTED, italic=True)
        ], horizontal_alignment="center")
    )
    
    main_content = ft.Row(
        [history_table, action_card],
        alignment="start",
        vertical_alignment="start",
        spacing=20
    )
    dash.content_column.controls = [balance_cards,main_content]
    dash.page.update()
    
def open_payment_modal(dash):
    ref_amount = ft.TextField(
        label="Enter Amount",
        prefix=ft.Text("£ "),
        value="",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ACCENT_BLUE,
        label_style=ft.TextStyle(weight="bold")
    )
    
    ref_method = ft.Dropdown(
        label="Select Payment Method",
        value="Visa / Mastercard",
        options=[
            ft.dropdown.Option("Visa / Mastercard"),
            ft.dropdown.Option("PayPal"),
            ft.dropdown.Option("Google Pay"),
            ft.dropdown.Option("Apple Pay"),
        ],
        border_color=ACCENT_BLUE,
        label_style=ft.TextStyle(weight="bold")
    )
    def handle_confirm_payment(e):
        try:
            val = float(ref_amount.value)
            if val <= 0:
                raise ValueError
        except ValueError:
            dash.show_message("Invalid Amount! Please enter a valid number (e.g. 250.50)")
            ref_amount.border_color = ft.Colors.RED
            ref_amount.update()
            return
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        success = False
        message = "Payment added"
        if hasattr(dash, "backend"):
            success, message = dash.backend.add_payment(val, ref_method.value, f"Payment via {ref_method.value}")
        if success:
            dash.show_message(f"Success! Paid £{val:,.2f} successfully!")
        else:
            dash.show_message(f"Could not save payment: {message}")
        dash.close_dialog()
        show_payments(dash)

    payment_content = ft.Column([
        ft.Text("Verify payment details before confirming.", size=12, color=TEXT_MUTED),
        ref_amount,
        ref_method,
    ], spacing=15, tight=True, width=400)

    actions = [
        ft.TextButton("Cancel", on_click=dash.close_dialog),
        ft.Button(
            content=ft.Text("CONFIRM PAYMENT", color="white", weight="bold"),
            bgcolor=ACCENT_BLUE,
            on_click=handle_confirm_payment
        ),
    ]

    dash.show_custom_modal("Secure Payment", payment_content, actions)
