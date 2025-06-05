from eth_account.messages import encode_defunct
from .web3_instance import get_web3_instance, get_contract_instance
from web3 import Web3 
from flask_smorest import abort

web3 = get_web3_instance()
contract_instance = get_contract_instance()

def verify_register_data(wallet_address, signed_message, username):

    if not username or not username.strip():
        abort(400,
              message="Username cannot be empty !!")
        
    if not signed_message or not signed_message.strip():
        abort(
            400,
            "Signed message can't be empty!!"
        )
    
    if not Web3.is_address(wallet_address):
        abort(400,
              message="Invalid wallet address!!")
    
    ORIGINAL_REGISTER_MESSAGE = "You are registering to LinkedInPost Reward Dapp !!  You agree with our terms and conditions."

    try:
        message = encode_defunct(text=ORIGINAL_REGISTER_MESSAGE)
        signer_address = Web3().eth.account.recover_message(message, signature=signed_message)
    except Exception as e:
        print(e)
        abort(400,
              message="Invalid signed message")
    
    if signer_address.lower() != wallet_address.lower():
        abort(400,
              message="Signed message does not match wallet address")
    
    return True

def verify_post_submit_data(user_address, post_content, post_base64, signed_message):

    if not Web3.is_address(user_address):
        abort(400,
              message="Invalid wallet address!!")
        
    if not signed_message or not signed_message.strip():
        abort(
            400,
            "Signed message can't be empty!!"
        )

    if not post_base64 or not post_base64.strip():
        abort(400,
            message="Image can't be empty!!" )
        
    if not post_content or not post_content.strip():
        abort(
            400,
            message="Post content can't be empty!!"
        )

    ORIGINAL_POST_SUBMIT_MESSAGE = "You are submiting your linkedin post screenshot and post content to LinkedInPost Reward Dapp !!"

    try:
        message = encode_defunct(text=ORIGINAL_POST_SUBMIT_MESSAGE)
        signer_address = Web3().eth.account.recover_message(message, signature=signed_message)
    except Exception as e:
        print(e)
        abort(400,
              message="Invalid signed message")
    
    if signer_address.lower() != user_address.lower():
        abort(400,
              message="Signed message does not match wallet address")
    
    return True
    


