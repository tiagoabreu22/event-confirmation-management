from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    return decorated


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @token_required
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            if current_user["role"] not in roles:
                return jsonify({"error": "Access denied"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
