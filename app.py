from flask import Flask, redirect, url_for

from config import Config
from database.init_db import create_tables

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.products import products_bp
from routes.billing import billing_bp


# Create Flask Application
app = Flask(__name__)

# Load Configuration
app.config.from_object(Config)

# Create Database Tables
create_tables()


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(products_bp)
app.register_blueprint(billing_bp)


# Home Route
@app.route("/")
def home():
    return redirect(url_for("auth.login"))


# Run Application
if __name__ == "__main__":
    app.run(debug=True)