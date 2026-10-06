"""
auth_routes.py - User registration and login.

POST /api/auth/register   -> create a new user
POST /api/auth/login      -> check email + password
GET  /api/auth/users      -> list all users
GET  /api/auth/users/<id> -> get one user
"""
import re
from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash

import models
from utils.helpers import success_response, error_response

auth_bp = Blueprint("auth", __name__)

EMAIL_PATTERN = re.compile(r"^[\w\.\-+]+@[\w\-]+\.[\w\.\-]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON")

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    # ---- validation ----
    if not name or not email or not password:
        return error_response("name, email and password are required")
    if not EMAIL_PATTERN.match(email):
        return error_response("Invalid email format")
    if len(password) < 6:
        return error_response("Password must be at least 6 characters")
    if models.get_user_by_email(email):
        return error_response("Email is already registered", 409)

    # Never store the real password - store a hash
    user_id = models.create_user(name, email, generate_password_hash(password))
    return success_response(
        "User registered successfully",
        {"id": user_id, "name": name, "email": email},
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON")

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not email or not password:
        return error_response("email and password are required")

    user = models.get_user_by_email(email)
    if not user or not check_password_hash(user["password"], password):
        return error_response("Invalid email or password", 401)

    return success_response(
        "Login successful",
        {"id": user["id"], "name": user["name"], "email": user["email"]},
    )


@auth_bp.route("/users", methods=["GET"])
def list_users():
    return success_response("Users fetched", models.get_all_users())


@auth_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = models.get_user_by_id(user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response("User fetched", user)
