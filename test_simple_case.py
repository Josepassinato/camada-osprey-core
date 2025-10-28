#!/usr/bin/env python3
"""
Simple test to debug case update issues
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_case_operations():
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'SimpleCaseTest/1.0'
    })
    
    print("🧪 TESTING CASE OPERATIONS")
    print("=" * 50)
    
    # Step 1: Create case
    print("\n1. Creating case...")
    payload = {}
    response = session.post(f"{API_BASE}/auto-application/start", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        case_data = data.get('case', {})
        case_id = case_data.get('case_id')
        print(f"Case ID: {case_id}")
        
        if case_id:
            # Step 2: Update case with H-1B
            print(f"\n2. Updating case {case_id} with H-1B...")
            update_payload = {
                "form_code": "H-1B",
                "status": "form_selected"
            }
            
            update_response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=update_payload)
            print(f"Status: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            
            # Step 3: Get case to verify update
            print(f"\n3. Getting case {case_id} to verify...")
            get_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
            print(f"Status: {get_response.status_code}")
            print(f"Response: {get_response.text}")

if __name__ == "__main__":
    test_case_operations()