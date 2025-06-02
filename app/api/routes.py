from flask import request, jsonify
from flask_smorest import Blueprint, abort
from werkzeug.exceptions import HTTPException
from app.services.gemini_service import check_post_authenticity
from app.services.ipfs_service import upload_post_and_get_cid

post_blp = Blueprint("linkedin_post", __name__, description="Opreations that involves Gemini API")


@post_blp.route("/welcome", methods=["GET"])
def welcome():
    return jsonify({"message": "Welcome to the LinkedIn Post Rewards"})


@post_blp.route("/submit-post", methods=["POST"])
def submit_post():
    """
    Initially Verify the post via Gemini API,
    if post is verified, and submit it ipfs to get Cid,
    then sending cid to frontend for storing in the database.
    """

    try:
        post_content = request.json['postContent']
        post_base64 = request.json["postBase64"]
        linkedin_username = request.json["linkedin_username"]
        
        is_post_authenticated = check_post_authenticity(post_content, post_base64=post_base64)

        if is_post_authenticated:
            cid = upload_post_and_get_cid(post_content=post_content, linkedin_username=linkedin_username)

        return {"message" : "Congratulations !! Your post data matched !!", "upload_cid" : cid}
    
    except HTTPException as http_err:
        # Re-raise so Smorest handles it cleanly
        raise http_err
    except Exception as err :
        print(f"Error in post submitting : {err}")
        abort(500,
            message="Error submitting the post."
            )    