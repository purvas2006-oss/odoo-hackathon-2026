
from database.db import get_db_connection


def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'staff', 'customer')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            product_type TEXT,
            sales_price REAL NOT NULL,
            cost_price REAL DEFAULT 0,
            notes TEXT
        )
    """)

    # 3. Product variants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            variant_name TEXT NOT NULL,
            additional_price REAL DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    # 4. Plans table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            frequency TEXT NOT NULL,
            price REAL NOT NULL,
            minimum_quantity INTEGER DEFAULT 1,
            start_date DATE,
            end_date DATE
        )
    """)

    # 5. Subscriptions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'draft',
            FOREIGN KEY (customer_id) REFERENCES users(id),
            FOREIGN KEY (plan_id) REFERENCES plans(id)
        )
    """)

    # 6. Invoices table
    
    # 6. Invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subscription_id INTEGER NOT NULL,
            invoice_number TEXT NOT NULL UNIQUE,
            customer_id INTEGER,
            invoice_date DATE NOT NULL,
            due_date DATE,
            subtotal REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            tax REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'draft',
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(id),
            FOREIGN KEY (customer_id) REFERENCES users(id)
        )
    """)

    # Add missing invoice columns to existing databases
    existing_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(invoices)").fetchall()
    }

    migrations = {
        "customer_id": "INTEGER REFERENCES users(id)",
        "subtotal": "REAL DEFAULT 0",
        "discount": "REAL DEFAULT 0",
        "tax": "REAL DEFAULT 0"
    }

    for column, definition in migrations.items():
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE invoices ADD COLUMN {column} {definition}"
            )
    # 7. Payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT,
            payment_date DATE,
            note TEXT,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    """)

    # 8. Discounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            discount_type TEXT NOT NULL,
            discount_value REAL NOT NULL,
            minimum_quantity INTEGER DEFAULT 1,
            start_date DATE,
            end_date DATE,
            usage_limit INTEGER,
            is_active INTEGER DEFAULT 1
        )
    """)

    connection.commit()
    connection.close()

    print("All database tables created successfully!")


if __name__ == "__main__":
    create_tables()
