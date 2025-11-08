#!/usr/bin/env python3
"""
Debug Form Code Test - Detailed investigation
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://owlagent.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def debug_form_code():
    """Debug the form code issue with detailed logging"""
    print("🐛 DEBUG FORM CODE INVESTIGATION")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'DebugFormCodeTester/1.0'
    })
    
    # Create a new H-1B case
    print("🔍 Creating new H-1B case...")
    
    h1b_payload = {
        "session_token": "debug_h1b_test",
        "form_code": "H-1B"
    }
    
    try:
        # Step 1: Create case
        create_response = session.post(f"{API_BASE}/auto-application/start", json=h1b_payload)
        print(f"Create Status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            create_data = create_response.json()
            print("CREATE RESPONSE:")
            print(json.dumps(create_data, indent=2))
            
            case_data = create_data.get("case", {})
            case_id = case_data.get("case_id")
            create_form_code = case_data.get("form_code")
            
            print(f"\nCREATE RESULTS:")
            print(f"  Case ID: {case_id}")
            print(f"  Form Code: {create_form_code}")
            
            # Step 2: Retrieve case immediately
            print(f"\n🔍 Retrieving case {case_id}...")
            
            get_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
            print(f"Get Status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                print("GET RESPONSE:")
                print(json.dumps(get_data, indent=2))
                
                # Check if response has "case" wrapper
                if "case" in get_data:
                    retrieved_case = get_data["case"]
                    retrieved_form_code = retrieved_case.get("form_code")
                    print(f"\nGET RESULTS (with case wrapper):")
                    print(f"  Form Code: {retrieved_form_code}")
                else:
                    # Maybe it's returned directly
                    retrieved_form_code = get_data.get("form_code")
                    print(f"\nGET RESULTS (direct):")
                    print(f"  Form Code: {retrieved_form_code}")
                
                # Step 3: Compare
                print(f"\n📊 COMPARISON:")
                print(f"  Created with: {create_form_code}")
                print(f"  Retrieved as: {retrieved_form_code}")
                
                if create_form_code == retrieved_form_code:
                    print("✅ FORM CODE CONSISTENCY: PASS")
                else:
                    print("❌ FORM CODE CONSISTENCY: FAIL")
                    print("🚨 BUG CONFIRMED: Form code changes between create and retrieve")
            else:
                print(f"❌ GET FAILED: {get_response.text}")
        else:
            print(f"❌ CREATE FAILED: {create_response.text}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_form_code()