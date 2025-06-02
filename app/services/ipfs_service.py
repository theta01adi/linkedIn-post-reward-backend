import requests
import os
import io
import json
from datetime import date
from flask_smorest import  abort

def upload_post_and_get_cid( post_content, linkedin_username ):

    today_date = str(date.today())
    try:
        post_data = {
            "post_content": post_content,
            "upload_date": today_date,
            "linkedin_username": linkedin_username
        }

        json_string = json.dumps(post_data)  # May raise TypeError
        json_post_file = io.BytesIO(json_string.encode('utf-8'))
        file_name = f"{linkedin_username}@{today_date}"  # May raise TypeError or ValueError
    except (TypeError, ValueError, AttributeError) as e:
        abort(400, message=f"Invalid input data for file generation: {str(e)}")

    headers = {
        "Authorization": os.getenv("PINATA_JWT")
    }

    data = {
        "network": "private",
        "name": file_name,
        "group_id": os.getenv("POST_DATA_PRIVATE_GROUP_ID"),
        "keyvalues": "{}"
    }

    files = {
        "file": (f"{file_name}.json", json_post_file, "application/json")
    }

    try:
        response = requests.post(os.getenv("PINATA_API_URL"), headers=headers, data=data, files=files)
        response.raise_for_status()  # raises HTTPError for non-2xx responses

        json_response = response.json()
    except requests.exceptions.RequestException as e:
        abort(502, message=f"Network error while uploading: {str(e)}")
    except ValueError:
        abort(500, message="Invalid JSON response from Pinata")
    
    error = json_response.get("error")
    if error:
        abort(
            error.get("code", 500),
            message=error.get("message", "Unknown error")
        )

    data = json_response.get("data")
    if data and data.get("cid"):
        return data["cid"]

    abort(500, message="Unexpected response format: CID not found")

    
