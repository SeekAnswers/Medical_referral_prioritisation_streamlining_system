import base64  # Module for encoding images in base64 format
import requests  # Module for making API requests
import io  # Module for handling byte streams
from PIL import Image  # Library for image processing
from dotenv import load_dotenv  # Module for loading environment variables
import os  # Module for interacting with the operating system
import logging  # Module for logging errors and events

# Configure logging to display info and error messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Define the API URL
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Retrieve the API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ensure the API key is available; raise an error if missing
if not GROQ_API_KEY:
    raise ValueError("GROQ API KEY is not set in the .env file")

def process_image(image_path, query):
    """Processes an image and sends it to the API for analysis based on the query."""
    try:
        # Open the image file in binary mode and read its content
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
            # Encode the image to base64 format
            encoded_image = base64.b64encode(image_content).decode("utf-8")

        # Validate if the file is a proper image
        try:
            img = Image.open(io.BytesIO(image_content))
            img.verify()  # Check if the image is corrupted
        except Exception as e:
            logger.error(f"Invalid image format: {str(e)}")
            return {"error": f"Invalid image format: {str(e)}"}

        # Construct the request payload with query text and encoded image
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ]

        def make_api_request(model):
            """Sends an API request to the specified model."""
            response = requests.post(
                GROQ_API_URL, 
                json={"model": model, "messages": messages, "max_tokens": 1000},
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                timeout=30  # Set timeout for the request
            )
            return response
        
        # Send requests to two different AI models
        llama_11b_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct")
        llama_90b_response = make_api_request("meta-llama/llama-4-scout-17b-16e-instruct")

        # Store responses from both models
        responses = {}
        for model, response in [("llama11b", llama_11b_response), ("llama90b", llama_90b_response)]:
            if response.status_code == 200:  # Check if request was successful
                result = response.json()
                answer = result["choices"][0]["message"]["content"]  # Extract response text
                logger.info(f"Processed response from {model} API: {answer}")
                responses[model] = answer  # Store successful response
            else:
                # Log and store error if the request failed
                logger.error(f"Error from {model} API: {response.status_code} - {response.text}")
                responses[model] = f"Error from {model} API: {response.status_code}"
        
        return responses  # Return responses from both models

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"An unexpected error occurred: {str(e)}")
        return {"error": f"An unexpected error occurred: {str(e)}"}

# Run the script when executed directly
if __name__ == "__main__":
    image_path = "test1.png"  # Define the image file path
    query = "what are the encoders in this picture?"  # Define the question for the AI model
    result = process_image(image_path, query)  # Process the image and get a response
    print(result)  # Print the API response
