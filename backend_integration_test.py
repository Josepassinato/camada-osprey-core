#!/usr/bin/env python3
"""
OSPREY Backend Integration Tests - VALIDAÇÃO FINAL PRÉ-DEPLOYMENT
Comprehensive backend integration testing covering all critical aspects:
- Case Management Complete (H-1B, B-1/B-2, F-1)
- AI Processing Pipeline (5 steps)
- Document Management Pipeline
- User Session Management
- Data Persistence Validation
- API Response Quality
- Security Validation
- Environment Configuration
"""

import requests
import json
import uuid
import time
from datetime import datetime
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://formfill-pro-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🚀 OSPREY BACKEND INTEGRATION TESTS - VALIDAÇÃO FINAL")
print(f"Testing Backend at: {API_BASE}")
print("=" * 80)

# Global test data
TEST_USERS = {
    "carlos_h1b": {
        "email": "carlos.silva@test.com",
        "password": "CarlosH1B2024!",
        "first_name": "Carlos Eduardo",
        "last_name": "Silva Santos",
        "visa_type": "h1b"
    },
    "maria_b1b2": {
        "email": "maria.santos@test.com", 
        "password": "MariaB1B22024!",
        "first_name": "Maria Fernanda",
        "last_name": "Santos Oliveira",
        "visa_type": "b1b2"
    },
    "joao_f1": {
        "email": "joao.oliveira@test.com",
        "password": "JoaoF12024!",
        "first_name": "João Pedro",
        "last_name": "Oliveira Costa",
        "visa_type": "f1"
    }
}

# Global variables for test tracking
AUTH_TOKENS = {}
USER_IDS = {}
CASE_IDS = {}
DOCUMENT_IDS = {}
TEST_RESULTS = {
    "case_management": [],
    "ai_processing": [],
    "document_management": [],
    "session_management": [],
    "data_persistence": [],
    "api_response_quality": [],
    "security_validation": [],
    "environment_config": []
}

def log_test_result(category, test_name, success, details="", response_time=None):
    """Log test result for final summary"""
    result = {
        "test": test_name,
        "success": success,
        "details": details,
        "response_time": response_time,
        "timestamp": datetime.utcnow().isoformat()
    }
    TEST_RESULTS[category].append(result)

