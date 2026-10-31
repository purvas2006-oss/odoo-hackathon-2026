
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection
import sqlite3


def create_user(name, email, password, role="customer"):
    connection = get_db_connection()

    try:
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        connection.execute(
            """
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, hashed_password, role)
        )

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_user_by_email(email):
    connection = get_db_connection()

    try:
        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        return user

    finally:
        connection.close()


def verify_password(stored_password, entered_password):
    return check_password_hash(stored_password, entered_password)
