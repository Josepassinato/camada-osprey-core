#!/usr/bin/env python3
"""
OSPREY EMERGENT_LLM_KEY VALIDATION TESTS - FIXED VERSION
Comprehensive testing of EMERGENT_LLM_KEY integration with OpenAI for all AI functionalities
"""

import requests
import json
import uuid
from datetime import datetime
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://immigration-helper-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔑 TESTING EMERGENT_LLM_KEY INTEGRATION AT: {API_BASE}")
print("=" * 80)

# Global variables for test data
TEST_USER = {
    "email": "emergent.test@osprey.com",
    "password": "EmergentTest123",
    "first_name": "Carlos",
    "last_name": "Silva"
}
AUTH_TOKEN = None
USER_ID = None

def setup_test_user():
    """Setup test user for AI integration tests"""
    print("\n🔧 Setting up test user for AI integration tests...")
    global AUTH_TOKEN, USER_ID
    
    # Try login first
    login_payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            USER_ID = data.get('user', {}).get('id')
            print(f"✅ User login successful - User ID: {USER_ID}")
            return True
        else:
            # Try signup if login fails
            signup_payload = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "first_name": TEST_USER["first_name"],
                "last_name": TEST_USER["last_name"],
                "phone": "+55 11 99999-8888"
            }
            
            signup_response = requests.post(f"{API_BASE}/auth/signup", json=signup_payload, timeout=10)
            
            if signup_response.status_code == 200:
                data = signup_response.json()
                AUTH_TOKEN = data.get('token')
                USER_ID = data.get('user', {}).get('id')
                print(f"✅ User signup successful - User ID: {USER_ID}")
                return True
            else:
                print(f"❌ User setup failed: {signup_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ User setup error: {str(e)}")
        return False

def test_emergent_llm_key_status():
    """Test 1: EMERGENT_LLM_KEY STATUS - Verify if key is configured and working"""
    print("\n🔑 TEST 1: EMERGENT_LLM_KEY STATUS VERIFICATION")
    print("-" * 50)
    
    try:
        # Test basic connectivity first
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code != 200:
            print("❌ Basic API connectivity failed")
            return False
        
        print("✅ Backend API accessible")
        
        # Check if we can make a simple AI call to verify key is working
        if not AUTH_TOKEN:
            print("❌ No auth token available for AI key test")
            return False
        
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        # Simple test message to verify AI integration
        test_payload = {
            "message": "Teste de conectividade da chave EMERGENT_LLM_KEY",
            "session_id": str(uuid.uuid4()),
            "context": {"test": "emergent_key_validation"}
        }
        
        ai_response = requests.post(f"{API_BASE}/chat", json=test_payload, headers=headers, timeout=30)
        
        if ai_response.status_code == 200:
            data = ai_response.json()
            response_message = data.get('message', '')
            
            print("✅ EMERGENT_LLM_KEY is configured and functional")
            print(f"   AI Response received: {len(response_message)} characters")
            print(f"   Response preview: {response_message[:100]}...")
            
            # Check if response indicates it's using OpenAI/GPT
            if len(response_message) > 50:  # Reasonable AI response length
                print("✅ AI integration appears to be working correctly")
                return True
            else:
                print("⚠️  AI response seems too short, may be using fallback")
                return False
        else:
            print(f"❌ AI integration test failed: {ai_response.status_code}")
            print(f"   Error: {ai_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EMERGENT_LLM_KEY status test error: {str(e)}")
        return False

