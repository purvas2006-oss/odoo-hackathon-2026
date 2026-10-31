
from flask import Flask
from database.db import get_db_connection

app = Flask(__name__)

@app.route("/")
def home():
    # Test database connection
    connection = get_db_connection()
    connection.execute("SELECT 1")
    connection.close()

    return """
    <h1>Brightloop Subscription Management System</h1>
    <p>Flask is running successfully!</p>
    <p>SQLite database connected successfully!</p>
    """

if __name__ == "__main__":
    app.run(debug=True)
