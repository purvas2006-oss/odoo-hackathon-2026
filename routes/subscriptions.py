
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection

subscriptions_bp = Blueprint("subscriptions", __name__)

VALID_STATUSES = [
    "draft",
    "quotation",
    "confirmed",
    "active",
    "closed"
]


def valid_status_change(old_status, new_status):
    return new_status in VALID_STATUSES


# Display subscriptions and create a new subscription
@subscriptions_bp.route("/subscriptions", methods=["GET", "POST"])
def subscriptions():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        try:
            customer_id = int(request.form.get("customer_id"))
            product_id = int(request.form.get("product_id"))
            plan_id = int(request.form.get("plan_id"))
            quantity = int(request.form.get("quantity"))
        except (ValueError, TypeError):
            connection.close()
            flash("Please enter valid subscription details.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date") or None

        customer = cursor.execute(
            "SELECT id FROM users WHERE id = ? AND role = 'customer'",
            (customer_id,)
        ).fetchone()

        product = cursor.execute(
            "SELECT id FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        plan = cursor.execute(
            "SELECT * FROM plans WHERE id = ?",
            (plan_id,)
        ).fetchone()

        if not customer or not product or not plan or not start_date:
            connection.close()
            flash("Please select valid customer, product, plan and start date.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

        if quantity < 1 or quantity < plan["minimum_quantity"]:
            connection.close()
            flash(
                f"Minimum quantity for this plan is {plan['minimum_quantity']}.",
                "danger"
            )
            return redirect(url_for("subscriptions.subscriptions"))

        if plan["start_date"] and start_date < plan["start_date"]:
            connection.close()
            flash("Subscription starts before the plan becomes available.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

        if plan["end_date"] and start_date > plan["end_date"]:
            connection.close()
            flash("This plan is no longer available on the selected date.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

        if end_date and end_date < start_date:
            connection.close()
            flash("End date cannot be before start date.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

        cursor.execute("""
            INSERT INTO subscriptions
            (customer_id, product_id, plan_id, start_date, end_date, quantity, status)
            VALUES (?, ?, ?, ?, ?, ?, 'draft')
        """, (
            customer_id,
            product_id,
            plan_id,
            start_date,
            end_date,
            quantity
        ))

        connection.commit()
        connection.close()

        flash("Subscription created successfully with Draft status!", "success")
        return redirect(url_for("subscriptions.subscriptions"))

    customers = cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE role = 'customer'
        ORDER BY name
    """).fetchall()

    products = cursor.execute("""
        SELECT id, name, sales_price
        FROM products
        ORDER BY name
    """).fetchall()

    plans = cursor.execute("""
        SELECT id, name, frequency, price, minimum_quantity,
               start_date, end_date
        FROM plans
        ORDER BY name
    """).fetchall()

    all_subscriptions = cursor.execute("""
        SELECT
            s.*,
            u.name AS customer_name,
            p.name AS product_name,
            pl.name AS plan_name,
            pl.frequency AS frequency,
            pl.price AS plan_price
        FROM subscriptions s
        JOIN users u ON s.customer_id = u.id
        LEFT JOIN products p ON s.product_id = p.id
        JOIN plans pl ON s.plan_id = pl.id
        ORDER BY s.id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "subscriptions.html",
        customers=customers,
        products=products,
        plans=plans,
        subscriptions=all_subscriptions
    )


# Edit subscription
@subscriptions_bp.route(
    "/subscriptions/<int:subscription_id>/edit",
    methods=["GET", "POST"]
)
def edit_subscription(subscription_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    subscription = cursor.execute(
        "SELECT * FROM subscriptions WHERE id = ?",
        (subscription_id,)
    ).fetchone()

    if not subscription:
        connection.close()
        flash("Subscription not found.", "danger")
        return redirect(url_for("subscriptions.subscriptions"))

    if request.method == "POST":

        try:
            customer_id = int(request.form.get("customer_id"))
            product_id = int(request.form.get("product_id"))
            plan_id = int(request.form.get("plan_id"))
            quantity = int(request.form.get("quantity"))
        except (ValueError, TypeError):
            connection.close()
            flash("Please enter valid subscription details.", "danger")
            return redirect(url_for(
                "subscriptions.edit_subscription",
                subscription_id=subscription_id
            ))

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date") or None
        new_status = (request.form.get("status") or "").lower()

        customer = cursor.execute(
            "SELECT id FROM users WHERE id = ? AND role = 'customer'",
            (customer_id,)
        ).fetchone()

        product = cursor.execute(
            "SELECT id FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        plan = cursor.execute(
            "SELECT * FROM plans WHERE id = ?",
            (plan_id,)
        ).fetchone()

        if not customer:
            error = "Selected customer does not exist."

        elif not product:
            error = "Selected product does not exist."

        elif not plan:
            error = "Selected plan does not exist."

        elif not start_date:
            error = "Start date is missing."

        elif not valid_status_change(subscription["status"], new_status):
            error = "Invalid subscription status."

        elif quantity < 1 or quantity < plan["minimum_quantity"]:
            error = f"Minimum quantity for this plan is {plan['minimum_quantity']}."

        elif end_date and end_date < start_date:
            error = "End date cannot be before start date."

        elif (
            (plan_id != subscription["plan_id"]
             or start_date != subscription["start_date"])
            and (
                (plan["start_date"] and start_date < plan["start_date"])
                or (plan["end_date"] and start_date > plan["end_date"])
            )
        ):
            error = "Selected plan is unavailable on this date."

        else:
            error = None

        if error:
            connection.close()
            flash(error, "danger")
            return redirect(url_for(
                "subscriptions.edit_subscription",
                subscription_id=subscription_id
            ))

        cursor.execute("""
            UPDATE subscriptions
            SET customer_id = ?,
                product_id = ?,
                plan_id = ?,
                start_date = ?,
                end_date = ?,
                quantity = ?,
                status = ?
            WHERE id = ?
        """, (
            customer_id,
            product_id,
            plan_id,
            start_date,
            end_date,
            quantity,
            new_status,
            subscription_id
        ))

        connection.commit()
        connection.close()

        flash("Subscription updated successfully!", "success")
        return redirect(url_for("subscriptions.subscriptions"))

    customers = cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE role = 'customer'
        ORDER BY name
    """).fetchall()

    products = cursor.execute("""
        SELECT id, name, sales_price
        FROM products
        ORDER BY name
    """).fetchall()

    plans = cursor.execute("""
        SELECT id, name, frequency, price, minimum_quantity,
               start_date, end_date
        FROM plans
        ORDER BY name
    """).fetchall()

    connection.close()

    return render_template(
        "edit_subscription.html",
        subscription=subscription,
        customers=customers,
        products=products,
        plans=plans,
        statuses=VALID_STATUSES
    )


# Delete subscription
@subscriptions_bp.route(
    "/subscriptions/<int:subscription_id>/delete",
    methods=["POST"]
)
def delete_subscription(subscription_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    invoice = cursor.execute("""
        SELECT id FROM invoices WHERE subscription_id = ?
    """, (subscription_id,)).fetchone()

    if invoice:
        connection.close()
        flash("Cannot delete a subscription that has invoices.", "danger")
        return redirect(url_for("subscriptions.subscriptions"))

    cursor.execute(
        "DELETE FROM subscriptions WHERE id = ?",
        (subscription_id,)
    )

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    if deleted:
        flash("Subscription deleted successfully!", "success")
    else:
        flash("Subscription not found.", "danger")

    return redirect(url_for("subscriptions.subscriptions"))
