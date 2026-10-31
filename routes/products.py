
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection
from routes.dashboard import login_required, role_required

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET", "POST"])
@login_required
@role_required("admin")
def products():

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        name = request.form["name"]
        product_type = request.form["product_type"]
        sales_price = request.form["sales_price"]
        cost_price = request.form["cost_price"]
        notes = request.form["notes"]

        cursor.execute("""
            INSERT INTO products
            (name, product_type, sales_price, cost_price, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (name, product_type, sales_price, cost_price, notes))

        connection.commit()
        connection.close()

        flash("Product added successfully!")
        return redirect(url_for("products.products"))

    cursor.execute("SELECT * FROM products ORDER BY id DESC")
    all_products = cursor.fetchall()

    connection.close()

    return render_template("products.html", products=all_products)
