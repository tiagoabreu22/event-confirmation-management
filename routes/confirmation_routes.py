from flask import Blueprint, jsonify, current_app as app, request, render_template
from bson import ObjectId
import datetime

confirmation_routes = Blueprint('confirmation_routes', __name__)


@confirmation_routes.route("/<token>", methods=["GET"])
def confirm_participation(token):
    serializer = app.serializer
    db = app.db

    try:
        data = serializer.loads(token, salt="email-confirmation")
        event_start_datetime = datetime.datetime.fromisoformat(data["event_start_datetime"])

        if datetime.datetime.now() > event_start_datetime:
            return jsonify({"error": "Token expired"}), 400

        return render_template("confirmation_form.html", token=token)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@confirmation_routes.route("/submit-confirmation", methods=["POST"])
def submit_confirmation():
    serializer = app.serializer
    db = app.db

    data = request.form
    token = data.get("token")
    status = data.get("status")
    justification = data.get("justification", None)

    try:
        decoded_data = serializer.loads(token, salt="email-confirmation")
        event_id = decoded_data["event_id"]
        email = decoded_data["email"]

        result = db.confirmations.update_one(
            {"event_id": ObjectId(event_id), "email": email, "token": token},
            {"$set": {"status": status, "justification": justification}}
        )

        if result.matched_count:
            return jsonify({"message": "Your response has been recorded."}), 200
        return jsonify({"error": "Invalid token or record not found."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400
