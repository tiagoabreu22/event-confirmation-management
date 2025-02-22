from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


class User:
    def __init__(self, email, password=None, created_at=None, approved=None, approved_at=None, role=None):
        self.email = email
        self.password_hash = generate_password_hash(password) if password else None
        self.created_at = created_at
        self.approved = approved
        self.approved_at = approved_at
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        return create_access_token(identity=self.email, additional_claims={'role': self.role})
