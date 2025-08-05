from functools import wraps
from flask import request, jsonify

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", None)
        if not token or token != "Bearer your-token-here":
            return jsonify({"error": "Unauthorized or missing token"}), 401
        current_user = {"username": "testuser"}
        return f(current_user, *args, **kwargs)
    return decorated

