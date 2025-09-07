"""
Test individual AI responses to debug any Unknown priority issue
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_API_URL = "https://models.inference.ai.azure.com/v1/chat/completions"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL_NAME = "phi-4"

def test_ai_response():
    """Test a single AI response to see the actual output"""
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple routine case
    messages = [
        {
            "role": "system",
            "content": "You are a senior NHS clinical triage specialist with 15+ years emergency medicine experience. Follow NHS Emergency Care Standards and NICE guidelines for accurate medical referral prioritization. CRITICAL: Avoid over-escalation of routine cases - most NHS referrals are routine unless there are acute concerning features. Be concise and decisive."
        },
        {
            "role": "user",
            "content": """You are an NHS clinical triage specialist. Classify this referral according to NHS Emergency Care Standards:

**NHS PRIORITY CLASSIFICATIONS (BE PRECISE - AVOID OVER-ESCALATION):**

• **EMERGENT (<15 minutes)**: ONLY life-threatening conditions requiring immediate intervention
• **URGENT (<2 hours)**: Serious conditions requiring prompt assessment  
• **ROUTINE (<18 weeks)**: MOST standard NHS care - DO NOT over-escalate these
  - ALL routine follow-ups and monitoring (diabetes, hypertension, COPD, stable heart disease)
  - ALL screening appointments (mammography, colonoscopy, cervical, diabetic eye)

**CRITICAL RULE: If the case mentions 'routine', 'annual', 'follow-up', 'screening', 'stable', 'well-controlled', or 'monitoring' - it is likely ROUTINE unless there are acute concerning features.**

**CASE DETAILS:**
Patient ID: PT002
Name: Mary Johnson  
Age: 58
Address: 456 Oak Avenue, Manchester

Annual diabetes review. Patient reports good glucose control with metformin 1g BD.
Recent HbA1c 6.8% (improved from 7.2% six months ago). BP 128/78 on lisinopril 10mg.
No symptoms of diabetic complications. Feet examination normal, pulses present.
Requests dietary advice and annual retinal screening due.

Staff: Practice Nurse Jenkins
Location: Greenfield Medical Centre

Respond with the NHS priority: Emergent, Urgent, or Routine. Then explain your reasoning."""
        }
    ]
    
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 750,
        "temperature": 0.05,
        "top_p": 0.8,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }
    
    try:
        response = requests.post(GITHUB_API_URL, headers=headers, json=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
            print(f"\n AI Response:")
            print(f" {content}")
            
            # Test priority extraction
            priority = extract_priority(content)
            print(f"\n Extracted Priority: {priority}")
            
        else:
            print(f" Error Response: {response.text}")
            
    except Exception as e:
        print(f" Exception: {str(e)}")

def extract_priority(response_text):
    """Extract priority from AI response - improved logic"""
    if not response_text:
        return "Unknown"
    
    text_lower = response_text.lower()
    
    # Look for explicit priority classifications first
    patterns = [
        "priority classification: routine",
        "priority: routine", 
        "classification: routine",
        "nhs priority: routine",
        "priority classification: emergent",
        "priority: emergent",
        "classification: emergent", 
        "nhs priority: emergent",
        "priority classification: urgent",
        "priority: urgent",
        "classification: urgent",
        "nhs priority: urgent"
    ]
    
    for pattern in patterns:
        if pattern in text_lower:
            if "routine" in pattern:
                return "Routine"
            elif "emergent" in pattern:
                return "Emergent"
            elif "urgent" in pattern:
                return "Urgent"
    
    # Look for standalone priority words in context
    lines = response_text.split('\n')
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check for lines that explicitly state the priority
        if (line_lower.startswith('routine') or 
            line_lower.startswith('**routine') or
            'this case should be classified as routine' in line_lower or
            'classification: routine' in line_lower):
            return "Routine"
        elif (line_lower.startswith('emergent') or 
              line_lower.startswith('**emergent') or
              'this case should be classified as emergent' in line_lower or
              'classification: emergent' in line_lower):
            return "Emergent"
        elif (line_lower.startswith('urgent') or 
              line_lower.startswith('**urgent') or
              'this case should be classified as urgent' in line_lower or
              'classification: urgent' in line_lower):
            return "Urgent"
    
    # Fallback to simple keyword matching (last resort)
    if "emergent" in text_lower and "routine" not in text_lower and "urgent" not in text_lower:
        return "Emergent"
    elif "routine" in text_lower and "emergent" not in text_lower:
        return "Routine"
    elif "urgent" in text_lower and "routine" not in text_lower and "emergent" not in text_lower:
        return "Urgent"
    
    return "Unknown"

if __name__ == "__main__":
    test_ai_response()
