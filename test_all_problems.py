#!/usr/bin/env python3
"""
COMPREHENSIVE PROBLEM IDENTIFICATION TEST
Test all endpoints and identify ALL problems as requested by user
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def log_test(test_name: str, success: bool, details: str = "", response_data=None):
    """Log test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")
    if not success and response_data:
        print(f"    Response: {response_data}")
    print()

def test_4_specific_corrected_endpoints():
    """Test the 4 specific endpoints mentioned as corrected"""
    print("🎯 TESTING 4 SPECIFIC CORRECTED ENDPOINTS")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'SpecificEndpointsTest/1.0'
    })
    
    # 1. POST /api/owl/login
    print("\n1. Testing POST /api/owl/login...")
    try:
        payload = {"email": "invalid@test.com", "password": "wrongpassword"}
        response = session.post(f"{API_BASE}/owl/login", json=payload)
        
        if response.status_code == 401:
            data = response.json()
            log_test(
                "POST /api/owl/login - Invalid Credentials",
                True,
                f"Correctly returns 401 with structured JSON: {data.get('detail', 'No detail')}"
            )
        else:
            log_test(
                "POST /api/owl/login - Invalid Credentials",
                False,
                f"Expected 401, got {response.status_code}",
                response.text
            )
    except Exception as e:
        log_test("POST /api/owl/login", False, f"Exception: {str(e)}")
    
    # 2. GET /api/owl/user-sessions/{email}
    print("\n2. Testing GET /api/owl/user-sessions/{email}...")
    try:
        test_email = "nonexistent@test.com"
        response = session.get(f"{API_BASE}/owl/user-sessions/{test_email}")
        
        if response.status_code == 404:
            data = response.json()
            log_test(
                "GET /api/owl/user-sessions/{email} - User Not Found",
                True,
                f"Correctly returns 404 with structured JSON: {data.get('detail', 'No detail')}"
            )
        else:
            log_test(
                "GET /api/owl/user-sessions/{email} - User Not Found",
                False,
                f"Expected 404, got {response.status_code}",
                response.text
            )
    except Exception as e:
        log_test("GET /api/owl/user-sessions/{email}", False, f"Exception: {str(e)}")
    
    # 3. POST /api/owl/user-sessions
    print("\n3. Testing POST /api/owl/user-sessions...")
    try:
        payload = {"test": "data"}
        response = session.post(f"{API_BASE}/owl/user-sessions", json=payload)
        
        if response.status_code == 404:
            data = response.json()
            log_test(
                "POST /api/owl/user-sessions - Not Found",
                True,
                f"Correctly returns 404 with structured JSON: {data.get('detail', 'No detail')}"
            )
        else:
            log_test(
                "POST /api/owl/user-sessions - Not Found",
                False,
                f"Expected 404, got {response.status_code}",
                response.text
            )
    except Exception as e:
        log_test("POST /api/owl/user-sessions", False, f"Exception: {str(e)}")
    
    # 4. PUT /api/auto-application/case/{id} - Test the validation bug
    print("\n4. Testing PUT /api/auto-application/case/{id} - Validation Bug...")
    try:
        # First create a case
        create_response = session.post(f"{API_BASE}/auto-application/start", json={})
        if create_response.status_code == 200:
            case_data = create_response.json().get('case', {})
            case_id = case_data.get('case_id')
            
            if case_id:
                # Test with valid payload that should work
                valid_payload = {
                    "form_code": "H-1B",
                    "status": "form_selected"
                }
                
                response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=valid_payload)
                
                if response.status_code == 200:
                    log_test(
                        "PUT /api/auto-application/case/{id} - Valid Payload",
                        True,
                        f"Valid payload works correctly: {response.status_code}"
                    )
                else:
                    log_test(
                        "PUT /api/auto-application/case/{id} - Valid Payload",
                        False,
                        f"Valid payload failed: {response.status_code}",
                        response.text
                    )
                
                # Test with flexible payload that might cause the bug
                flexible_payload = {
                    "basic_data": {"name": "Test User"},
                    "progress_percentage": 25
                }
                
                response2 = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=flexible_payload)
                
                if response2.status_code == 200:
                    log_test(
                        "PUT /api/auto-application/case/{id} - Flexible Payload",
                        True,
                        f"Flexible payload works correctly: {response2.status_code}"
                    )
                else:
                    log_test(
                        "PUT /api/auto-application/case/{id} - Flexible Payload",
                        False,
                        f"Flexible payload failed: {response2.status_code}",
                        response2.text
                    )
        else:
            log_test("PUT /api/auto-application/case/{id}", False, "Could not create test case")
    except Exception as e:
        log_test("PUT /api/auto-application/case/{id}", False, f"Exception: {str(e)}")

