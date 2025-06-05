from .web3_instance import get_web3_instance, get_contract_instance
from .web3_config import OWNER_PRIVATE_KEY, OWNER_PUBLIC_ADDRESS
from flask import jsonify
from web3 import Web3
from flask_smorest import abort
from web3.exceptions import ContractLogicError

web3 = get_web3_instance()
contract_instance = get_contract_instance()

def get_username(user_address):

    username = contract_instance.functions.userToName(Web3.to_checksum_address(user_address)).call()

    return username

def get_is_post_submitted(user_address):

    submit_status = contract_instance.functions.isPostSubmitted(Web3.to_checksum_address(user_address)).call()

    return submit_status

def register_user(user_address, username):

    try:
        user_address = Web3.to_checksum_address(user_address)
        txn = contract_instance.functions.register_user(user_address, username).build_transaction({
        "from": OWNER_PUBLIC_ADDRESS,
        "nonce": web3.eth.get_transaction_count(OWNER_PUBLIC_ADDRESS),
        "gasPrice": web3.eth.gas_price 

        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=OWNER_PRIVATE_KEY)

        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print("Transaction sent:", tx_hash.hex())

        # receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        # print("Transaction mined in block", receipt.blockNumber)

        return tx_hash.hex()
    except ContractLogicError as e:
        error_message = str(e)
        print(error_message)
        abort(
            400,
            message="Contract execution failed"
        )

    except Exception as e:
        print(str(e))
        abort(
            500,
            message="Unexpected error : failed!!"
        )


def submit_user_cid(user_address, post_cid):


    try:
        user_address = Web3.to_checksum_address(user_address)
        txn = contract_instance.functions.submit_cid(user_address, post_cid).build_transaction({
        "from": OWNER_PUBLIC_ADDRESS,
        "nonce": web3.eth.get_transaction_count(OWNER_PUBLIC_ADDRESS),
        "gasPrice": web3.eth.gas_price 

        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=OWNER_PRIVATE_KEY)

        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print("Transaction sent:", tx_hash.hex())

        # receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        # print("Transaction mined in block", receipt.blockNumber)

        return tx_hash.hex()
    except ContractLogicError as e:
        error_message = str(e).split(': ')[1]
        print(error_message)
        abort(
            400,
            message="Unable to submit post!!"
        )

    except Exception as e:
        print(str(e))
        abort(
            500,
            message="Unable to submit post!!"
        )