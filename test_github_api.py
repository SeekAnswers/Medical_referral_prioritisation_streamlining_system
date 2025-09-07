"""
Quick test script to verify GitHub Models API is working with Phi-4-Reasoning
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub Models configuration
GITHUB_API_URL = "https://models.inference.ai.azure.com/v1/chat/completions"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL_NAME = "microsoft/phi-4-reasoning"

def test_github_models_api():
    """Test GitHub Models API directly"""
    
    if not GITHUB_TOKEN:
        print(" GITHUB_TOKEN not found in environment variables")
        return False
    
    print(f" GitHub Token: {GITHUB_TOKEN[:20]}...")
    print(f" Model: {MODEL_NAME}")
    print(f" API URL: {GITHUB_API_URL}")
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Simple test message
    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "You are a medical AI assistant. Classify medical cases as Emergent, Urgent, or Routine."
            },
            {
                "role": "user", 
                "content": "Patient with severe chest pain, shortness of breath, and crushing sensation. Please classify priority as Emergent, Urgent, or Routine and explain why."
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1,
        "top_p": 0.9
    }
    
    print("\n Testing GitHub Models API...")
    
    try:
        response = requests.post(GITHUB_API_URL, headers=headers, json=data, timeout=30)
        
        print(f" Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(" API Call Successful!")
            print(f" Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
            return True
        else:
            print(f" API Error: {response.status_code}")
            print(f" Response: {response.text}")
            return False
            
    except Exception as e:
        print(f" Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_github_models_api()
