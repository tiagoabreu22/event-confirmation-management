from flask import Blueprint, current_app as app, request
import datetime

mail_template_routes = Blueprint("mail_template_routes", __name__)
@mail_template_routes.route("", methods=["POST"])
def create_mail_template():
    db = app.db
    data = request.form
    template_name = data.get("name")
    template_body_file = request.files.get("template_body_file")
    template_subject = data.get("subject")

    print(template_name)
    print(template_body_file)
    print(template_subject)

    if not template_body_file or not template_name:
        return {"error": "Missing required fields"}, 400

    html_content = template_body_file.read().decode("utf-8")

    result = db.mail_templates.insert_one({
        "name": template_name,
        "body": html_content,
        "subject": template_subject,
        "created_at": datetime.datetime.now()
    })
    return {"template_id": str(result.inserted_id)}, 201
