
import sqlite3
import os

# Get the project folder location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database file location
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "brightloop.db")


def get_db_connection():
    # Create the instance folder if it does not exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    # Connect to SQLite database
    connection = sqlite3.connect(DATABASE_PATH)

    # Return rows like dictionaries
    connection.row_factory = sqlite3.Row

    return connection
