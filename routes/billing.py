
from flask import Blueprint, render_template, session, redirect, url_for, flash

from models.billing_reports import (
    get_invoice_summary,
    get_payment_summary,
    get_invoice_balances,
    get_overdue_invoices
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

    # Check whether the user is logged in
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    # Allow only Admin and Staff
    user_role = session.get("user_role")

    if user_role not in ["admin", "staff"]:
        flash("You are not authorized to access Billing Reports.", "error")
        return redirect(url_for("dashboard.customer_dashboard"))

    # Fetch report data
    invoice_summary = get_invoice_summary()
    payment_summary = get_payment_summary()
    invoice_balances = get_invoice_balances()
    overdue_invoices = get_overdue_invoices()

    # Display the billing reports page
    return render_template(
        "billing_reports.html",
        invoice_summary=invoice_summary,
        payment_summary=payment_summary,
        invoice_balances=invoice_balances,
        overdue_invoices=overdue_invoices
    )
