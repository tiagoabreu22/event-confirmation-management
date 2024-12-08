from flask import Flask, request, jsonify, url_for
from pymongo import MongoClient
from bson import ObjectId
from itsdangerous import URLSafeTimedSerializer
from emailsender import EmailSender
import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# MongoDB setup
client = MongoClient(app.config["MONGO_URI"])
db = client.event_management

# Serializer for generating tokens
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Initialize the EmailSender
email_sender = EmailSender()

### ROUTES ###

# Create an event
@app.route("/events", methods=["POST"])
def create_event():
    data = request.json

    try:
        result = db.events.insert_one(data)
        print(data)
        print(result)
        return jsonify({"message": "Event created successfully", "event_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Add participants and send confirmation links
@app.route("/events/<event_id>/send-invitations", methods=["POST"])
def send_invitations(event_id):
    data = request.json
    emails = data.get("emails", [])

    if not emails:
        return jsonify({"error": "Emails list is required"}), 400

    event = db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        return jsonify({"error": "Event not found"}), 404

    recipients = []
    for email in emails:
        print(email)
        token = serializer.dumps({"event_id": event_id, "email": email}, salt="email-confirmation")
        confirmation_url = url_for("confirm_participation", token=token, _external=True)
        print(confirmation_url)

        subject = f"Invitation to {event['name']}"
        body = f"Hi,\n\nYou're invited to '{event['name']}'! Confirm your participation here: {confirmation_url}"
        recipients.append((email, subject, body))

        # Save confirmation entry
        db.confirmations.insert_one({
            "event_id": ObjectId(event_id),
            "email": email,
            "confirmed": False,
            "token": token
        })
        print("Confirmation saved")

    send_emails(recipients)

    return jsonify({"message": "Invitations sent successfully"}), 200

# Confirm participation
@app.route("/confirm/<token>", methods=["GET"])
def confirm_participation(token):
    try:
        data = serializer.loads(token, salt="email-confirmation", max_age=3600)
        event_id = data["event_id"]
        email = data["email"]

        # Update confirmation status
        result = db.confirmations.update_one(
            {"event_id": ObjectId(event_id), "email": email, "token": token},
            {"$set": {"confirmed": True}}
        )

        if result.matched_count:
            return jsonify({"message": "Your participation is confirmed!"}), 200
        return jsonify({"error": "Invalid token or already confirmed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

### HELPER FUNCTIONS ###

def send_emails(recipients):
    email_sender.send_emails(recipients)

#force close the connection when done
import atexit
atexit.register(email_sender.close)

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)