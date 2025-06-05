import os
from web3 import Web3
from eth_account import Account
from flask import request, jsonify
from flask_smorest import Blueprint, abort
from werkzeug.exceptions import HTTPException
from app.services.gemini_service import check_post_authenticity
from app.services.ipfs_service import upload_post_and_get_cid
from app.blockchain.web3_config import OWNER_PRIVATE_KEY, LINKEDIN_CONTRACT_ADDRESS
from app.blockchain.verification_service import verify_register_data, verify_post_submit_data
from app.blockchain.web3_services import register_user, get_username, submit_user_cid, get_is_post_submitted
from app.api.schemas import RegisterDataSchema, PostSubmitSchema

post_blp = Blueprint("linkedin_post", __name__, description="Opreations that involves Gemini API")


@post_blp.route("/welcome", methods=["GET"])
def welcome():
    return jsonify({"message": "Welcome to the LinkedIn Post Rewards"})

@post_blp.route("/register-user", methods=["POST"])
@post_blp.arguments(RegisterDataSchema)
def register(request_data):
    
    try:
        wallet_address = request_data["walletAddress"]
        signed_message = request_data["signedMessage"]
        username = request_data["username"]
        
        if verify_register_data(wallet_address=wallet_address, signed_message=signed_message, username=username):
            user_address = wallet_address
        
        print(user_address)

        tx_hash = register_user(user_address=user_address, username=username)
        print(tx_hash)
        return ({ 'success' : 'user registered successfully!!', "tx_hash" : tx_hash, "user_address" : user_address })
    except HTTPException as http_err:
        # Re-raise so Smorest handles it cleanly
        raise http_err
    except Exception as err :
        print(f"Error in post submitting : {err}")
        abort(500,
            message="Error submitting the post."
            )    


@post_blp.route("/submit-post", methods=["POST"])
@post_blp.arguments(PostSubmitSchema)
def submit_post(request_data):
    """
    Initially Verify the post via Gemini API,
    if post is verified, and submit it ipfs to get Cid,
    then sending cid to frontend for storing in the database.
    """

    try:
        post_content = request_data['postContent']
        post_base64 = request_data["postBase64"]
        user_address = request_data["userAddress"]
        signed_message = request_data["signedMessage"]

        if verify_post_submit_data(post_base64=post_base64, post_content=post_content, user_address=user_address, signed_message=signed_message):
            linkedin_username = get_username(user_address=user_address)

        if not linkedin_username:
            abort(
                400,
                message="You are not registered for the dapp."
            )
        print(LINKEDIN_CONTRACT_ADDRESS)
        print("LinkedIn username : ", linkedin_username)
        if get_is_post_submitted(user_address=user_address):
            abort(
                400,
                message="You have already submitted the post."
            )

        if check_post_authenticity(post_content=post_content, post_base64=post_base64):
            cid = upload_post_and_get_cid(post_content=post_content, linkedin_username=linkedin_username)

        tx_hash = submit_user_cid(user_address=user_address, post_cid=cid)

        return {"success" : "Congratulations !! Your post data matched and is added to the blockchain !!", "upload_cid" : cid, "linkedin_username" : linkedin_username, "tx_hash" : tx_hash}
    
    except HTTPException as http_err:
        print(http_err)
        # Re-raise so Smorest handles it cleanly
        raise http_err
    except Exception as err :
        print(f"Error in post submitting : {err}")
        abort(500,
            message="Error submitting the post."
            )    