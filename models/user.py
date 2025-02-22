from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from config import Config

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
        payload = {
            'email': self.email,
            'role': self.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return payload['email']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None