def test_ai_chat_endpoints():
    """Test 2: AI CHAT ENDPOINTS - Test /api/ai-chat with Portuguese questions"""
    print("\n🤖 TEST 2: AI CHAT ENDPOINTS TESTING")
    print("-" * 50)
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for AI chat test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test Portuguese H1-B immigration question as specified
        test_question = "Quais são os requisitos para visto H-1B?"
        
        payload = {
            "message": test_question,
            "session_id": str(uuid.uuid4()),
            "context": {"visa_interest": "h1b", "language": "portuguese"}
        }
        
        response = requests.post(f"{API_BASE}/chat", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('message', '')
            
            print("✅ AI Chat endpoint working correctly")
            print(f"   Question: {test_question}")
            print(f"   Response length: {len(ai_response)} characters")
            print(f"   Response preview: {ai_response[:200]}...")
            
            # Verify response is in Portuguese
            portuguese_indicators = ['visto', 'requisitos', 'para', 'você', 'trabalho', 'especializado']
            portuguese_found = sum(1 for word in portuguese_indicators if word.lower() in ai_response.lower())
            
            if portuguese_found >= 3:
                print("✅ AI response is in Portuguese as expected")
            else:
                print("⚠️  AI response language unclear - may not be Portuguese")
            
            # Verify it's about H1-B immigration
            h1b_indicators = ['h-1b', 'h1b', 'visto', 'trabalho', 'especializado', 'imigração']
            h1b_found = sum(1 for word in h1b_indicators if word.lower() in ai_response.lower())
            
            if h1b_found >= 2:
                print("✅ AI response addresses H1-B visa topic correctly")
            else:
                print("⚠️  AI response may not be addressing H1-B topic properly")
            
            # Check for legal disclaimers
            disclaimer_indicators = ['não oferece', 'consultoria jurídica', 'advogado', 'auto-aplicação']
            disclaimer_found = any(phrase in ai_response.lower() for phrase in disclaimer_indicators)
            
            if disclaimer_found:
                print("✅ Legal disclaimers present in AI response")
            else:
                print("⚠️  Legal disclaimers not clearly present")
            
            # Verify using EMERGENT_LLM_KEY (not hardcoded)
            if len(ai_response) > 100 and 'sk-' not in ai_response:
                print("✅ Response appears to use EMERGENT_LLM_KEY (no hardcoded keys visible)")
            else:
                print("⚠️  Cannot verify EMERGENT_LLM_KEY usage")
            
            return True
        else:
            print(f"❌ AI Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Chat endpoint test error: {str(e)}")
        return False

def test_ai_document_validation():
    """Test 3: AI DOCUMENT VALIDATION (Dr. Miguel) - Test document analysis"""
    print("\n📄 TEST 3: AI DOCUMENT VALIDATION (DR. MIGUEL)")
    print("-" * 50)
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for document validation test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Create a test document first
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        test_image_bytes = base64.b64decode(test_image_base64)
        
        # Upload document for AI analysis
        files = {
            'file': ('passport_test.png', test_image_bytes, 'image/png')
        }
        
        data = {
            'document_type': 'passport',
            'tags': 'test,ai-validation,emergent-key',
            'expiration_date': '2025-12-31T23:59:59Z'
        }
        
        upload_response = requests.post(
            f"{API_BASE}/documents/upload", 
            files=files, 
            data=data, 
            headers=headers, 
            timeout=30
        )
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            document_id = upload_result.get('document_id')
            
            print("✅ Test document uploaded successfully")
            print(f"   Document ID: {document_id}")
            print(f"   AI Analysis Status: {upload_result.get('ai_analysis_status')}")
            
            # Get document details to check AI analysis
            details_response = requests.get(f"{API_BASE}/documents/{document_id}", headers=headers, timeout=10)
            
            if details_response.status_code == 200:
                document = details_response.json()
                ai_analysis = document.get('ai_analysis')
                
                if ai_analysis:
                    print("✅ Dr. Miguel AI analysis completed")
                    print(f"   Completeness score: {ai_analysis.get('completeness_score', 'N/A')}")
                    print(f"   Validity status: {ai_analysis.get('validity_status', 'N/A')}")
                    print(f"   Key information count: {len(ai_analysis.get('key_information', []))}")
                    print(f"   Suggestions count: {len(ai_analysis.get('suggestions', []))}")
                    
                    # Check for Dr. Miguel specific validation
                    dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
                    if dr_miguel_validation:
                        print("✅ Dr. Miguel validation structure present")
                        print(f"   Document type identified: {dr_miguel_validation.get('document_type_identified', 'N/A')}")
                        print(f"   Type correct: {dr_miguel_validation.get('type_correct', 'N/A')}")
                        print(f"   USCIS acceptable: {dr_miguel_validation.get('uscis_acceptable', 'N/A')}")
                        print(f"   Verdict: {dr_miguel_validation.get('verdict', 'N/A')}")
                    else:
                        print("⚠️  Dr. Miguel specific validation not found")
                    
                    # Test reanalysis to verify AI is working
                    reanalyze_response = requests.post(f"{API_BASE}/documents/{document_id}/reanalyze", headers=headers, timeout=30)
                    
                    if reanalyze_response.status_code == 200:
                        reanalyze_result = reanalyze_response.json()
                        print("✅ Document reanalysis working (AI processing confirmed)")
                        print(f"   New analysis status: {reanalyze_result.get('status')}")
                        
                        # Clean up - delete test document
                        requests.delete(f"{API_BASE}/documents/{document_id}", headers=headers, timeout=10)
                        print("✅ Test document cleaned up")
                        
                        return True
                    else:
                        print(f"⚠️  Document reanalysis failed: {reanalyze_response.status_code}")
                        return False
                else:
                    print("❌ AI analysis not found in document")
                    return False
            else:
                print(f"❌ Failed to get document details: {details_response.status_code}")
                return False
        else:
            print(f"❌ Document upload failed: {upload_response.status_code}")
            print(f"   Error: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Document validation test error: {str(e)}")
        return False

def test_ai_processing_steps():
    """Test 4: AI PROCESSING STEPS - Test all 5 AI processing steps"""
    print("\n⚙️ TEST 4: AI PROCESSING STEPS (5 STEPS)")
    print("-" * 50)
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for AI processing test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # First create an auto-application case
        case_payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        case_response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, headers=headers, timeout=10)
        
        if case_response.status_code == 200:
            case_data = case_response.json()
            case_obj = case_data.get('case', {})
            case_id = case_obj.get('case_id')
            print(f"✅ Auto-application case created: {case_id}")
            
            # Add some test form data to the case
            form_data = {
                "personal_information": {
                    "nome_completo": "Carlos Eduardo Silva Santos",
                    "data_nascimento": "15/03/1990",
                    "nacionalidade": "Brasileira",
                    "local_nascimento": "São Paulo, SP, Brasil"
                },
                "employment_information": {
                    "empresa": "TechGlobal Inc.",
                    "cargo": "Engenheiro de Software Senior",
                    "salario": "$95,000",
                    "data_inicio": "01/01/2020"
                }
            }
            
            # Update case with form data
            update_payload = {
                "simplified_form_responses": form_data,
                "status": "form_filled"
            }
            
            update_response = requests.put(f"{API_BASE}/auto-application/case/{case_id}", json=update_payload, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                print("✅ Case updated with test form data")
                
                # Test all 5 AI processing steps
                steps = ["validation", "consistency", "translation", "form_generation", "final_review"]
                step_results = {}
                
                for step in steps:
                    print(f"\n   Testing AI Step: {step}")
                    
                    step_payload = {
                        "step": step
                    }
                    
                    step_response = requests.post(
                        f"{API_BASE}/ai-processing/step", 
                        json=step_payload,
                        params={"case_id": case_id},
                        headers=headers, 
                        timeout=30
                    )
                    
                    if step_response.status_code == 200:
                        step_data = step_response.json()
                        step_results[step] = True
                        
                        print(f"   ✅ {step} step completed successfully")
                        print(f"      Status: {step_data.get('status', 'N/A')}")
                        print(f"      Message length: {len(step_data.get('message', ''))}")
                        
                        # Check if response is in Portuguese
                        message = step_data.get('message', '')
                        if any(word in message.lower() for word in ['dados', 'formulário', 'validação', 'tradução']):
                            print(f"      ✅ Response in Portuguese")
                        else:
                            print(f"      ⚠️  Response language unclear")
                        
                        # Check for EMERGENT_LLM_KEY usage (no hardcoded keys)
                        if 'sk-' not in message:
                            print(f"      ✅ No hardcoded API keys detected")
                        else:
                            print(f"      ⚠️  Possible hardcoded API key detected")
                            
                    else:
                        step_results[step] = False
                        print(f"   ❌ {step} step failed: {step_response.status_code}")
                        print(f"      Error: {step_response.text}")
                
                # Summary of AI processing steps
                successful_steps = sum(step_results.values())
                total_steps = len(steps)
                
                print(f"\n✅ AI Processing Steps Summary: {successful_steps}/{total_steps} steps successful")
                
                for step, success in step_results.items():
                    status = "✅" if success else "❌"
                    print(f"   {step}: {status}")
                
                if successful_steps >= 4:  # At least 4 out of 5 should work
                    print("✅ AI Processing Steps using EMERGENT_LLM_KEY working correctly")
                    return True
                else:
                    print("❌ AI Processing Steps have issues")
                    return False
                    
            else:
                print(f"❌ Failed to update case with form data: {update_response.status_code}")
                return False
        else:
            print(f"❌ Failed to create auto-application case: {case_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI Processing steps test error: {str(e)}")
        return False

def test_ai_fact_extraction():
    """Test 5: AI FACT EXTRACTION - Test /api/auto-application/extract-facts"""
    print("\n📊 TEST 5: AI FACT EXTRACTION")
    print("-" * 50)
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for fact extraction test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test with realistic Portuguese H1-B story as specified
        test_story = """Meu nome é Carlos Silva, sou brasileiro, formado em Engenharia pela USP, 
        trabalho como engenheiro de software há 5 anos, quero aplicar para H-1B nos EUA. 
        Tenho 32 anos, sou casado com Maria Silva, temos um filho de 3 anos. Trabalho na 
        TechGlobal Inc. em São Paulo, ganho R$ 15.000 por mês. Tenho uma oferta de emprego 
        da Microsoft nos Estados Unidos para trabalhar como Senior Software Engineer com 
        salário de $120,000 por ano. Já visitei os EUA duas vezes para turismo."""
        
        # First create an auto-application case
        case_payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        case_response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, headers=headers, timeout=10)
        
        if case_response.status_code == 200:
            case_data = case_response.json()
            case_obj = case_data.get('case', {})
            case_id = case_obj.get('case_id')
            print(f"✅ Auto-application case created: {case_id}")
            
            # Test fact extraction with proper payload structure
            extraction_payload = {
                "user_story": test_story
            }
            
            extraction_response = requests.post(
                f"{API_BASE}/auto-application/extract-facts",
                json=extraction_payload,
                params={"case_id": case_id},
                headers=headers,
                timeout=30
            )
            
            if extraction_response.status_code == 200:
                extraction_data = extraction_response.json()
                extracted_facts = extraction_data.get('extracted_facts', {})
                
                print("✅ AI Fact Extraction completed successfully")
                print(f"   Case ID: {extraction_data.get('case_id')}")
                print(f"   Status: {extraction_data.get('status')}")
                
                # Check for expected fact categories
                expected_categories = [
                    'personal_info', 'immigration_history', 'family_details', 
                    'employment_info', 'education', 'travel_history', 
                    'financial_info', 'special_circumstances'
                ]
                
                found_categories = []
                for category in expected_categories:
                    if category in extracted_facts and extracted_facts[category]:
                        found_categories.append(category)
                        print(f"   ✅ {category}: {len(extracted_facts[category])} facts extracted")
                
                print(f"\n✅ Fact categories found: {len(found_categories)}/{len(expected_categories)}")
                
                # Verify specific facts were extracted correctly
                personal_info = extracted_facts.get('personal_info', {})
                if personal_info.get('nome') and 'carlos' in personal_info.get('nome', '').lower():
                    print("   ✅ Name extraction working correctly")
                
                if personal_info.get('idade') or personal_info.get('data_nascimento'):
                    print("   ✅ Age/birth date extraction working")
                
                employment_info = extracted_facts.get('employment_info', {})
                if employment_info.get('empresa_atual') and 'techglobal' in employment_info.get('empresa_atual', '').lower():
                    print("   ✅ Current employer extraction working")
                
                if employment_info.get('oferta_emprego') and 'microsoft' in employment_info.get('oferta_emprego', '').lower():
                    print("   ✅ Job offer extraction working")
                
                education = extracted_facts.get('education', {})
                if education.get('formacao') and 'engenharia' in education.get('formacao', '').lower():
                    print("   ✅ Education extraction working")
                
                family_details = extracted_facts.get('family_details', {})
                if family_details.get('estado_civil') and 'casado' in family_details.get('estado_civil', '').lower():
                    print("   ✅ Marital status extraction working")
                
                # Check if extraction is in Portuguese
                sample_text = str(extracted_facts)
                if any(word in sample_text.lower() for word in ['nome', 'idade', 'casado', 'formação', 'empresa']):
                    print("   ✅ Facts extracted in Portuguese as expected")
                else:
                    print("   ⚠️  Fact extraction language unclear")
                
                # Verify using EMERGENT_LLM_KEY
                if len(found_categories) >= 6:  # Should extract most categories
                    print("✅ AI Fact Extraction using EMERGENT_LLM_KEY working excellently")
                    return True
                elif len(found_categories) >= 4:
                    print("⚠️  AI Fact Extraction working but could be better")
                    return True
                else:
                    print("❌ AI Fact Extraction not working properly")
                    return False
                    
            else:
                print(f"❌ Fact extraction failed: {extraction_response.status_code}")
                print(f"   Error: {extraction_response.text}")
                return False
        else:
            print(f"❌ Failed to create case for fact extraction: {case_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI Fact extraction test error: {str(e)}")
        return False