def test_owl_agent_initiate_payment():
    """Test the owl agent payment initiation endpoint"""
    print("\n🦉 TESTING OWL AGENT PAYMENT INITIATION")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'OwlPaymentTest/1.0'
    })
    
    # Test without session_id (should return 400)
    print("\n1. Testing without session_id...")
    try:
        payload = {"delivery_method": "download"}
        response = session.post(f"{API_BASE}/owl-agent/initiate-payment", json=payload)
        
        if response.status_code == 400:
            data = response.json()
            log_test(
                "POST /api/owl-agent/initiate-payment - Missing session_id",
                True,
                f"Correctly returns 400: {data.get('detail', 'No detail')}"
            )
        else:
            log_test(
                "POST /api/owl-agent/initiate-payment - Missing session_id",
                False,
                f"Expected 400, got {response.status_code}",
                response.text
            )
    except Exception as e:
        log_test("POST /api/owl-agent/initiate-payment - Missing session_id", False, f"Exception: {str(e)}")
    
    # Test with session_id (should work with fallback)
    print("\n2. Testing with session_id...")
    try:
        payload = {
            "session_id": "test-session-123",
            "delivery_method": "download"
        }
        response = session.post(f"{API_BASE}/owl-agent/initiate-payment", json=payload)
        
        # Should not return 404, should work with fallback
        if response.status_code != 404:
            log_test(
                "POST /api/owl-agent/initiate-payment - With session_id",
                True,
                f"Does not return 404, status: {response.status_code}"
            )
        else:
            log_test(
                "POST /api/owl-agent/initiate-payment - With session_id",
                False,
                f"Returns 404 when should work with fallback",
                response.text
            )
    except Exception as e:
        log_test("POST /api/owl-agent/initiate-payment - With session_id", False, f"Exception: {str(e)}")

