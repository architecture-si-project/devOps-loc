from flask import Blueprint, request, jsonify

from ..decorators import token_required, admin_required
from ..services.user_service import get_all_users, get_user_by_id, update_user, delete_user, update_user_role

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
@token_required
def list_users(current_user):
    users = get_all_users()
    return jsonify(users)


@users_bp.route("/<int:user_id>", methods=["GET"])
@token_required
def get_user(current_user, user_id):
    user = get_user_by_id(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user)


@users_bp.route("/<int:user_id>", methods=["PUT"])
@token_required
def edit_user(current_user, user_id):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Missing required fields"}), 400

    user = update_user(user_id, name, email)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user)


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def remove_user(current_user, user_id):
    deleted = delete_user(user_id)

    if not deleted:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User deleted"}), 200


@users_bp.route("/<int:user_id>/role", methods=["PATCH"])
@admin_required
def change_role(current_user, user_id):
    data = request.get_json()
    role = data.get("role")

    if role not in ("user", "admin"):
        return jsonify({"error": "Invalid role"}), 400

    user = update_user_role(user_id, role)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user)
