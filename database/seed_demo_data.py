
from database.db import get_db_connection
from werkzeug.security import generate_password_hash
from datetime import date, timedelta


def seed_demo_data():

    connection = get_db_connection()
    cursor = connection.cursor()

    today = date.today()

    # ---------------------------------
    # 1. Create demo customers
    # ---------------------------------

    customers = [
        ("Demo Customer 1", "demo1@example.com"),
        ("Demo Customer 2", "demo2@example.com"),
        ("Demo Customer 3", "demo3@example.com"),
    ]

    customer_ids = []

    for name, email in customers:

        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )

        customer = cursor.fetchone()

        if customer:
            customer_ids.append(customer["id"])
        else:
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, 'customer')
            """, (
                name,
                email,
                generate_password_hash("Demo@123")
            ))

            customer_ids.append(cursor.lastrowid)

    # ---------------------------------
    # 2. Create demo products
    # ---------------------------------

    products = [
        ("Demo Software Basic", "Service", 1000, 600),
        ("Demo Software Pro", "Service", 2000, 1200),
        ("Demo Software Premium", "Service", 3000, 1800),
    ]

    product_ids = []

    for name, product_type, sales_price, cost_price in products:

        cursor.execute(
            "SELECT id FROM products WHERE name = ?",
            (name,)
        )

        product = cursor.fetchone()

        if product:
            product_ids.append(product["id"])
        else:
            cursor.execute("""
                INSERT INTO products
                (name, product_type, sales_price, cost_price)
                VALUES (?, ?, ?, ?)
            """, (name, product_type, sales_price, cost_price))

            product_ids.append(cursor.lastrowid)

    # ---------------------------------
    # 3. Create demo plans
    # ---------------------------------

    cursor.execute(
        "SELECT id FROM plans WHERE name = ?",
        ("Demo Monthly Plan",)
    )

    plan = cursor.fetchone()

    if plan:
        plan_id = plan["id"]
    else:
        cursor.execute("""
            INSERT INTO plans
            (name, frequency, price, minimum_quantity,
             start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Demo Monthly Plan",
            "Monthly",
            1000,
            1,
            (today - timedelta(days=120)).isoformat(),
            (today + timedelta(days=365)).isoformat()
        ))

        plan_id = cursor.lastrowid

    # ---------------------------------
    # 4. Create demo subscriptions
    # ---------------------------------

    subscription_ids = []

    for customer_id in customer_ids:

        cursor.execute("""
            SELECT id FROM subscriptions
            WHERE customer_id = ? AND plan_id = ?
            LIMIT 1
        """, (customer_id, plan_id))

        subscription = cursor.fetchone()

        if subscription:
            subscription_ids.append(subscription["id"])
        else:
            cursor.execute("""
                INSERT INTO subscriptions
                (customer_id, plan_id, start_date, end_date,
                 quantity, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                customer_id,
                plan_id,
                (today - timedelta(days=90)).isoformat(),
                (today + timedelta(days=270)).isoformat(),
                1,
                "Active"
            ))

            subscription_ids.append(cursor.lastrowid)

    # ---------------------------------
    # 5. Create different invoice cases
    # ---------------------------------

    invoice_scenarios = [
        {
            "number": "DEMO-INV-001",
            "customer": 0,
            "subscription": 0,
            "days_ago": 5,
            "due_days": 25,
            "subtotal": 2000,
            "discount": 100,
            "tax": 342,
            "total": 2242,
            "payments": [2242],
            "status": "Paid"
        },
        {
            "number": "DEMO-INV-002",
            "customer": 1,
            "subscription": 1,
            "days_ago": 15,
            "due_days": 15,
            "subtotal": 3000,
            "discount": 300,
            "tax": 486,
            "total": 3186,
            "payments": [1500, 500],
            "status": "Confirmed"
        },
        {
            "number": "DEMO-INV-003",
            "customer": 2,
            "subscription": 2,
            "days_ago": 40,
            "due_days": -10,
            "subtotal": 1500,
            "discount": 0,
            "tax": 270,
            "total": 1770,
            "payments": [],
            "status": "Confirmed"
        },
        {
            "number": "DEMO-INV-004",
            "customer": 0,
            "subscription": 0,
            "days_ago": 65,
            "due_days": -35,
            "subtotal": 2500,
            "discount": 250,
            "tax": 405,
            "total": 2655,
            "payments": [],
            "status": "Confirmed"
        },
        {
            "number": "DEMO-INV-005",
            "customer": 1,
            "subscription": 1,
            "days_ago": 95,
            "due_days": -65,
            "subtotal": 1000,
            "discount": 50,
            "tax": 171,
            "total": 1121,
            "payments": [1121],
            "status": "Paid"
        },
        {
            "number": "DEMO-INV-006",
            "customer": 2,
            "subscription": 2,
            "days_ago": 2,
            "due_days": 28,
            "subtotal": 4000,
            "discount": 500,
            "tax": 630,
            "total": 4130,
            "payments": [],
            "status": "Draft"
        }
    ]

    for invoice in invoice_scenarios:

        cursor.execute(
            "SELECT id FROM invoices WHERE invoice_number = ?",
            (invoice["number"],)
        )

        if cursor.fetchone():
            continue

        invoice_date = today - timedelta(days=invoice["days_ago"])
        due_date = today + timedelta(days=invoice["due_days"])

        cursor.execute("""
            INSERT INTO invoices
            (subscription_id, invoice_number, customer_id,
             invoice_date, due_date, subtotal, discount,
             tax, total_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subscription_ids[invoice["subscription"]],
            invoice["number"],
            customer_ids[invoice["customer"]],
            invoice_date.isoformat(),
            due_date.isoformat(),
            invoice["subtotal"],
            invoice["discount"],
            invoice["tax"],
            invoice["total"],
            invoice["status"]
        ))

        invoice_id = cursor.lastrowid

        # ---------------------------------
        # 6. Add payments
        # ---------------------------------

        for index, amount in enumerate(invoice["payments"]):

            cursor.execute("""
                INSERT INTO payments
                (invoice_id, amount, payment_method,
                 payment_date, note)
                VALUES (?, ?, ?, ?, ?)
            """, (
                invoice_id,
                amount,
                "UPI",
                (invoice_date + timedelta(days=index + 2)).isoformat(),
                "Demo payment"
            ))

    connection.commit()
    connection.close()

    print("Demo data inserted successfully!")


if __name__ == "__main__":
    seed_demo_data()
