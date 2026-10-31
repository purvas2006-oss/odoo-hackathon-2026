
from flask import Flask, redirect, url_for

from config import Config
from database.init_db import create_tables

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.products import products_bp
from routes.billing import billing_bp
from routes.plans import plans_bp

app = Flask(__name__)

# Load application configuration
app.config.from_object(Config)

# Secret key for sessions and flash messages
app.secret_key = app.config.get(
    "SECRET_KEY",
    "brightloop_hackathon_2026_secret"
)

# Create database tables
create_tables()

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(products_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(plans_bp)


@app.route("/")
def home():
    return redirect(url_for("billing.billing_reports"))


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
