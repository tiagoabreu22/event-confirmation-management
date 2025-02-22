from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from config import Config
from decorators.auth_decorator import roles_required
from models.user import User
import datetime

admin_routes = Blueprint('admin_routes', __name__)
client = MongoClient(Config.MONGO_URI)
db = client.event_management


@admin_routes.route('/approve-user', methods=['POST'])
@roles_required('admin')
def approve_user():
    data = request.json
    email = data.get('email')
    user_data = db.users.find_one({'email': email})
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
    db.users.update_one({'email': email}, {'$set': {'approved': True, 'approved_at': datetime.datetime.utcnow()}})
    return jsonify({'message': 'User approved'}), 200
