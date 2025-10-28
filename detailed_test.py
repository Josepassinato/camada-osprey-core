#!/usr/bin/env python3
"""
DETAILED INVESTIGATION - SPECIFIC ENDPOINT TESTING
Investigate specific issues found in regression test
"""

import requests
import json
import uuid
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 DETAILED INVESTIGATION")
print(f"🌐 URL: {BACKEND_URL}")
print("="*60)

def test_case_update_issue():
    """Test the case update issue specifically"""
    print("📋 TESTING CASE UPDATE ISSUE...")
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # First create a user and get auth token
    test_email = f"detailed.test.{uuid.uuid4().hex[:6]}@test.com"
    signup_data = {
        "email": test_email,
        "password": "DetailedTest2024!",
        "first_name": "Detailed",
        "last_name": "Test"
    }
    
    try:
        signup_response = session.post(f"{API_BASE}/auth/signup", json=signup_data)
        print(f"   Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            data = signup_response.json()
            token = data.get('token')
            if token:
                session.headers.update({'Authorization': f'Bearer {token}'})
                print(f"   ✅ Auth token obtained")
            else:
                print(f"   ❌ No token in response: {data}")
                return
        else:
            print(f"   ❌ Signup failed: {signup_response.text[:200]}")
            return
        
        # Create a case
        start_response = session.post(f"{API_BASE}/auto-application/start", json={})
        print(f"   Start Case Status: {start_response.status_code}")
        
        if start_response.status_code == 200:
            start_data = start_response.json()
            print(f"   Start Response: {json.dumps(start_data, indent=2)}")
            
            case_data = start_data.get('case', {})
            case_id = case_data.get('case_id')
            
            if case_id:
                print(f"   ✅ Case created: {case_id}")
                
                # Try to update the case
                update_data = {
                    "form_code": "H-1B",
                    "status": "form_selected"
                }
                
                update_response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=update_data)
                print(f"   Update Status: {update_response.status_code}")
                print(f"   Update Response: {update_response.text}")
                
                if update_response.status_code == 200:
                    update_result = update_response.json()
                    print(f"   ✅ Update successful: {json.dumps(update_result, indent=2)}")
                else:
                    print(f"   ❌ Update failed")
            else:
                print(f"   ❌ No case_id in response")
        else:
            print(f"   ❌ Start case failed: {start_response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def test_owl_agent_issue():
    """Test the Owl Agent session issue"""
    print("\n🦉 TESTING OWL AGENT ISSUE...")
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # Test without auth first
    session_data = {
        "case_id": "TEST-CASE-123",
        "visa_type": "H-1B",
        "language": "pt"
    }
    
    try:
        response = session.post(f"{API_BASE}/owl-agent/start-session", json=session_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Session data: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Failed to create session")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def test_document_validation_capabilities():
    """Test document validation capabilities endpoint"""
    print("\n📄 TESTING DOCUMENT VALIDATION CAPABILITIES...")
    
    session = requests.Session()
    
    try:
        response = session.get(f"{API_BASE}/documents/validation-capabilities")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Capabilities available")
            print(f"   Keys: {list(data.keys())}")
            
            # Check for specific fields that were mentioned in the test
            capabilities = data.get('capabilities', {})
            validation_engines = data.get('validation_engines')
            supported_types = data.get('supported_document_types')
            
            print(f"   Capabilities: {'✓' if capabilities else '✗'}")
            print(f"   Validation Engines: {'✓' if validation_engines else '✗'}")
            print(f"   Supported Types: {'✓' if supported_types else '✗'}")
            
        else:
            print(f"   ❌ Failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def test_cors_issue():
    """Test CORS issue"""
    print("\n🌐 TESTING CORS ISSUE...")
    
    session = requests.Session()
    
    try:
        # Test OPTIONS request
        response = session.options(f"{API_BASE}/auth/login")
        print(f"   OPTIONS Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # Check CORS headers
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        print(f"   CORS Headers: {cors_headers}")
        
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_case_update_issue()
    test_owl_agent_issue()
    test_document_validation_capabilities()
    test_cors_issue()
    print("\n" + "="*60)
    print("🔍 DETAILED INVESTIGATION COMPLETE")