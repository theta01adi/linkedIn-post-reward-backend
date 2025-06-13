from .web3_instance import get_web3_instance, get_contract_instance
from .web3_config import OWNER_PRIVATE_KEY, OWNER_PUBLIC_ADDRESS, PINATA_JWT
from flask import jsonify
from web3 import Web3
from flask_smorest import abort
from web3.exceptions import ContractLogicError
import requests
import os
from requests.exceptions import RequestException, HTTPError, Timeout
import time

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

        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction mined in block", receipt.blockNumber)

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

def download_private_json(cid, expires=100):
    try:
        file_url = f"https://{os.getenv('PINATA_GATEWAY_DOMAIN')}.mypinata.cloud/files/{cid}"
        headers = {
            "Authorization": PINATA_JWT,
            "Content-Type": "application/json"
        }
        payload = {
            "url": file_url,
            "expires": expires,
            "date" : int(time.time()),
            "method": "GET"
        }

        # Step 1: Get presigned download link
        resp = requests.post(
            os.getenv("PINATA_DOWNLOAD_URL"),
            json=payload,
            headers=headers,
            timeout=10
        )
        if not resp.ok:
            print("🔴 Error from Pinata while generating presigned link:", resp.text)
            abort(resp.status_code, message="Failed to get presigned download link from Pinata.")


        presigned_url = resp.json().get("data")
        if not presigned_url:
            raise ValueError("Presigned URL not found in Pinata response")

        # Fetching content from presigned URL
        file_resp = requests.get(presigned_url, timeout=10)
        if not file_resp.ok:
            print("🔴 Failed to download file:", file_resp.text)
            abort(file_resp.status_code, message="Failed to download file from IPFS.")

        return file_resp.json()

    except (HTTPError, RequestException, Timeout) as net_err:
        print(f"🔴 Network error during file download: {net_err}")
        raise RuntimeError("Failed to download file from IPFS: network error")

    except ValueError as ve:
        print(f"🔴 Data format error: {ve}")
        raise RuntimeError("Invalid response from Pinata service")

    except Exception as e:
        print(f"❌ Unexpected error during IPFS download: {e}")
        raise RuntimeError("Unknown error during IPFS download")

def get_all_posts_data():

    try:

        submitted_data = contract_instance.functions.getSubmittedCids().call({'from': OWNER_PUBLIC_ADDRESS})

        parsed_submitted_data = parse_submitted_cids(submitted_data=submitted_data)
        if not parsed_submitted_data:
            return ({ "submitted_posts" : "No posts submitted yet!" })
        
        user_adresses = list(parsed_submitted_data.keys())
        for user_address in user_adresses:
            cid = parsed_submitted_data[user_address]['post_cid']
            post_json_data = download_private_json(cid=cid)
            parsed_submitted_data[user_address].update(post_json_data)

        return (parsed_submitted_data)
    except ContractLogicError as err:
        print(err)
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
    

def parse_submitted_cids(submitted_data):

    parsed_data = {}

    if not submitted_data:
        return {}
    
    for data in submitted_data:

        user_address = data[0]
        cid = data[1]
        # Nested dictionary to store user address and associated CID
        parsed_data[user_address] = {"post_cid" : cid}
    return parsed_data


def announce_winner(winner_address):

    try:

        winner_address = Web3.to_checksum_address(winner_address)
        txn = contract_instance.functions.announce_winner(winner_address).build_transaction({
        "from": OWNER_PUBLIC_ADDRESS,
        "nonce": web3.eth.get_transaction_count(OWNER_PUBLIC_ADDRESS),
        "gasPrice": web3.eth.gas_price 
        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=OWNER_PRIVATE_KEY)

        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print("Transaction sent:", tx_hash.hex())

        return tx_hash.hex()

    except ContractLogicError as err:
        print(err)
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
