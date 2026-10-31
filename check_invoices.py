
from database.db import get_db_connection

connection = get_db_connection()

cursor = connection.cursor()

cursor.execute("""
    SELECT invoice_number, total_amount, status, due_date
    FROM invoices
    WHERE invoice_number LIKE 'DEMO-INV-%'
    ORDER BY invoice_number
""")

invoices = cursor.fetchall()

for invoice in invoices:
    print(dict(invoice))

connection.close()
