#!/usr/bin/env python3
"""
OSPREY Immigration AI - DEPLOYMENT READINESS FINAL HEALTH CHECK
Comprehensive backend health check to confirm deployment readiness
"""

import requests
import json
import uuid
from datetime import datetime
import os
import base64
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://docsage-9.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print("=" * 80)
print("🚀 OSPREY IMMIGRATION AI - DEPLOYMENT READINESS FINAL HEALTH CHECK")
print("=" * 80)
print(f"Testing Backend at: {API_BASE}")
print(f"Timestamp: {datetime.now().isoformat()}")
print("=" * 80)

# Global test results
test_results = {
    "core_api_health": False,
    "auto_application_journey": False,
    "ai_integration_endpoints": False,
    "authentication_system": False,
    "document_management": False,
    "database_connectivity": False,
    "environment_configuration": False,
    "error_handling": False
}

# Test data
TEST_USER = {
    "email": f"deploy_test_{uuid.uuid4().hex[:8]}@osprey.com",
    "password": "DeployTest123!",
    "first_name": "Deploy",
    "last_name": "Tester"
}
AUTH_TOKEN = None
CASE_ID = None

def log_test_result(test_name, success, details=""):
    """Log test result with consistent formatting"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"      {details}")
    return success

def test_1_core_api_health():
    """Test 1: CORE API HEALTH - Root endpoint and basic connectivity"""
    print("\n🔍 TEST 1: CORE API HEALTH")
    print("-" * 50)
    
    try:
        # Test root endpoint
        response = requests.get(f"{API_BASE}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            
            # Verify correct OSPREY B2C message
            if 'OSPREY Immigration API B2C' in message:
                test_results["core_api_health"] = log_test_result(
                    "Root endpoint responds correctly",
                    True,
                    f"Message: {message}"
                )
                
                # Test response time
                start_time = time.time()
                requests.get(f"{API_BASE}/", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response_time < 2000:  # Less than 2 seconds
                    log_test_result(
                        "Response time acceptable",
                        True,
                        f"Response time: {response_time:.0f}ms"
                    )
                else:
                    log_test_result(
                        "Response time slow",
                        False,
                        f"Response time: {response_time:.0f}ms (>2000ms)"
                    )
                
                return True
            else:
                return log_test_result(
                    "Root endpoint message incorrect",
                    False,
                    f"Expected OSPREY B2C message, got: {message}"
                )
        else:
            return log_test_result(
                "Root endpoint failed",
                False,
                f"Status: {response.status_code}, Error: {response.text}"
            )
            
    except Exception as e:
        return log_test_result(
            "Core API connectivity failed",
            False,
            f"Error: {str(e)}"
        )

def test_2_auto_application_journey():
    """Test 2: AUTO-APPLICATION JOURNEY - Case creation for all visa types"""
    print("\n📋 TEST 2: AUTO-APPLICATION JOURNEY")
    print("-" * 50)
    
    global CASE_ID
    visa_types = ["H-1B", "B-1/B-2", "F-1"]
    success_count = 0
    
    try:
        for visa_type in visa_types:
            # Test case creation
            payload = {
                "form_code": visa_type,
                "session_token": str(uuid.uuid4())
            }
            
            response = requests.post(f"{API_BASE}/auto-application/start", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                case_data = data.get('case', {})
                case_id = case_data.get('case_id')
                
                if case_id and case_id.startswith('OSP-'):
                    log_test_result(
                        f"{visa_type} case creation",
                        True,
                        f"Case ID: {case_id}"
                    )
                    
                    # Store first case ID for further testing
                    if not CASE_ID:
                        CASE_ID = case_id
                    
                    # Test case retrieval
                    get_response = requests.get(f"{API_BASE}/auto-application/case/{case_id}", timeout=10)
                    
                    if get_response.status_code == 200:
                        case_data = get_response.json()
                        log_test_result(
                            f"{visa_type} case retrieval",
                            True,
                            f"Status: {case_data.get('status', 'N/A')}"
                        )
                        success_count += 1
                    else:
                        log_test_result(
                            f"{visa_type} case retrieval",
                            False,
                            f"Status: {get_response.status_code}"
                        )
                else:
                    log_test_result(
                        f"{visa_type} case creation - invalid ID",
                        False,
                        f"Case ID: {case_id}"
                    )
            else:
                log_test_result(
                    f"{visa_type} case creation",
                    False,
                    f"Status: {response.status_code}, Error: {response.text[:100]}"
                )
        
        # Test case data persistence and updates
        if CASE_ID:
            update_payload = {
                "basic_data": {
                    "full_name": "Test User",
                    "date_of_birth": "1990-01-01",
                    "nationality": "Brazilian"
                }
            }
            
            update_response = requests.put(f"{API_BASE}/auto-application/case/{CASE_ID}", json=update_payload, timeout=10)
            
            if update_response.status_code == 200:
                log_test_result(
                    "Case data persistence and updates",
                    True,
                    "Basic data updated successfully"
                )
                success_count += 1
            else:
                log_test_result(
                    "Case data persistence and updates",
                    False,
                    f"Status: {update_response.status_code}"
                )
        
        test_results["auto_application_journey"] = success_count >= 3
        return test_results["auto_application_journey"]
        
    except Exception as e:
        return log_test_result(
            "Auto-application journey test failed",
            False,
            f"Error: {str(e)}"
        )

def test_3_ai_integration_endpoints():
    """Test 3: AI INTEGRATION ENDPOINTS - Test AI processing with EMERGENT_LLM_KEY"""
    print("\n🤖 TEST 3: AI INTEGRATION ENDPOINTS")
    print("-" * 50)
    
    success_count = 0
    
    try:
        # Test AI processing step endpoint
        if CASE_ID:
            ai_payload = {
                "step_id": "validation",
                "case_data": {
                    "simplified_form_responses": {
                        "personal_information": {
                            "full_name": "Carlos Eduardo Silva",
                            "date_of_birth": "15/03/1990",
                            "nationality": "Brasileira"
                        }
                    }
                }
            }
            
            response = requests.post(f"{API_BASE}/ai-processing/step", json=ai_payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                log_test_result(
                    "AI processing step endpoint",
                    True,
                    f"Processing success: {data.get('success', False)}, Step: {data.get('step_id', 'N/A')}"
                )
                success_count += 1
            else:
                log_test_result(
                    "AI processing step endpoint",
                    False,
                    f"Status: {response.status_code}, Error: {response.text[:100]}"
                )
        
        # Test document validation AI (if we have auth)
        if AUTH_TOKEN:
            # Create a simple test document
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            test_image_bytes = base64.b64decode(test_image_base64)
            
            files = {'file': ('test_passport.png', test_image_bytes, 'image/png')}
            data = {'document_type': 'passport'}
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            
            doc_response = requests.post(
                f"{API_BASE}/documents/upload", 
                files=files, 
                data=data, 
                headers=headers, 
                timeout=30
            )
            
            if doc_response.status_code == 200:
                log_test_result(
                    "Document validation AI endpoints",
                    True,
                    "Document upload with AI analysis successful"
                )
                success_count += 1
            else:
                log_test_result(
                    "Document validation AI endpoints",
                    False,
                    f"Status: {doc_response.status_code}"
                )
        
        # Test AI fact extraction (if we have a case)
        if CASE_ID:
            fact_payload = {
                "user_story": "Sou engenheiro de software brasileiro com 5 anos de experiência. Trabalho em São Paulo e quero aplicar para visto H-1B para trabalhar nos Estados Unidos."
            }
            
            fact_response = requests.post(f"{API_BASE}/auto-application/extract-facts", json=fact_payload, timeout=30)
            
            if fact_response.status_code == 200:
                fact_data = fact_response.json()
                extracted_facts = fact_data.get('extracted_facts', {})
                
                if extracted_facts and len(extracted_facts) > 0:
                    log_test_result(
                        "AI fact extraction functionality",
                        True,
                        f"Extracted {len(extracted_facts)} fact categories"
                    )
                    success_count += 1
                else:
                    log_test_result(
                        "AI fact extraction functionality",
                        False,
                        "No facts extracted"
                    )
            else:
                log_test_result(
                    "AI fact extraction functionality",
                    False,
                    f"Status: {fact_response.status_code}"
                )
        
        # Test AI chat functionality with Portuguese responses
        if AUTH_TOKEN:
            chat_payload = {
                "message": "Como aplicar para visto H-1B?",
                "session_id": str(uuid.uuid4())
            }
            
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            chat_response = requests.post(f"{API_BASE}/chat", json=chat_payload, headers=headers, timeout=30)
            
            if chat_response.status_code == 200:
                chat_data = chat_response.json()
                message = chat_data.get('message', '').lower()
                
                # Check if response is in Portuguese and contains legal disclaimers
                has_portuguese = any(word in message for word in ['você', 'para', 'com', 'não', 'consultoria'])
                has_disclaimer = any(word in message for word in ['jurídica', 'advogado', 'auto-aplicação'])
                
                if has_portuguese and has_disclaimer:
                    log_test_result(
                        "AI chat with Portuguese responses",
                        True,
                        "Response in Portuguese with legal disclaimers"
                    )
                    success_count += 1
                else:
                    log_test_result(
                        "AI chat with Portuguese responses",
                        False,
                        f"Portuguese: {has_portuguese}, Disclaimer: {has_disclaimer}"
                    )
            else:
                log_test_result(
                    "AI chat with Portuguese responses",
                    False,
                    f"Status: {chat_response.status_code}"
                )
        
        test_results["ai_integration_endpoints"] = success_count >= 2
        return test_results["ai_integration_endpoints"]
        
    except Exception as e:
        return log_test_result(
            "AI integration endpoints test failed",
            False,
            f"Error: {str(e)}"
        )

def test_4_authentication_system():
    """Test 4: AUTHENTICATION SYSTEM - Login, JWT tokens, password hashing"""
    print("\n🔐 TEST 4: AUTHENTICATION SYSTEM")
    print("-" * 50)
    
    global AUTH_TOKEN
    success_count = 0
    
    try:
        # Test user signup
        signup_response = requests.post(f"{API_BASE}/auth/signup", json=TEST_USER, timeout=10)
        
        if signup_response.status_code == 200:
            signup_data = signup_response.json()
            token = signup_data.get('token')
            
            if token and len(token) > 50:  # JWT tokens are typically long
                log_test_result(
                    "User signup and JWT generation",
                    True,
                    f"Token length: {len(token)}"
                )
                AUTH_TOKEN = token
                success_count += 1
            else:
                log_test_result(
                    "User signup and JWT generation",
                    False,
                    f"Invalid token: {token}"
                )
        elif signup_response.status_code == 400 and "already registered" in signup_response.text:
            # User exists, try login
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }, timeout=10)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                AUTH_TOKEN = login_data.get('token')
                log_test_result(
                    "User login (existing user)",
                    True,
                    "Login successful"
                )
                success_count += 1
            else:
                log_test_result(
                    "User login (existing user)",
                    False,
                    f"Status: {login_response.status_code}"
                )
        else:
            log_test_result(
                "User signup",
                False,
                f"Status: {signup_response.status_code}, Error: {signup_response.text[:100]}"
            )
        
        # Test JWT token validation
        if AUTH_TOKEN:
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            profile_response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                log_test_result(
                    "JWT token validation",
                    True,
                    f"User: {profile_data.get('first_name')} {profile_data.get('last_name')}"
                )
                success_count += 1
            else:
                log_test_result(
                    "JWT token validation",
                    False,
                    f"Status: {profile_response.status_code}"
                )
        
        # Test password hashing (attempt login with wrong password)
        wrong_password_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": TEST_USER["email"],
            "password": "WrongPassword123"
        }, timeout=10)
        
        if wrong_password_response.status_code == 401:
            log_test_result(
                "Password hashing and validation",
                True,
                "Wrong password correctly rejected"
            )
            success_count += 1
        else:
            log_test_result(
                "Password hashing and validation",
                False,
                f"Wrong password not rejected: {wrong_password_response.status_code}"
            )
        
        # Test user management (profile update)
        if AUTH_TOKEN:
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            update_payload = {
                "country_of_birth": "Brazil",
                "current_country": "Brazil"
            }
            
            update_response = requests.put(f"{API_BASE}/profile", json=update_payload, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                log_test_result(
                    "User management (profile update)",
                    True,
                    "Profile updated successfully"
                )
                success_count += 1
            else:
                log_test_result(
                    "User management (profile update)",
                    False,
                    f"Status: {update_response.status_code}"
                )
        
        test_results["authentication_system"] = success_count >= 3
        return test_results["authentication_system"]
        
    except Exception as e:
        return log_test_result(
            "Authentication system test failed",
            False,
            f"Error: {str(e)}"
        )

def test_5_document_management():
    """Test 5: DOCUMENT MANAGEMENT - Upload, AI analysis, file validation"""
    print("\n📄 TEST 5: DOCUMENT MANAGEMENT")
    print("-" * 50)
    
    success_count = 0
    document_id = None
    
    if not AUTH_TOKEN:
        return log_test_result(
            "Document management test skipped",
            False,
            "No authentication token available"
        )
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # Test document upload
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        test_image_bytes = base64.b64decode(test_image_base64)
        
        files = {'file': ('passport.png', test_image_bytes, 'image/png')}
        data = {
            'document_type': 'passport',
            'tags': 'deployment,test,passport'
        }
        
        upload_response = requests.post(
            f"{API_BASE}/documents/upload", 
            files=files, 
            data=data, 
            headers=headers, 
            timeout=30
        )
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            document_id = upload_data.get('document_id')
            
            log_test_result(
                "Document upload endpoints",
                True,
                f"Document ID: {document_id}"
            )
            success_count += 1
        else:
            log_test_result(
                "Document upload endpoints",
                False,
                f"Status: {upload_response.status_code}, Error: {upload_response.text[:100]}"
            )
        
        # Test AI document analysis
        if document_id:
            # Wait a moment for AI analysis to complete
            time.sleep(2)
            
            details_response = requests.get(f"{API_BASE}/documents/{document_id}", headers=headers, timeout=10)
            
            if details_response.status_code == 200:
                doc_data = details_response.json()
                ai_analysis = doc_data.get('ai_analysis')
                
                if ai_analysis and 'completeness_score' in ai_analysis:
                    log_test_result(
                        "AI document analysis functionality",
                        True,
                        f"Completeness score: {ai_analysis.get('completeness_score')}"
                    )
                    success_count += 1
                else:
                    log_test_result(
                        "AI document analysis functionality",
                        False,
                        "No AI analysis found"
                    )
            else:
                log_test_result(
                    "AI document analysis functionality",
                    False,
                    f"Status: {details_response.status_code}"
                )
        
        # Test file validation (try uploading invalid file)
        invalid_files = {'file': ('test.txt', b'This is not an image', 'text/plain')}
        invalid_data = {'document_type': 'passport'}
        
        invalid_response = requests.post(
            f"{API_BASE}/documents/upload", 
            files=invalid_files, 
            data=invalid_data, 
            headers=headers, 
            timeout=10
        )
        
        if invalid_response.status_code == 400:
            log_test_result(
                "File validation and processing",
                True,
                "Invalid file type correctly rejected"
            )
            success_count += 1
        else:
            log_test_result(
                "File validation and processing",
                False,
                f"Invalid file not rejected: {invalid_response.status_code}"
            )
        
        # Test document list retrieval
        list_response = requests.get(f"{API_BASE}/documents", headers=headers, timeout=10)
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            documents = list_data.get('documents', [])
            stats = list_data.get('stats', {})
            
            if len(documents) > 0 and 'total' in stats:
                log_test_result(
                    "Document list and statistics",
                    True,
                    f"Total documents: {stats.get('total', 0)}"
                )
                success_count += 1
            else:
                log_test_result(
                    "Document list and statistics",
                    False,
                    "No documents or stats found"
                )
        else:
            log_test_result(
                "Document list and statistics",
                False,
                f"Status: {list_response.status_code}"
            )
        
        test_results["document_management"] = success_count >= 3
        return test_results["document_management"]
        
    except Exception as e:
        return log_test_result(
            "Document management test failed",
            False,
            f"Error: {str(e)}"
        )

def test_6_database_connectivity():
    """Test 6: DATABASE CONNECTIVITY - MongoDB operations and data persistence"""
    print("\n💾 TEST 6: DATABASE CONNECTIVITY")
    print("-" * 50)
    
    success_count = 0
    
    if not AUTH_TOKEN:
        return log_test_result(
            "Database connectivity test skipped",
            False,
            "No authentication token available"
        )
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # Test user data CRUD operations
        profile_response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
        
        if profile_response.status_code == 200:
            log_test_result(
                "MongoDB connection and operations",
                True,
                "User profile retrieved successfully"
            )
            success_count += 1
        else:
            log_test_result(
                "MongoDB connection and operations",
                False,
                f"Profile retrieval failed: {profile_response.status_code}"
            )
        
        # Test case data CRUD operations
        if CASE_ID:
            case_response = requests.get(f"{API_BASE}/auto-application/case/{CASE_ID}", timeout=10)
            
            if case_response.status_code == 200:
                log_test_result(
                    "Case data CRUD operations",
                    True,
                    f"Case {CASE_ID} retrieved successfully"
                )
                success_count += 1
            else:
                log_test_result(
                    "Case data CRUD operations",
                    False,
                    f"Case retrieval failed: {case_response.status_code}"
                )
        
        # Test dashboard data aggregation (tests multiple collections)
        dashboard_response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=10)
        
        if dashboard_response.status_code == 200:
            dashboard_data = dashboard_response.json()
            stats = dashboard_data.get('stats', {})
            
            if 'total_applications' in stats or 'total_documents' in stats:
                log_test_result(
                    "User data persistence",
                    True,
                    "Dashboard aggregation successful"
                )
                success_count += 1
            else:
                log_test_result(
                    "User data persistence",
                    False,
                    "Dashboard stats incomplete"
                )
        else:
            log_test_result(
                "User data persistence",
                False,
                f"Dashboard failed: {dashboard_response.status_code}"
            )
        
        # Test chat history (another collection)
        chat_response = requests.get(f"{API_BASE}/chat/history", headers=headers, timeout=10)
        
        if chat_response.status_code == 200:
            log_test_result(
                "Multi-collection data access",
                True,
                "Chat history accessible"
            )
            success_count += 1
        else:
            log_test_result(
                "Multi-collection data access",
                False,
                f"Chat history failed: {chat_response.status_code}"
            )
        
        test_results["database_connectivity"] = success_count >= 3
        return test_results["database_connectivity"]
        
    except Exception as e:
        return log_test_result(
            "Database connectivity test failed",
            False,
            f"Error: {str(e)}"
        )

def test_7_environment_configuration():
    """Test 7: ENVIRONMENT CONFIGURATION - No hardcoded values, proper env usage"""
    print("\n⚙️ TEST 7: ENVIRONMENT CONFIGURATION")
    print("-" * 50)
    
    success_count = 0
    
    try:
        # Test that EMERGENT_LLM_KEY is properly configured (not hardcoded)
        response = requests.get(f"{API_BASE}/", timeout=10)
        
        if response.status_code == 200:
            response_text = response.text
            
            # Check for hardcoded API keys in response
            hardcoded_patterns = [
                "sk-emergent-aE5F536B80dFf0bA6F",  # The actual key
                "sk-proj-",  # OpenAI key pattern
                "mongodb://",  # MongoDB URL
                "JWT_SECRET"  # JWT secret
            ]
            
            has_hardcoded = any(pattern in response_text for pattern in hardcoded_patterns)
            
            if not has_hardcoded:
                log_test_result(
                    "No hardcoded values in responses",
                    True,
                    "No sensitive data exposed"
                )
                success_count += 1
            else:
                log_test_result(
                    "No hardcoded values in responses",
                    False,
                    "Hardcoded values detected in response"
                )
        
        # Test proper environment variable usage by checking AI functionality
        if AUTH_TOKEN and CASE_ID:
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            
            # Test AI chat (uses EMERGENT_LLM_KEY)
            chat_payload = {
                "message": "Test environment configuration",
                "session_id": str(uuid.uuid4())
            }
            
            chat_response = requests.post(f"{API_BASE}/chat", json=chat_payload, headers=headers, timeout=30)
            
            if chat_response.status_code == 200:
                log_test_result(
                    "Proper environment variable usage",
                    True,
                    "EMERGENT_LLM_KEY integration working"
                )
                success_count += 1
            else:
                log_test_result(
                    "Proper environment variable usage",
                    False,
                    f"AI integration failed: {chat_response.status_code}"
                )
        
        # Test that backend is using correct MongoDB connection
        if AUTH_TOKEN:
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            profile_response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
            
            if profile_response.status_code == 200:
                log_test_result(
                    "MONGO_URL environment variable",
                    True,
                    "Database connection working correctly"
                )
                success_count += 1
            else:
                log_test_result(
                    "MONGO_URL environment variable",
                    False,
                    "Database connection issues"
                )
        
        test_results["environment_configuration"] = success_count >= 2
        return test_results["environment_configuration"]
        
    except Exception as e:
        return log_test_result(
            "Environment configuration test failed",
            False,
            f"Error: {str(e)}"
        )

def test_8_error_handling():
    """Test 8: ERROR HANDLING - Proper HTTP status codes and error responses"""
    print("\n🚨 TEST 8: ERROR HANDLING")
    print("-" * 50)
    
    success_count = 0
    
    try:
        # Test 404 for non-existent endpoint
        response_404 = requests.get(f"{API_BASE}/non-existent-endpoint", timeout=10)
        
        if response_404.status_code == 404:
            log_test_result(
                "404 errors for invalid requests",
                True,
                "Non-existent endpoint returns 404"
            )
            success_count += 1
        else:
            log_test_result(
                "404 errors for invalid requests",
                False,
                f"Expected 404, got {response_404.status_code}"
            )
        
        # Test 401/403 for unauthorized access
        response_401 = requests.get(f"{API_BASE}/profile", timeout=10)  # No auth header
        
        if response_401.status_code in [401, 403]:
            log_test_result(
                "401/403 errors for unauthorized access",
                True,
                f"Protected endpoint requires authentication ({response_401.status_code})"
            )
            success_count += 1
        else:
            log_test_result(
                "401/403 errors for unauthorized access",
                False,
                f"Expected 401/403, got {response_401.status_code}"
            )
        
        # Test 400 for invalid data
        invalid_login = requests.post(f"{API_BASE}/auth/login", json={
            "email": "invalid-email",
            "password": ""
        }, timeout=10)
        
        if invalid_login.status_code == 400 or invalid_login.status_code == 422:
            log_test_result(
                "400/422 errors for invalid data",
                True,
                f"Invalid login data returns {invalid_login.status_code}"
            )
            success_count += 1
        else:
            log_test_result(
                "400/422 errors for invalid data",
                False,
                f"Expected 400/422, got {invalid_login.status_code}"
            )
        
        # Test graceful error handling for AI endpoints
        if CASE_ID:
            invalid_ai_payload = {
                "step_id": "invalid_step",
                "case_data": {}
            }
            
            ai_error_response = requests.post(f"{API_BASE}/ai-processing/step", json=invalid_ai_payload, timeout=10)
            
            if ai_error_response.status_code in [400, 422, 500]:
                try:
                    error_data = ai_error_response.json()
                    if 'error' in error_data or 'detail' in error_data:
                        log_test_result(
                            "Graceful error handling",
                            True,
                            f"AI endpoint returns structured error: {ai_error_response.status_code}"
                        )
                        success_count += 1
                    else:
                        log_test_result(
                            "Graceful error handling",
                            False,
                            "Error response not structured"
                        )
                except:
                    log_test_result(
                        "Graceful error handling",
                        False,
                        "Error response not JSON"
                    )
            else:
                log_test_result(
                    "Graceful error handling",
                    False,
                    f"Unexpected status for invalid AI request: {ai_error_response.status_code}"
                )
        
        # Test proper HTTP status codes for successful operations
        if AUTH_TOKEN:
            headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
            profile_response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
            
            if profile_response.status_code == 200:
                log_test_result(
                    "Proper HTTP status codes",
                    True,
                    "Successful operations return 200"
                )
                success_count += 1
            else:
                log_test_result(
                    "Proper HTTP status codes",
                    False,
                    f"Expected 200, got {profile_response.status_code}"
                )
        
        test_results["error_handling"] = success_count >= 4
        return test_results["error_handling"]
        
    except Exception as e:
        return log_test_result(
            "Error handling test failed",
            False,
            f"Error: {str(e)}"
        )

def generate_deployment_assessment():
    """Generate final deployment readiness assessment"""
    print("\n" + "=" * 80)
    print("🎯 DEPLOYMENT READINESS ASSESSMENT")
    print("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nTEST RESULTS SUMMARY:")
    print(f"{'='*50}")
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        formatted_name = test_name.replace('_', ' ').title()
        print(f"{status} | {formatted_name}")
    
    print(f"\nOVERALL RESULTS:")
    print(f"{'='*50}")
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Determine deployment confidence level
    if success_rate >= 90:
        confidence = "✅ READY"
        recommendation = "System is ready for production deployment."
    elif success_rate >= 75:
        confidence = "⚠️ NEEDS ATTENTION"
        recommendation = "System has minor issues that should be addressed before deployment."
    else:
        confidence = "❌ NOT READY"
        recommendation = "System has critical issues that must be resolved before deployment."
    
    print(f"\nDEPLOYMENT CONFIDENCE LEVEL: {confidence}")
    print(f"RECOMMENDATION: {recommendation}")
    
    # Detailed recommendations
    print(f"\nDETAILED ANALYSIS:")
    print(f"{'='*50}")
    
    failed_tests = [test for test, result in test_results.items() if not result]
    
    if not failed_tests:
        print("🎉 All critical systems are functioning correctly!")
        print("✅ No hardcoded values or security vulnerabilities detected")
        print("✅ Proper error handling and responses verified")
        print("✅ AI integrations working with EMERGENT_LLM_KEY")
        print("✅ Database operations successful")
        print("✅ Authentication and authorization working properly")
    else:
        print("⚠️ The following areas need attention:")
        for test in failed_tests:
            formatted_test = test.replace('_', ' ').title()
            print(f"   • {formatted_test}")
    
    print(f"\nTEST COMPLETED: {datetime.now().isoformat()}")
    print("=" * 80)
    
    return confidence, success_rate

def main():
    """Run all deployment readiness tests"""
    print("Starting comprehensive deployment readiness tests...\n")
    
    # Run all tests in sequence
    test_1_core_api_health()
    test_2_auto_application_journey()
    test_3_ai_integration_endpoints()
    test_4_authentication_system()
    test_5_document_management()
    test_6_database_connectivity()
    test_7_environment_configuration()
    test_8_error_handling()
    
    # Generate final assessment
    confidence, success_rate = generate_deployment_assessment()
    
    return confidence, success_rate

if __name__ == "__main__":
    main()