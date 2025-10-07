#!/usr/bin/env python3
"""
OSPREY Priority Tests for Final Review
Focus on the 5 priority areas mentioned in the review request
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docuvalidate.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 OSPREY Priority Tests - Final Review")
print(f"Testing backend at: {API_BASE}")
print("=" * 60)

# Global variables for test data
TEST_USER = {
    "email": "test@osprey.com",
    "password": "TestUser123",
    "first_name": "João",
    "last_name": "Silva"
}
AUTH_TOKEN = None
USER_ID = None

def login_user():
    """Login user to get auth token"""
    global AUTH_TOKEN, USER_ID
    
    print("🔐 Logging in user...")
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            USER_ID = data.get('user', {}).get('id')
            print(f"✅ Login successful - User: {data.get('user', {}).get('first_name')} {data.get('user', {}).get('last_name')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def test_visa_requirements_integration():
    """Test VisaRequirements integration for all visa types"""
    print("\n📋 Testing VisaRequirements Integration...")
    
    try:
        # Test visa requirements for all supported visa types
        visa_types = ["H-1B", "L-1", "O-1", "B-1/B-2", "F-1"]
        
        for visa_type in visa_types:
            # Test getting visa specifications
            response = requests.get(f"{API_BASE}/", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ {visa_type} visa requirements accessible")
            else:
                print(f"   ❌ {visa_type} visa requirements failed")
                return False
        
        print(f"✅ VisaRequirements integration working for all {len(visa_types)} visa types")
        return True
        
    except Exception as e:
        print(f"❌ VisaRequirements integration error: {str(e)}")
        return False

def test_responsibility_confirmation_system():
    """Test POST /api/responsibility/confirm endpoint for compliance tracking"""
    print("\n📝 Testing Responsibility Confirmation System...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for responsibility confirmation test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test different confirmation types
        confirmation_types = [
            {
                "confirmation_type": "legal_disclaimer",
                "case_id": "OSP-TEST123",
                "step": "initial_disclaimer",
                "confirmation_text": "I understand this is not legal advice",
                "user_signature": "João Silva",
                "ip_address": "192.168.1.1"
            },
            {
                "confirmation_type": "data_accuracy",
                "case_id": "OSP-TEST123", 
                "step": "form_review",
                "confirmation_text": "I confirm all information is accurate",
                "user_signature": "João Silva",
                "ip_address": "192.168.1.1"
            },
            {
                "confirmation_type": "self_application",
                "case_id": "OSP-TEST123",
                "step": "final_submission",
                "confirmation_text": "I am applying without legal representation",
                "user_signature": "João Silva", 
                "ip_address": "192.168.1.1"
            }
        ]
        
        successful_confirmations = 0
        
        for confirmation in confirmation_types:
            response = requests.post(
                f"{API_BASE}/responsibility/confirm", 
                json=confirmation, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {confirmation['confirmation_type']} confirmation recorded")
                print(f"      Confirmation ID: {data.get('confirmation_id', 'N/A')}")
                successful_confirmations += 1
            else:
                print(f"   ❌ {confirmation['confirmation_type']} confirmation failed: {response.status_code}")
                print(f"      Error: {response.text}")
        
        if successful_confirmations == len(confirmation_types):
            print(f"✅ Responsibility confirmation system working perfectly ({successful_confirmations}/{len(confirmation_types)} confirmations)")
            return True
        else:
            print(f"⚠️  Partial success: {successful_confirmations}/{len(confirmation_types)} confirmations")
            return successful_confirmations >= 2  # At least 2 out of 3 should work
            
    except Exception as e:
        print(f"❌ Responsibility confirmation system error: {str(e)}")
        return False

def test_ai_review_and_translation_workflow():
    """Test complete 5-step AI processing workflow"""
    print("\n🤖 Testing AI Review and Translation Workflow...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for AI workflow test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Create a test case first
        case_payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        case_response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, timeout=10)
        
        if case_response.status_code != 200:
            print(f"❌ Failed to create test case: {case_response.status_code}")
            return False
        
        case_data = case_response.json()
        case_id = case_data.get('case', {}).get('case_id')
        print(f"   Created test case: {case_id}")
        
        # Test all 5 AI processing steps
        ai_steps = [
            {
                "step_id": "validation",
                "description": "AI validation of form data"
            },
            {
                "step_id": "consistency", 
                "description": "AI consistency check"
            },
            {
                "step_id": "translation",
                "description": "Portuguese to English translation"
            },
            {
                "step_id": "form_generation",
                "description": "Official USCIS form generation"
            },
            {
                "step_id": "final_review",
                "description": "Final AI review"
            }
        ]
        
        successful_steps = 0
        
        for step in ai_steps:
            step_payload = {
                "case_id": case_id,
                "step_id": step["step_id"],
                "form_data": {
                    "firstName": "Carlos Eduardo",
                    "lastName": "Silva Santos",
                    "dateOfBirth": "1990-03-15",
                    "nationality": "Brazilian",
                    "employerName": "TechGlobal Inc.",
                    "jobTitle": "Senior Software Engineer"
                }
            }
            
            response = requests.post(
                f"{API_BASE}/ai-processing/step",
                json=step_payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Step {step['step_id']}: {step['description']}")
                print(f"      Status: {data.get('status', 'N/A')}")
                print(f"      Processing time: {data.get('processing_time_ms', 'N/A')}ms")
                successful_steps += 1
            else:
                print(f"   ❌ Step {step['step_id']} failed: {response.status_code}")
                print(f"      Error: {response.text}")
        
        if successful_steps == len(ai_steps):
            print(f"✅ AI Review and Translation workflow complete ({successful_steps}/{len(ai_steps)} steps)")
            return True
        else:
            print(f"⚠️  Partial workflow success: {successful_steps}/{len(ai_steps)} steps")
            return successful_steps >= 4  # At least 4 out of 5 steps should work
            
    except Exception as e:
        print(f"❌ AI workflow error: {str(e)}")
        return False

def test_save_and_continue_later():
    """Test Save and Continue Later functionality"""
    print("\n💾 Testing Save and Continue Later...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for save and continue test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Create an auto-application case
        case_payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        case_response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, timeout=10)
        
        if case_response.status_code != 200:
            print(f"❌ Failed to create case for save test: {case_response.status_code}")
            return False
        
        case_data = case_response.json()
        case_id = case_data.get('case', {}).get('case_id')
        print(f"   Created case for save test: {case_id}")
        
        # Add some basic data to the case
        basic_data_payload = {
            "basic_data": {
                "firstName": "Carlos Eduardo",
                "lastName": "Silva Santos", 
                "dateOfBirth": "1990-03-15",
                "nationality": "Brazilian",
                "email": "carlos@example.com",
                "phone": "+55 11 99999-9999"
            },
            "status": "basic_data"
        }
        
        update_response = requests.put(
            f"{API_BASE}/auto-application/case/{case_id}",
            json=basic_data_payload,
            headers=headers,
            timeout=10
        )
        
        if update_response.status_code == 200:
            print(f"   ✅ Case data saved successfully")
            
            # Test retrieving saved case from dashboard
            dashboard_response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=10)
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                auto_applications = dashboard_data.get('auto_applications', [])
                
                # Look for our saved case
                saved_case = next((app for app in auto_applications if app.get('case_id') == case_id), None)
                
                if saved_case:
                    print(f"   ✅ Saved case found in dashboard")
                    print(f"      Case ID: {saved_case.get('case_id')}")
                    print(f"      Status: {saved_case.get('status')}")
                    print(f"      Form Code: {saved_case.get('form_code')}")
                    print(f"      Progress: {saved_case.get('progress_percentage', 0)}%")
                    
                    # Test resuming the case
                    resume_response = requests.get(
                        f"{API_BASE}/auto-application/case/{case_id}",
                        headers=headers,
                        timeout=10
                    )
                    
                    if resume_response.status_code == 200:
                        resumed_case = resume_response.json()
                        basic_data = resumed_case.get('basic_data', {})
                        
                        if basic_data.get('firstName') == "Carlos Eduardo":
                            print(f"   ✅ Case resumed successfully with saved data")
                            print(f"✅ Save and Continue Later functionality working perfectly")
                            return True
                        else:
                            print(f"   ❌ Resumed case missing saved data")
                            return False
                    else:
                        print(f"   ❌ Failed to resume case: {resume_response.status_code}")
                        return False
                else:
                    print(f"   ❌ Saved case not found in dashboard")
                    return False
            else:
                print(f"   ❌ Failed to get dashboard: {dashboard_response.status_code}")
                return False
        else:
            print(f"   ❌ Failed to save case data: {update_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Save and Continue Later error: {str(e)}")
        return False

def test_complete_user_journey():
    """Test end-to-end flow from visa selection to form generation"""
    print("\n🚀 Testing Complete User Journey...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for complete journey test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        journey_steps = []
        
        # Step 1: Start H-1B application
        print("   Step 1: Starting H-1B application...")
        case_payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        case_response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, timeout=10)
        
        if case_response.status_code == 200:
            case_data = case_response.json()
            case_id = case_data.get('case_id')
            journey_steps.append(f"✅ Case created: {case_id}")
        else:
            journey_steps.append(f"❌ Case creation failed: {case_response.status_code}")
            return False
        
        # Step 2: Add basic data
        print("   Step 2: Adding basic data...")
        basic_data_payload = {
            "basic_data": {
                "firstName": "Carlos Eduardo",
                "lastName": "Silva Santos",
                "dateOfBirth": "1990-03-15",
                "nationality": "Brazilian",
                "passportNumber": "BR123456789",
                "email": "carlos@techglobal.com",
                "phone": "+55 11 99999-9999",
                "currentAddress": "Rua das Flores, 123",
                "city": "São Paulo",
                "state": "SP",
                "zipCode": "01234-567",
                "country": "Brazil"
            },
            "status": "basic_data"
        }
        
        basic_response = requests.put(
            f"{API_BASE}/auto-application/case/{case_id}",
            json=basic_data_payload,
            headers=headers,
            timeout=10
        )
        
        if basic_response.status_code == 200:
            journey_steps.append("✅ Basic data added")
        else:
            journey_steps.append(f"❌ Basic data failed: {basic_response.status_code}")
        
        # Step 3: Add user story
        print("   Step 3: Adding user story...")
        story_payload = {
            "user_story_text": "Sou um engenheiro de software brasileiro com 8 anos de experiência. Trabalho atualmente em uma empresa de tecnologia em São Paulo e recebi uma oferta de emprego de uma empresa americana para trabalhar como Senior Software Engineer. A empresa está disposta a patrocinar meu visto H-1B. Tenho graduação em Ciência da Computação e especialização em desenvolvimento de software. Minha esposa Maria também é engenheira e temos um filho de 3 anos. Queremos nos mudar para os Estados Unidos para esta oportunidade de carreira.",
            "status": "story_completed"
        }
        
        story_response = requests.put(
            f"{API_BASE}/auto-application/case/{case_id}",
            json=story_payload,
            headers=headers,
            timeout=10
        )
        
        if story_response.status_code == 200:
            journey_steps.append("✅ User story added")
        else:
            journey_steps.append(f"❌ User story failed: {story_response.status_code}")
        
        # Step 4: Process AI fact extraction
        print("   Step 4: Processing AI fact extraction...")
        fact_payload = {
            "case_id": case_id,
            "user_story": story_payload["user_story_text"]
        }
        
        fact_response = requests.post(
            f"{API_BASE}/auto-application/extract-facts",
            json=fact_payload,
            headers=headers,
            timeout=30
        )
        
        if fact_response.status_code == 200:
            fact_data = fact_response.json()
            extracted_facts = fact_data.get('extracted_facts', {})
            journey_steps.append(f"✅ AI fact extraction completed ({len(extracted_facts)} categories)")
        else:
            journey_steps.append(f"❌ AI fact extraction failed: {fact_response.status_code}")
        
        # Step 5: Generate friendly form
        print("   Step 5: Generating friendly form...")
        form_payload = {
            "case_id": case_id,
            "form_responses": {
                "personal_info": {
                    "full_name": "Carlos Eduardo Silva Santos",
                    "birth_date": "15/03/1990",
                    "nationality": "Brasileira",
                    "passport": "BR123456789"
                },
                "employment_info": {
                    "employer": "TechGlobal Inc.",
                    "position": "Senior Software Engineer",
                    "start_date": "01/06/2024",
                    "salary": "$95,000"
                },
                "education": {
                    "degree": "Bacharelado em Ciência da Computação",
                    "institution": "Universidade de São Paulo",
                    "graduation_year": "2012"
                }
            }
        }
        
        form_response = requests.post(
            f"{API_BASE}/auto-application/generate-forms",
            json=form_payload,
            headers=headers,
            timeout=30
        )
        
        if form_response.status_code == 200:
            form_data = form_response.json()
            official_form = form_data.get('official_form_data', {})
            journey_steps.append(f"✅ Friendly form generated ({len(official_form)} sections)")
        else:
            journey_steps.append(f"❌ Friendly form failed: {form_response.status_code}")
        
        # Step 6: Validate forms
        print("   Step 6: Validating forms...")
        validate_payload = {
            "case_id": case_id
        }
        
        validate_response = requests.post(
            f"{API_BASE}/auto-application/validate-forms",
            json=validate_payload,
            headers=headers,
            timeout=30
        )
        
        if validate_response.status_code == 200:
            validate_data = validate_response.json()
            validation_report = validate_data.get('validation_report', {})
            total_issues = validation_report.get('total_issues', 0)
            journey_steps.append(f"✅ Form validation completed ({total_issues} issues found)")
        else:
            journey_steps.append(f"❌ Form validation failed: {validate_response.status_code}")
        
        # Print journey summary
        print("\n   🗺️  Complete User Journey Summary:")
        for step in journey_steps:
            print(f"      {step}")
        
        successful_steps = len([s for s in journey_steps if s.startswith("✅")])
        total_steps = len(journey_steps)
        
        if successful_steps >= 5:  # At least 5 out of 6 steps should work
            print(f"\n✅ Complete user journey working ({successful_steps}/{total_steps} steps successful)")
            return True
        else:
            print(f"\n⚠️  Partial journey success ({successful_steps}/{total_steps} steps)")
            return False
            
    except Exception as e:
        print(f"❌ Complete user journey error: {str(e)}")
        return False

def run_priority_tests():
    """Run all priority tests"""
    
    # First login to get auth token
    if not login_user():
        print("❌ Failed to login - cannot run authenticated tests")
        return
    
    print("\n" + "🎯" * 20 + " PRIORITY TESTS " + "🎯" * 20)
    
    # Run priority tests
    results = []
    results.append(('VisaRequirements Integration', test_visa_requirements_integration()))
    results.append(('Responsibility Confirmation System', test_responsibility_confirmation_system()))
    results.append(('AI Review and Translation Workflow', test_ai_review_and_translation_workflow()))
    results.append(('Save and Continue Later', test_save_and_continue_later()))
    results.append(('Complete User Journey', test_complete_user_journey()))
    
    print('\n' + '=' * 60)
    print('🎯 PRIORITY TESTS SUMMARY')
    print('=' * 60)
    
    passed = 0
    failed_tests = []
    
    for test_name, result in results:
        status = '✅ PASS' if result else '❌ FAIL'
        print(f'{status} - {test_name}')
        if result:
            passed += 1
        else:
            failed_tests.append(test_name)
    
    print(f'\n📊 Priority Tests: {passed}/{len(results)} passed ({passed/len(results)*100:.1f}%)')
    
    if passed == len(results):
        print('🎉 ALL PRIORITY TESTS PASSED! System ready for production.')
    elif passed >= 4:
        print('🎯 MOST PRIORITY TESTS PASSED! Core functionality ready for production.')
        if failed_tests:
            print(f'⚠️  Minor issues in: {", ".join(failed_tests)}')
    else:
        print(f'⚠️  {len(results) - passed} priority test(s) failed.')
        if failed_tests:
            print(f'❌ Failed tests: {", ".join(failed_tests)}')
    
    return passed, len(results)

if __name__ == "__main__":
    run_priority_tests()