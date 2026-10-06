"""
expense_routes.py - Add expenses (with split) and view expense history.

POST /api/expenses                     -> add an expense
GET  /api/expenses/group/<group_id>    -> expense history of a group
GET  /api/expenses/<expense_id>        -> one expense with its split

Request body for POST /api/expenses:
{
  "group_id": 1,
  "description": "Dinner",
  "amount": 900,
  "paid_by": 1,
  "date": "2025-01-20",                 (optional, default = today)
  "split_type": "equal" | "percentage" | "custom",

  // equal:      "participants": [1, 2, 3]            (optional, default = all members)
  // percentage: "splits": [{"user_id": 1, "percentage": 50}, ...]
  // custom:     "splits": [{"user_id": 1, "amount": 500}, ...]
}
"""
from datetime import date, datetime
from decimal import Decimal
from flask import Blueprint, request

import models
from utils.helpers import success_response, error_response
from utils.split_algorithm import (
    to_money, equal_split, percentage_split, custom_split,
)

expense_bp = Blueprint("expenses", __name__)


def _build_shares(split_type, amount, data, member_ids):
    """
    Turn the request into {user_id: share}. Raises ValueError with a
    friendly message if anything is wrong.
    """
    if split_type == "equal":
        participants = data.get("participants") or member_ids
        if not isinstance(participants, list):
            raise ValueError("participants must be a list of user ids")
        if len(set(participants)) != len(participants):
            raise ValueError("participants contains duplicate users")
        _check_all_members(participants, member_ids)
        return equal_split(amount, participants)

    # percentage and custom both need a "splits" list
    splits = data.get("splits")
    if not isinstance(splits, list) or not splits:
        raise ValueError("splits list is required for this split_type")

    values = {}
    field = "percentage" if split_type == "percentage" else "amount"
    for item in splits:
        if not isinstance(item, dict) or "user_id" not in item or field not in item:
            raise ValueError(f"Each split needs 'user_id' and '{field}'")
        if item["user_id"] in values:
            raise ValueError("splits contains duplicate users")
        values[item["user_id"]] = item[field]

    _check_all_members(list(values.keys()), member_ids)

    if split_type == "percentage":
        return percentage_split(amount, values)
    return custom_split(amount, values)


def _check_all_members(user_ids, member_ids):
    for user_id in user_ids:
        if user_id not in member_ids:
            raise ValueError(f"User {user_id} is not a member of this group")


@expense_bp.route("", methods=["POST"])
def add_expense():
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON")

    # ---- required fields ----
    for field in ("group_id", "description", "amount", "paid_by", "split_type"):
        if data.get(field) in (None, ""):
            return error_response(f"{field} is required")

    group_id = data["group_id"]
    paid_by = data["paid_by"]
    description = str(data["description"]).strip()
    split_type = str(data["split_type"]).lower()

    if not isinstance(group_id, int) or not isinstance(paid_by, int):
        return error_response("group_id and paid_by must be numbers")
    if split_type not in ("equal", "percentage", "custom"):
        return error_response("split_type must be equal, percentage or custom")

    try:
        amount = to_money(data["amount"])
    except ValueError:
        return error_response("amount must be a valid number")
    if amount <= Decimal("0"):
        return error_response("amount must be greater than 0")

    # ---- date ----
    if data.get("date"):
        try:
            expense_date = datetime.strptime(str(data["date"]), "%Y-%m-%d").date()
        except ValueError:
            return error_response("date must be in YYYY-MM-DD format")
    else:
        expense_date = date.today()

    # ---- group and payer checks ----
    if not models.get_group(group_id):
        return error_response("Group not found", 404)
    member_ids = [m["id"] for m in models.get_members(group_id)]
    if paid_by not in member_ids:
        return error_response("Payer must be a member of the group")

    # ---- calculate split ----
    try:
        shares = _build_shares(split_type, amount, data, member_ids)
    except ValueError as error:
        return error_response(str(error))

    expense_id = models.create_expense(
        group_id, description, amount, paid_by, expense_date, shares
    )
    return success_response(
        "Expense added successfully",
        {
            "expense_id": expense_id,
            "description": description,
            "amount": amount,
            "paid_by": paid_by,
            "split_type": split_type,
            "shares": [{"user_id": uid, "share_amount": s} for uid, s in shares.items()],
        },
        201,
    )


@expense_bp.route("/group/<int:group_id>", methods=["GET"])
def expense_history(group_id):
    if not models.get_group(group_id):
        return error_response("Group not found", 404)

    expenses = models.get_expenses_by_group(group_id)
    for expense in expenses:
        expense["splits"] = models.get_splits(expense["id"])

    total = sum((e["amount"] for e in expenses), Decimal("0"))
    return success_response(
        "Expense history fetched",
        {"group_id": group_id, "total_spent": total, "expenses": expenses},
    )


@expense_bp.route("/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    expense = models.get_expense(expense_id)
    if not expense:
        return error_response("Expense not found", 404)
    expense["splits"] = models.get_splits(expense_id)
    return success_response("Expense fetched", expense)
