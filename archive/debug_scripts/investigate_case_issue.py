#!/usr/bin/env python3
"""
INVESTIGATE CASE PERSISTENCE ISSUE
Detailed investigation of the case retrieval problem
"""

import requests
import json
import uuid
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://immigration-helper-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 INVESTIGANDO PROBLEMA DE PERSISTÊNCIA DE CASO")
print(f"🌐 URL: {BACKEND_URL}")
print("="*60)

def investigate_case_persistence():
    """Investigate the case persistence issue in detail"""
    
    session = requests.Session()
    session.headers.update({'Content-Type': 'application/json'})
    
    # Setup authentication
    test_email = f"investigate.{uuid.uuid4().hex[:6]}@test.com"
    signup_data = {
        "email": test_email,
        "password": "InvestigateTest2024!",
        "first_name": "Investigate",
        "last_name": "Test"
    }
    
    try:
        # Signup
        signup_response = session.post(f"{API_BASE}/auth/signup", json=signup_data)
        print(f"📋 Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code == 200:
            data = signup_response.json()
            token = data.get('token')
            if token:
                session.headers.update({'Authorization': f'Bearer {token}'})
                print(f"   ✅ Auth token obtained")
            else:
                print(f"   ❌ No token in response")
                return
        else:
            print(f"   ❌ Signup failed: {signup_response.text[:200]}")
            return
        
        # Create case
        print(f"\n📋 Creating case...")
        start_response = session.post(f"{API_BASE}/auto-application/start", json={})
        print(f"   Start Status: {start_response.status_code}")
        
        if start_response.status_code == 200:
            start_data = start_response.json()
            print(f"   Start Response Keys: {list(start_data.keys())}")
            
            case_data = start_data.get('case', {})
            case_id = case_data.get('case_id')
            print(f"   Case ID: {case_id}")
            
            if case_id:
                # Update case
                print(f"\n📋 Updating case {case_id}...")
                update_data = {
                    "form_code": "H-1B",
                    "status": "form_selected"
                }
                
                update_response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=update_data)
                print(f"   Update Status: {update_response.status_code}")
                
                if update_response.status_code == 200:
                    update_result = update_response.json()
                    print(f"   Update Response Keys: {list(update_result.keys())}")
                    
                    case_updated = update_result.get('case', update_result)
                    print(f"   Updated Case Keys: {list(case_updated.keys())}")
                    print(f"   Form Code: {case_updated.get('form_code')}")
                    print(f"   Status: {case_updated.get('status')}")
                    print(f"   Case ID: {case_updated.get('case_id')}")
                    
                    # Now try to retrieve the case
                    print(f"\n📋 Retrieving case {case_id}...")
                    get_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
                    print(f"   Get Status: {get_response.status_code}")
                    
                    if get_response.status_code == 200:
                        get_data = get_response.json()
                        print(f"   Get Response Keys: {list(get_data.keys())}")
                        print(f"   Retrieved Case ID: {get_data.get('case_id')}")
                        print(f"   Retrieved Form Code: {get_data.get('form_code')}")
                        print(f"   Retrieved Status: {get_data.get('status')}")
                        
                        # Check if data matches
                        case_id_match = get_data.get('case_id') == case_id
                        form_code_match = get_data.get('form_code') == 'H-1B'
                        status_match = get_data.get('status') == 'form_selected'
                        
                        print(f"\n📊 VERIFICATION:")
                        print(f"   Case ID Match: {'✓' if case_id_match else '✗'}")
                        print(f"   Form Code Match: {'✓' if form_code_match else '✗'}")
                        print(f"   Status Match: {'✓' if status_match else '✗'}")
                        
                        if not (case_id_match and form_code_match and status_match):
                            print(f"\n🔍 DETAILED COMPARISON:")
                            print(f"   Expected Case ID: {case_id}")
                            print(f"   Actual Case ID: {get_data.get('case_id')}")
                            print(f"   Expected Form Code: H-1B")
                            print(f"   Actual Form Code: {get_data.get('form_code')}")
                            print(f"   Expected Status: form_selected")
                            print(f"   Actual Status: {get_data.get('status')}")
                            
                            print(f"\n📄 FULL GET RESPONSE:")
                            print(json.dumps(get_data, indent=2))
                        else:
                            print(f"\n✅ ALL DATA MATCHES - CASE PERSISTENCE WORKING CORRECTLY!")
                    else:
                        print(f"   ❌ Get failed: {get_response.text[:200]}")
                else:
                    print(f"   ❌ Update failed: {update_response.text[:200]}")
            else:
                print(f"   ❌ No case_id in start response")
        else:
            print(f"   ❌ Start failed: {start_response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    investigate_case_persistence()
    print("\n" + "="*60)
    print("🔍 INVESTIGATION COMPLETE")