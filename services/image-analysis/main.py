from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import base64
import requests
import io
from PIL import Image
import os
from datetime import datetime
import redis
from minio import Minio
import json

# Initialize FastAPI app
app = FastAPI(title="Medical Image Analysis Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Initialize MinIO
minio_client = Minio(
    "minio:9000",
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
    secure=False  # Set to True in production with proper SSL
)

# Ensure bucket exists
BUCKET_NAME = "medical-images"
try:
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
except Exception as e:
    print(f"Error creating bucket: {e}")

# Constants
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...), query: str = File(...)):
    try:
        # Read and validate image
        image_content = await image.read()
        if not image_content:
            raise HTTPException(status_code=400, detail="Empty file")

        # Validate image format
        try:
            img = Image.open(io.BytesIO(image_content))
            img.verify()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

        # Generate unique filename
        filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{image.filename}"

        # Upload to MinIO
        try:
            minio_client.put_object(
                BUCKET_NAME,
                filename,
                io.BytesIO(image_content),
                length=len(image_content)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")

        # Check cache for similar queries
        cache_key = f"{filename}:{query}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)

        # Prepare image for AI model
        encoded_image = base64.b64encode(image_content).decode("utf-8")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]
            }
        ]

        # Function to make API requests
        def make_api_request(model: str) -> Dict:
            response = requests.post(
                GROQ_API_URL,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 1000
                },
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            return response

        # Get responses from both models
        responses = {}
        for model_name, model in [
            ("llama", "meta-llama/llama-4-scout-17b-16e-instruct"),
            ("llava", "meta-llama/llama-4-scout-17b-16e-instruct")
        ]:
            response = make_api_request(model)
            if response.status_code == 200:
                result = response.json()
                responses[model_name] = result["choices"][0]["message"]["content"]
            else:
                responses[model_name] = f"Error: {response.status_code}"

        # Cache the result
        redis_client.setex(
            cache_key,
            3600,  # Cache for 1 hour
            json.dumps(responses)
        )

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
