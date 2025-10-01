#!/usr/bin/env python3
"""
Test generate-directives with correct visa type formats
"""

import requests
import json
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://immigent.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_correct_visa_types():
    """Test with correct visa type formats from YAML"""
    
    # Correct visa types from YAML file
    visa_types = ["H1B", "L1A", "O1", "F1", "B1_B2", "I130_MARRIAGE", "I485"]
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'DirectivesTest/1.0'
    })
    
    for visa_type in visa_types:
        print(f"\n🔍 Testing visa type: {visa_type}")
        print("-" * 40)
        
        payload = {
            "visa_type": visa_type,
            "language": "pt"
        }
        
        try:
            response = session.post(
                f"{API_BASE}/llm/dr-paula/generate-directives",
                json=payload
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" in data:
                    print(f"❌ Error: {data['error']}")
                else:
                    directives_text = data.get("directives_text", "")
                    print(f"✅ Generated {len(directives_text)} characters")
                    if directives_text:
                        print(f"Preview: {directives_text[:100]}...")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_correct_visa_types()