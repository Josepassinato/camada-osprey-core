#!/usr/bin/env python3
"""
Form Code Bug Investigation - Focused Testing
Specifically tests the H-1B vs B-1/B-2 form code mismatch issue
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://doc-validator-7.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_form_code_bug():
    """Test the specific form code bug reported"""
    print("🚨 FORM CODE BUG INVESTIGATION")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"API Base: {API_BASE}")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'FormCodeBugTester/1.0'
    })
    
    # Test 1: Create H-1B case
    print("\n🔍 TEST 1: Creating H-1B Case")
    print("-" * 40)
    
    h1b_payload = {
        "session_token": "bug_test_h1b",
        "form_code": "H-1B"
    }
    
    try:
        response = session.post(f"{API_BASE}/auto-application/start", json=h1b_payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            case_data = data.get("case", {})
            case_id = case_data.get("case_id")
            form_code = case_data.get("form_code")
            
            print(f"Case ID: {case_id}")
            print(f"Form Code Returned: {form_code}")
            print(f"Expected: H-1B")
            
            if form_code == "H-1B":
                print("✅ RESULT: H-1B form code is CORRECT")
            else:
                print(f"❌ RESULT: BUG CONFIRMED - Expected 'H-1B', got '{form_code}'")
            
            # Test 2: Update the case to see if it changes
            print(f"\n🔍 TEST 2: Updating H-1B Case {case_id}")
            print("-" * 40)
            
            update_payload = {
                "form_code": "H-1B",
                "session_token": "bug_test_h1b"
            }
            
            update_response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=update_payload)
            print(f"Update Status Code: {update_response.status_code}")
            
            if update_response.status_code == 200:
                update_data = update_response.json()
                updated_case = update_data.get("case", {})
                updated_form_code = updated_case.get("form_code")
                
                print(f"Updated Form Code: {updated_form_code}")
                
                if updated_form_code == "H-1B":
                    print("✅ RESULT: H-1B form code MAINTAINED after update")
                else:
                    print(f"❌ RESULT: BUG CONFIRMED - Form code changed to '{updated_form_code}' after update")
            
            # Test 3: Retrieve the case to verify persistence
            print(f"\n🔍 TEST 3: Retrieving H-1B Case {case_id}")
            print("-" * 40)
            
            get_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
            print(f"Get Status Code: {get_response.status_code}")
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                retrieved_form_code = get_data.get("form_code")
                
                print(f"Retrieved Form Code: {retrieved_form_code}")
                
                if retrieved_form_code == "H-1B":
                    print("✅ RESULT: H-1B form code PERSISTED correctly")
                else:
                    print(f"❌ RESULT: PERSISTENCE BUG - Form code is '{retrieved_form_code}' in database")
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    # Test 4: Create B-1/B-2 case for comparison
    print("\n🔍 TEST 4: Creating B-1/B-2 Case for Comparison")
    print("-" * 40)
    
    b1b2_payload = {
        "session_token": "bug_test_b1b2",
        "form_code": "B-1/B-2"
    }
    
    try:
        response = session.post(f"{API_BASE}/auto-application/start", json=b1b2_payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            case_data = data.get("case", {})
            case_id = case_data.get("case_id")
            form_code = case_data.get("form_code")
            
            print(f"Case ID: {case_id}")
            print(f"Form Code Returned: {form_code}")
            print(f"Expected: B-1/B-2")
            
            if form_code == "B-1/B-2":
                print("✅ RESULT: B-1/B-2 form code is CORRECT")
            else:
                print(f"❌ RESULT: B-1/B-2 BUG - Expected 'B-1/B-2', got '{form_code}'")
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    # Test 5: Check for default behavior
    print("\n🔍 TEST 5: Testing Default Behavior (No form_code)")
    print("-" * 40)
    
    default_payload = {
        "session_token": "bug_test_default"
    }
    
    try:
        response = session.post(f"{API_BASE}/auto-application/start", json=default_payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            case_data = data.get("case", {})
            case_id = case_data.get("case_id")
            form_code = case_data.get("form_code")
            
            print(f"Case ID: {case_id}")
            print(f"Default Form Code: {form_code}")
            
            if form_code is None:
                print("✅ RESULT: No default form code (correct)")
            elif form_code == "B-1/B-2":
                print("⚠️ RESULT: Default is B-1/B-2 - this might be the source of the bug")
            else:
                print(f"ℹ️ RESULT: Default form code is '{form_code}'")
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 FORM CODE BUG INVESTIGATION COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_form_code_bug()