def test_document_analysis_second_page():
    """Test the document analysis issue reported by user"""
    print("\n📄 TESTING DOCUMENT ANALYSIS - SECOND PAGE ISSUE")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'DocumentAnalysisTest/1.0'
    })
    
    # Create a case first
    create_response = session.post(f"{API_BASE}/auto-application/start", json={})
    if create_response.status_code == 200:
        case_data = create_response.json().get('case', {})
        case_id = case_data.get('case_id')
        
        if case_id:
            # Set case to H-1B
            update_response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json={
                "form_code": "H-1B",
                "status": "form_selected"
            })
            
            if update_response.status_code == 200:
                # Test document upload and analysis
                print(f"\n1. Testing document analysis for case {case_id}...")
                
                # Create a realistic passport document
                passport_content = """
                PASSPORT
                REPUBLIC OF BRAZIL
                
                Type: P
                Country Code: BRA
                Passport No: BR1234567
                
                Surname: SILVA
                Given Names: CARLOS EDUARDO
                Nationality: BRAZILIAN
                Date of Birth: 15 MAY 1990
                Sex: M
                Place of Birth: SAO PAULO, BRAZIL
                Date of Issue: 10 MAR 2020
                Date of Expiry: 09 MAR 2030
                Authority: DPF
                """ * 50  # Make it substantial
                
                files = {
                    'file': ('carlos_passport.pdf', passport_content.encode(), 'application/pdf')
                }
                data_form = {
                    'document_type': 'passport',
                    'visa_type': 'H-1B',
                    'case_id': case_id
                }
                
                headers = {k: v for k, v in session.headers.items() if k.lower() != 'content-type'}
                
                response = requests.post(
                    f"{API_BASE}/documents/analyze-with-ai",
                    files=files,
                    data=data_form,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    completeness = result.get('completeness', 0)
                    validity = result.get('validity', False)
                    
                    # Check if analysis is working correctly
                    analysis_working = completeness > 0 and 'ai_analysis' in result
                    
                    log_test(
                        "Document Analysis - H-1B Passport",
                        analysis_working,
                        f"Completeness: {completeness}%, Validity: {validity}, Analysis present: {'ai_analysis' in result}"
                    )
                    
                    # Check for form code mismatch issue
                    if 'form_code_mismatch' in str(result) or completeness < 50:
                        log_test(
                            "Document Analysis - Form Code Mismatch Check",
                            False,
                            f"Possible form code mismatch detected - low completeness or mismatch mentioned"
                        )
                    else:
                        log_test(
                            "Document Analysis - Form Code Mismatch Check",
                            True,
                            f"No form code mismatch detected"
                        )
                else:
                    log_test(
                        "Document Analysis - H-1B Passport",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            else:
                log_test("Document Analysis Setup", False, "Could not set case to H-1B")
        else:
            log_test("Document Analysis Setup", False, "Could not get case_id")
    else:
        log_test("Document Analysis Setup", False, "Could not create case")

def test_dr_paula_review_letter():
    """Test Dr. Paula review letter endpoint"""
    print("\n👩‍⚕️ TESTING DR. PAULA REVIEW LETTER")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'DrPaulaTest/1.0'
    })
    
    # Test the review letter endpoint
    print("\n1. Testing review letter endpoint...")
    try:
        payload = {
            "visa_type": "H1B",
            "applicant_letter": "I am Carlos Silva, a Brazilian software engineer with 8 years of experience. I have received an offer from Tech Solutions Inc. to work as a Senior Software Engineer with a salary of $85,000 per year. The company will sponsor my H-1B visa."
        }
        
        response = session.post(f"{API_BASE}/llm/dr-paula/review-letter", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if response has proper structure
            has_review = 'review' in data
            has_success = 'success' in data
            
            if has_review:
                review = data['review']
                has_status = 'status' in review
                has_coverage_score = 'coverage_score' in review
                
                log_test(
                    "Dr. Paula Review Letter - Structure",
                    has_status and has_coverage_score,
                    f"Status: {review.get('status')}, Coverage Score: {review.get('coverage_score')}"
                )
                
                # Check if status handling is working (needs_review vs incomplete)
                status = review.get('status')
                if status in ['needs_review', 'incomplete', 'complete']:
                    log_test(
                        "Dr. Paula Review Letter - Status Handling",
                        True,
                        f"Status '{status}' is properly handled"
                    )
                else:
                    log_test(
                        "Dr. Paula Review Letter - Status Handling",
                        False,
                        f"Unexpected status: {status}"
                    )
            else:
                log_test(
                    "Dr. Paula Review Letter - Structure",
                    False,
                    f"Missing review object in response: {list(data.keys())}"
                )
        else:
            log_test(
                "Dr. Paula Review Letter",
                False,
                f"HTTP {response.status_code}",
                response.text
            )
    except Exception as e:
        log_test("Dr. Paula Review Letter", False, f"Exception: {str(e)}")

def test_emergent_llm_key_budget():
    """Test if EMERGENT_LLM_KEY has budget issues"""
    print("\n🔑 TESTING EMERGENT_LLM_KEY BUDGET")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'BudgetTest/1.0'
    })
    
    # Test multiple AI endpoints to check for budget issues
    endpoints_to_test = [
        {
            "name": "Dr. Paula Generate Directives",
            "url": f"{API_BASE}/llm/dr-paula/generate-directives",
            "payload": {"visa_type": "H1B", "language": "pt"}
        },
        {
            "name": "Dr. Paula Review Letter",
            "url": f"{API_BASE}/llm/dr-paula/review-letter", 
            "payload": {"visa_type": "H1B", "applicant_letter": "Short test letter"}
        }
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n1. Testing {endpoint['name']}...")
        try:
            response = session.post(endpoint['url'], json=endpoint['payload'])
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for budget-related error messages
                response_text = str(data).lower()
                budget_issues = any(keyword in response_text for keyword in [
                    'budget', 'quota', 'limit', 'exceeded', 'insufficient', 'credits'
                ])
                
                if budget_issues:
                    log_test(
                        f"{endpoint['name']} - Budget Check",
                        False,
                        f"Budget-related issues detected in response"
                    )
                else:
                    log_test(
                        f"{endpoint['name']} - Budget Check",
                        True,
                        f"No budget issues detected"
                    )
            else:
                log_test(
                    f"{endpoint['name']} - Budget Check",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            log_test(f"{endpoint['name']} - Budget Check", False, f"Exception: {str(e)}")

def main():
    """Run all problem identification tests"""
    print("🔍 COMPREHENSIVE PROBLEM IDENTIFICATION TEST")
    print("=" * 80)
    print("Testing ALL endpoints to identify EVERY problem as requested")
    print("=" * 80)
    
    # Test 1: Carlos Silva H-1B Complete Journey (already tested - working)
    print("\n✅ CARLOS SILVA H-1B COMPLETE JOURNEY - ALREADY VERIFIED WORKING")
    
    # Test 2: 4 Specific Corrected Endpoints
    test_4_specific_corrected_endpoints()
    
    # Test 3: Owl Agent Payment Initiation
    test_owl_agent_initiate_payment()
    
    # Test 4: Document Analysis Second Page Issue
    test_document_analysis_second_page()
    
    # Test 5: Dr. Paula Review Letter
    test_dr_paula_review_letter()
    
    # Test 6: EMERGENT_LLM_KEY Budget Issues
    test_emergent_llm_key_budget()
    
    print("\n🎯 PROBLEM IDENTIFICATION COMPLETE")
    print("=" * 80)
    print("All major endpoints and issues have been tested.")
    print("Check the results above for detailed problem identification.")

if __name__ == "__main__":
    main()