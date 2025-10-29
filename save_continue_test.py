#!/usr/bin/env python3
"""
OSPREY Save and Continue Later Functionality Tests
Focused testing for the review request: Save and Continue Later functionality
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 Testing Save and Continue Later at: {API_BASE}")
print("=" * 60)

# Global variables for test data
TEST_USER = {
    "email": "savetest@osprey.com",
    "password": "SaveTest123",
    "first_name": "Carlos Eduardo",
    "last_name": "Silva Santos"
}
AUTH_TOKEN = None
USER_ID = None
AUTO_APPLICATION_CASE_ID = None

def test_user_signup():
    """Test user registration"""
    print("\n👤 Testing User Signup...")
    global AUTH_TOKEN, USER_ID
    
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "first_name": TEST_USER["first_name"],
        "last_name": TEST_USER["last_name"],
        "phone": "+55 11 99999-9999"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/signup", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            USER_ID = data.get('user', {}).get('id')
            print(f"✅ User signup successful")
            print(f"   User ID: {USER_ID}")
            print(f"   Email: {data.get('user', {}).get('email')}")
            print(f"   Name: {data.get('user', {}).get('first_name')} {data.get('user', {}).get('last_name')}")
            print(f"   Token received: {'Yes' if AUTH_TOKEN else 'No'}")
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️  User already exists, proceeding to login test")
            return True
        else:
            print(f"❌ User signup failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User signup error: {str(e)}")
        return False

def test_user_login():
    """Test user authentication"""
    print("\n🔐 Testing User Login...")
    global AUTH_TOKEN, USER_ID
    
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            USER_ID = data.get('user', {}).get('id')
            print(f"✅ User login successful")
            print(f"   User ID: {USER_ID}")
            print(f"   Email: {data.get('user', {}).get('email')}")
            print(f"   Name: {data.get('user', {}).get('first_name')} {data.get('user', {}).get('last_name')}")
            print(f"   Token received: {'Yes' if AUTH_TOKEN else 'No'}")
            return True
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User login error: {str(e)}")
        return False

def test_save_and_continue_later_flow():
    """Test complete Save and Continue Later functionality"""
    print("\n💾 Testing Save and Continue Later Flow...")
    global AUTO_APPLICATION_CASE_ID
    
    try:
        # Step 1: Create an anonymous auto application case (H-1B visa type)
        print("   Step 1: Creating anonymous H-1B auto application case...")
        
        case_payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            case_data = data.get('case', {})
            AUTO_APPLICATION_CASE_ID = case_data.get('case_id')
            print(f"   ✅ Anonymous case created: {AUTO_APPLICATION_CASE_ID}")
            
            # Step 2: Add some basic data to the case
            print("   Step 2: Adding basic data to case...")
            
            basic_data = {
                "firstName": "Carlos Eduardo",
                "lastName": "Silva Santos",
                "dateOfBirth": "1990-03-15",
                "nationality": "Brazilian",
                "email": "carlos.silva@email.com",
                "phone": "+55 11 99999-8888",
                "currentAddress": "Rua das Flores, 123",
                "city": "São Paulo",
                "state": "SP",
                "zipCode": "01234-567"
            }
            
            update_payload = {
                "basic_data": basic_data,
                "status": "basic_data",
                "current_step": "basic-data"
            }
            
            update_response = requests.put(
                f"{API_BASE}/auto-application/case/{AUTO_APPLICATION_CASE_ID}", 
                json=update_payload, 
                timeout=10
            )
            
            if update_response.status_code == 200:
                print("   ✅ Basic data added to case")
                
                # Step 3: Associate case with user account (Save Progress)
                print("   Step 3: Associating case with user account...")
                
                if not AUTH_TOKEN:
                    print("   ❌ No auth token available for case association")
                    return False
                
                headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
                
                associate_response = requests.post(
                    f"{API_BASE}/auto-application/case/{AUTO_APPLICATION_CASE_ID}/associate-user",
                    json={"save_progress": True},
                    headers=headers,
                    timeout=10
                )
                
                if associate_response.status_code == 200:
                    assoc_data = associate_response.json()
                    print(f"   ✅ Case associated with user: {assoc_data.get('user_id')}")
                    
                    # Step 4: Verify dashboard shows the saved application
                    print("   Step 4: Verifying dashboard shows saved application...")
                    
                    dashboard_response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=10)
                    
                    if dashboard_response.status_code == 200:
                        dashboard_data = dashboard_response.json()
                        auto_applications = dashboard_data.get('auto_applications', [])
                        
                        # Check if our case appears in auto_applications
                        saved_case = next((app for app in auto_applications if app.get('id') == AUTO_APPLICATION_CASE_ID), None)
                        
                        if saved_case:
                            print(f"   ✅ Saved application found in dashboard")
                            print(f"      Title: {saved_case.get('title')}")
                            print(f"      Status: {saved_case.get('status')}")
                            print(f"      Form Code: {saved_case.get('form_code')}")
                            print(f"      Progress: {saved_case.get('progress_percentage')}%")
                            
                            # Step 5: Test case retrieval and data persistence
                            print("   Step 5: Testing case retrieval and data persistence...")
                            
                            case_response = requests.get(
                                f"{API_BASE}/auto-application/case/{AUTO_APPLICATION_CASE_ID}",
                                headers=headers,
                                timeout=10
                            )
                            
                            if case_response.status_code == 200:
                                case_data = case_response.json()
                                retrieved_case = case_data.get('case', {})
                                
                                # Verify all data is preserved
                                preserved_basic_data = retrieved_case.get('basic_data', {})
                                user_id = retrieved_case.get('user_id')
                                is_anonymous = retrieved_case.get('is_anonymous', True)
                                
                                print(f"   ✅ Case data retrieved successfully")
                                print(f"      User ID: {user_id}")
                                print(f"      Is Anonymous: {is_anonymous}")
                                print(f"      Form Code: {retrieved_case.get('form_code')}")
                                print(f"      Status: {retrieved_case.get('status')}")
                                
                                # Verify basic data preservation
                                if (preserved_basic_data.get('firstName') == basic_data['firstName'] and
                                    preserved_basic_data.get('email') == basic_data['email'] and
                                    preserved_basic_data.get('nationality') == basic_data['nationality']):
                                    print("   ✅ All application data preserved correctly")
                                    
                                    # Step 6: Test user cases endpoint
                                    print("   Step 6: Testing user cases endpoint...")
                                    
                                    user_cases_response = requests.get(f"{API_BASE}/user/cases", headers=headers, timeout=10)
                                    
                                    if user_cases_response.status_code == 200:
                                        cases_data = user_cases_response.json()
                                        user_cases = cases_data.get('cases', [])
                                        
                                        # Find our case in user's cases
                                        our_case = next((case for case in user_cases if case.get('case_id') == AUTO_APPLICATION_CASE_ID), None)
                                        
                                        if our_case:
                                            print(f"   ✅ Case found in user's cases list")
                                            print(f"      Total user cases: {cases_data.get('total', 0)}")
                                            
                                            print("\n✅ SAVE AND CONTINUE LATER FLOW - COMPLETE SUCCESS!")
                                            print("   All test scenarios passed:")
                                            print("   ✓ Anonymous case creation")
                                            print("   ✓ Basic data addition")
                                            print("   ✓ User association (Save Progress)")
                                            print("   ✓ Dashboard integration")
                                            print("   ✓ Case retrieval")
                                            print("   ✓ Data persistence")
                                            print("   ✓ User cases listing")
                                            
                                            return True
                                        else:
                                            print("   ❌ Case not found in user's cases list")
                                            return False
                                    else:
                                        print(f"   ❌ User cases endpoint failed: {user_cases_response.status_code}")
                                        return False
                                else:
                                    print("   ❌ Application data not preserved correctly")
                                    return False
                            else:
                                print(f"   ❌ Case retrieval failed: {case_response.status_code}")
                                return False
                        else:
                            print("   ❌ Saved application not found in dashboard")
                            return False
                    else:
                        print(f"   ❌ Dashboard check failed: {dashboard_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Case association failed: {associate_response.status_code}")
                    print(f"      Error: {associate_response.text}")
                    return False
            else:
                print(f"   ❌ Basic data update failed: {update_response.status_code}")
                return False
        else:
            print(f"   ❌ Case creation failed: {response.status_code}")
            print(f"      Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Save and Continue Later flow error: {str(e)}")
        return False

def test_authentication_with_case_association():
    """Test authentication system works with case association"""
    print("\n🔐 Testing Authentication with Case Association...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for authentication test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test 1: Verify login works
        print("   Test 1: Verifying user authentication...")
        
        profile_response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print(f"   ✅ User authenticated successfully")
            print(f"      User: {profile.get('first_name')} {profile.get('last_name')}")
            print(f"      Email: {profile.get('email')}")
            
            # Test 2: Verify JWT token validation works for case association
            print("   Test 2: Testing JWT token validation...")
            
            # Create a test case to associate
            test_case_payload = {
                "form_code": "F-1",
                "session_token": str(uuid.uuid4())
            }
            
            case_response = requests.post(f"{API_BASE}/auto-application/start", json=test_case_payload, timeout=10)
            
            if case_response.status_code == 200:
                test_case_data = case_response.json()
                case_info = test_case_data.get('case', {})
                test_case_id = case_info.get('case_id')
                
                print(f"   ✅ Test case created: {test_case_id}")
                
                # Try to associate with valid token
                associate_response = requests.post(
                    f"{API_BASE}/auto-application/case/{test_case_id}/associate-user",
                    json={"test_association": True},
                    headers=headers,
                    timeout=10
                )
                
                if associate_response.status_code == 200:
                    print("   ✅ JWT token validation working for case association")
                    
                    # Test 3: Try with invalid token
                    print("   Test 3: Testing invalid token rejection...")
                    
                    invalid_headers = {"Authorization": "Bearer invalid-token-12345"}
                    
                    invalid_response = requests.post(
                        f"{API_BASE}/auto-application/case/{test_case_id}/associate-user",
                        json={"test_association": True},
                        headers=invalid_headers,
                        timeout=10
                    )
                    
                    if invalid_response.status_code == 401:
                        print("   ✅ Invalid token properly rejected")
                        
                        # Test 4: Try without token
                        print("   Test 4: Testing missing token rejection...")
                        
                        no_token_response = requests.post(
                            f"{API_BASE}/auto-application/case/{test_case_id}/associate-user",
                            json={"test_association": True},
                            timeout=10
                        )
                        
                        if no_token_response.status_code == 401:
                            print("   ✅ Missing token properly rejected")
                            return True
                        else:
                            print(f"   ❌ Missing token not rejected: {no_token_response.status_code}")
                            return False
                    else:
                        print(f"   ❌ Invalid token not rejected: {invalid_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Case association with valid token failed: {associate_response.status_code}")
                    return False
            else:
                print(f"   ❌ Test case creation failed: {case_response.status_code}")
                return False
        else:
            print(f"   ❌ User authentication failed: {profile_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication with case association error: {str(e)}")
        return False

def test_dashboard_auto_applications():
    """Test dashboard returns user's auto_applications correctly"""
    print("\n📊 Testing Dashboard Auto Applications...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for dashboard test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for auto_applications in response
            auto_applications = data.get('auto_applications', [])
            all_applications = data.get('applications', [])
            
            print(f"✅ Dashboard loaded successfully")
            print(f"   Auto applications: {len(auto_applications)}")
            print(f"   Total applications: {len(all_applications)}")
            
            # Verify structure of auto_applications
            if auto_applications:
                sample_app = auto_applications[0]
                required_fields = ['id', 'title', 'status', 'type', 'form_code', 'progress_percentage']
                
                missing_fields = [field for field in required_fields if field not in sample_app]
                
                if not missing_fields:
                    print("   ✅ Auto application structure correct")
                    print(f"      Sample app: {sample_app.get('title')} ({sample_app.get('form_code')})")
                    print(f"      Status: {sample_app.get('status')}")
                    print(f"      Progress: {sample_app.get('progress_percentage')}%")
                    
                    # Check if auto_applications are also included in main applications list
                    auto_app_ids = [app.get('id') for app in auto_applications]
                    main_app_ids = [app.get('id') for app in all_applications]
                    
                    auto_in_main = any(app_id in main_app_ids for app_id in auto_app_ids)
                    
                    if auto_in_main:
                        print("   ✅ Auto applications properly integrated in main applications list")
                    else:
                        print("   ⚠️  Auto applications not found in main applications list")
                    
                    return True
                else:
                    print(f"   ❌ Auto application missing fields: {missing_fields}")
                    return False
            else:
                print("   ⚠️  No auto applications found (may be expected if none saved)")
                return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard auto applications test error: {str(e)}")
        return False

def test_case_data_persistence():
    """Test that case association preserves all application data"""
    print("\n💾 Testing Case Data Persistence...")
    
    if not AUTO_APPLICATION_CASE_ID or not AUTH_TOKEN:
        print("❌ No case ID or auth token available for persistence test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Get the case details
        response = requests.get(
            f"{API_BASE}/auto-application/case/{AUTO_APPLICATION_CASE_ID}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            case = data.get('case', {})
            
            print(f"✅ Case retrieved successfully")
            print(f"   Case ID: {case.get('case_id')}")
            print(f"   Form Code: {case.get('form_code')}")
            print(f"   Status: {case.get('status')}")
            print(f"   User ID: {case.get('user_id')}")
            print(f"   Is Anonymous: {case.get('is_anonymous')}")
            
            # Check critical data preservation
            checks = {
                "Case ID preserved": case.get('case_id') == AUTO_APPLICATION_CASE_ID,
                "Form code preserved": case.get('form_code') == 'H-1B',
                "User association": case.get('user_id') is not None,
                "No longer anonymous": case.get('is_anonymous') == False,
                "Basic data preserved": case.get('basic_data') is not None,
                "Status preserved": case.get('status') is not None,
                "Created timestamp": case.get('created_at') is not None,
                "Updated timestamp": case.get('updated_at') is not None
            }
            
            passed_checks = sum(checks.values())
            total_checks = len(checks)
            
            print(f"\n   Data Persistence Checks: {passed_checks}/{total_checks}")
            
            for check_name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
            
            # Check basic data details if present
            basic_data = case.get('basic_data', {})
            if basic_data:
                print(f"\n   Basic Data Details:")
                print(f"      Name: {basic_data.get('firstName')} {basic_data.get('lastName')}")
                print(f"      Email: {basic_data.get('email')}")
                print(f"      Nationality: {basic_data.get('nationality')}")
                print(f"      Phone: {basic_data.get('phone')}")
            
            if passed_checks >= 6:  # At least 75% of checks should pass
                print(f"\n✅ Case data persistence working correctly")
                return True
            else:
                print(f"\n❌ Case data persistence issues detected")
                return False
        else:
            print(f"❌ Case retrieval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Case data persistence test error: {str(e)}")
        return False

def run_save_and_continue_tests():
    """Run focused Save and Continue Later tests"""
    print("🎯 STARTING SAVE AND CONTINUE LATER FOCUSED TESTS")
    print("=" * 60)
    
    # Ensure we have authentication first
    print("Setting up authentication...")
    if not test_user_signup():
        print("Trying login instead...")
        if not test_user_login():
            print("❌ Authentication setup failed")
            return False
    
    test_results = []
    
    # Run focused tests
    test_results.append(("Save and Continue Later Flow", test_save_and_continue_later_flow()))
    test_results.append(("Authentication with Case Association", test_authentication_with_case_association()))
    test_results.append(("Dashboard Auto Applications", test_dashboard_auto_applications()))
    test_results.append(("Case Data Persistence", test_case_data_persistence()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 SAVE AND CONTINUE LATER TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"📊 TOTAL: {len(test_results)} tests | ✅ PASSED: {passed} | ❌ FAILED: {failed}")
    
    success_rate = (passed / len(test_results)) * 100
    print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Save and Continue Later functionality working perfectly")
    elif success_rate >= 75:
        print("👍 GOOD! Minor issues to address")
    elif success_rate >= 50:
        print("⚠️  NEEDS ATTENTION! Several issues found")
    else:
        print("🚨 CRITICAL! Major issues require immediate attention")
    
    return success_rate >= 75

if __name__ == "__main__":
    run_save_and_continue_tests()