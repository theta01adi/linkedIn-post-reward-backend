import os
from google import genai
from pydantic import BaseModel
from flask import jsonify, json
from flask_smorest import abort

def get_post_details(post_content, post_base64):

    image_analyze_prompt = f"""
    First if image UI is not of LinkedIn post, return {{"is_linkedIn_post": false}} and stop further evaluation.
    Analyze the provided image and determine whether it depicts a LinkedIn post. If it does, extract the post's main textual content and compare it to the separately provided content.

    ---
    **Separately Provided Post Content:**
    {post_content}
    ---

    Return your results in the following JSON format:

    
    {{
    "is_linkedIn_post": true/false,
    "is_my_post": true/false,
    "match_pr": percentage_match_as_float_between_0_and_1
    }}
   
    Definitions:
    is_linkedIn_post: Set to true only if the image clearly shows LinkedIn UI elements, such as the LinkedIn logo, user name with timestamp, profile picture, and post interaction buttons like "Like", "Comment", or "Share". If not, return {{"is_linkedIn_post": false}} and stop further evaluation.

    is_my_post: If is_linkedIn_post is true, check if the profile info in the image includes an indicator like "• You" next to the name. If yes, set to true; otherwise, set to false.

    match_pr: After extracting the main textual content of the post (not including profile names, likes/comments, or UI elements), compute the similarity with the separately provided content. Return a float between 0.0 and 1.0 representing the degree of match, where:

    1.0 means perfect or near-perfect match,

    ~0.8+ means substantially similar with only minor differences,

    Lower values indicate progressively less similarity.

    Only the final JSON should be returned.
    """

    class PostContent(BaseModel):
        is_linkedIn_post : bool
        is_my_post: bool
        match_pr: float
    
    try:
        client = genai.Client(api_key= os.getenv("GEMINI_API_KEY"))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {
                    "inline_data":  {
            "data" : post_base64,
            "mime_type" : "image/png"
        }
                },
                {
                    "text": image_analyze_prompt
                }
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": PostContent,
            }
        )

        print("\n--- Gemini Response ---")
        print(response.text)

        # Parse the model output (expecting JSON text)
        parsed_json = json.loads(response.text)

        # Validate and convert to Pydantic model
        post_details = PostContent(**parsed_json)
       
        return parsed_json
    except Exception as e:
        print(f"\nAn error occurred during the API call: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Error response: {e.response.text}")

def check_post_authenticity(post_content, post_base64):

    post_details = get_post_details(post_content=post_content, post_base64=post_base64)

    print("---------------------------- Post Details ---------------------------- ")
    print(post_details)

    if not post_details["is_linkedIn_post"]:
        abort(
            400,
            message="Provided image is not a linkedIn post"
        )

    if not post_details["is_my_post"]:
        abort(
            400,
            message="Provided image is not your linkedIn post"
        )

   

    if post_details["match_pr"] < 0.80 :
        abort(
            400,
            message="Your post content provided is not matching with post screenshot data."
        )
    
    return True


    