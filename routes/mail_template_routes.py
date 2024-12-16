from flask import Blueprint, current_app as app, request
import datetime

mail_template_routes = Blueprint("mail_template_routes", __name__)


@mail_template_routes.route("", methods=["POST"])
def create_mail_template():
    db = app.db
    data = request.json
    template_name = data.get("name")
    template_content = data.get("content")

    if not template_content or not template_name:
        return {"error": "Missing required fields"}, 400

    result = db.mail_templates.insert_one({
        "name": template_name,
        "content": template_content,
        "created_at": datetime.datetime.now()
    })

    return {"template_id": str(result.inserted_id)}, 201