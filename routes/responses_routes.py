from flask import Blueprint, jsonify, current_app as app
from bson import ObjectId
from pymongo.errors import PyMongoError

from decorators.auth_decorator import roles_required

responses_routes = Blueprint('responses_routes', __name__)


@responses_routes.route("<event_id>", methods=["GET"])
@roles_required(["user", "admin"])
def get_responses(event_id):
    db = app.db
    responses = db.confirmations.find({"event_id": ObjectId(event_id)})
    response_list = []
    for response in responses:
        response["_id"] = str(response["_id"])
        response["event_id"] = str(response["event_id"])
        response_list.append(response)
    return jsonify(response_list), 200
