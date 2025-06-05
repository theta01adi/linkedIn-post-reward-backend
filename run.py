from flask import Flask
from dotenv import load_dotenv
from flask_smorest import Api
from flask_cors import CORS

from app.api.routes import post_blp as post_blueprint


def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "LinkedIn Post Reward API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    cors_config = {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
    }

    CORS(app, resources={r"/*": cors_config})

    api = Api(app=app)

    api.register_blueprint(post_blueprint)

    return app

