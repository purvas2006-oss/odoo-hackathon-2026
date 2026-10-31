from flask import Flask
from database.init_db import create_tables

app = Flask(__name__)
app.secret_key = "brightloop_hackathon_2026_secret"

create_tables()
from flask import Flask, redirect, url_for
from routes.products import products_bp
from routes.billing import billing_bp

app.register_blueprint(products_bp)
app.register_blueprint(billing_bp)
@app.route("/")
def home():
    return redirect(url_for("billing.billing_reports"))

if __name__ == "__main__":
    app.run(debug=True)