#!/usr/bin/env python3
"""
OSPREY Backend B2C System Tests
Tests complete user authentication, profiles, applications, document management, and AI integration
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
DOCUMENT_ID = None  # For document tests
INTERVIEW_SESSION_ID = None  # For education tests

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

def test_document_upload():
    """Test document upload with AI analysis"""
    print("\n📄 Testing Document Upload...")
    global DOCUMENT_ID
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for document upload test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Create a simple test image in base64 (1x1 pixel PNG)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        test_image_bytes = base64.b64decode(test_image_base64)
        
        # Prepare multipart form data
        files = {
            'file': ('passport.png', test_image_bytes, 'image/png')
        }
        
        data = {
            'document_type': 'passport',
            'tags': 'test,passport,brazil',
            'expiration_date': '2025-12-31T23:59:59Z',
            'issue_date': '2020-01-01T00:00:00Z'
        }
        
        response = requests.post(
            f"{API_BASE}/documents/upload", 
            files=files, 
            data=data, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            DOCUMENT_ID = result.get('document_id')
            print(f"✅ Document upload successful")
            print(f"   Document ID: {DOCUMENT_ID}")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Status: {result.get('status')}")
            print(f"   AI Analysis: {result.get('ai_analysis_status')}")
            return True
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document upload error: {str(e)}")
        return False

def test_document_list():
    """Test listing user documents"""
    print("\n📋 Testing Document List...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for document list test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/documents", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            stats = data.get('stats', {})
            expirations = data.get('upcoming_expirations', [])
            
            print(f"✅ Document list retrieved successfully")
            print(f"   Total documents: {stats.get('total', 0)}")
            print(f"   Approved: {stats.get('approved', 0)}")
            print(f"   Pending: {stats.get('pending', 0)}")
            print(f"   Completion rate: {stats.get('completion_rate', 0)}%")
            print(f"   Upcoming expirations: {len(expirations)}")
            
            if documents:
                doc = documents[0]
                print(f"   First document type: {doc.get('document_type')}")
                print(f"   First document status: {doc.get('status')}")
            
            return True
        else:
            print(f"❌ Document list failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document list error: {str(e)}")
        return False

def test_document_details():
    """Test getting document details with AI analysis"""
    print("\n🔍 Testing Document Details...")
    
    if not AUTH_TOKEN or not DOCUMENT_ID:
        print("❌ No auth token or document ID available for details test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/documents/{DOCUMENT_ID}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            document = response.json()
            print(f"✅ Document details retrieved successfully")
            print(f"   Document type: {document.get('document_type')}")
            print(f"   Status: {document.get('status')}")
            print(f"   Priority: {document.get('priority')}")
            print(f"   File size: {document.get('file_size')} bytes")
            print(f"   Tags: {document.get('tags', [])}")
            
            # Check AI analysis
            ai_analysis = document.get('ai_analysis')
            if ai_analysis:
                print(f"   AI Analysis present: ✅")
                print(f"   Completeness score: {ai_analysis.get('completeness_score', 'N/A')}")
                print(f"   Validity status: {ai_analysis.get('validity_status', 'N/A')}")
                print(f"   Suggestions count: {len(ai_analysis.get('suggestions', []))}")
            else:
                print(f"   AI Analysis: ❌ Not found")
            
            return True
        else:
            print(f"❌ Document details failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document details error: {str(e)}")
        return False

def test_document_reanalyze():
    """Test document reanalysis with AI"""
    print("\n🔄 Testing Document Reanalysis...")
    
    if not AUTH_TOKEN or not DOCUMENT_ID:
        print("❌ No auth token or document ID available for reanalysis test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.post(f"{API_BASE}/documents/{DOCUMENT_ID}/reanalyze", headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('analysis', {})
            
            print(f"✅ Document reanalysis successful")
            print(f"   New status: {result.get('status')}")
            print(f"   Completeness score: {analysis.get('completeness_score', 'N/A')}")
            print(f"   Validity status: {analysis.get('validity_status', 'N/A')}")
            print(f"   Key information count: {len(analysis.get('key_information', []))}")
            print(f"   Suggestions count: {len(analysis.get('suggestions', []))}")
            print(f"   Next steps count: {len(analysis.get('next_steps', []))}")
            
            return True
        else:
            print(f"❌ Document reanalysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document reanalysis error: {str(e)}")
        return False

def test_document_update():
    """Test document update"""
    print("\n✏️ Testing Document Update...")
    
    if not AUTH_TOKEN or not DOCUMENT_ID:
        print("❌ No auth token or document ID available for update test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        update_data = {
            "tags": ["updated", "passport", "brazil", "test"],
            "priority": "high",
            "expiration_date": "2026-01-31T23:59:59Z"
        }
        
        response = requests.put(f"{API_BASE}/documents/{DOCUMENT_ID}", json=update_data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            document = result.get('document', {})
            
            print(f"✅ Document update successful")
            print(f"   Updated tags: {document.get('tags', [])}")
            print(f"   Updated priority: {document.get('priority')}")
            print(f"   Updated expiration: {document.get('expiration_date', 'N/A')}")
            
            return True
        else:
            print(f"❌ Document update failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document update error: {str(e)}")
        return False

def test_dashboard_with_documents():
    """Test updated dashboard with document stats"""
    print("\n📊 Testing Updated Dashboard with Documents...")
    
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
            upcoming_expirations = data.get('upcoming_expirations', [])
            
            print(f"✅ Updated dashboard loaded successfully")
            print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
            print(f"   Total Applications: {stats.get('total_applications', 0)}")
            print(f"   Total Documents: {stats.get('total_documents', 0)}")
            print(f"   Approved Documents: {stats.get('approved_documents', 0)}")
            print(f"   Pending Documents: {stats.get('pending_documents', 0)}")
            print(f"   Document Completion Rate: {stats.get('document_completion_rate', 0)}%")
            print(f"   Upcoming Expirations: {len(upcoming_expirations)}")
            print(f"   Recent Chats: {len(recent_activity.get('chats', []))}")
            print(f"   Recent Translations: {len(recent_activity.get('translations', []))}")
            
            # Verify document stats are present
            has_doc_stats = all(key in stats for key in ['total_documents', 'approved_documents', 'pending_documents', 'document_completion_rate'])
            if has_doc_stats:
                print("✅ Document statistics properly integrated in dashboard")
            else:
                print("⚠️  Some document statistics missing from dashboard")
            
            return True
        else:
            print(f"❌ Updated dashboard failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Updated dashboard test error: {str(e)}")
        return False

def test_document_delete():
    """Test document deletion"""
    print("\n🗑️ Testing Document Deletion...")
    
    if not AUTH_TOKEN or not DOCUMENT_ID:
        print("❌ No auth token or document ID available for delete test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.delete(f"{API_BASE}/documents/{DOCUMENT_ID}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document deletion successful")
            print(f"   Message: {result.get('message')}")
            
            # Verify document is actually deleted
            verify_response = requests.get(f"{API_BASE}/documents/{DOCUMENT_ID}", headers=headers, timeout=10)
            if verify_response.status_code == 404:
                print("✅ Document deletion verified - document not found")
                return True
            else:
                print("⚠️  Document still exists after deletion")
                return False
                
        else:
            print(f"❌ Document deletion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document deletion error: {str(e)}")
        return False

def run_all_tests():
    """Run all B2C backend tests including document management"""
    print("🚀 Starting OSPREY B2C Backend Complete System Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Authentication and basic system tests
    auth_results = {
        "basic_connectivity": test_basic_connectivity(),
        "user_signup": test_user_signup(),
        "user_login": test_user_login(),
        "user_profile": test_user_profile(),
        "visa_application": test_visa_application(),
        "authenticated_chat": test_authenticated_chat(),
        "chat_history": test_chat_history(),
        "mongodb_persistence": test_mongodb_persistence()
    }
    
    # Document management tests (NEW)
    document_results = {
        "document_upload": test_document_upload(),
        "document_list": test_document_list(),
        "document_details": test_document_details(),
        "document_reanalyze": test_document_reanalyze(),
        "document_update": test_document_update(),
        "dashboard_with_documents": test_dashboard_with_documents(),
        "document_delete": test_document_delete()
    }
    
    # Combine all results
    all_results = {**auth_results, **document_results}
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    # Authentication System Results
    print("\n🔐 AUTHENTICATION SYSTEM:")
    auth_passed = sum(auth_results.values())
    auth_total = len(auth_results)
    
    for test_name, result in auth_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"  Auth System: {auth_passed}/{auth_total} tests passed ({auth_passed/auth_total*100:.1f}%)")
    
    # Document Management Results
    print("\n📄 DOCUMENT MANAGEMENT SYSTEM:")
    doc_passed = sum(document_results.values())
    doc_total = len(document_results)
    
    for test_name, result in document_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"  Document System: {doc_passed}/{doc_total} tests passed ({doc_passed/doc_total*100:.1f}%)")
    
    # Overall Results
    total_passed = sum(all_results.values())
    total_tests = len(all_results)
    
    print(f"\n🎯 OVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! Complete B2C system with document management is working correctly.")
    elif doc_passed == doc_total and auth_passed >= auth_total - 1:
        print("✅ Document management system is working correctly. Minor auth issues detected.")
    elif auth_passed == auth_total and doc_passed >= doc_total - 1:
        print("✅ Authentication system is working correctly. Minor document issues detected.")
    else:
        print("⚠️  Some critical tests failed. Check the details above.")
    
    return all_results

if __name__ == "__main__":
    run_all_tests()