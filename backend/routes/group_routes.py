"""
group_routes.py - Create groups, add members, view group details.

POST /api/groups                    -> create a group
GET  /api/groups/user/<user_id>     -> all groups of a user
GET  /api/groups/<group_id>         -> group details + members
POST /api/groups/<group_id>/members -> add a member (by user_id or email)
"""
from flask import Blueprint, request

import models
from utils.helpers import success_response, error_response

group_bp = Blueprint("groups", __name__)


@group_bp.route("", methods=["POST"])
def create_group():
    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON")

    group_name = str(data.get("group_name", "")).strip()
    created_by = data.get("created_by")

    if not group_name or created_by is None:
        return error_response("group_name and created_by are required")
    if not isinstance(created_by, int):
        return error_response("created_by must be a user id (number)")
    if not models.get_user_by_id(created_by):
        return error_response("Creator user not found", 404)

    group_id = models.create_group(group_name, created_by)
    return success_response(
        "Group created successfully",
        {"id": group_id, "group_name": group_name, "created_by": created_by},
        201,
    )


@group_bp.route("/user/<int:user_id>", methods=["GET"])
def groups_of_user(user_id):
    if not models.get_user_by_id(user_id):
        return error_response("User not found", 404)
    return success_response("Groups fetched", models.get_groups_for_user(user_id))


@group_bp.route("/<int:group_id>", methods=["GET"])
def group_details(group_id):
    group = models.get_group(group_id)
    if not group:
        return error_response("Group not found", 404)

    group["members"] = models.get_members(group_id)
    group["member_count"] = len(group["members"])
    return success_response("Group details fetched", group)


@group_bp.route("/<int:group_id>/members", methods=["POST"])
def add_member(group_id):
    if not models.get_group(group_id):
        return error_response("Group not found", 404)

    data = request.get_json(silent=True)
    if not data:
        return error_response("Request body must be valid JSON")

    # Member can be added using user_id OR email
    if data.get("user_id") is not None:
        user = models.get_user_by_id(data["user_id"])
    elif data.get("email"):
        user = models.get_user_by_email(str(data["email"]).strip().lower())
    else:
        return error_response("Provide either user_id or email")

    if not user:
        return error_response("User not found", 404)
    if models.is_member(group_id, user["id"]):
        return error_response("User is already a member of this group", 409)

    models.add_member(group_id, user["id"])
    return success_response(
        "Member added successfully",
        {"group_id": group_id, "user_id": user["id"], "name": user["name"]},
        201,
    )
