from flask import Blueprint, request, jsonify, current_app as app, url_for
from flask_jwt_extended import get_jwt_identity
from bson import ObjectId
from marshmallow import ValidationError
from schemas.event_schema import EventSchema, validate_datetime
import datetime

from decorators.auth_decorator import roles_required
from services.emailsender import EmailSender

event_routes = Blueprint('event_routes', __name__)
email_sender = EmailSender()


@event_routes.route("", methods=["POST"])
@roles_required(["user", "admin"])
def create_event():
    db = app.db
    data = request.json

    schema = EventSchema()

    try:
        validated_data = schema.load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    try:
        current_user = get_jwt_identity()
        if isinstance(current_user, str):
            current_user = {"email": current_user}
        data["created_by"] = current_user["email"]
        print(data["created_by"])
        result = db.events.insert_one(data)
        return jsonify({"message": "Event created successfully", "event_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@event_routes.route("<event_id>/send-invitations", methods=["POST"])
@roles_required(["user", "admin"])
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
    event_end_datetime = datetime.datetime.fromisoformat(event["end_datetime"])
    mail_template = db.mail_templates.find_one({"_id": ObjectId(event["template_id"])})
    recipients = prepare_recipients(emails, event, mail_template, event_start_datetime, event_end_datetime, serializer,
                                    event_id, db)

    send_emails(recipients)
    return jsonify({"message": "Invitations sent successfully"}), 200


def prepare_recipients(emails, event, mail_template, event_start_datetime, event_end_datetime, serializer, event_id,
                       db):
    recipients = []
    for email in emails:
        token = serializer.dumps(
            {"event_id": event_id,
             "email": email,
             "event_start_datetime": event_start_datetime.isoformat()},
            salt="email-confirmation")
        confirmation_url = url_for("confirmation_routes.confirm_participation", token=token, _external=True)
        html = False
        if mail_template:
            subject = mail_template["subject"]
            body = mail_template["body"].replace("{{confirmation_url}}", confirmation_url).replace("{{start_datetime}}",
                                                                                                   event_start_datetime.isoformat()).replace(
                "{{end_datetime}}", event_end_datetime.isoformat())
            html = True
        else:
            subject = f"Invitation to {event['name']}"
            body = f"Hi,\n\nYou're invited to '{event['name']}'! Confirm your participation here: {confirmation_url}"

        recipients.append((email, subject, body, html))
        db.confirmations.insert_one({
            "event_id": ObjectId(event_id),
            "email": email,
            "status": "pending",
            "token": token
        })
    return recipients


@event_routes.route("", methods=["GET"])
@roles_required(["user", "admin"])
def get_events():
    db = app.db
    events = list(db.events.find())
    for event in events:
        event["_id"] = str(event["_id"])
    return jsonify(events), 200


def send_emails(recipients):
    email_sender.send_emails(recipients)
