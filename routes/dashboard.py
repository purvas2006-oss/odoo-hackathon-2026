
from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps

dashboard_bp = Blueprint("dashboard", __name__)


# Check whether user is logged in
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("auth.login"))

        return function(*args, **kwargs)

    return wrapper


# Check user role
def role_required(*allowed_roles):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:
                flash("Please login first.", "error")
                return redirect(url_for("auth.login"))

            if session.get("user_role") not in allowed_roles:
                flash("You are not authorized to access this page.", "error")
                return redirect(url_for("home"))

            return function(*args, **kwargs)

        return wrapper
    return decorator


# Admin Dashboard
@dashboard_bp.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    return render_template(
        "dashboard.html",
        page_title="Admin Dashboard",
        dashboard_message="Welcome to the Admin Dashboard!"
    )


# Staff Dashboard
@dashboard_bp.route("/staff")
@login_required
@role_required("staff", "admin")
def staff_dashboard():
    return render_template(
        "dashboard.html",
        page_title="Staff Dashboard",
        dashboard_message="Welcome to the Staff Dashboard!"
    )


# Customer Dashboard
@dashboard_bp.route("/customer")
@login_required
@role_required("customer")
def customer_dashboard():
    return render_template(
        "dashboard.html",
        page_title="Customer Portal",
        dashboard_message="Welcome to your Customer Portal!"
    )
