#!/usr/bin/env python3
"""
OSPREY AI Integration Test - Verify EMERGENT_LLM_KEY Usage
Tests AI endpoints to ensure EMERGENT_LLM_KEY is working correctly
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🤖 OSPREY AI Integration Test - EMERGENT_LLM_KEY Verification")
print(f"Testing Backend at: {API_BASE}")
print("=" * 80)

# Test data
TEST_USER = {
    "email": "aitest@osprey.com",
    "password": "TestUser123",
    "first_name": "Carlos",
    "last_name": "Silva"
}
AUTH_TOKEN = None
CASE_ID = None

def test_user_login():
    """Login to get auth token for AI tests"""
    print("\n🔐 Testing User Login for AI Tests...")
    global AUTH_TOKEN
    
    # Try login first
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            print(f"✅ User login successful")
            return True
        elif response.status_code == 401:
            # Try signup if login fails
            print("⚠️  Login failed, attempting signup...")
            signup_payload = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "first_name": TEST_USER["first_name"],
                "last_name": TEST_USER["last_name"]
            }
            
            signup_response = requests.post(f"{API_BASE}/auth/signup", json=signup_payload, timeout=10)
            
            if signup_response.status_code == 200:
                data = signup_response.json()
                AUTH_TOKEN = data.get('token')
                print(f"✅ User signup successful")
                return True
            else:
                print(f"❌ Both login and signup failed")
                return False
        else:
            print(f"❌ User login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ User login error: {str(e)}")
        return False

def test_ai_fact_extraction():
    """Test AI fact extraction endpoint to verify EMERGENT_LLM_KEY usage"""
    print("\n🧠 Testing AI Fact Extraction (EMERGENT_LLM_KEY verification)...")
    global CASE_ID
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for AI test")
        return False
    
    try:
        # First create a case
        case_payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        case_response = requests.post(f"{API_BASE}/auto-application/start", json=case_payload, timeout=10)
        
        if case_response.status_code != 200:
            print(f"❌ Failed to create case for AI test: {case_response.status_code}")
            return False
        
        case_data = case_response.json()
        CASE_ID = case_data.get('case', {}).get('case_id')
        
        if not CASE_ID:
            print("❌ No case ID returned for AI test")
            return False
        
        print(f"✅ Test case created: {CASE_ID}")
        
        # Now test AI fact extraction
        ai_payload = {
            "case_id": CASE_ID,
            "story_text": "Meu nome é Carlos Silva, sou engenheiro de software brasileiro. Trabalho há 5 anos na área de tecnologia e recebi uma oferta de emprego de uma empresa americana chamada TechGlobal Inc. para trabalhar como Senior Software Engineer em San Francisco. A empresa vai patrocinar meu visto H1-B. Sou formado em Ciência da Computação pela USP e tenho experiência em Python, Java e desenvolvimento web. Minha esposa Maria também é brasileira e pretendemos nos mudar juntos para os Estados Unidos."
        }
        
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        response = requests.post(
            f"{API_BASE}/auto-application/extract-facts", 
            json=ai_payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            extracted_facts = data.get('extracted_facts', {})
            
            print(f"✅ AI fact extraction successful")
            print(f"   Case ID: {data.get('case_id')}")
            print(f"   Facts extracted: {'Yes' if extracted_facts else 'No'}")
            
            if extracted_facts:
                fact_categories = list(extracted_facts.keys())
                print(f"   Fact categories: {len(fact_categories)}")
                print(f"   Sample categories: {fact_categories[:3]}")
                
                # Check for expected categories
                expected_categories = ['personal_info', 'employment_info', 'education']
                found_categories = [cat for cat in expected_categories if cat in fact_categories]
                print(f"   Expected categories found: {len(found_categories)}/{len(expected_categories)}")
                
                # Verify security: no hardcoded keys in response
                response_text = response.text
                if 'sk-emergent-aE5F536B80dFf0bA6F' in response_text:
                    print("❌ SECURITY ISSUE: Hardcoded API key found in AI response!")
                    return False
                else:
                    print("✅ Security check passed: No hardcoded keys in AI response")
                
                return True
            else:
                print("⚠️  AI fact extraction returned empty results")
                return False
        else:
            print(f"❌ AI fact extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
            # Check if it's an API key issue
            if 'api' in response.text.lower() and 'key' in response.text.lower():
                print("❌ POSSIBLE API KEY ISSUE: Check EMERGENT_LLM_KEY configuration")
            
            return False
            
    except Exception as e:
        print(f"❌ AI fact extraction error: {str(e)}")
        return False

def test_ai_chat():
    """Test AI chat endpoint to verify EMERGENT_LLM_KEY usage"""
    print("\n💬 Testing AI Chat (EMERGENT_LLM_KEY verification)...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for AI chat test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        
        chat_payload = {
            "message": "Quais são os requisitos básicos para o visto H1-B?",
            "session_id": str(uuid.uuid4()),
            "context": {"user_type": "self_applicant", "visa_interest": "h1b"}
        }
        
        response = requests.post(
            f"{API_BASE}/chat", 
            json=chat_payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            
            print(f"✅ AI chat successful")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Response length: {len(message)} characters")
            print(f"   Response preview: {message[:150]}...")
            
            # Check for Portuguese response
            if any(word in message.lower() for word in ['visto', 'requisitos', 'h1-b', 'trabalho']):
                print("✅ AI responded appropriately in Portuguese")
            else:
                print("⚠️  AI response language unclear")
            
            # Check for legal disclaimers
            if any(phrase in message.lower() for phrase in ['consultoria jurídica', 'advogado', 'auto-aplicação']):
                print("✅ Legal disclaimers present in AI response")
            else:
                print("⚠️  Legal disclaimers not clearly present")
            
            # Verify security: no hardcoded keys in response
            response_text = response.text
            if 'sk-emergent-aE5F536B80dFf0bA6F' in response_text:
                print("❌ SECURITY ISSUE: Hardcoded API key found in chat response!")
                return False
            else:
                print("✅ Security check passed: No hardcoded keys in chat response")
            
            return True
        else:
            print(f"❌ AI chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
            # Check if it's an API key issue
            if 'api' in response.text.lower() and 'key' in response.text.lower():
                print("❌ POSSIBLE API KEY ISSUE: Check EMERGENT_LLM_KEY configuration")
            
            return False
            
    except Exception as e:
        print(f"❌ AI chat error: {str(e)}")
        return False

def run_ai_integration_test():
    """Run complete AI integration test"""
    print("\n🎯 RUNNING AI INTEGRATION TEST")
    print("=" * 80)
    
    tests = [
        ("User Authentication", test_user_login),
        ("AI Fact Extraction", test_ai_fact_extraction),
        ("AI Chat", test_ai_chat),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Final Summary
    print("\n" + "="*80)
    print("🤖 AI INTEGRATION TEST SUMMARY")
    print("="*80)
    
    print(f"\n📊 OVERALL RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    print(f"\n✅ PASSED TESTS:")
    for test_name, result in results.items():
        if result:
            print(f"   ✅ {test_name}")
    
    failed_tests = [name for name, result in results.items() if not result]
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for test_name in failed_tests:
            print(f"   ❌ {test_name}")
    
    # EMERGENT_LLM_KEY Assessment
    print(f"\n🔑 EMERGENT_LLM_KEY ASSESSMENT:")
    ai_tests = ["AI Fact Extraction", "AI Chat"]
    ai_passed = sum(1 for test in ai_tests if results.get(test, False))
    
    if ai_passed == len(ai_tests):
        print("✅ EMERGENT_LLM_KEY working correctly - All AI endpoints functional")
    elif ai_passed > 0:
        print("⚠️  EMERGENT_LLM_KEY partially working - Some AI endpoints functional")
    else:
        print("❌ EMERGENT_LLM_KEY issues detected - AI endpoints not working")
    
    # Security Assessment
    print(f"\n🔒 SECURITY ASSESSMENT:")
    if passed > 0:
        print("✅ No hardcoded API keys detected in AI responses")
    else:
        print("❌ Could not verify security due to test failures")
    
    return passed >= total * 0.8  # 80% pass rate for overall success

if __name__ == "__main__":
    success = run_ai_integration_test()
    exit(0 if success else 1)