
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_db_connection

products_bp = Blueprint("products", __name__)


# Product Management: Add and Display Products
@products_bp.route("/products", methods=["GET", "POST"])
def products():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Add new product
    if request.method == "POST":

        name = request.form["name"].strip()
        product_type = request.form["product_type"]
        sales_price = request.form["sales_price"]
        cost_price = request.form["cost_price"]
        notes = request.form.get("notes", "").strip()

        try:
            sales_price = float(sales_price)
            cost_price = float(cost_price)

            if sales_price < 0 or cost_price < 0:
                raise ValueError

        except ValueError:
            connection.close()
            flash("Please enter valid non-negative prices.", "danger")
            return redirect(url_for("products.products"))

        if not name:
            connection.close()
            flash("Product name is required.", "danger")
            return redirect(url_for("products.products"))

        cursor.execute("""
            INSERT INTO products
            (name, product_type, sales_price, cost_price, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (name, product_type, sales_price, cost_price, notes))

        connection.commit()
        connection.close()

        flash("Product added successfully!", "success")
        return redirect(url_for("products.products"))

    # Fetch all products
    cursor.execute("""
        SELECT * FROM products
        ORDER BY id DESC
    """)

    all_products = cursor.fetchall()

    # Fetch all product variants
    cursor.execute("""
        SELECT * FROM product_variants
        ORDER BY id DESC
    """)

    all_variants = cursor.fetchall()

    connection.close()

    # Group variants by product ID
    variants_by_product = {}

    for variant in all_variants:
        product_id = variant["product_id"]

        if product_id not in variants_by_product:
            variants_by_product[product_id] = []

        variants_by_product[product_id].append(variant)

    return render_template(
        "products.html",
        products=all_products,
        variants_by_product=variants_by_product
    )


# Edit Product
@products_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    # Find product
    cursor.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()
        flash("Product not found.", "danger")
        return redirect(url_for("products.products"))

    # Update product
    if request.method == "POST":

        name = request.form["name"].strip()
        product_type = request.form["product_type"]
        notes = request.form.get("notes", "").strip()

        try:
            sales_price = float(request.form["sales_price"])
            cost_price = float(request.form["cost_price"])

            if sales_price < 0 or cost_price < 0:
                raise ValueError

        except ValueError:
            connection.close()
            flash("Please enter valid non-negative prices.", "danger")
            return redirect(
                url_for("products.edit_product", product_id=product_id)
            )

        if not name or product_type not in ["Goods", "Service"]:
            connection.close()
            flash("Please enter valid product details.", "danger")
            return redirect(
                url_for("products.edit_product", product_id=product_id)
            )

        cursor.execute("""
            UPDATE products
            SET name = ?,
                product_type = ?,
                sales_price = ?,
                cost_price = ?,
                notes = ?
            WHERE id = ?
        """, (
            name,
            product_type,
            sales_price,
            cost_price,
            notes,
            product_id
        ))

        connection.commit()
        connection.close()

        flash("Product updated successfully!", "success")
        return redirect(url_for("products.products"))

    connection.close()

    return render_template(
        "edit_product.html",
        product=product
    )


# Add Product Variant
@products_bp.route("/products/<int:product_id>/variants", methods=["POST"])
def add_variant(product_id):

    variant_name = request.form["variant_name"].strip()
    additional_price = request.form["additional_price"]

    if not variant_name or not additional_price:
        flash("Please enter all variant details.", "danger")
        return redirect(url_for("products.products"))

    try:
        additional_price = float(additional_price)

        if additional_price < 0:
            raise ValueError

    except ValueError:
        flash("Please enter a valid non-negative additional price.", "danger")
        return redirect(url_for("products.products"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM products WHERE id = ?",
        (product_id,)
    )

    product = cursor.fetchone()

    if product is None:
        connection.close()
        flash("Product not found.", "danger")
        return redirect(url_for("products.products"))

    cursor.execute("""
        INSERT INTO product_variants
        (product_id, variant_name, additional_price)
        VALUES (?, ?, ?)
    """, (product_id, variant_name, additional_price))

    connection.commit()
    connection.close()

    flash("Product variant added successfully!", "success")
    return redirect(url_for("products.products"))


# Delete Product Variant
@products_bp.route(
    "/products/<int:product_id>/variants/<int:variant_id>/delete",
    methods=["POST"]
)
def delete_variant(product_id, variant_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM product_variants
        WHERE id = ? AND product_id = ?
    """, (variant_id, product_id))

    deleted_count = cursor.rowcount

    connection.commit()
    connection.close()

    if deleted_count:
        flash("Product variant deleted successfully!", "success")
    else:
        flash("Variant not found.", "danger")

    return redirect(url_for("products.products"))
