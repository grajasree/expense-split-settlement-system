"""
app.py - Main file. Run this file to start the backend.

    python app.py
"""
from flask import Flask
from flask_cors import CORS
from mysql.connector import Error as MySQLError
from werkzeug.exceptions import HTTPException

from config import Config
from database import get_connection
from routes.auth_routes import auth_bp
from routes.group_routes import group_bp
from routes.expense_routes import expense_bp
from routes.settlement_routes import settlement_bp
from utils.helpers import success_response, error_response

app = Flask(__name__)
CORS(app)  # allows a frontend on another port to call this API

# ---- register all route files (blueprints) ----
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(group_bp, url_prefix="/api/groups")
app.register_blueprint(expense_bp, url_prefix="/api/expenses")
app.register_blueprint(settlement_bp, url_prefix="/api/settlements")


@app.route("/")
def home():
    return success_response("Expense Split and Settlement System API is running")


@app.route("/api/health")
def health():
    """Checks that MySQL is reachable."""
    conn = get_connection()
    conn.close()
    return success_response("Server and database connection are OK")


# ---- global error handlers ----
@app.errorhandler(HTTPException)
def handle_http_error(error):
    # 404 Not Found, 405 Method Not Allowed, etc.
    return error_response(error.description, error.code)


@app.errorhandler(MySQLError)
def handle_database_error(error):
    print("Database error:", error)
    return error_response(f"Database error: {error.msg}", 500)


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    print("Unexpected error:", error)
    return error_response("Something went wrong on the server", 500)


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)
