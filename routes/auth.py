
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)

from models.user import (
    create_user,
    get_user_by_email,
    verify_password
)

import re

# Create Authentication Blueprint
auth_bp = Blueprint("auth", __name__)


# Password validation
def validate_password(password):

    if len(password) <= 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[^A-Za-z0-9]", password):
        return False

    return True


# Registration route
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("auth.register"))

        if not validate_password(password):
            flash(
                "Password must be longer than 8 characters "
                "and contain uppercase, lowercase and special characters.",
                "error"
            )
            return redirect(url_for("auth.register"))

        if get_user_by_email(email):
            flash("Email already registered.", "error")
            return redirect(url_for("auth.register"))

        success = create_user(name, email, password, "customer")

        if success:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        flash("Registration failed. Please try again.", "error")

    return render_template("register.html")


# Login route
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)

        if user and verify_password(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]

            flash("Login successful!", "success")

            if user["role"] == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))

            elif user["role"] == "staff":
                return redirect(url_for("dashboard.staff_dashboard"))

            else:
                return redirect(url_for("dashboard.customer_dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# Logout route
@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("auth.login"))

