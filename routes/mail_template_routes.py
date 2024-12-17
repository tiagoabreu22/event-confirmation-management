from flask import Blueprint, current_app as app, request
import datetime

mail_template_routes = Blueprint("mail_template_routes", __name__)


@mail_template_routes.route("", methods=["POST"])
def create_mail_template():
    db = app.db
    data = request.json
    template_name = data.get("name")
    template_body = data.get("body")
    template_subject = data.get("subject")

    if not template_body or not template_name:
        return {"error": "Missing required fields"}, 400

    result = db.mail_templates.insert_one({
        "name": template_name,
        "body": template_body,
        "subject": template_subject,
        "created_at": datetime.datetime.now()
    })

    return {"template_id": str(result.inserted_id)}, 201