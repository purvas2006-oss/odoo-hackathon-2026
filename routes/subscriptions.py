
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


# Display subscriptions and create a new subscription
@subscriptions_bp.route("/subscriptions", methods=["GET", "POST"])
def subscriptions():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        customer_id = request.form.get("customer_id")
        product_id = request.form.get("product_id")
        plan_id = request.form.get("plan_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date") or None
        quantity = request.form.get("quantity")
        status = request.form.get("status", "draft")

        try:
            customer_id = int(customer_id)
            product_id = int(product_id)
            plan_id = int(plan_id)
            quantity = int(quantity)

            if quantity < 1:
                raise ValueError

        except (ValueError, TypeError):
            connection.close()
            flash("Please enter valid customer, product, plan and quantity.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

        if not start_date or status not in VALID_STATUSES:
            connection.close()
            flash("Please enter valid subscription details.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

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

        if not customer or not product or not plan:
            connection.close()
            flash("Selected customer, product or plan does not exist.", "danger")
            return redirect(url_for("subscriptions.subscriptions"))

        if quantity < plan["minimum_quantity"]:
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
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            product_id,
            plan_id,
            start_date,
            end_date,
            quantity,
            status
        ))

        connection.commit()
        connection.close()

        flash("Subscription created successfully!", "success")
        return redirect(url_for("subscriptions.subscriptions"))

    # Fetch registered customers
    customers = cursor.execute("""
        SELECT id, name, email
        FROM users
        WHERE role = 'customer'
        ORDER BY name
    """).fetchall()

    # Fetch products
    products = cursor.execute("""
        SELECT id, name, sales_price
        FROM products
        ORDER BY name
    """).fetchall()

    # Fetch plans
    plans = cursor.execute("""
        SELECT id, name, frequency, price, minimum_quantity,
               start_date, end_date
        FROM plans
        ORDER BY name
    """).fetchall()

    # Fetch subscriptions
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

    subscription = cursor.execute("""
        SELECT * FROM subscriptions WHERE id = ?
    """, (subscription_id,)).fetchone()

    if not subscription:
        connection.close()
        flash("Subscription not found.", "danger")
        return redirect(url_for("subscriptions.subscriptions"))

    if request.method == "POST":

        customer_id = request.form.get("customer_id")
        product_id = request.form.get("product_id")
        plan_id = request.form.get("plan_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date") or None
        quantity = request.form.get("quantity")
        status = request.form.get("status")

        try:
            customer_id = int(customer_id)
            product_id = int(product_id)
            plan_id = int(plan_id)
            quantity = int(quantity)

            if quantity < 1:
                raise ValueError

        except (ValueError, TypeError):
            connection.close()
            flash("Please enter valid subscription details.", "danger")
            return redirect(
                url_for("subscriptions.edit_subscription",
                        subscription_id=subscription_id)
            )

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

        if (
            not customer or not product or not plan
            or not start_date or status not in VALID_STATUSES
            or quantity < plan["minimum_quantity"]
            or (end_date and end_date < start_date)
            or (plan["start_date"] and start_date < plan["start_date"])
            or (plan["end_date"] and start_date > plan["end_date"])
        ):
            connection.close()
            flash("Please check the subscription details and try again.", "danger")
            return redirect(
                url_for("subscriptions.edit_subscription",
                        subscription_id=subscription_id)
            )

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
            status,
            subscription_id
        ))

        connection.commit()
        connection.close()

        flash("Subscription updated successfully!", "success")
        return redirect(url_for("subscriptions.subscriptions"))

    customers = cursor.execute("""
        SELECT id, name, email FROM users
        WHERE role = 'customer' ORDER BY name
    """).fetchall()

    products = cursor.execute("""
        SELECT id, name, sales_price FROM products ORDER BY name
    """).fetchall()

    plans = cursor.execute("""
        SELECT id, name, frequency, price, minimum_quantity,
               start_date, end_date
        FROM plans ORDER BY name
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

    # Do not delete subscriptions that already have invoices
    invoice = cursor.execute("""
        SELECT id FROM invoices WHERE subscription_id = ?
    """, (subscription_id,)).fetchone()

    if invoice:
        connection.close()
        flash("Cannot delete a subscription that has invoices.", "danger")
        return redirect(url_for("subscriptions.subscriptions"))

    cursor.execute("""
        DELETE FROM subscriptions WHERE id = ?
    """, (subscription_id,))

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    if deleted:
        flash("Subscription deleted successfully!", "success")
    else:
        flash("Subscription not found.", "danger")

    return redirect(url_for("subscriptions.subscriptions"))
