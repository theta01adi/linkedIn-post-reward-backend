from flask import request, jsonify
from flask_smorest import Blueprint, abort


post_blp = Blueprint("linkedin_post", __name__, description="Opreations that involves Gemini API")


@post_blp.route("/welcome", methods=["GET"])
def welcome():
    return jsonify({"message": "Welcome to the LinkedIn Post Rewards"})



    