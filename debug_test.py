#!/usr/bin/env python3
"""
Debug specific issues found in production verification
"""

import requests
import json
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://iaimmigration.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def debug_case_update():
    """Debug the case update issue"""
    print("🔍 DEBUGGING CASE UPDATE ISSUE")
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
    
    # Test different update payloads
    test_payloads = [
        {"form_code": "H-1B"},
        {"status": "form_selected"},
        {"form_code": "H-1B", "status": "form_selected"},
        {"basic_data": {"nome": "Carlos Silva"}},
        {"form_code": "H-1B", "status": "form_selected", "basic_data": {"nome": "Carlos Silva"}}
    ]
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\n🧪 Test {i}: {payload}")
        
        response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=payload)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: form_code={data.get('form_code')}, status={data.get('status')}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
    
    # Get final case state
    get_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
    if get_response.status_code == 200:
        final_data = get_response.json()
        print(f"\n📋 Final case state:")
        print(f"   form_code: {final_data.get('form_code')}")
        print(f"   status: {final_data.get('status')}")
        print(f"   basic_data: {final_data.get('basic_data')}")

def debug_owl_agent():
    """Debug the Owl Agent issue"""
    print("\n🦉 DEBUGGING OWL AGENT ISSUE")
    print("="*50)
    
    session = requests.Session()
    
    # Test Owl Agent start session
    session_data = {
        "case_id": "TEST-CASE-123",
        "visa_type": "H-1B",
        "language": "pt"
    }
    
    response = session.post(f"{API_BASE}/owl-agent/start-session", json=session_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    debug_case_update()
    debug_owl_agent()