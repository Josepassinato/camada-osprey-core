#!/usr/bin/env python3
"""
Simple test for the visa API endpoint to debug the issue
"""

import requests
import json

BACKEND_URL = "https://visaflow-5.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_simple():
    """Simple test to debug the visa API"""
    
    print("🧪 SIMPLE VISA API TEST")
    print("=" * 50)
    
    # Test the corrected payload format based on the API definition
    payload = {
        "user_input": "Preciso estender meu visto de turista B-2 por 6 meses devido a emergência médica",
        "applicant_data": {},
        "enable_qa": True
    }
    
    try:
        print(f"🔗 Testing: POST {API_BASE}/visa/generate")
        print(f"📤 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{API_BASE}/visa/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ SUCCESS: API is working correctly")
                return True
            else:
                print(f"❌ API returned success=false: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_simple()
    print(f"\n🎯 Result: {'PASSED' if success else 'FAILED'}")