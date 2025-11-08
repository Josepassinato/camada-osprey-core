#!/usr/bin/env python3
"""
Debug the actual response structure
"""

import requests
import json
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://owlagent.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def debug_response_structure():
    """Debug the actual response structure"""
    print("🔍 DEBUGGING RESPONSE STRUCTURE")
    print("="*50)
    
    # Login first
    login_data = {
        "email": "carlos.silva.bd5ede@gmail.com",
        "password": "CarlosSilva2024!"
    }
    
    session = requests.Session()
    login_response = session.post(f"{API_BASE}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()['token']
    session.headers.update({'Authorization': f'Bearer {token}'})
    print(f"✅ Login successful")
    
    # Create a new case
    start_response = session.post(f"{API_BASE}/auto-application/start", json={})
    if start_response.status_code != 200:
        print(f"❌ Case creation failed: {start_response.status_code}")
        return
    
    case_data = start_response.json().get('case', {})
    case_id = case_data.get('case_id')
    print(f"✅ Case created: {case_id}")
    
    # Test update
    payload = {"form_code": "H-1B", "status": "form_selected"}
    
    response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=payload)
    print(f"\n📋 PUT Response:")
    print(f"   Status: {response.status_code}")
    print(f"   Full Response: {json.dumps(response.json(), indent=2)}")
    
    # Get case to verify
    get_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
    print(f"\n📋 GET Response:")
    print(f"   Status: {get_response.status_code}")
    print(f"   Full Response: {json.dumps(get_response.json(), indent=2)}")

if __name__ == "__main__":
    debug_response_structure()