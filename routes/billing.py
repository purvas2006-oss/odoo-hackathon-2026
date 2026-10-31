
from flask import Blueprint, render_template

from models.billing_reports import (
    get_invoice_summary,
    get_payment_summary,
    get_invoice_balances
)

# Create Billing Blueprint
billing_bp = Blueprint(
    "billing",
    __name__,
    url_prefix="/billing"
)


# Billing Reports Dashboard
@billing_bp.route("/")
def billing_reports():

    # Fetch report data
    invoice_summary = get_invoice_summary()
    payment_summary = get_payment_summary()
    invoice_balances = get_invoice_balances()

    # Display the billing reports page
    return render_template(
        "billing_reports.html",
        invoice_summary=invoice_summary,
        payment_summary=payment_summary,
        invoice_balances=invoice_balances
    )
