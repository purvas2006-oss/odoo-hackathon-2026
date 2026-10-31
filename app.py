from flask import Flask
from database.init_db import create_tables

app = Flask(__name__)

app.secret_key = "brightloop_hackathon_2026_secret"

create_tables()

@app.route("/")
def home():
    return "Brightloop Subscription Management System is Running!"

from routes.products import products_bp

app.register_blueprint(products_bp)

if __name__ == "__main__":
    app.run(debug=True)