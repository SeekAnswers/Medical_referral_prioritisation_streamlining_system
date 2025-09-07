"""
For checking available models on GitHub Models API
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_available_models():
    """Get list of available models"""
    
    print(f" Using token: {GITHUB_TOKEN[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Try different endpoints to get model list
    endpoints_to_try = [
        "https://models.inference.ai.azure.com/v1/models",
        "https://models.inference.ai.azure.com/models",
        "https://api.github.com/models",
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n Trying: {endpoint}")
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
            print(f" Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f" Success! Found {len(data.get('data', data))} models")
                
                # Print available models
                models = data.get('data', data) if isinstance(data, dict) else data
                
                if isinstance(models, list):
                    print("\n Available Models:")
                    for i, model in enumerate(models[:10]):  # Show first 10
                        if isinstance(model, dict):
                            model_id = model.get('id', model.get('name', 'Unknown'))
                            print(f"   {i+1}. {model_id}")
                        else:
                            print(f"   {i+1}. {model}")
                    
                    if len(models) > 10:
                        print(f"   ... and {len(models) - 10} more")
                        
                return models
                
            else:
                print(f" Error: {response.text[:200]}")
                
        except Exception as e:
            print(f" Exception: {str(e)[:100]}")
    
    print("\n Could not get model list")
    return None

def test_common_models():
    """Test some common model names that might work"""
    
    print("\n Testing Common Model Names...")
    
    common_models = [
        "phi-4",
        "gpt-4",
        "gpt-4o",
        "gpt-3.5-turbo",
        "microsoft/phi-4",
        "microsoft/Phi-4",
        "phi-4-reasoning",
        "Phi-4",
        "microsoft/DialoGPT-large"
    ]
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    endpoint = "https://models.inference.ai.azure.com/v1/chat/completions"
    
    for model in common_models:
        print(f"\n Testing model: {model}")
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        try:
            response = requests.post(endpoint, headers=headers, json=data, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    SUCCESS! Model '{model}' works!")
                result = response.json()
                if result.get('choices'):
                    print(f"    Response: {result['choices'][0].get('message', {}).get('content', '')}")
                return model
            else:
                error_text = response.text[:100]
                if "unknown_model" in error_text.lower():
                    print(f"    Unknown model")
                elif "unauthorized" in error_text.lower():
                    print(f"    Unauthorized")
                else:
                    print(f"    Error: {error_text}")
                    
        except Exception as e:
            print(f"    Exception: {str(e)[:50]}")
    
    return None

if __name__ == "__main__":
    print("🔍 GitHub Models Discovery")
    print("=" * 40)
    
    # First try to get official model list
    models = get_available_models()
    
    # Then test common model names
    working_model = test_common_models()
    
    if working_model:
        print(f"\n WORKING MODEL FOUND: {working_model}")
        print(f"Update your app.py with: MODEL_NAME = \"{working_model}\"")
    else:
        print("\n No working models found")
        print("Consider switching to Azure OpenAI as backup plan")
