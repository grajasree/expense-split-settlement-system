"""
helpers.py - Small helpers to keep every API response in the same JSON format.

Success:  {"success": true,  "message": "...", "data": ...}
Error:    {"success": false, "message": "..."}
"""
from datetime import date, datetime
from decimal import Decimal
from flask import jsonify


def make_json_safe(obj):
    """Convert Decimal -> float and date -> string so Flask can return JSON."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {key: make_json_safe(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_json_safe(item) for item in obj]
    return obj


def success_response(message, data=None, status=200):
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = make_json_safe(data)
    return jsonify(body), status


def error_response(message, status=400):
    return jsonify({"success": False, "message": message}), status
