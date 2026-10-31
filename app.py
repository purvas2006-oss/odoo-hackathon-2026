from flask import Flask
from config import Config
from database.db import get_db_connection

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)

app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")


@app.route("/")
def home():
    connection = get_db_connection()
    connection.execute("SELECT 1")
    connection.close()

    return """
    <h1>Brightloop Subscription Management System</h1>
    <p>Flask is running successfully!</p>
    <p>SQLite database connected successfully!</p>
    <p>Configuration loaded successfully!</p>
    """

print(app.url_map)
if __name__ == "__main__":
    app.run(debug=True)