#!/usr/bin/env python3
"""
Debug specific failing tests
"""

import requests
import json

API_BASE = "https://validai-imm.preview.emergentagent.com/api"

def test_request_complement():
    """Test request complement endpoint"""
    payload = {
        "visa_type": "H1B",
        "issues": ["Missing salary information", "Work location not specified"]
    }
    
    response = requests.post(
        f"{API_BASE}/llm/dr-paula/request-complement",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        guidance = result.get('complement_request', '')
        print(f"Guidance length: {len(guidance)}")
        return len(guidance) > 10
    
    return False

if __name__ == "__main__":
    success = test_request_complement()
    print(f"Test success: {success}")