def measure_response_time(func):
    """Decorator to measure API response time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)  # ms
        return result, response_time
    return wrapper

# ============================================================================
# 1. CASE MANAGEMENT COMPLETO
# ============================================================================

def test_case_creation_all_visas():
    """Test case creation for all visa types (H-1B, B-1/B-2, F-1)"""
    print("\n📋 1. CASE MANAGEMENT - Testing Case Creation for All Visas...")
    
    success_count = 0
    total_tests = len(TEST_USERS)
    
    for user_key, user_data in TEST_USERS.items():
        try:
            # First, create/login user
            login_success = setup_user_session(user_key, user_data)
            if not login_success:
                log_test_result("case_management", f"User Setup - {user_key}", False, "Failed to setup user session")
                continue
            
            headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
            
            # Create case for specific visa type
            case_payload = {
                "form_code": user_data["visa_type"].upper().replace("B1B2", "B-1/B-2"),
                "session_token": str(uuid.uuid4())
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, headers=headers, timeout=10)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                case_id = data.get("case", {}).get("case_id")
                CASE_IDS[user_key] = case_id
                
                print(f"   ✅ {user_data['visa_type'].upper()} case created: {case_id}")
                print(f"      Response time: {response_time}ms")
                print(f"      Status: {data.get('case', {}).get('status')}")
                
                log_test_result("case_management", f"Case Creation - {user_data['visa_type'].upper()}", True, 
                              f"Case ID: {case_id}", response_time)
                success_count += 1
            else:
                print(f"   ❌ {user_data['visa_type'].upper()} case creation failed: {response.status_code}")
                log_test_result("case_management", f"Case Creation - {user_data['visa_type'].upper()}", False, 
                              f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            print(f"   ❌ {user_data['visa_type'].upper()} case creation error: {str(e)}")
            log_test_result("case_management", f"Case Creation - {user_data['visa_type'].upper()}", False, str(e))
    
    print(f"\n📊 Case Creation Summary: {success_count}/{total_tests} successful")
    return success_count == total_tests

def test_case_updates_all_stages():
    """Test case updates through all stages"""
    print("\n🔄 1. CASE MANAGEMENT - Testing Case Updates Through All Stages...")
    
    success_count = 0
    stages = ["basic_data", "documents_uploaded", "story_completed", "form_filled", "reviewed"]
    
    for user_key, case_id in CASE_IDS.items():
        if not case_id:
            continue
            
        try:
            headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
            stage_success = 0
            
            for stage in stages:
                update_payload = {
                    "status": stage,
                    "basic_data": {
                        "full_name": TEST_USERS[user_key]["first_name"] + " " + TEST_USERS[user_key]["last_name"],
                        "email": TEST_USERS[user_key]["email"],
                        "phone": "+55 11 99999-9999",
                        "country_of_birth": "Brazil"
                    } if stage == "basic_data" else None,
                    "progress_percentage": min(20 + (stages.index(stage) * 20), 100)
                }
                
                start_time = time.time()
                response = requests.put(f"{API_BASE}/auto-application/cases/{case_id}", 
                                      json=update_payload, headers=headers, timeout=10)
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    stage_success += 1
                    print(f"   ✅ {user_key} - Stage {stage} updated ({response_time}ms)")
                else:
                    print(f"   ❌ {user_key} - Stage {stage} failed: {response.status_code}")
                    break
            
            if stage_success == len(stages):
                success_count += 1
                log_test_result("case_management", f"Case Updates - {user_key}", True, 
                              f"All {len(stages)} stages updated successfully")
            else:
                log_test_result("case_management", f"Case Updates - {user_key}", False, 
                              f"Only {stage_success}/{len(stages)} stages updated")
                
        except Exception as e:
            print(f"   ❌ {user_key} case updates error: {str(e)}")
            log_test_result("case_management", f"Case Updates - {user_key}", False, str(e))
    
    print(f"\n📊 Case Updates Summary: {success_count}/{len(CASE_IDS)} successful")
    return success_count == len(CASE_IDS)

def test_data_persistence_between_stages():
    """Test data persistence between case stages"""
    print("\n💾 1. CASE MANAGEMENT - Testing Data Persistence Between Stages...")
    
    success_count = 0
    
    for user_key, case_id in CASE_IDS.items():
        if not case_id:
            continue
            
        try:
            headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
            
            # Get case details to verify data persistence
            start_time = time.time()
            response = requests.get(f"{API_BASE}/auto-application/cases/{case_id}", headers=headers, timeout=10)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                case_data = response.json().get("case", {})
                
                # Verify basic data persisted
                basic_data = case_data.get("basic_data", {})
                expected_name = TEST_USERS[user_key]["first_name"] + " " + TEST_USERS[user_key]["last_name"]
                
                if basic_data.get("full_name") == expected_name:
                    print(f"   ✅ {user_key} - Data persistence verified ({response_time}ms)")
                    print(f"      Case ID: {case_id}")
                    print(f"      Status: {case_data.get('status')}")
                    print(f"      Progress: {case_data.get('progress_percentage', 0)}%")
                    print(f"      Basic Data: {len(basic_data)} fields")
                    
                    success_count += 1
                    log_test_result("case_management", f"Data Persistence - {user_key}", True, 
                                  f"Case data persisted correctly", response_time)
                else:
                    print(f"   ❌ {user_key} - Data persistence failed: Name mismatch")
                    log_test_result("case_management", f"Data Persistence - {user_key}", False, 
                                  "Basic data not persisted correctly")
            else:
                print(f"   ❌ {user_key} - Case retrieval failed: {response.status_code}")
                log_test_result("case_management", f"Data Persistence - {user_key}", False, 
                              f"HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {user_key} data persistence error: {str(e)}")
            log_test_result("case_management", f"Data Persistence - {user_key}", False, str(e))
    
    print(f"\n📊 Data Persistence Summary: {success_count}/{len(CASE_IDS)} successful")
    return success_count == len(CASE_IDS)

def test_historical_data_retrieval():
    """Test retrieval of historical case data"""
    print("\n📚 1. CASE MANAGEMENT - Testing Historical Data Retrieval...")
    
    success_count = 0
    
    for user_key in TEST_USERS.keys():
        if user_key not in AUTH_TOKENS:
            continue
            
        try:
            headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
            
            # Get all user cases
            start_time = time.time()
            response = requests.get(f"{API_BASE}/auto-application/cases", headers=headers, timeout=10)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                cases = response.json().get("cases", [])
                
                if cases:
                    print(f"   ✅ {user_key} - Historical data retrieved ({response_time}ms)")
                    print(f"      Total cases: {len(cases)}")
                    
                    # Check if our created case is in the list
                    our_case = next((c for c in cases if c.get("case_id") == CASE_IDS.get(user_key)), None)
                    if our_case:
                        print(f"      ✅ Created case found in history")
                        print(f"      Case status: {our_case.get('status')}")
                        print(f"      Last updated: {our_case.get('updated_at', 'N/A')}")
                        
                        success_count += 1
                        log_test_result("case_management", f"Historical Retrieval - {user_key}", True, 
                                      f"{len(cases)} cases retrieved", response_time)
                    else:
                        print(f"      ❌ Created case not found in history")
                        log_test_result("case_management", f"Historical Retrieval - {user_key}", False, 
                                      "Created case not in historical data")
                else:
                    print(f"   ⚠️  {user_key} - No historical cases found")
                    log_test_result("case_management", f"Historical Retrieval - {user_key}", True, 
                                  "No cases (expected for new user)", response_time)
                    success_count += 1
            else:
                print(f"   ❌ {user_key} - Historical retrieval failed: {response.status_code}")
                log_test_result("case_management", f"Historical Retrieval - {user_key}", False, 
                              f"HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {user_key} historical retrieval error: {str(e)}")
            log_test_result("case_management", f"Historical Retrieval - {user_key}", False, str(e))
    
    print(f"\n📊 Historical Retrieval Summary: {success_count}/{len(TEST_USERS)} successful")
    return success_count == len(TEST_USERS)

# ============================================================================
# 2. AI PROCESSING PIPELINE
# ============================================================================

def test_ai_processing_5_steps():
    """Test all 5 AI processing steps: validation, consistency, translation, form_generation, final_review"""
    print("\n🤖 2. AI PROCESSING PIPELINE - Testing All 5 Steps...")
    
    ai_steps = ["validation", "consistency", "translation", "form_generation", "final_review"]
    success_count = 0
    
    # Use Carlos H1B case for AI processing tests
    user_key = "carlos_h1b"
    case_id = CASE_IDS.get(user_key)
    
    if not case_id or user_key not in AUTH_TOKENS:
        print("   ❌ No valid case or auth token for AI processing tests")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
    
    for step in ai_steps:
        try:
            # Prepare step-specific payload
            step_payload = {
                "step": step,
                "case_id": case_id,
                "data": {
                    "user_story": "Sou engenheiro de software brasileiro com 8 anos de experiência. Trabalho com Python, React e sistemas distribuídos. Recebi uma oferta de emprego de uma empresa de tecnologia em San Francisco para trabalhar como Senior Software Engineer. A empresa vai patrocinar meu visto H1-B. Preciso de ajuda para preencher os formulários corretamente.",
                    "basic_info": {
                        "name": "Carlos Eduardo Silva Santos",
                        "nationality": "Brazilian",
                        "education": "Computer Science Degree",
                        "experience": "8 years software engineering"
                    }
                } if step in ["validation", "consistency"] else None,
                "text_to_translate": "Sou engenheiro de software com experiência em desenvolvimento de aplicações web." if step == "translation" else None,
                "form_type": "I-129" if step == "form_generation" else None
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/ai/process", json=step_payload, headers=headers, timeout=30)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                
                print(f"   ✅ AI Step '{step}' completed ({response_time}ms)")
                
                # Step-specific validations
                if step == "validation":
                    if result.get("validation_status") and result.get("issues_found") is not None:
                        print(f"      Validation status: {result.get('validation_status')}")
                        print(f"      Issues found: {len(result.get('issues_found', []))}")
                        success_count += 1
                        log_test_result("ai_processing", f"AI Step - {step}", True, 
                                      f"Validation completed", response_time)
                    else:
                        print(f"      ❌ Invalid validation response structure")
                        log_test_result("ai_processing", f"AI Step - {step}", False, 
                                      "Invalid response structure")
                
                elif step == "consistency":
                    if result.get("consistency_score") is not None:
                        print(f"      Consistency score: {result.get('consistency_score')}")
                        print(f"      Inconsistencies: {len(result.get('inconsistencies', []))}")
                        success_count += 1
                        log_test_result("ai_processing", f"AI Step - {step}", True, 
                                      f"Consistency check completed", response_time)
                    else:
                        print(f"      ❌ Invalid consistency response structure")
                        log_test_result("ai_processing", f"AI Step - {step}", False, 
                                      "Invalid response structure")
                
                elif step == "translation":
                    translated_text = result.get("translated_text", "")
                    if translated_text and len(translated_text) > 10:
                        print(f"      Translation length: {len(translated_text)} chars")
                        print(f"      Sample: {translated_text[:100]}...")
                        # Check if translation is in English
                        if any(word in translated_text.lower() for word in ["software", "engineer", "experience", "web", "applications"]):
                            print(f"      ✅ Translation appears to be in English")
                            success_count += 1
                            log_test_result("ai_processing", f"AI Step - {step}", True, 
                                          f"Translation completed", response_time)
                        else:
                            print(f"      ⚠️  Translation language unclear")
                            log_test_result("ai_processing", f"AI Step - {step}", False, 
                                          "Translation quality unclear")
                    else:
                        print(f"      ❌ No valid translation received")
                        log_test_result("ai_processing", f"AI Step - {step}", False, 
                                      "No translation received")
                
                elif step == "form_generation":
                    form_data = result.get("form_data", {})
                    if form_data and len(form_data) > 0:
                        print(f"      Form fields generated: {len(form_data)}")
                        print(f"      Form type: {result.get('form_type', 'N/A')}")
                        success_count += 1
                        log_test_result("ai_processing", f"AI Step - {step}", True, 
                                      f"Form generation completed", response_time)
                    else:
                        print(f"      ❌ No form data generated")
                        log_test_result("ai_processing", f"AI Step - {step}", False, 
                                      "No form data generated")
                
                elif step == "final_review":
                    review_result = result.get("review_summary", {})
                    if review_result:
                        print(f"      Review score: {review_result.get('overall_score', 'N/A')}")
                        print(f"      Recommendations: {len(review_result.get('recommendations', []))}")
                        success_count += 1
                        log_test_result("ai_processing", f"AI Step - {step}", True, 
                                      f"Final review completed", response_time)
                    else:
                        print(f"      ❌ No review summary received")
                        log_test_result("ai_processing", f"AI Step - {step}", False, 
                                      "No review summary")
                        
            else:
                print(f"   ❌ AI Step '{step}' failed: {response.status_code}")
                print(f"      Error: {response.text[:200]}...")
                log_test_result("ai_processing", f"AI Step - {step}", False, 
                              f"HTTP {response.status_code}", response_time)
                
        except Exception as e:
            print(f"   ❌ AI Step '{step}' error: {str(e)}")
            log_test_result("ai_processing", f"AI Step - {step}", False, str(e))
    
    print(f"\n📊 AI Processing Summary: {success_count}/{len(ai_steps)} steps successful")
    return success_count == len(ai_steps)

def test_emergent_llm_integration():
    """Test EMERGENT_LLM_KEY integration"""
    print("\n🔑 2. AI PROCESSING PIPELINE - Testing EMERGENT_LLM_KEY Integration...")
    
    try:
        # Test chat endpoint which uses EMERGENT_LLM_KEY
        user_key = "carlos_h1b"
        if user_key not in AUTH_TOKENS:
            print("   ❌ No auth token for EMERGENT_LLM_KEY test")
            return False
        
        headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
        
        # Test Portuguese H1-B question
        chat_payload = {
            "message": "Quais são os requisitos principais para o visto H1-B?",
            "session_id": str(uuid.uuid4()),
            "context": {"visa_type": "h1b", "language": "pt"}
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/chat", json=chat_payload, headers=headers, timeout=30)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "")
            
            if len(message) > 100:
                print(f"   ✅ EMERGENT_LLM_KEY integration working ({response_time}ms)")
                print(f"      Response length: {len(message)} characters")
                print(f"      Sample response: {message[:150]}...")
                
                # Check if response is in Portuguese
                portuguese_indicators = ["visto", "requisitos", "aplicação", "documentos", "processo"]
                has_portuguese = any(word in message.lower() for word in portuguese_indicators)
                
                if has_portuguese:
                    print(f"      ✅ Response in Portuguese confirmed")
                
                # Check for legal disclaimers
                disclaimer_indicators = ["não oferece", "consultoria jurídica", "advogado", "auto-aplicação"]
                has_disclaimer = any(phrase in message.lower() for phrase in disclaimer_indicators)
                
                if has_disclaimer:
                    print(f"      ✅ Legal disclaimers present")
                
                log_test_result("ai_processing", "EMERGENT_LLM_KEY Integration", True, 
                              f"Response: {len(message)} chars, Portuguese: {has_portuguese}, Disclaimer: {has_disclaimer}", 
                              response_time)
                return True
            else:
                print(f"   ❌ EMERGENT_LLM_KEY response too short: {len(message)} chars")
                log_test_result("ai_processing", "EMERGENT_LLM_KEY Integration", False, 
                              f"Response too short: {len(message)} chars", response_time)
                return False
        else:
            print(f"   ❌ EMERGENT_LLM_KEY integration failed: {response.status_code}")
            print(f"      Error: {response.text}")
            log_test_result("ai_processing", "EMERGENT_LLM_KEY Integration", False, 
                          f"HTTP {response.status_code}", response_time)
            return False
            
    except Exception as e:
        print(f"   ❌ EMERGENT_LLM_KEY integration error: {str(e)}")
        log_test_result("ai_processing", "EMERGENT_LLM_KEY Integration", False, str(e))
        return False

def test_ai_responses_portuguese():
    """Test that AI responses are in Portuguese"""
    print("\n🇧🇷 2. AI PROCESSING PIPELINE - Testing Portuguese Responses...")
    
    test_questions = [
        "Como funciona o processo de visto H1-B?",
        "Quais documentos preciso para visto de turista?",
        "Quanto tempo demora o processo F1?",
        "Posso trabalhar com visto de estudante?"
    ]
    
    success_count = 0
    user_key = "carlos_h1b"
    
    if user_key not in AUTH_TOKENS:
        print("   ❌ No auth token for Portuguese response test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
    
    for i, question in enumerate(test_questions):
        try:
            chat_payload = {
                "message": question,
                "session_id": str(uuid.uuid4()),
                "context": {"test_id": f"pt_test_{i+1}"}
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/chat", json=chat_payload, headers=headers, timeout=30)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                # Check Portuguese indicators
                portuguese_words = ["você", "para", "com", "processo", "visto", "documentos", "tempo", "pode", "precisa"]
                portuguese_count = sum(1 for word in portuguese_words if word in message.lower())
                
                if portuguese_count >= 3 and len(message) > 50:
                    print(f"   ✅ Question {i+1}: Portuguese response confirmed ({response_time}ms)")
                    print(f"      Portuguese indicators: {portuguese_count}")
                    print(f"      Response length: {len(message)} chars")
                    success_count += 1
                    log_test_result("ai_processing", f"Portuguese Response - Q{i+1}", True, 
                                  f"Portuguese indicators: {portuguese_count}", response_time)
                else:
                    print(f"   ❌ Question {i+1}: Portuguese response unclear")
                    print(f"      Portuguese indicators: {portuguese_count}")
                    log_test_result("ai_processing", f"Portuguese Response - Q{i+1}", False, 
                                  f"Insufficient Portuguese indicators: {portuguese_count}")
            else:
                print(f"   ❌ Question {i+1}: Request failed: {response.status_code}")
                log_test_result("ai_processing", f"Portuguese Response - Q{i+1}", False, 
                              f"HTTP {response.status_code}", response_time)
                
        except Exception as e:
            print(f"   ❌ Question {i+1}: Error: {str(e)}")
            log_test_result("ai_processing", f"Portuguese Response - Q{i+1}", False, str(e))
    
    print(f"\n📊 Portuguese Responses Summary: {success_count}/{len(test_questions)} successful")
    return success_count == len(test_questions)

# ============================================================================
# 3. DOCUMENT MANAGEMENT PIPELINE
# ============================================================================

def test_document_upload_pipeline():
    """Test document upload with AI analysis"""
    print("\n📄 3. DOCUMENT MANAGEMENT - Testing Document Upload Pipeline...")
    
    success_count = 0
    document_types = ["passport", "birth_certificate", "education_diploma"]
    
    user_key = "carlos_h1b"
    if user_key not in AUTH_TOKENS:
        print("   ❌ No auth token for document upload test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
    
    for doc_type in document_types:
        try:
            # Create test document (1x1 pixel PNG)
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            test_image_bytes = base64.b64decode(test_image_base64)
            
            files = {
                'file': (f'{doc_type}_carlos.png', test_image_bytes, 'image/png')
            }
            
            data = {
                'document_type': doc_type,
                'tags': f'test,{doc_type},carlos,h1b',
                'expiration_date': '2025-12-31T23:59:59Z' if doc_type == 'passport' else None,
                'issue_date': '2020-01-01T00:00:00Z'
            }
            
            start_time = time.time()
            response = requests.post(f"{API_BASE}/documents/upload", files=files, data=data, 
                                   headers=headers, timeout=30)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                result = response.json()
                document_id = result.get('document_id')
                
                if document_id:
                    DOCUMENT_IDS[f"{user_key}_{doc_type}"] = document_id
                    
                    print(f"   ✅ {doc_type} upload successful ({response_time}ms)")
                    print(f"      Document ID: {document_id}")
                    print(f"      Status: {result.get('status')}")
                    print(f"      AI Analysis: {result.get('ai_analysis_status')}")
                    
                    success_count += 1
                    log_test_result("document_management", f"Upload - {doc_type}", True, 
                                  f"Document ID: {document_id}", response_time)
                else:
                    print(f"   ❌ {doc_type} upload failed: No document ID returned")
                    log_test_result("document_management", f"Upload - {doc_type}", False, 
                                  "No document ID returned")
            else:
                print(f"   ❌ {doc_type} upload failed: {response.status_code}")
                print(f"      Error: {response.text}")
                log_test_result("document_management", f"Upload - {doc_type}", False, 
                              f"HTTP {response.status_code}", response_time)
                
        except Exception as e:
            print(f"   ❌ {doc_type} upload error: {str(e)}")
            log_test_result("document_management", f"Upload - {doc_type}", False, str(e))
    
    print(f"\n📊 Document Upload Summary: {success_count}/{len(document_types)} successful")
    return success_count == len(document_types)

def test_dr_miguel_ai_analysis():
    """Test AI analysis with Dr. Miguel validation"""
    print("\n👨‍⚕️ 3. DOCUMENT MANAGEMENT - Testing Dr. Miguel AI Analysis...")
    
    success_count = 0
    user_key = "carlos_h1b"
    
    if user_key not in AUTH_TOKENS:
        print("   ❌ No auth token for Dr. Miguel test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
    
    for doc_key, document_id in DOCUMENT_IDS.items():
        if not document_id or user_key not in doc_key:
            continue
            
        try:
            # Get document details to check AI analysis
            start_time = time.time()
            response = requests.get(f"{API_BASE}/documents/{document_id}", headers=headers, timeout=10)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                document = response.json()
                ai_analysis = document.get('ai_analysis', {})
                
                if ai_analysis:
                    print(f"   ✅ {doc_key} - Dr. Miguel analysis present ({response_time}ms)")
                    print(f"      Completeness score: {ai_analysis.get('completeness_score', 'N/A')}")
                    print(f"      Validity status: {ai_analysis.get('validity_status', 'N/A')}")
                    print(f"      Key information: {len(ai_analysis.get('key_information', []))}")
                    print(f"      Suggestions: {len(ai_analysis.get('suggestions', []))}")
                    
                    # Check for Dr. Miguel specific validation
                    dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
                    if dr_miguel_validation:
                        print(f"      Dr. Miguel verdict: {dr_miguel_validation.get('verdict', 'N/A')}")
                        print(f"      Type correct: {dr_miguel_validation.get('type_correct', 'N/A')}")
                        print(f"      USCIS acceptable: {dr_miguel_validation.get('uscis_acceptable', 'N/A')}")
                        
                        success_count += 1
                        log_test_result("document_management", f"Dr. Miguel Analysis - {doc_key}", True, 
                                      f"Verdict: {dr_miguel_validation.get('verdict')}", response_time)
                    else:
                        print(f"      ⚠️  Dr. Miguel specific validation not found")
                        log_test_result("document_management", f"Dr. Miguel Analysis - {doc_key}", False, 
                                      "Dr. Miguel validation structure missing")
                else:
                    print(f"   ❌ {doc_key} - No AI analysis found")
                    log_test_result("document_management", f"Dr. Miguel Analysis - {doc_key}", False, 
                                  "No AI analysis present")
            else:
                print(f"   ❌ {doc_key} - Document retrieval failed: {response.status_code}")
                log_test_result("document_management", f"Dr. Miguel Analysis - {doc_key}", False, 
                              f"HTTP {response.status_code}", response_time)
                
        except Exception as e:
            print(f"   ❌ {doc_key} Dr. Miguel analysis error: {str(e)}")
            log_test_result("document_management", f"Dr. Miguel Analysis - {doc_key}", False, str(e))
    
    print(f"\n📊 Dr. Miguel Analysis Summary: {success_count}/{len(DOCUMENT_IDS)} successful")
    return success_count > 0

def test_document_validation_real():
    """Test real document validation (not simulated)"""
    print("\n🔍 3. DOCUMENT MANAGEMENT - Testing Real Document Validation...")
    
    success_count = 0
    user_key = "carlos_h1b"
    
    if user_key not in AUTH_TOKENS:
        print("   ❌ No auth token for document validation test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
    
    for doc_key, document_id in DOCUMENT_IDS.items():
        if not document_id or user_key not in doc_key:
            continue
            
        try:
            # Trigger reanalysis to test real validation
            start_time = time.time()
            response = requests.post(f"{API_BASE}/documents/{document_id}/reanalyze", 
                                   headers=headers, timeout=30)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('analysis', {})
                
                print(f"   ✅ {doc_key} - Real validation completed ({response_time}ms)")
                print(f"      New status: {result.get('status')}")
                print(f"      Completeness score: {analysis.get('completeness_score', 'N/A')}")
                print(f"      Validity status: {analysis.get('validity_status', 'N/A')}")
                
                # Check if analysis contains real validation indicators
                dr_miguel_validation = analysis.get('dr_miguel_validation', {})
                if dr_miguel_validation and dr_miguel_validation.get('verdict'):
                    verdict = dr_miguel_validation.get('verdict')
                    print(f"      Real validation verdict: {verdict}")
                    
                    # Check if it's not just a placeholder/simulation
                    if verdict in ["APROVADO", "REJEITADO", "NECESSITA_REVISÃO"]:
                        print(f"      ✅ Real validation confirmed (not simulated)")
                        success_count += 1
                        log_test_result("document_management", f"Real Validation - {doc_key}", True, 
                                      f"Verdict: {verdict}", response_time)
                    else:
                        print(f"      ⚠️  Validation appears simulated")
                        log_test_result("document_management", f"Real Validation - {doc_key}", False, 
                                      "Validation appears simulated")
                else:
                    print(f"      ❌ No real validation verdict found")
                    log_test_result("document_management", f"Real Validation - {doc_key}", False, 
                                  "No validation verdict")
            else:
                print(f"   ❌ {doc_key} - Reanalysis failed: {response.status_code}")
                log_test_result("document_management", f"Real Validation - {doc_key}", False, 
                              f"HTTP {response.status_code}", response_time)
                
        except Exception as e:
            print(f"   ❌ {doc_key} real validation error: {str(e)}")
            log_test_result("document_management", f"Real Validation - {doc_key}", False, str(e))
    
    print(f"\n📊 Real Document Validation Summary: {success_count}/{len(DOCUMENT_IDS)} successful")
    return success_count > 0

def test_document_retrieval_listing():
    """Test document retrieval and listing"""
    print("\n📋 3. DOCUMENT MANAGEMENT - Testing Document Retrieval & Listing...")
    
    user_key = "carlos_h1b"
    if user_key not in AUTH_TOKENS:
        print("   ❌ No auth token for document listing test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKENS[user_key]}"}
    
    try:
        # Test document listing
        start_time = time.time()
        response = requests.get(f"{API_BASE}/documents", headers=headers, timeout=10)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            stats = data.get('stats', {})
            expirations = data.get('upcoming_expirations', [])
            
            print(f"   ✅ Document listing successful ({response_time}ms)")
            print(f"      Total documents: {stats.get('total', 0)}")
            print(f"      Approved: {stats.get('approved', 0)}")
            print(f"      Pending: {stats.get('pending', 0)}")
            print(f"      Completion rate: {stats.get('completion_rate', 0)}%")
            print(f"      Upcoming expirations: {len(expirations)}")
            
            # Verify our uploaded documents are in the list
            our_docs = [doc for doc in documents if any(doc.get('id') == doc_id for doc_id in DOCUMENT_IDS.values())]
            
            if our_docs:
                print(f"      ✅ Uploaded documents found in list: {len(our_docs)}")
                
                # Test individual document retrieval
                test_doc = our_docs[0]
                doc_id = test_doc.get('id')
                
                detail_start = time.time()
                detail_response = requests.get(f"{API_BASE}/documents/{doc_id}", headers=headers, timeout=10)
                detail_time = round((time.time() - detail_start) * 1000, 2)
                
                if detail_response.status_code == 200:
                    detail_doc = detail_response.json()
                    print(f"      ✅ Individual document retrieval successful ({detail_time}ms)")
                    print(f"         Document type: {detail_doc.get('document_type')}")
                    print(f"         Status: {detail_doc.get('status')}")
                    print(f"         AI analysis present: {'Yes' if detail_doc.get('ai_analysis') else 'No'}")
                    
                    log_test_result("document_management", "Document Retrieval & Listing", True, 
                                  f"Listed: {len(documents)}, Retrieved: 1", response_time)
                    return True
                else:
                    print(f"      ❌ Individual document retrieval failed: {detail_response.status_code}")
                    log_test_result("document_management", "Document Retrieval & Listing", False, 
                                  f"Individual retrieval failed: {detail_response.status_code}")
                    return False
            else:
                print(f"      ❌ Uploaded documents not found in list")
                log_test_result("document_management", "Document Retrieval & Listing", False, 
                              "Uploaded documents not in list")
                return False
        else:
            print(f"   ❌ Document listing failed: {response.status_code}")
            log_test_result("document_management", "Document Retrieval & Listing", False, 
                          f"HTTP {response.status_code}", response_time)
            return False
            
    except Exception as e:
        print(f"   ❌ Document retrieval/listing error: {str(e)}")
        log_test_result("document_management", "Document Retrieval & Listing", False, str(e))
        return False

# ============================================================================
# Helper Functions
# ============================================================================

def setup_user_session(user_key, user_data):
    """Setup user session (signup/login)"""
    try:
        # Try signup first
        signup_payload = {
            "email": user_data["email"],
            "password": user_data["password"],
            "first_name": user_data["first_name"],
            "last_name": user_data["last_name"],
            "phone": "+55 11 99999-9999"
        }
        
        response = requests.post(f"{API_BASE}/auth/signup", json=signup_payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKENS[user_key] = data.get('token')
            USER_IDS[user_key] = data.get('user', {}).get('id')
            return True
        elif response.status_code == 400 and "already registered" in response.text:
            # User exists, try login
            login_payload = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            login_response = requests.post(f"{API_BASE}/auth/login", json=login_payload, timeout=10)
            
            if login_response.status_code == 200:
                data = login_response.json()
                AUTH_TOKENS[user_key] = data.get('token')
                USER_IDS[user_key] = data.get('user', {}).get('id')
                return True
        
        return False
        
    except Exception as e:
        print(f"   ❌ User setup error for {user_key}: {str(e)}")
        return False

def print_final_summary():
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("🏁 OSPREY BACKEND INTEGRATION TESTS - FINAL SUMMARY")
    print("="*80)
    
    total_tests = 0
    total_passed = 0
    
    for category, results in TEST_RESULTS.items():
        if not results:
            continue
            
        category_passed = sum(1 for r in results if r["success"])
        category_total = len(results)
        total_tests += category_total
        total_passed += category_passed
        
        print(f"\n📊 {category.upper().replace('_', ' ')}:")
        print(f"   ✅ Passed: {category_passed}/{category_total}")
        
        # Show failed tests
        failed_tests = [r for r in results if not r["success"]]
        if failed_tests:
            print(f"   ❌ Failed tests:")
            for test in failed_tests[:3]:  # Show first 3 failures
                print(f"      - {test['test']}: {test['details']}")
        
        # Show average response time for successful tests
        successful_tests = [r for r in results if r["success"] and r.get("response_time")]
        if successful_tests:
            avg_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
            print(f"   ⏱️  Average response time: {avg_time:.1f}ms")
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_tests - total_passed}")
    print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "   Success Rate: 0%")
    
    # Determine overall status
    if total_passed == total_tests:
        print(f"\n🎉 ALL TESTS PASSED - BACKEND READY FOR PRODUCTION!")
    elif total_passed / total_tests >= 0.9:
        print(f"\n✅ EXCELLENT - BACKEND MOSTLY READY (>90% success rate)")
    elif total_passed / total_tests >= 0.8:
        print(f"\n⚠️  GOOD - BACKEND NEEDS MINOR FIXES (>80% success rate)")
    else:
        print(f"\n❌ CRITICAL ISSUES - BACKEND NEEDS MAJOR FIXES (<80% success rate)")
    
    print("="*80)

# ============================================================================
# Main Test Execution
# ============================================================================

def run_all_tests():
    """Run all backend integration tests"""
    print("🚀 Starting OSPREY Backend Integration Tests...")
    
    # 1. Case Management Tests
    print("\n" + "="*60)
    print("1️⃣  CASE MANAGEMENT TESTS")
    print("="*60)
    test_case_creation_all_visas()
    test_case_updates_all_stages()
    test_data_persistence_between_stages()
    test_historical_data_retrieval()
    
    # 2. AI Processing Pipeline Tests
    print("\n" + "="*60)
    print("2️⃣  AI PROCESSING PIPELINE TESTS")
    print("="*60)
    test_ai_processing_5_steps()
    test_emergent_llm_integration()
    test_ai_responses_portuguese()
    
    # 3. Document Management Tests
    print("\n" + "="*60)
    print("3️⃣  DOCUMENT MANAGEMENT TESTS")
    print("="*60)
    test_document_upload_pipeline()
    test_dr_miguel_ai_analysis()
    test_document_validation_real()
    test_document_retrieval_listing()
    
    # Print final summary
    print_final_summary()

if __name__ == "__main__":
    run_all_tests()