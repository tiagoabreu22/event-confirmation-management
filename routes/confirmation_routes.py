from flask import Blueprint, jsonify, current_app as app
from bson import ObjectId
import datetime

confirmation_routes = Blueprint('confirmation_routes', __name__)


@confirmation_routes.route("/<token>", methods=["GET"])
def confirm_participation(token):
    serializer = app.serializer
    db = app.db

    try:
        data = serializer.loads(token, salt="email-confirmation")
        event_id = data["event_id"]
        email = data["email"]
        event_start_datetime = datetime.datetime.fromisoformat(data["event_start_datetime"])

        if datetime.datetime.now() > event_start_datetime:
            return jsonify({"error": "Token expired"}), 400

        result = db.confirmations.update_one(
            {"event_id": ObjectId(event_id), "email": email, "token": token},
            {"$set": {"confirmed": True}}
        )

        if result.matched_count:
            return jsonify({"message": "Your participation is confirmed!"}), 200
        return jsonify({"error": "Invalid token or already confirmed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400
