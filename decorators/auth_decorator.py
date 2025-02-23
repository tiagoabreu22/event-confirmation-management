from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt


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
            claims = get_jwt()
            accepted_roles = roles[0] if len(roles) == 1 and isinstance(roles[0], list) else roles
            if claims.get("role") not in accepted_roles:
                return jsonify({"error": "Access denied"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
