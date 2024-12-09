# routes/event_routes.py
from flask import Blueprint, request, jsonify, current_app as app, url_for
from bson import ObjectId
import datetime
from emailsender import EmailSender

event_routes = Blueprint('event_routes', __name__)
email_sender = EmailSender()

@event_routes.route("", methods=["POST"])
def create_event():
    db = app.db
    data = request.json

    try:
        result = db.events.insert_one(data)
        return jsonify({"message": "Event created successfully", "event_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@event_routes.route("<event_id>/send-invitations", methods=["POST"])
def send_invitations(event_id):
    serializer = app.serializer
    db = app.db
    data = request.json
    emails = data.get("emails", [])

    if not emails:
        return jsonify({"error": "Emails list is required"}), 400

    event = db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        return jsonify({"error": "Event not found"}), 404

    event_start_datetime = datetime.datetime.fromisoformat(event["start_datetime"])

    recipients = []
    for email in emails:
        token = serializer.dumps(
            {"event_id": event_id,
             "email": email,
             "event_start_datetime": event_start_datetime.isoformat()},
            salt="email-confirmation")
        confirmation_url = url_for("confirmation_routes.confirm_participation", token=token, _external=True)

        subject = f"Invitation to {event['name']}"
        body = f"Hi,\n\nYou're invited to '{event['name']}'! Confirm your participation here: {confirmation_url}"
        recipients.append((email, subject, body))

        db.confirmations.insert_one({
            "event_id": ObjectId(event_id),
            "email": email,
            "confirmed": False,
            "token": token
        })

    send_emails(recipients)

    return jsonify({"message": "Invitations sent successfully"}), 200

def send_emails(recipients):
    email_sender.send_emails(recipients)