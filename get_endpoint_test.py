#!/usr/bin/env python3
"""
GET Endpoint Investigation - Test the retrieval issue
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_get_endpoint():
    """Test the GET endpoint with different parameters"""
    print("🔍 GET ENDPOINT INVESTIGATION")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'GetEndpointTester/1.0'
    })
    
    # Test case from database: OSP-112BB414 with session bug_test_h1b
    case_id = "OSP-112BB414"
    session_token = "bug_test_h1b"
    
    print(f"Testing Case ID: {case_id}")
    print(f"Session Token: {session_token}")
    print()
    
    # Test 1: GET without session_token
    print("🔍 TEST 1: GET without session_token")
    print("-" * 30)
    
    try:
        response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            case_data = data.get("case", {})
            form_code = case_data.get("form_code")
            print(f"Form Code: {form_code}")
            print(f"Full Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    print()
    
    # Test 2: GET with session_token
    print("🔍 TEST 2: GET with session_token")
    print("-" * 30)
    
    try:
        response = session.get(f"{API_BASE}/auto-application/case/{case_id}?session_token={session_token}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            case_data = data.get("case", {})
            form_code = case_data.get("form_code")
            print(f"Form Code: {form_code}")
            print(f"Full Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")
    
    print()
    
    # Test 3: Test B-1/B-2 case
    print("🔍 TEST 3: GET B-1/B-2 case")
    print("-" * 30)
    
    b1b2_case_id = "OSP-3D658059"
    b1b2_session = "bug_test_b1b2"
    
    try:
        response = session.get(f"{API_BASE}/auto-application/case/{b1b2_case_id}?session_token={b1b2_session}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            case_data = data.get("case", {})
            form_code = case_data.get("form_code")
            print(f"Form Code: {form_code}")
            print(f"Expected: B-1/B-2")
            
            if form_code == "B-1/B-2":
                print("✅ B-1/B-2 retrieval is CORRECT")
            else:
                print(f"❌ B-1/B-2 retrieval BUG: got '{form_code}'")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    test_get_endpoint()