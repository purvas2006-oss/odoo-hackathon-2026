
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection

plans_bp = Blueprint("plans", __name__)

VALID_FREQUENCIES = ["Daily", "Weekly", "Monthly", "Yearly"]


# Display plans and add a new plan
@plans_bp.route("/plans", methods=["GET", "POST"])
def plans():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        frequency = request.form.get("frequency", "")
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None

        try:
            price = float(request.form.get("price", ""))
            minimum_quantity = int(request.form.get("minimum_quantity", ""))

            if price < 0 or minimum_quantity < 1:
                raise ValueError

        except (ValueError, TypeError):
            connection.close()
            flash("Enter a valid price and minimum quantity.", "danger")
            return redirect(url_for("plans.plans"))

        if not name or frequency not in VALID_FREQUENCIES:
            connection.close()
            flash("Please enter a valid plan name and frequency.", "danger")
            return redirect(url_for("plans.plans"))

        if start_date and end_date and end_date < start_date:
            connection.close()
            flash("End date cannot be before start date.", "danger")
            return redirect(url_for("plans.plans"))

        cursor.execute("""
            INSERT INTO plans
            (name, frequency, price, minimum_quantity, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            frequency,
            price,
            minimum_quantity,
            start_date,
            end_date
        ))

        connection.commit()
        connection.close()

        flash("Plan added successfully!", "success")
        return redirect(url_for("plans.plans"))

    cursor.execute("""
        SELECT * FROM plans
        ORDER BY id DESC
    """)

    all_plans = cursor.fetchall()

    connection.close()

    return render_template("plans.html", plans=all_plans)


# Edit an existing plan
@plans_bp.route("/plans/<int:plan_id>/edit", methods=["GET", "POST"])
def edit_plan(plan_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM plans WHERE id = ?",
        (plan_id,)
    )

    plan = cursor.fetchone()

    if plan is None:
        connection.close()
        flash("Plan not found.", "danger")
        return redirect(url_for("plans.plans"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        frequency = request.form.get("frequency", "")
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None

        try:
            price = float(request.form.get("price", ""))
            minimum_quantity = int(request.form.get("minimum_quantity", ""))

            if price < 0 or minimum_quantity < 1:
                raise ValueError

        except (ValueError, TypeError):
            connection.close()
            flash("Enter a valid price and minimum quantity.", "danger")
            return redirect(
                url_for("plans.edit_plan", plan_id=plan_id)
            )

        if not name or frequency not in VALID_FREQUENCIES:
            connection.close()
            flash("Please enter a valid plan name and frequency.", "danger")
            return redirect(
                url_for("plans.edit_plan", plan_id=plan_id)
            )

        if start_date and end_date and end_date < start_date:
            connection.close()
            flash("End date cannot be before start date.", "danger")
            return redirect(
                url_for("plans.edit_plan", plan_id=plan_id)
            )

        cursor.execute("""
            UPDATE plans
            SET name = ?,
                frequency = ?,
                price = ?,
                minimum_quantity = ?,
                start_date = ?,
                end_date = ?
            WHERE id = ?
        """, (
            name,
            frequency,
            price,
            minimum_quantity,
            start_date,
            end_date,
            plan_id
        ))

        connection.commit()
        connection.close()

        flash("Plan updated successfully!", "success")
        return redirect(url_for("plans.plans"))

    connection.close()

    return render_template("edit_plan.html", plan=plan)


# Delete a plan if it is not being used by a subscription
@plans_bp.route("/plans/<int:plan_id>/delete", methods=["POST"])
def delete_plan(plan_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM plans WHERE id = ?",
        (plan_id,)
    )

    plan = cursor.fetchone()

    if plan is None:
        connection.close()
        flash("Plan not found.", "danger")
        return redirect(url_for("plans.plans"))

    cursor.execute(
        "SELECT COUNT(*) AS total FROM subscriptions WHERE plan_id = ?",
        (plan_id,)
    )

    subscription_count = cursor.fetchone()["total"]

    if subscription_count > 0:
        connection.close()
        flash(
            "This plan cannot be deleted because subscriptions are linked to it.",
            "warning"
        )
        return redirect(url_for("plans.plans"))

    cursor.execute(
        "DELETE FROM plans WHERE id = ?",
        (plan_id,)
    )

    connection.commit()
    connection.close()

    flash("Plan deleted successfully!", "success")
    return redirect(url_for("plans.plans"))