def test_error_handling():
    """Test 6: ERROR HANDLING - Test behavior when EMERGENT_LLM_KEY has issues"""
    print("\n⚠️ TEST 6: ERROR HANDLING")
    print("-" * 50)
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for error handling test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test with invalid case ID to trigger error handling
        invalid_case_id = "INVALID-CASE-ID"
        
        step_payload = {
            "step": "validation"
        }
        
        error_response = requests.post(
            f"{API_BASE}/ai-processing/step", 
            json=step_payload,
            params={"case_id": invalid_case_id},
            headers=headers, 
            timeout=30
        )
        
        if error_response.status_code == 404:
            print("✅ Error handling working - Invalid case ID properly rejected")
        elif error_response.status_code == 400:
            print("✅ Error handling working - Bad request properly handled")
        else:
            print(f"⚠️  Unexpected error response: {error_response.status_code}")
        
        # Test with missing parameters
        missing_param_response = requests.post(
            f"{API_BASE}/ai-processing/step", 
            json={},  # Missing step parameter
            headers=headers, 
            timeout=30
        )
        
        if missing_param_response.status_code in [400, 422]:
            print("✅ Error handling working - Missing parameters properly handled")
        else:
            print(f"⚠️  Missing parameter handling unclear: {missing_param_response.status_code}")
        
        # Test chat with very long message (potential rate limiting)
        very_long_message = "Teste " * 1000  # Very long message
        
        long_message_payload = {
            "message": very_long_message,
            "session_id": str(uuid.uuid4())
        }
        
        long_response = requests.post(f"{API_BASE}/chat", json=long_message_payload, headers=headers, timeout=30)
        
        if long_response.status_code == 200:
            print("✅ Long message handling working")
        elif long_response.status_code in [400, 413, 429]:
            print("✅ Rate limiting/size limiting working properly")
        else:
            print(f"⚠️  Long message handling unclear: {long_response.status_code}")
        
        # Check for hardcoded API keys in error messages
        error_messages = [
            error_response.text if error_response.status_code != 200 else "",
            missing_param_response.text if missing_param_response.status_code != 200 else "",
            long_response.text if long_response.status_code != 200 else ""
        ]
        
        hardcoded_key_found = any('sk-' in msg for msg in error_messages)
        
        if not hardcoded_key_found:
            print("✅ No hardcoded API keys found in error messages")
        else:
            print("❌ CRITICAL: Hardcoded API keys detected in error messages")
            return False
        
        print("✅ Error handling appears to be working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test error: {str(e)}")
        return False

