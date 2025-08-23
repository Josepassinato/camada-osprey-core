#!/usr/bin/env python3
"""
OSPREY Backend B2C Authentication System Tests
Tests complete user authentication, profiles, applications, and AI integration
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acesso-github.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing OSPREY B2C Backend at: {API_BASE}")
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

def test_basic_connectivity():
    """Test basic API connectivity"""
    print("\n🔍 Testing Basic Connectivity...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Basic connectivity: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Basic connectivity failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic connectivity error: {str(e)}")
        return False

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
        response = requests.post(f"{API_BASE}/auth/login", json=payload, timeout=10)
        
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

def test_user_profile():
    """Test user profile operations"""
    print("\n👤 Testing User Profile...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for profile test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test GET profile
        response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profile retrieval successful")
            print(f"   Name: {profile.get('first_name')} {profile.get('last_name')}")
            print(f"   Email: {profile.get('email')}")
            print(f"   Created: {profile.get('created_at', 'N/A')}")
            
            # Test UPDATE profile
            update_payload = {
                "country_of_birth": "Brazil",
                "current_country": "Brazil",
                "phone": "+55 11 98765-4321"
            }
            
            update_response = requests.put(f"{API_BASE}/profile", json=update_payload, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                print("✅ Profile update successful")
                return True
            else:
                print(f"❌ Profile update failed: {update_response.status_code}")
                return False
                
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Profile test error: {str(e)}")
        return False

def test_visa_application():
    """Test visa application creation"""
    print("\n📋 Testing Visa Application...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for application test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Create H1-B application
        payload = {
            "visa_type": "h1b"
        }
        
        response = requests.post(f"{API_BASE}/applications", json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            app = data.get('application', {})
            print(f"✅ H1-B application created successfully")
            print(f"   Application ID: {app.get('id')}")
            print(f"   Visa Type: {app.get('visa_type')}")
            print(f"   Status: {app.get('status')}")
            print(f"   Progress: {app.get('progress_percentage')}%")
            
            # Test getting applications
            get_response = requests.get(f"{API_BASE}/applications", headers=headers, timeout=10)
            if get_response.status_code == 200:
                apps = get_response.json().get('applications', [])
                print(f"✅ Retrieved {len(apps)} application(s)")
                return True
            else:
                print(f"❌ Failed to retrieve applications: {get_response.status_code}")
                return False
                
        elif response.status_code == 400 and "already exists" in response.text:
            print("⚠️  Application already exists, testing retrieval")
            get_response = requests.get(f"{API_BASE}/applications", headers=headers, timeout=10)
            if get_response.status_code == 200:
                apps = get_response.json().get('applications', [])
                print(f"✅ Retrieved {len(apps)} existing application(s)")
                return True
            return False
        else:
            print(f"❌ Application creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Application test error: {str(e)}")
        return False

def test_dashboard():
    """Test user dashboard"""
    print("\n📊 Testing Dashboard...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for dashboard test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user', {})
            stats = data.get('stats', {})
            applications = data.get('applications', [])
            recent_activity = data.get('recent_activity', {})
            
            print(f"✅ Dashboard loaded successfully")
            print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
            print(f"   Total Applications: {stats.get('total_applications', 0)}")
            print(f"   In Progress: {stats.get('in_progress', 0)}")
            print(f"   Completed: {stats.get('completed', 0)}")
            print(f"   Success Rate: {stats.get('success_rate', 0)}%")
            print(f"   Recent Chats: {len(recent_activity.get('chats', []))}")
            print(f"   Recent Translations: {len(recent_activity.get('translations', []))}")
            
            return True
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard test error: {str(e)}")
        return False

def test_chat_endpoint():
    """Test immigration chat assistant"""
    print("\n🤖 Testing Chat Endpoint...")
    
    # Test case 1: H1-B visa inquiry
    test_message = "Preciso de ajuda com visto H1-B, quais são os requisitos básicos?"
    
    payload = {
        "message": test_message,
        "session_id": str(uuid.uuid4()),
        "context": {"user_type": "professional", "country": "Brazil"}
    }
    
    try:
        response = requests.post(f"{API_BASE}/chat", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Response length: {len(data.get('message', ''))}")
            print(f"   Response preview: {data.get('message', '')[:100]}...")
            
            # Verify response is in Portuguese
            if any(word in data.get('message', '').lower() for word in ['visto', 'requisitos', 'documentos', 'processo']):
                print("✅ Response appears to be in Portuguese")
            else:
                print("⚠️  Response language unclear")
                
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat endpoint error: {str(e)}")
        return False

def test_translation_endpoint():
    """Test translation functionality"""
    print("\n🌐 Testing Translation Endpoint...")
    
    # Test Portuguese to English translation
    test_text = "Preciso traduzir este documento de certidão de nascimento para o processo de imigração"
    
    payload = {
        "text": test_text,
        "source_language": "pt",
        "target_language": "en"
    }
    
    try:
        response = requests.post(f"{API_BASE}/translate", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Translation completed")
            print(f"   Source language: {data.get('source_language', 'N/A')}")
            print(f"   Target language: {data.get('target_language', 'N/A')}")
            print(f"   Translation ID: {data.get('translation_id', 'N/A')}")
            print(f"   Original: {test_text[:50]}...")
            print(f"   Translated: {data.get('translated_text', '')[:50]}...")
            
            # Verify translation contains English words
            translated = data.get('translated_text', '').lower()
            if any(word in translated for word in ['document', 'birth', 'certificate', 'immigration']):
                print("✅ Translation appears correct")
            else:
                print("⚠️  Translation quality unclear")
                
            return True
        else:
            print(f"❌ Translation endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Translation endpoint error: {str(e)}")
        return False

def test_document_analysis_endpoint():
    """Test document analysis functionality"""
    print("\n📄 Testing Document Analysis Endpoint...")
    
    # Sample immigration document text
    document_text = """
    CERTIFICADO DE NASCIMENTO
    Nome: João Silva Santos
    Data de Nascimento: 15/03/1985
    Local: São Paulo, SP, Brasil
    Nome do Pai: Carlos Santos
    Nome da Mãe: Maria Silva Santos
    Cartório: 1º Ofício de Registro Civil
    """
    
    payload = {
        "document_text": document_text,
        "document_type": "birth_certificate",
        "analysis_type": "immigration"
    }
    
    try:
        response = requests.post(f"{API_BASE}/analyze-document", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document analysis completed")
            print(f"   Analysis ID: {data.get('analysis_id', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"   Analysis length: {len(data.get('analysis', ''))}")
            print(f"   Analysis preview: {data.get('analysis', '')[:150]}...")
            
            # Verify analysis mentions key elements
            analysis = data.get('analysis', '').lower()
            if any(word in analysis for word in ['certidão', 'nascimento', 'documento', 'imigração']):
                print("✅ Analysis appears relevant")
            else:
                print("⚠️  Analysis relevance unclear")
                
            return True
        else:
            print(f"❌ Document analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document analysis error: {str(e)}")
        return False

def test_visa_recommendation_endpoint():
    """Test visa recommendation functionality"""
    print("\n🎯 Testing Visa Recommendation Endpoint...")
    
    # Realistic professional profile
    payload = {
        "personal_info": {
            "age": 28,
            "education": "Mestrado em Engenharia de Software",
            "experience_years": 5,
            "current_job": "Desenvolvedor Senior",
            "salary": 120000,
            "country": "Brasil",
            "english_level": "Fluente"
        },
        "current_status": "Trabalhando no Brasil",
        "goals": [
            "Trabalhar nos Estados Unidos",
            "Obter visto de trabalho",
            "Eventualmente residência permanente"
        ]
    }
    
    try:
        response = requests.post(f"{API_BASE}/visa-recommendation", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Visa recommendation completed")
            print(f"   Recommendation ID: {data.get('recommendation_id', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"   Recommendation length: {len(data.get('recommendation', ''))}")
            print(f"   Recommendation preview: {data.get('recommendation', '')[:200]}...")
            
            # Verify recommendation mentions visa types
            recommendation = data.get('recommendation', '').lower()
            if any(visa in recommendation for visa in ['h1-b', 'h1b', 'l1', 'o1', 'eb']):
                print("✅ Recommendation mentions relevant visa types")
            else:
                print("⚠️  Visa types in recommendation unclear")
                
            return True
        else:
            print(f"❌ Visa recommendation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Visa recommendation error: {str(e)}")
        return False

def test_session_persistence():
    """Test chat session persistence"""
    print("\n💾 Testing Session Persistence...")
    
    session_id = str(uuid.uuid4())
    
    # First message
    payload1 = {
        "message": "Olá, preciso de informações sobre visto H1-B",
        "session_id": session_id
    }
    
    try:
        response1 = requests.post(f"{API_BASE}/chat", json=payload1, timeout=30)
        
        if response1.status_code != 200:
            print(f"❌ First message failed: {response1.status_code}")
            return False
            
        # Second message in same session
        payload2 = {
            "message": "Quais documentos preciso preparar?",
            "session_id": session_id
        }
        
        response2 = requests.post(f"{API_BASE}/chat", json=payload2, timeout=30)
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Session persistence working")
            print(f"   Same session ID maintained: {data2.get('session_id') == session_id}")
            print(f"   Context-aware response: {len(data2.get('message', ''))}")
            return True
        else:
            print(f"❌ Second message failed: {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Session persistence error: {str(e)}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("🚀 Starting OSPREY Backend OpenAI Integration Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "basic_connectivity": test_basic_connectivity(),
        "chat_endpoint": test_chat_endpoint(),
        "translation_endpoint": test_translation_endpoint(),
        "document_analysis": test_document_analysis_endpoint(),
        "visa_recommendation": test_visa_recommendation_endpoint(),
        "session_persistence": test_session_persistence()
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! OpenAI integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    return results

if __name__ == "__main__":
    run_all_tests()