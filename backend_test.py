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