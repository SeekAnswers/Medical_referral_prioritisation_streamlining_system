"""
Alternative test for GitHub Models - try different authentication approaches
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def test_github_models_access():
    """Test if we have GitHub Models access"""
    
    if not GITHUB_TOKEN:
        print(" No GitHub token found")
        return
    
    print(f" Testing token: {GITHUB_TOKEN[:20]}...")
    
    # Test 1: Check basic GitHub API access
    print("\n Test 1: Basic GitHub API Access")
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f" GitHub API works - User: {user_data.get('login', 'Unknown')}")
        else:
            print(f" GitHub API failed: {response.text}")
            return
    except Exception as e:
        print(f" GitHub API error: {e}")
        return
    
    # Test 2: Try GitHub Models endpoint with different headers
    print("\n Test 2: GitHub Models Access")
    
    endpoints_to_try = [
        "https://models.inference.ai.azure.com/v1/chat/completions",
        "https://api.github.com/models/chat/completions",
        "https://models.github.com/v1/chat/completions"
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n Testing endpoint: {endpoint}")
        
        # Try different header formats
        headers_variants = [
            {"Authorization": f"Bearer {GITHUB_TOKEN}", "Content-Type": "application/json"},
            {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"},
            {"X-GitHub-Token": GITHUB_TOKEN, "Content-Type": "application/json"}
        ]
        
        for i, headers in enumerate(headers_variants):
            print(f"   Header variant {i+1}...")
            
            data = {
                "model": "microsoft/phi-4-reasoning",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            try:
                response = requests.post(endpoint, headers=headers, json=data, timeout=10)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"    SUCCESS with endpoint: {endpoint}")
                    print(f"    SUCCESS with headers variant: {i+1}")
                    return endpoint, headers
                elif response.status_code == 401:
                    print(f"    Unauthorized - need different permissions")
                elif response.status_code == 404:
                    print(f"    Endpoint not found")
                else:
                    print(f"    Other error: {response.text[:200]}")
                    
            except Exception as e:
                print(f"    Request failed: {e}")
    
    print("\n No working configuration found")
    return None

if __name__ == "__main__":
    test_github_models_access()
