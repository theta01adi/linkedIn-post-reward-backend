import os
from google import genai
from pydantic import BaseModel
from flask import jsonify, json
from flask_smorest import abort

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
        client = genai.Client(api_key= GEMINI_API_KEY)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
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



def rate_post_content(post_content): 

    rating_prompt = f"""
    I will provide you with the content of a LinkedIn post.
    Please evaluate the post on a percentage scale of 1 to 100, based on the following criteria:

    Clarity and Readability - Is the content easy to understand and well-structured?

    Originality and Authenticity - Does it feel personal and genuine? Does it avoid sounding generic or AI-written?

    Relevance - Is the topic relevant to the intended professional audience?

    Engagement Potential - Does it invite interaction (comments, reactions, discussion)?

    Structure and Formatting - Is it visually readable with short paragraphs, spacing, or bullet points?

    Hook / Opening Line - Does it grab attention and make you want to keep reading?

    Impact or Takeaway - Does it leave a lasting impression or provide a clear lesson?

    Tone and Voice - Is the tone professional, approachable, and consistent with personal branding?

    Emotion and Storytelling - Does it include relatable moments, challenges, or emotional insight?

    Length - Is it concise but complete, ideally under 300-500 words?

    After reading the post, assign a percentage score from 1 (poor) to 100 (excellent) based on overall performance across these criteria.
    Then, briefly explain why it received that score.

    Here is the LinkedIn post content:
    {post_content}
    """

    class PostRating(BaseModel):
        overall_score : int

    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[rating_prompt],
        config={
        "response_mime_type": "application/json",
        "response_schema": PostRating,
    },
    )

    response = json.loads(response.text)
    score = int(response["overall_score"])
    if not score:
        abort(
            500,
            message="Error in rating the post content."
        )

    return (score)