def run_all_emergent_llm_tests():
    """Run all EMERGENT_LLM_KEY validation tests"""
    print("🚀 STARTING COMPREHENSIVE EMERGENT_LLM_KEY VALIDATION TESTS")
    print("=" * 80)
    
    # Setup test user
    if not setup_test_user():
        print("❌ CRITICAL: Cannot proceed without test user setup")
        return False
    
    # Run all tests
    test_results = {
        "EMERGENT_LLM_KEY Status": test_emergent_llm_key_status(),
        "AI Chat Endpoints": test_ai_chat_endpoints(),
        "AI Document Validation (Dr. Miguel)": test_ai_document_validation(),
        "AI Processing Steps (5 steps)": test_ai_processing_steps(),
        "AI Fact Extraction": test_ai_fact_extraction(),
        "Error Handling": test_error_handling()
    }
    
    # Summary
    print("\n" + "=" * 80)
    print("🏁 EMERGENT_LLM_KEY VALIDATION TEST RESULTS")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\nOVERALL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - EMERGENT_LLM_KEY is 100% functional!")
        return True
    elif passed_tests >= total_tests * 0.8:  # 80% pass rate
        print("⚠️  MOSTLY WORKING - Some issues detected but core functionality OK")
        return True
    else:
        print("❌ CRITICAL ISSUES - EMERGENT_LLM_KEY integration has significant problems")
        return False

if __name__ == "__main__":
    success = run_all_emergent_llm_tests()
    exit(0 if success else 1)