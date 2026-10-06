"""
settlement_routes.py - Balances and settlements.

GET  /api/settlements/balances/<group_id>  -> paid, owed, net balance of each user
GET  /api/settlements/suggest/<group_id>   -> "who owes whom" (preview, not saved)
POST /api/settlements/generate/<group_id>  -> save "who owes whom" as pending settlements
GET  /api/settlements/group/<group_id>     -> list saved settlements
PUT  /api/settlements/<id>/status          -> mark pending / completed
"""
from decimal import Decimal
from flask import Blueprint, request

import models
from utils.helpers import success_response, error_response
from utils.split_algorithm import calculate_balances, simplify_debts

settlement_bp = Blueprint("settlements", __name__)


def _get_group_balances(group_id):
    """Collect data from the database and run the balance calculation."""
    members = models.get_members(group_id)
    member_ids = [m["id"] for m in members]

    paid = models.get_total_paid(group_id)
    owed = models.get_total_owed(group_id)
    sent, received = models.get_completed_settlement_totals(group_id)

    balances = calculate_balances(member_ids, paid, owed, sent, received)
    return members, balances


@settlement_bp.route("/balances/<int:group_id>", methods=["GET"])
def balances(group_id):
    if not models.get_group(group_id):
        return error_response("Group not found", 404)

    members, balances_by_user = _get_group_balances(group_id)

    report = []
    for member in members:
        b = balances_by_user[member["id"]]
        net = b["net_balance"]
        if net > 0:
            status = "gets back"
        elif net < 0:
            status = "owes"
        else:
            status = "settled"
        report.append({
            "user_id": member["id"],
            "name": member["name"],
            "total_paid": b["total_paid"],
            "total_owed": b["total_owed"],
            "net_balance": net,
            "status": status,
        })
    return success_response("Balances calculated", {"group_id": group_id, "balances": report})


def _calculate_payments(group_id):
    """Returns a list of payments with user names added."""
    members, balances_by_user = _get_group_balances(group_id)
    names = {m["id"]: m["name"] for m in members}
    net = {uid: b["net_balance"] for uid, b in balances_by_user.items()}

    payments = simplify_debts(net)
    for p in payments:
        p["from_name"] = names[p["from_user"]]
        p["to_name"] = names[p["to_user"]]
        p["message"] = f'{p["from_name"]} owes {p["to_name"]} Rs. {p["amount"]}'
    return payments


@settlement_bp.route("/suggest/<int:group_id>", methods=["GET"])
def suggest(group_id):
    if not models.get_group(group_id):
        return error_response("Group not found", 404)
    payments = _calculate_payments(group_id)
    return success_response(
        "Who owes whom calculated", {"group_id": group_id, "payments": payments}
    )


@settlement_bp.route("/generate/<int:group_id>", methods=["POST"])
def generate(group_id):
    if not models.get_group(group_id):
        return error_response("Group not found", 404)

    payments = _calculate_payments(group_id)
    models.replace_pending_settlements(group_id, payments)
    saved = models.get_settlements_by_group(group_id)
    return success_response("Settlements generated", {"group_id": group_id, "settlements": saved}, 201)


@settlement_bp.route("/group/<int:group_id>", methods=["GET"])
def list_settlements(group_id):
    if not models.get_group(group_id):
        return error_response("Group not found", 404)
    return success_response(
        "Settlements fetched",
        {"group_id": group_id, "settlements": models.get_settlements_by_group(group_id)},
    )


@settlement_bp.route("/<int:settlement_id>/status", methods=["PUT"])
def update_status(settlement_id):
    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return error_response("status is required")

    status = str(data["status"]).lower()
    if status not in ("pending", "completed"):
        return error_response("status must be 'pending' or 'completed'")
    if not models.get_settlement(settlement_id):
        return error_response("Settlement not found", 404)

    models.update_settlement_status(settlement_id, status)
    return success_response("Settlement status updated", {"id": settlement_id, "status": status})
