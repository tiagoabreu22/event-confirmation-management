from flask import Flask
from config import Config
from pymongo import MongoClient
from itsdangerous import URLSafeTimedSerializer
from routes.confirmation_routes import confirmation_routes
from routes.event_routes import event_routes

# Using the application factory pattern
def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    # Initialize resources
    flask_app.serializer = URLSafeTimedSerializer(flask_app.config["SECRET_KEY"])
    flask_app.mongo_client = MongoClient(flask_app.config["MONGO_URI"])
    flask_app.db = flask_app.mongo_client.event_management

    # Register blueprints
    flask_app.register_blueprint(event_routes, url_prefix='/events')
    flask_app.register_blueprint(confirmation_routes, url_prefix='/confirm')

    return flask_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)