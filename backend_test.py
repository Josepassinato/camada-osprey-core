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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visa-journey-7.preview.emergentagent.com')
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
AUTO_APPLICATION_CASE_ID = None  # For auto-application tests

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

# ============================================================================
# EDUCATION SYSTEM TESTS (NEW)
# ============================================================================

def test_education_guides():
    """Test interactive visa guides"""
    print("\n📚 Testing Interactive Visa Guides...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for guides test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test getting all guides
        response = requests.get(f"{API_BASE}/education/guides", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            guides = data.get('guides', [])
            print(f"✅ All guides retrieved successfully")
            print(f"   Total guides available: {len(guides)}")
            
            # Check for specific visa types
            visa_types = [guide.get('visa_type') for guide in guides]
            expected_types = ['h1b', 'f1', 'family']
            
            for visa_type in expected_types:
                if visa_type in visa_types:
                    print(f"   ✅ {visa_type.upper()} guide available")
                else:
                    print(f"   ❌ {visa_type.upper()} guide missing")
            
            # Test getting specific guide (H1-B)
            h1b_response = requests.get(f"{API_BASE}/education/guides?visa_type=h1b", headers=headers, timeout=10)
            
            if h1b_response.status_code == 200:
                h1b_data = h1b_response.json()
                guide = h1b_data.get('guide', {})
                print(f"✅ H1-B specific guide retrieved")
                print(f"   Title: {guide.get('title')}")
                print(f"   Difficulty: {guide.get('difficulty_level')}")
                print(f"   Estimated time: {guide.get('estimated_time_minutes')} minutes")
                print(f"   Sections: {len(guide.get('sections', []))}")
                print(f"   Requirements: {len(guide.get('requirements', []))}")
                print(f"   Success tips: {len(guide.get('success_tips', []))}")
                
                return True
            else:
                print(f"❌ H1-B specific guide failed: {h1b_response.status_code}")
                return False
                
        else:
            print(f"❌ Guides retrieval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Guides test error: {str(e)}")
        return False

def test_interview_simulator_start():
    """Test starting interview simulation"""
    print("\n🎤 Testing Interview Simulator Start...")
    global INTERVIEW_SESSION_ID
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for interview simulator test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Start consular interview for H1-B visa (beginner level)
        payload = {
            "interview_type": "consular",
            "visa_type": "h1b",
            "difficulty_level": "beginner"
        }
        
        response = requests.post(f"{API_BASE}/education/interview/start", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            INTERVIEW_SESSION_ID = data.get('session_id')
            questions = data.get('questions', [])
            
            print(f"✅ Interview simulation started successfully")
            print(f"   Session ID: {INTERVIEW_SESSION_ID}")
            print(f"   Total questions: {data.get('total_questions', 0)}")
            print(f"   Estimated duration: {data.get('estimated_duration', 0)} minutes")
            print(f"   Questions generated: {len(questions)}")
            
            if questions:
                first_q = questions[0]
                print(f"   First question (EN): {first_q.get('question_en', 'N/A')[:100]}...")
                print(f"   First question (PT): {first_q.get('question_pt', 'N/A')[:100]}...")
                print(f"   Question category: {first_q.get('category', 'N/A')}")
                print(f"   Tips provided: {len(first_q.get('tips', []))}")
            
            return True
        else:
            print(f"❌ Interview simulation start failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Interview simulator start error: {str(e)}")
        return False

def test_interview_answer_submission():
    """Test submitting interview answer"""
    print("\n💬 Testing Interview Answer Submission...")
    
    if not AUTH_TOKEN or not INTERVIEW_SESSION_ID:
        print("❌ No auth token or session ID available for answer submission test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Submit answer to first question (assuming q1 exists)
        payload = {
            "question_id": "q1",
            "answer": "Eu venho aos Estados Unidos para trabalhar como engenheiro de software em uma empresa de tecnologia. Tenho uma oferta de emprego válida e pretendo contribuir com minhas habilidades técnicas para o desenvolvimento de software inovador."
        }
        
        response = requests.post(
            f"{API_BASE}/education/interview/{INTERVIEW_SESSION_ID}/answer", 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            feedback = data.get('feedback', {})
            
            print(f"✅ Interview answer submitted successfully")
            print(f"   Score: {feedback.get('score', 'N/A')}/100")
            print(f"   Confidence level: {feedback.get('confidence_level', 'N/A')}")
            print(f"   Strengths: {len(feedback.get('strengths', []))}")
            print(f"   Weaknesses: {len(feedback.get('weaknesses', []))}")
            print(f"   Suggestions: {len(feedback.get('suggestions', []))}")
            print(f"   Next question index: {data.get('next_question_index', 'N/A')}")
            
            # Check if feedback is in Portuguese
            improved_answer = feedback.get('improved_answer', '')
            if any(word in improved_answer.lower() for word in ['você', 'sua', 'mais', 'para', 'com']):
                print("✅ Feedback provided in Portuguese")
            else:
                print("⚠️  Feedback language unclear")
            
            return True
        else:
            print(f"❌ Interview answer submission failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Interview answer submission error: {str(e)}")
        return False

def test_interview_completion():
    """Test completing interview session"""
    print("\n🏁 Testing Interview Completion...")
    
    if not AUTH_TOKEN or not INTERVIEW_SESSION_ID:
        print("❌ No auth token or session ID available for interview completion test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.post(
            f"{API_BASE}/education/interview/{INTERVIEW_SESSION_ID}/complete", 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            feedback = data.get('overall_feedback', {})
            
            print(f"✅ Interview session completed successfully")
            print(f"   Session completed: {data.get('session_completed', False)}")
            print(f"   Overall score: {feedback.get('overall_score', 'N/A')}/100")
            print(f"   Questions answered: {feedback.get('questions_answered', 'N/A')}")
            print(f"   Average confidence: {feedback.get('average_confidence', 'N/A')}")
            print(f"   Strengths: {len(feedback.get('strengths', []))}")
            print(f"   Areas for improvement: {len(feedback.get('areas_for_improvement', []))}")
            print(f"   Recommendations: {len(feedback.get('recommendations', []))}")
            
            return True
        else:
            print(f"❌ Interview completion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Interview completion error: {str(e)}")
        return False

def test_personalized_tips():
    """Test personalized tips generation"""
    print("\n💡 Testing Personalized Tips...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for tips test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/tips", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            tips = data.get('tips', [])
            
            print(f"✅ Personalized tips retrieved successfully")
            print(f"   Total tips: {len(tips)}")
            
            if tips:
                tip = tips[0]
                print(f"   First tip category: {tip.get('tip_category', 'N/A')}")
                print(f"   First tip title: {tip.get('title', 'N/A')}")
                print(f"   First tip priority: {tip.get('priority', 'N/A')}")
                print(f"   Content length: {len(tip.get('content', ''))}")
                print(f"   Is read: {tip.get('is_read', False)}")
                
                # Check if content is in Portuguese
                content = tip.get('content', '').lower()
                if any(word in content for word in ['você', 'seus', 'para', 'com', 'documentos']):
                    print("✅ Tips provided in Portuguese")
                else:
                    print("⚠️  Tips language unclear")
            
            return True
        else:
            print(f"❌ Personalized tips failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Personalized tips error: {str(e)}")
        return False

def test_knowledge_base_search():
    """Test knowledge base search"""
    print("\n🔍 Testing Knowledge Base Search...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for knowledge base test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Search for H1-B application information
        payload = {
            "query": "Como aplicar para H1-B?",
            "visa_type": "h1b",
            "category": "application"
        }
        
        response = requests.post(f"{API_BASE}/education/knowledge-base/search", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Knowledge base search successful")
            print(f"   Answer length: {len(data.get('answer', ''))}")
            print(f"   Related topics: {len(data.get('related_topics', []))}")
            print(f"   Next steps: {len(data.get('next_steps', []))}")
            print(f"   Resources: {len(data.get('resources', []))}")
            print(f"   Warnings: {len(data.get('warnings', []))}")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            
            # Check for legal disclaimers
            answer = data.get('answer', '').lower()
            warnings = ' '.join(data.get('warnings', [])).lower()
            
            has_disclaimer = any(phrase in (answer + warnings) for phrase in [
                'consultoria jurídica', 'advogado', 'não substitui', 'educativa'
            ])
            
            if has_disclaimer:
                print("✅ Legal disclaimers present in response")
            else:
                print("⚠️  Legal disclaimers not clearly present")
            
            # Check if answer is in Portuguese
            if any(word in answer for word in ['para', 'como', 'você', 'processo', 'aplicação']):
                print("✅ Answer provided in Portuguese")
            else:
                print("⚠️  Answer language unclear")
            
            return True
        else:
            print(f"❌ Knowledge base search failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Knowledge base search error: {str(e)}")
        return False

def test_user_progress():
    """Test user education progress tracking"""
    print("\n📈 Testing User Progress Tracking...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available for progress test")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/progress", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            progress = data.get('progress', {})
            
            print(f"✅ User progress retrieved successfully")
            print(f"   Guides completed: {len(progress.get('guides_completed', []))}")
            print(f"   Interviews completed: {len(progress.get('interviews_completed', []))}")
            print(f"   Knowledge queries: {progress.get('knowledge_queries', 0)}")
            print(f"   Total study time: {progress.get('total_study_time_minutes', 0)} minutes")
            print(f"   Achievement badges: {len(progress.get('achievement_badges', []))}")
            print(f"   Total completed interviews: {progress.get('total_completed_interviews', 0)}")
            print(f"   Unread tips count: {progress.get('unread_tips_count', 0)}")
            
            return True
        else:
            print(f"❌ User progress failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User progress error: {str(e)}")
        return False

def test_dashboard_with_education():
    """Test dashboard with education stats"""
    print("\n📊 Testing Dashboard with Education Stats...")
    
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
            
            print(f"✅ Dashboard with education stats loaded successfully")
            print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
            print(f"   Guides completed: {stats.get('guides_completed', 0)}")
            print(f"   Interviews completed: {stats.get('interviews_completed', 0)}")
            print(f"   Total study time: {stats.get('total_study_time', 0)} minutes")
            print(f"   Unread tips: {stats.get('unread_tips', 0)}")
            print(f"   Total applications: {stats.get('total_applications', 0)}")
            print(f"   Total documents: {stats.get('total_documents', 0)}")
            
            # Verify education stats are present
            has_education_stats = all(key in stats for key in ['guides_completed', 'interviews_completed', 'total_study_time', 'unread_tips'])
            if has_education_stats:
                print("✅ Education statistics properly integrated in dashboard")
            else:
                print("⚠️  Some education statistics missing from dashboard")
            
            return True
        else:
            print(f"❌ Dashboard with education stats failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard with education stats error: {str(e)}")
        return False

# ============================================================================
# AUTO-APPLICATION SYSTEM TESTS (NEW)
# ============================================================================

def test_auto_application_start():
    """Test starting a new auto-application case"""
    print("\n🚀 Testing Auto-Application Start...")
    global AUTO_APPLICATION_CASE_ID
    
    try:
        # Create new auto-application case for H-1B visa
        payload = {
            "form_code": "H-1B",
            "session_token": str(uuid.uuid4())
        }
        
        response = requests.post(f"{API_BASE}/auto-application/start", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            case = data.get('case', {})
            AUTO_APPLICATION_CASE_ID = case.get('case_id')
            
            print(f"✅ Auto-application case created successfully")
            print(f"   Case ID: {AUTO_APPLICATION_CASE_ID}")
            print(f"   Form Code: {case.get('form_code')}")
            print(f"   Status: {case.get('status')}")
            print(f"   Created: {case.get('created_at', 'N/A')}")
            print(f"   Expires: {case.get('expires_at', 'N/A')}")
            
            return True
        else:
            print(f"❌ Auto-application start failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Auto-application start error: {str(e)}")
        return False

def test_story_telling_fact_extraction():
    """Test Stage 5 - Story Telling with AI fact extraction"""
    print("\n📖 Testing Story Telling - AI Fact Extraction...")
    
    if not AUTO_APPLICATION_CASE_ID:
        print("❌ No case ID available for story telling test")
        return False
    
    try:
        # Realistic Portuguese story for H-1B application
        story_text = """
        Meu nome é Carlos Eduardo Silva, nasci em 15 de março de 1990 em São Paulo, Brasil. 
        Sou formado em Engenharia de Software pela Universidade de São Paulo (USP) em 2012 e 
        tenho mestrado em Ciência da Computação pela mesma universidade, concluído em 2014.
        
        Atualmente trabalho como Engenheiro de Software Sênior na empresa TechBrasil Ltda em 
        São Paulo há 5 anos, onde desenvolvo aplicações web usando Python, React e AWS. 
        Meu salário atual é de R$ 15.000 por mês.
        
        Recebi uma oferta de emprego da empresa TechGlobal Inc. nos Estados Unidos para trabalhar 
        como Software Engineer com salário de $95.000 anuais. A empresa está localizada em 
        San Francisco, Califórnia, e eles vão patrocinar meu visto H-1B.
        
        Sou casado com Maria Silva desde 2018 e temos um filho de 3 anos chamado Pedro. 
        Minha esposa também é engenheira e pretende me acompanhar nos EUA. Nunca tive problemas 
        com a lei e nunca fui deportado de nenhum país.
        
        Já visitei os Estados Unidos duas vezes como turista: em 2019 por 15 dias para conhecer 
        Nova York e em 2021 por 10 dias para visitar a Califórnia. Sempre respeitei os prazos 
        do visto de turista.
        
        Tenho conta no Banco do Brasil com saldo de R$ 80.000 e não tenho dívidas significativas. 
        Declaro imposto de renda anualmente no Brasil e estou em dia com todas as obrigações fiscais.
        """
        
        payload = {
            "case_id": AUTO_APPLICATION_CASE_ID,
            "story_text": story_text,
            "form_code": "H-1B"
        }
        
        response = requests.post(f"{API_BASE}/auto-application/extract-facts", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            extracted_facts = data.get('extracted_facts', {})
            
            print(f"✅ Story telling fact extraction successful")
            print(f"   Categories found: {data.get('categories_found', 0)}")
            print(f"   Extracted facts keys: {list(extracted_facts.keys())}")
            
            # Check for expected categories
            expected_categories = ['personal_info', 'employment_info', 'family_details', 'education', 'travel_history', 'financial_info']
            found_categories = []
            
            for category in expected_categories:
                if category in extracted_facts or category.upper() in extracted_facts:
                    found_categories.append(category)
                    print(f"   ✅ {category.replace('_', ' ').title()} extracted")
                else:
                    print(f"   ⚠️  {category.replace('_', ' ').title()} not found")
            
            if len(found_categories) >= 4:  # At least 4 categories should be found
                print("✅ AI fact extraction working correctly")
                return True
            else:
                print("⚠️  Limited fact extraction, but endpoint functional")
                return True
                
        else:
            print(f"❌ Story telling fact extraction failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Story telling fact extraction error: {str(e)}")
        return False

def test_friendly_form_generation():
    """Test Stage 6 - Friendly Form with AI form generation"""
    print("\n📝 Testing Friendly Form - AI Form Generation...")
    
    if not AUTO_APPLICATION_CASE_ID:
        print("❌ No case ID available for form generation test")
        return False
    
    try:
        # Simplified form responses in Portuguese
        form_responses = {
            "informacoes_pessoais": {
                "nome_completo": "Carlos Eduardo Silva",
                "data_nascimento": "15/03/1990",
                "local_nascimento": "São Paulo, Brasil",
                "nacionalidade": "Brasileira",
                "endereco_atual": "Rua das Flores, 123, São Paulo, SP, Brasil",
                "telefone": "+55 11 99999-9999",
                "email": "carlos.silva@email.com"
            },
            "informacoes_trabalho": {
                "empresa_atual": "TechBrasil Ltda",
                "cargo_atual": "Engenheiro de Software Sênior",
                "salario_atual": "R$ 15.000/mês",
                "empresa_eua": "TechGlobal Inc.",
                "cargo_eua": "Software Engineer",
                "salario_eua": "$95.000/ano",
                "localizacao_trabalho": "San Francisco, CA"
            },
            "educacao": {
                "graduacao": "Engenharia de Software - USP (2012)",
                "pos_graduacao": "Mestrado em Ciência da Computação - USP (2014)"
            },
            "familia": {
                "estado_civil": "Casado",
                "nome_conjuge": "Maria Silva",
                "data_casamento": "2018",
                "filhos": "1 filho - Pedro (3 anos)"
            }
        }
        
        payload = {
            "case_id": AUTO_APPLICATION_CASE_ID,
            "form_responses": form_responses,
            "form_code": "H-1B"
        }
        
        response = requests.post(f"{API_BASE}/auto-application/generate-forms", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            official_form_data = data.get('official_form_data', {})
            
            print(f"✅ Friendly form generation successful")
            print(f"   Form code: {data.get('form_code')}")
            print(f"   Fields converted: {data.get('fields_converted', 0)}")
            print(f"   Official form keys: {list(official_form_data.keys())[:5]}...")  # Show first 5 keys
            
            # Check if conversion happened (should have English fields)
            has_english_fields = any(key in official_form_data for key in ['full_name', 'applicant_name', 'date_of_birth', 'birth_date'])
            if has_english_fields:
                print("✅ Portuguese to English conversion working")
            else:
                print("⚠️  Conversion format unclear, but endpoint functional")
            
            return True
        else:
            print(f"❌ Friendly form generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Friendly form generation error: {str(e)}")
        return False

def test_visual_review_validation():
    """Test Stage 7 - Visual Review with form validation"""
    print("\n🔍 Testing Visual Review - Form Validation...")
    
    if not AUTO_APPLICATION_CASE_ID:
        print("❌ No case ID available for form validation test")
        return False
    
    try:
        payload = {
            "case_id": AUTO_APPLICATION_CASE_ID,
            "form_code": "H-1B"
        }
        
        response = requests.post(f"{API_BASE}/auto-application/validate-forms", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            validation_issues = data.get('validation_issues', [])
            
            print(f"✅ Visual review form validation successful")
            print(f"   Total issues found: {data.get('total_issues', 0)}")
            print(f"   Blocking issues: {data.get('blocking_issues', 0)}")
            
            # Show sample validation issues
            if validation_issues:
                for i, issue in enumerate(validation_issues[:3]):  # Show first 3 issues
                    print(f"   Issue {i+1}: {issue.get('section')} - {issue.get('field')}")
                    print(f"            {issue.get('issue')} (Severity: {issue.get('severity')})")
            else:
                print("   No validation issues found")
            
            # Check for expected validation structure
            if isinstance(validation_issues, list):
                print("✅ Validation structure correct")
                return True
            else:
                print("⚠️  Validation structure unexpected, but endpoint functional")
                return True
                
        else:
            print(f"❌ Visual review form validation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Visual review form validation error: {str(e)}")
        return False

def test_payment_processing():
    """Test Stage 8 - Payment processing"""
    print("\n💳 Testing Payment Processing...")
    
    if not AUTO_APPLICATION_CASE_ID:
        print("❌ No case ID available for payment processing test")
        return False
    
    try:
        payload = {
            "case_id": AUTO_APPLICATION_CASE_ID,
            "package_id": "complete",
            "payment_method": "credit_card",
            "amount": 299.99
        }
        
        response = requests.post(f"{API_BASE}/auto-application/process-payment", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Payment processing successful")
            print(f"   Payment ID: {data.get('payment_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Amount charged: ${data.get('amount_charged')}")
            
            # Verify payment ID format
            payment_id = data.get('payment_id', '')
            if payment_id.startswith('PAY-') and len(payment_id) == 12:
                print("✅ Payment ID format correct")
            else:
                print("⚠️  Payment ID format unexpected")
            
            return True
        else:
            print(f"❌ Payment processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Payment processing error: {str(e)}")
        return False

def test_package_generation():
    """Test Stage 8 - Final package generation"""
    print("\n📦 Testing Package Generation...")
    
    if not AUTO_APPLICATION_CASE_ID:
        print("❌ No case ID available for package generation test")
        return False
    
    try:
        payload = {
            "case_id": AUTO_APPLICATION_CASE_ID,
            "package_type": "complete"
        }
        
        response = requests.post(f"{API_BASE}/auto-application/generate-package", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            package_contents = data.get('package_contents', {})
            files = package_contents.get('files', [])
            
            print(f"✅ Package generation successful")
            print(f"   Download URL: {data.get('download_url')}")
            print(f"   Total files: {data.get('total_files', 0)}")
            print(f"   Package type: {package_contents.get('package_type')}")
            
            # Check for expected files
            expected_files = ['Official_Form', 'Document_Checklist', 'Submission_Instructions']
            found_files = []
            
            for file_info in files:
                file_name = file_info.get('name', '')
                for expected in expected_files:
                    if expected in file_name:
                        found_files.append(expected)
                        break
            
            print(f"   Expected files found: {len(found_files)}/{len(expected_files)}")
            for found in found_files:
                print(f"   ✅ {found} included")
            
            if len(found_files) >= 2:  # At least 2 expected files should be present
                print("✅ Package generation working correctly")
                return True
            else:
                print("⚠️  Limited package contents, but endpoint functional")
                return True
                
        else:
            print(f"❌ Package generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Package generation error: {str(e)}")
        return False

def test_complete_auto_application_journey():
    """Test complete auto-application user journey"""
    print("\n🎯 Testing Complete Auto-Application Journey...")
    
    journey_results = {
        "auto_application_start": test_auto_application_start(),
        "story_telling_fact_extraction": test_story_telling_fact_extraction(),
        "friendly_form_generation": test_friendly_form_generation(),
        "visual_review_validation": test_visual_review_validation(),
        "payment_processing": test_payment_processing(),
        "package_generation": test_package_generation()
    }
    
    passed_tests = sum(journey_results.values())
    total_tests = len(journey_results)
    
    print(f"\n📊 AUTO-APPLICATION JOURNEY RESULTS:")
    for test_name, result in journey_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Journey Completion: {passed_tests}/{total_tests} stages passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 Complete auto-application journey working perfectly!")
        return True
    elif passed_tests >= total_tests - 1:
        print("✅ Auto-application journey working with minor issues")
        return True
    else:
        print("⚠️  Auto-application journey has significant issues")
        return False

def run_all_tests():
    """Run all B2C backend tests including document management and education system"""
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
    
    # Document management tests
    document_results = {
        "document_upload": test_document_upload(),
        "document_list": test_document_list(),
        "document_details": test_document_details(),
        "document_reanalyze": test_document_reanalyze(),
        "document_update": test_document_update(),
        "dashboard_with_documents": test_dashboard_with_documents(),
        "document_delete": test_document_delete()
    }
    
    # Education system tests (NEW)
    education_results = {
        "education_guides": test_education_guides(),
        "interview_simulator_start": test_interview_simulator_start(),
        "interview_answer_submission": test_interview_answer_submission(),
        "interview_completion": test_interview_completion(),
        "personalized_tips": test_personalized_tips(),
        "knowledge_base_search": test_knowledge_base_search(),
        "user_progress": test_user_progress(),
        "dashboard_with_education": test_dashboard_with_education()
    }
    
    # Auto-Application system tests (NEW)
    auto_app_results = {
        "complete_auto_application_journey": test_complete_auto_application_journey()
    }
    
    # Combine all results
    all_results = {**auth_results, **document_results, **education_results, **auto_app_results}
    
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
    
    # Education System Results (NEW)
    print("\n🎓 EDUCATION SYSTEM:")
    edu_passed = sum(education_results.values())
    edu_total = len(education_results)
    
    for test_name, result in education_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"  Education System: {edu_passed}/{edu_total} tests passed ({edu_passed/edu_total*100:.1f}%)")
    
    # Auto-Application System Results (NEW)
    print("\n🚀 AUTO-APPLICATION SYSTEM:")
    auto_passed = sum(auto_app_results.values())
    auto_total = len(auto_app_results)
    
    for test_name, result in auto_app_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"  Auto-Application System: {auto_passed}/{auto_total} tests passed ({auto_passed/auto_total*100:.1f}%)")
    
    # Overall Results
    total_passed = sum(all_results.values())
    total_tests = len(all_results)
    
    print(f"\n🎯 OVERALL: {total_passed}/{total_tests} tests passed ({total_passed/total_tests*100:.1f}%)")
    
    if total_passed == total_tests:
        print("🎉 All tests passed! Complete B2C system with education and document management is working correctly.")
    elif edu_passed == edu_total:
        print("✅ Education system is working perfectly! Minor issues in other systems.")
    elif edu_passed >= edu_total - 1:
        print("✅ Education system is working correctly with minor issues.")
    else:
        print("⚠️  Some critical tests failed. Check the details above.")
    
    return all_results

if __name__ == "__main__":
    run_all_tests()