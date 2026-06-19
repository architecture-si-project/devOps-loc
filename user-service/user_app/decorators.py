import os
from functools import wraps

import jwt
from flask import request, jsonify


def _decode_token():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Token is missing"}), 401)

    token = auth_header.split(" ")[1]

    try:
        data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return {"user_id": data["user_id"], "role": data["role"]}, None
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"error": "Token has expired"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"error": "Invalid token"}), 401)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user, error = _decode_token()
        if error:
            return error
        return f(current_user, *args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user, error = _decode_token()
        if error:
            return error
        if current_user["role"] != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(current_user, *args, **kwargs)
    return decorated
