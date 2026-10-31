
from database.db import get_db_connection


# 1. Get invoice summary
def get_invoice_summary():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_invoices,
                COALESCE(SUM(total_amount), 0) AS total_billed
            FROM invoices
        """)

        summary = cursor.fetchone()

        cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM invoices
            GROUP BY status
        """)

        status_summary = cursor.fetchall()

        return {
            "total_invoices": summary["total_invoices"],
            "total_billed": summary["total_billed"],
            "status_summary": [
                dict(row) for row in status_summary
            ]
        }

    finally:
        connection.close()


# 2. Get payment summary
def get_payment_summary():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_payments,
                COALESCE(SUM(amount), 0) AS total_received
            FROM payments
        """)

        return dict(cursor.fetchone())

    finally:
        connection.close()


# 3. Get invoice-wise outstanding balances
def get_invoice_balances():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                i.id,
                i.invoice_number,
                i.customer_id,
                i.invoice_date,
                i.due_date,
                i.total_amount,
                i.status,
                COALESCE(SUM(p.amount), 0) AS paid_amount,
                MAX(
                    i.total_amount - COALESCE(
                        (
                            SELECT SUM(p2.amount)
                            FROM payments p2
                            WHERE p2.invoice_id = i.id
                        ), 0
                    ), 0
                ) AS outstanding_amount

            FROM invoices i

            LEFT JOIN payments p
                ON i.id = p.invoice_id

            GROUP BY i.id

            ORDER BY i.invoice_date DESC
        """)

        return [
            dict(row) for row in cursor.fetchall()
        ]

    finally:
        connection.close()
