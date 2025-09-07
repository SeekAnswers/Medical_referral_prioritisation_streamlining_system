"""
Azure OpenAI Implementation - A Free Tier Alternative to GitHub Models
Reliable, fast, and excellent for medical AI decisions
"""

import os
import json
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

def test_azure_openai():
    """Test Azure OpenAI setup"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., https://your-resource.openai.azure.com/
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")  # Your deployment name
    
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY]):
        print(" Azure OpenAI credentials not found in .env")
        print("\nAdd these to your .env file:")
        print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("AZURE_OPENAI_KEY=your_azure_openai_key")
        print("AZURE_OPENAI_DEPLOYMENT=gpt-4")
        return False
    
    print(f" Azure Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f" Deployment: {AZURE_OPENAI_DEPLOYMENT}")
    print(f" Key: {AZURE_OPENAI_KEY[:20]}...")
    
    try:
        # Create client
        client = ChatCompletionsClient(
            endpoint=AZURE_OPENAI_ENDPOINT,
            credential=AzureKeyCredential(AZURE_OPENAI_KEY)
        )
        
        # Test message for medical AI
        messages = [
            {
                "role": "system",
                "content": """You are a specialist NHS clinical decision support AI. Follow NHS Emergency Care Standards for triage prioritization.

CLASSIFICATION RULES:
- EMERGENT (<15 min): Life-threatening conditions requiring immediate intervention
- URGENT (<2 hours): Serious conditions requiring prompt treatment  
- ROUTINE (<18 weeks): Standard care pathway cases

Always respond with: "Priority: [EMERGENT/URGENT/ROUTINE]" followed by clinical reasoning."""
            },
            {
                "role": "user",
                "content": "Patient presents with severe chest pain, crushing sensation, shortness of breath, and diaphoresis. Symptoms started 30 minutes ago during physical activity. Patient appears distressed and anxious. Please classify the priority level."
            }
        ]
        
        print("\n Testing Azure OpenAI...")
        
        # Make the request
        response = client.complete(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            max_tokens=500,
            temperature=0.1
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(" Azure OpenAI Response:")
            print(f" {content}")
            
            # Check if NHS format is being followed
            if "Priority:" in content and any(level in content for level in ["EMERGENT", "URGENT", "ROUTINE"]):
                print("\n NHS Format: CORRECT")
                return True
            else:
                print("\n NHS Format: Needs adjustment")
                return True
        else:
            print(" No response received")
            return False
            
    except Exception as e:
        print(f" Azure OpenAI Error: {str(e)}")
        return False

if __name__ == "__main__":
    print(" Testing Azure OpenAI for NHS Medical AI System")
    print("=" * 50)
    test_azure_openai()
