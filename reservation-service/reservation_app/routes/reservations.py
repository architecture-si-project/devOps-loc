from flask import Blueprint, request, jsonify

from ..decorators import token_required
from ..services.reservation_service import (
    create_reservation,
    get_reservations_by_user,
    get_reservation_by_id,
    cancel_reservation,
    RESERVATION_NOT_FOUND,
)

reservations_bp = Blueprint("reservations", __name__, url_prefix="/reservations")


@reservations_bp.route("", methods=["POST"])
@token_required
def create(current_user):
    data = request.get_json()

    housing_name = data.get("housing_name")
    check_in = data.get("check_in")
    check_out = data.get("check_out")

    if not housing_name or not check_in or not check_out:
        return jsonify({"error": "Missing required fields"}), 400

    reservation = create_reservation(current_user["user_id"], housing_name, check_in, check_out)

    return jsonify(reservation), 201


@reservations_bp.route("", methods=["GET"])
@token_required
def list_reservations(current_user):
    reservations = get_reservations_by_user(current_user["user_id"])
    return jsonify(reservations)


@reservations_bp.route("/<int:reservation_id>", methods=["GET"])
@token_required
def get_reservation(current_user, reservation_id):
    reservation = get_reservation_by_id(reservation_id)

    if not reservation:
        return jsonify({"error": RESERVATION_NOT_FOUND}), 404

    if reservation["user_id"] != current_user["user_id"] and current_user["role"] != "admin":
        return jsonify({"error": "Access denied"}), 403

    return jsonify(reservation)


@reservations_bp.route("/<int:reservation_id>", methods=["DELETE"])
@token_required
def cancel(current_user, reservation_id):
    reservation = get_reservation_by_id(reservation_id)

    if not reservation:
        return jsonify({"error": RESERVATION_NOT_FOUND}), 404

    if reservation["user_id"] != current_user["user_id"] and current_user["role"] != "admin":
        return jsonify({"error": "Access denied"}), 403

    cancelled = cancel_reservation(reservation_id)

    if not cancelled:
        return jsonify({"error": "Reservation already cancelled"}), 400

    return jsonify({"message": "Reservation cancelled"})
