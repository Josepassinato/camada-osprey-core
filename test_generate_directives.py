#!/usr/bin/env python3
"""
Test generate-directives endpoint specifically
"""

import requests
import json
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_generate_directives():
    """Test generate-directives with different visa types"""
    
    visa_types = ["I-589", "H1B", "F1", "B1B2"]
    
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
                print(f"Response keys: {list(data.keys())}")
                
                if "error" in data:
                    print(f"❌ Error: {data['error']}")
                else:
                    directives_text = data.get("directives_text", "")
                    print(f"✅ Generated {len(directives_text)} characters")
                    if directives_text:
                        print(f"Preview: {directives_text[:200]}...")
                    else:
                        print("⚠️ Empty directives text")
                        print(f"Full response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_generate_directives()