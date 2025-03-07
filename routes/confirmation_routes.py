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
            return render_template("confirmation_expired.html")

        event = db.events.find_one({"_id": ObjectId(data["event_id"])})
        if not event:
            return jsonify({"error": "Event not found"}), 404

        confirmation_deadline = event.get("confirmation_deadline")
        if confirmation_deadline:
            if datetime.datetime.now() > datetime.datetime.fromisoformat(confirmation_deadline):
                return render_template("confirmation_expired.html")

        location = event.get("location")

        prev_response = db.confirmations.find_one({"event_id": ObjectId(data["event_id"]), "email": data["email"]})
        confirmation_change_deadline = event.get("confirmation_change_deadline")

        if confirmation_change_deadline:
            if datetime.datetime.now() > datetime.datetime.fromisoformat(confirmation_change_deadline):
                return render_template("confirmation_expired.html")

        if prev_response:
            last_modified = prev_response.get("lastModified")
            return render_template("confirmation_form.html",
                                   token=token,
                                   event_name=event["name"],
                                   event_description=event["description"],
                                   event_start_datetime=event_start_datetime.strftime("%B %d, %Y %H:%M"),
                                   location=location,
                                   event_end_datetime=datetime.datetime.fromisoformat(event["end_datetime"]).strftime(
                                       "%B %d, %Y %H:%M"),
                                   status=prev_response["status"],
                                   justification=prev_response.get("justification", ""),
                                   last_modified=last_modified.strftime(
                                       "%B %d, %Y %H:%M") if last_modified else None)

        event_name = event["name"]
        event_description = event["description"]
        event_end_datetime = datetime.datetime.fromisoformat(event["end_datetime"])

        return render_template("confirmation_form.html",
                               token=token,
                               event_name=event_name,
                               event_description=event_description,
                               event_start_datetime=event_start_datetime.strftime("%B %d, %Y %H:%M"),
                               event_end_datetime=event_end_datetime.strftime("%B %d, %Y %H:%M"),
                               location=location,
                               status="",
                               justification="")

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
            {"event_id": ObjectId(event_id),
             "email": email,
             "token": token},
            {"$set": {"status": status, "justification": justification},
             "$currentDate": {"lastModified": True}}
        )

        if result.matched_count:
            return render_template("success.html")
        return render_template("error.html")

    except Exception:
        return render_template("error.html")
