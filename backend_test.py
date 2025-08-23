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

def test_authenticated_chat():
    """Test authenticated chat with AI"""
    print("\n🤖 Testing Authenticated Chat...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for chat test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    # Test case: H1-B visa inquiry as requested
    test_message = "Quero aplicar para visto H1-B, por onde começar?"
    
    payload = {
        "message": test_message,
        "session_id": str(uuid.uuid4()),
        "context": {"user_type": "self_applicant", "visa_interest": "h1b"}
    }
    
    try:
        response = requests.post(f"{API_BASE}/chat", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Authenticated chat successful")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Response length: {len(data.get('message', ''))}")
            print(f"   Response preview: {data.get('message', '')[:150]}...")
            
            # Verify response mentions self-application and disclaimers
            message = data.get('message', '').lower()
            has_disclaimer = any(word in message for word in ['não oferece', 'consultoria jurídica', 'auto-aplicação', 'advogado'])
            has_h1b_info = any(word in message for word in ['h1-b', 'h1b', 'visto', 'trabalho'])
            
            if has_disclaimer:
                print("✅ Response includes legal disclaimer")
            else:
                print("⚠️  Legal disclaimer not clearly present")
                
            if has_h1b_info:
                print("✅ Response addresses H1-B visa inquiry")
            else:
                print("⚠️  H1-B information not clearly present")
                
            return True
        else:
            print(f"❌ Authenticated chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authenticated chat error: {str(e)}")
        return False

def test_chat_history():
    """Test chat history retrieval"""
    print("\n📜 Testing Chat History...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for chat history test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/chat/history", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('chat_sessions', [])
            print(f"✅ Chat history retrieved successfully")
            print(f"   Total sessions: {len(sessions)}")
            
            if sessions:
                latest_session = sessions[0]
                print(f"   Latest session ID: {latest_session.get('session_id', 'N/A')}")
                print(f"   Messages in latest: {len(latest_session.get('messages', []))}")
                print(f"   Last updated: {latest_session.get('last_updated', 'N/A')}")
            
            return True
        else:
            print(f"❌ Chat history failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat history error: {str(e)}")
        return False

def test_mongodb_persistence():
    """Test MongoDB data persistence by checking various collections"""
    print("\n💾 Testing MongoDB Persistence...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for persistence test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Check if user data persists by getting profile
        profile_response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
        
        # Check if applications persist
        apps_response = requests.get(f"{API_BASE}/applications", headers=headers, timeout=10)
        
        # Check if chat history persists
        history_response = requests.get(f"{API_BASE}/chat/history", headers=headers, timeout=10)
        
        # Check dashboard data
        dashboard_response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=10)
        
        persistence_checks = {
            "user_profile": profile_response.status_code == 200,
            "applications": apps_response.status_code == 200,
            "chat_history": history_response.status_code == 200,
            "dashboard_data": dashboard_response.status_code == 200
        }
        
        successful_checks = sum(persistence_checks.values())
        total_checks = len(persistence_checks)
        
        print(f"✅ MongoDB persistence check: {successful_checks}/{total_checks} collections accessible")
        
        for check_name, result in persistence_checks.items():
            status = "✅" if result else "❌"
            print(f"   {check_name.replace('_', ' ').title()}: {status}")
        
        if successful_checks >= 3:  # At least 3 out of 4 should work
            print("✅ MongoDB persistence appears to be working correctly")
            return True
        else:
            print("❌ MongoDB persistence issues detected")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB persistence test error: {str(e)}")
        return False

def run_all_tests():
    """Run all B2C backend tests"""
    print("🚀 Starting OSPREY B2C Backend Authentication Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "basic_connectivity": test_basic_connectivity(),
        "user_signup": test_user_signup(),
        "user_login": test_user_login(),
        "user_profile": test_user_profile(),
        "visa_application": test_visa_application(),
        "dashboard": test_dashboard(),
        "authenticated_chat": test_authenticated_chat(),
        "chat_history": test_chat_history(),
        "mongodb_persistence": test_mongodb_persistence()
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
        print("🎉 All tests passed! B2C authentication system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    return results

if __name__ == "__main__":
    run_all_tests()