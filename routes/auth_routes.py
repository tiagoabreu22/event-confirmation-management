from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from config import Config
from models.user import User
import datetime

auth_routes = Blueprint('auth_routes', __name__)
client = MongoClient(Config.MONGO_URI)
db = client.event_management


@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if db.users.find_one({'email': email}):
        return jsonify({'error': 'User already exists'}), 400

    user = User(email, password, created_at=datetime.datetime.utcnow(), approved=False, approved_at=None, role='user')
    db.users.insert_one({'email': email,
                         'password_hash': user.password_hash,
                         'created_at': user.created_at,
                         'approved': False,
                         'approved_at': None,
                         'role': 'user'
                         })
    return jsonify({'message': 'User registered successfully'}), 201


@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user_data = db.users.find_one({'email': email})
    if not user_data:
        return jsonify({'error': 'Invalid credentials'}), 401
    if user_data['approved'] is False:
        return jsonify({'error': 'User not yet approved'}), 401

    user = User(email,password=password,role=user_data['role'])

    if not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = user.generate_token()
    return jsonify({'token': token}), 200
