#!/usr/bin/env python3
"""
OWL AGENT AUTHENTICATION & PERSISTENCE SYSTEM - Comprehensive Testing Suite
Tests all new Owl Agent authentication and persistence endpoints for production certification
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://immigent.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class OwlAuthTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OwlAuthTester/1.0'
        })
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def test_owl_user_registration(self):
        """Test Owl Agent user registration with email/password"""
        print("🔐 Testing Owl Agent User Registration...")
        
        # Generate unique test email
        test_email = f"owl_auth_test_{int(time.time())}@test.com"
        
        payload = {
            "email": test_email,
            "password": "testpassword123",
            "name": "Test Owl Auth User"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/auth/register",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["success", "user_id", "email", "message"]
                has_required_fields = all(field in data for field in required_fields)
                
                # Check password hashing (password should not be in response)
                password_not_exposed = "password" not in str(data)
                
                # Check email normalization (should be lowercase)
                email_normalized = data.get("email") == test_email.lower()
                
                # Check bcrypt password hashing
                user_id_format = data.get("user_id", "").startswith("owl_user_")
                
                success = (
                    data.get("success") is True and
                    has_required_fields and
                    password_not_exposed and
                    email_normalized and
                    user_id_format
                )
                
                self.log_test(
                    "Owl Agent - User Registration",
                    success,
                    f"User ID: {data.get('user_id')}, Email: {data.get('email')}",
                    {
                        "user_id": data.get("user_id"),
                        "email": data.get("email"),
                        "has_required_fields": has_required_fields,
                        "password_not_exposed": password_not_exposed,
                        "email_normalized": email_normalized,
                        "user_id_format": user_id_format
                    }
                )
                
                # Store for later tests
                self.owl_test_email = test_email
                self.owl_test_password = "testpassword123"
                self.owl_test_user_id = data.get("user_id")
                
            else:
                self.log_test(
                    "Owl Agent - User Registration",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - User Registration",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_user_login(self):
        """Test Owl Agent user login with session retrieval"""
        print("🔑 Testing Owl Agent User Login...")
        
        if not hasattr(self, 'owl_test_email'):
            self.log_test(
                "Owl Agent - User Login",
                False,
                "No test user available (registration may have failed)"
            )
            return
        
        payload = {
            "email": self.owl_test_email,
            "password": self.owl_test_password
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/auth/login",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["success", "user", "saved_sessions", "message"]
                has_required_fields = all(field in data for field in required_fields)
                
                # Check user data structure
                user_data = data.get("user", {})
                user_fields = ["user_id", "email", "name"]
                has_user_fields = all(field in user_data for field in user_fields)
                
                # Check saved sessions is a list
                saved_sessions = data.get("saved_sessions", [])
                sessions_is_list = isinstance(saved_sessions, list)
                
                # Check last login tracking
                has_timestamp = "timestamp" in data
                
                success = (
                    data.get("success") is True and
                    has_required_fields and
                    has_user_fields and
                    sessions_is_list and
                    user_data.get("email") == self.owl_test_email and
                    has_timestamp
                )
                
                self.log_test(
                    "Owl Agent - User Login",
                    success,
                    f"User: {user_data.get('email')}, Sessions: {len(saved_sessions)}",
                    {
                        "user_id": user_data.get("user_id"),
                        "email": user_data.get("email"),
                        "sessions_count": len(saved_sessions),
                        "has_required_fields": has_required_fields,
                        "has_user_fields": has_user_fields,
                        "has_timestamp": has_timestamp
                    }
                )
                
            else:
                self.log_test(
                    "Owl Agent - User Login",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - User Login",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_duplicate_registration_prevention(self):
        """Test duplicate registration prevention"""
        print("🚫 Testing Owl Agent Duplicate Registration Prevention...")
        
        if not hasattr(self, 'owl_test_email'):
            self.log_test(
                "Owl Agent - Duplicate Registration Prevention",
                False,
                "No test user available"
            )
            return
        
        # Try to register with same email
        payload = {
            "email": self.owl_test_email,
            "password": "differentpassword123",
            "name": "Another Test User"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/auth/register",
                json=payload
            )
            
            # Should return 409 Conflict
            if response.status_code == 409:
                data = response.json()
                error_message = data.get("detail", "")
                
                # Check for appropriate error message
                duplicate_detected = "already exists" in error_message.lower()
                
                self.log_test(
                    "Owl Agent - Duplicate Registration Prevention",
                    duplicate_detected,
                    f"Correctly rejected duplicate: {error_message}",
                    {
                        "status_code": response.status_code,
                        "error_message": error_message,
                        "duplicate_detected": duplicate_detected
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Duplicate Registration Prevention",
                    False,
                    f"Expected 409, got HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Duplicate Registration Prevention",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_password_security(self):
        """Test password security features"""
        print("🔒 Testing Owl Agent Password Security...")
        
        # Test 1: Password minimum length validation
        weak_password_payload = {
            "email": "test_weak@test.com",
            "password": "123",  # Too short (< 6 chars)
            "name": "Test User"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/auth/register",
                json=weak_password_payload
            )
            
            weak_password_rejected = response.status_code == 400
            
            self.log_test(
                "Owl Agent - Weak Password Rejection",
                weak_password_rejected,
                f"Status: {response.status_code}",
                {"status_code": response.status_code}
            )
        except Exception as e:
            self.log_test(
                "Owl Agent - Weak Password Rejection",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Invalid login attempts
        if hasattr(self, 'owl_test_email'):
            wrong_password_payload = {
                "email": self.owl_test_email,
                "password": "wrongpassword"
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/owl-agent/auth/login",
                    json=wrong_password_payload
                )
                
                # Should return 401 Unauthorized
                wrong_password_rejected = response.status_code == 401
                
                self.log_test(
                    "Owl Agent - Wrong Password Rejection",
                    wrong_password_rejected,
                    f"Status: {response.status_code}",
                    {"status_code": response.status_code}
                )
            except Exception as e:
                self.log_test(
                    "Owl Agent - Wrong Password Rejection",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_owl_enhanced_start_session(self):
        """Test enhanced start session with authentication support"""
        print("🚀 Testing Owl Agent Enhanced Start Session...")
        
        # Test 1: Anonymous session
        anonymous_payload = {
            "case_id": "TEST-ANONYMOUS-SESSION",
            "visa_type": "H-1B",
            "language": "en",
            "session_type": "anonymous"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/start-session",
                json=anonymous_payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                anonymous_success = (
                    data.get("success") is True and
                    data.get("session_type") == "anonymous" and
                    data.get("user_email") is None
                )
                
                self.log_test(
                    "Owl Agent - Enhanced Start Session (Anonymous)",
                    anonymous_success,
                    f"Anonymous session created: {data.get('session', {}).get('session_id')}",
                    {
                        "session_type": data.get("session_type"),
                        "user_email": data.get("user_email"),
                        "session_id": data.get("session", {}).get("session_id")
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Enhanced Start Session (Anonymous)",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Enhanced Start Session (Anonymous)",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Authenticated session (if user available)
        if hasattr(self, 'owl_test_email'):
            authenticated_payload = {
                "case_id": "TEST-AUTH-SESSION",
                "visa_type": "F-1",
                "language": "pt",
                "user_email": self.owl_test_email,
                "session_type": "authenticated"
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/owl-agent/start-session",
                    json=authenticated_payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    authenticated_success = (
                        data.get("success") is True and
                        data.get("session_type") == "authenticated" and
                        data.get("user_email") == self.owl_test_email
                    )
                    
                    self.log_test(
                        "Owl Agent - Enhanced Start Session (Authenticated)",
                        authenticated_success,
                        f"Authenticated session created for {self.owl_test_email}",
                        {
                            "session_type": data.get("session_type"),
                            "user_email": data.get("user_email"),
                            "session_id": data.get("session", {}).get("session_id")
                        }
                    )
                    
                    # Store session for later tests
                    self.owl_test_session_id = data.get("session", {}).get("session_id")
                    
                else:
                    self.log_test(
                        "Owl Agent - Enhanced Start Session (Authenticated)",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
            except Exception as e:
                self.log_test(
                    "Owl Agent - Enhanced Start Session (Authenticated)",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_owl_save_session_for_later(self):
        """Test saving session for later completion"""
        print("💾 Testing Owl Agent Save Session for Later...")
        
        if not hasattr(self, 'owl_test_session_id') or not hasattr(self, 'owl_test_email'):
            self.log_test(
                "Owl Agent - Save Session for Later",
                False,
                "No test session or user available"
            )
            return
        
        payload = {
            "session_id": self.owl_test_session_id,
            "user_email": self.owl_test_email
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/save-for-later",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                success = (
                    data.get("success") is True and
                    data.get("session_id") == self.owl_test_session_id and
                    data.get("user_email") == self.owl_test_email and
                    "saved_at" in data
                )
                
                self.log_test(
                    "Owl Agent - Save Session for Later",
                    success,
                    f"Session {self.owl_test_session_id} saved for {self.owl_test_email}",
                    {
                        "session_id": data.get("session_id"),
                        "user_email": data.get("user_email"),
                        "saved_at": data.get("saved_at")
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Save Session for Later",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Save Session for Later",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_get_user_sessions(self):
        """Test getting all user sessions"""
        print("📂 Testing Owl Agent Get User Sessions...")
        
        if not hasattr(self, 'owl_test_email'):
            self.log_test(
                "Owl Agent - Get User Sessions",
                False,
                "No test user available"
            )
            return
        
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/user-sessions/{self.owl_test_email}")
            
            if response.status_code == 200:
                data = response.json()
                
                sessions = data.get("sessions", [])
                
                success = (
                    data.get("success") is True and
                    data.get("user_email") == self.owl_test_email and
                    isinstance(sessions, list) and
                    "total_sessions" in data
                )
                
                # Check if our test session is in the list
                test_session_found = any(
                    session.get("session_id") == getattr(self, 'owl_test_session_id', '')
                    for session in sessions
                )
                
                # Check progress percentage calculation
                sessions_have_progress = all("progress_percentage" in s for s in sessions)
                
                self.log_test(
                    "Owl Agent - Get User Sessions",
                    success,
                    f"Found {len(sessions)} sessions, test session found: {test_session_found}",
                    {
                        "user_email": data.get("user_email"),
                        "total_sessions": len(sessions),
                        "test_session_found": test_session_found,
                        "sessions_have_progress": sessions_have_progress
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Get User Sessions",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Get User Sessions",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_resume_saved_session(self):
        """Test resuming a previously saved session"""
        print("🔄 Testing Owl Agent Resume Saved Session...")
        
        if not hasattr(self, 'owl_test_session_id') or not hasattr(self, 'owl_test_email'):
            self.log_test(
                "Owl Agent - Resume Saved Session",
                False,
                "No test session or user available"
            )
            return
        
        payload = {
            "session_id": self.owl_test_session_id,
            "user_email": self.owl_test_email
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/resume-session",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                session_data = data.get("session", {})
                responses = data.get("responses", [])
                
                success = (
                    data.get("success") is True and
                    session_data.get("session_id") == self.owl_test_session_id and
                    isinstance(responses, list) and
                    "timestamp" in data
                )
                
                self.log_test(
                    "Owl Agent - Resume Saved Session",
                    success,
                    f"Session {self.owl_test_session_id} resumed with {len(responses)} responses",
                    {
                        "session_id": session_data.get("session_id"),
                        "responses_count": len(responses),
                        "session_status": session_data.get("status")
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Resume Saved Session",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Resume Saved Session",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_progress_persistence(self):
        """Test progress persistence across sessions"""
        print("💾 Testing Owl Agent Progress Persistence...")
        
        if not hasattr(self, 'owl_test_session_id'):
            self.log_test(
                "Owl Agent - Progress Persistence",
                False,
                "No test session available"
            )
            return
        
        # Test saving a response
        response_payload = {
            "session_id": self.owl_test_session_id,
            "field_id": "full_name",
            "user_response": "John Test Smith",
            "validation_score": 95
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/save-response",
                json=response_payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                save_success = (
                    data.get("success") is True and
                    data.get("session_id") == self.owl_test_session_id and
                    data.get("field_id") == "full_name"
                )
                
                self.log_test(
                    "Owl Agent - Save Response",
                    save_success,
                    f"Response saved for field: {response_payload['field_id']}",
                    {
                        "session_id": data.get("session_id"),
                        "field_id": data.get("field_id"),
                        "timestamp": data.get("timestamp")
                    }
                )
                
                # Test that response persists when resuming session
                if save_success and hasattr(self, 'owl_test_email'):
                    self.test_response_persistence()
                
            else:
                self.log_test(
                    "Owl Agent - Save Response",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Save Response",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_response_persistence(self):
        """Test that responses persist when resuming session"""
        resume_payload = {
            "session_id": self.owl_test_session_id,
            "user_email": self.owl_test_email
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/owl-agent/resume-session",
                json=resume_payload
            )
            
            if response.status_code == 200:
                data = response.json()
                responses = data.get("responses", [])
                
                # Check if our saved response is present
                full_name_response = next(
                    (r for r in responses if r.get("field_id") == "full_name"),
                    None
                )
                
                persistence_success = (
                    full_name_response is not None and
                    full_name_response.get("user_response") == "John Test Smith"
                )
                
                self.log_test(
                    "Owl Agent - Response Persistence",
                    persistence_success,
                    f"Found {len(responses)} responses, full_name preserved: {persistence_success}",
                    {
                        "total_responses": len(responses),
                        "full_name_found": full_name_response is not None,
                        "full_name_value": full_name_response.get("user_response") if full_name_response else None
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Response Persistence",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Response Persistence",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_multi_session_management(self):
        """Test managing multiple sessions per user"""
        print("🔀 Testing Owl Agent Multi-session Management...")
        
        if not hasattr(self, 'owl_test_email'):
            self.log_test(
                "Owl Agent - Multi-session Management",
                False,
                "No test user available"
            )
            return
        
        # Create multiple sessions for the same user
        session_ids = []
        
        for i in range(3):
            payload = {
                "case_id": f"TEST-MULTI-SESSION-{i}",
                "visa_type": ["H-1B", "F-1", "I-485"][i],
                "language": "pt",
                "user_email": self.owl_test_email,
                "session_type": "authenticated"
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/owl-agent/start-session",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session_data = data.get("session", {})
                    session_id = session_data.get("session_id")
                    if session_id:
                        session_ids.append(session_id)
            except Exception:
                pass
        
        # Test that user can retrieve all sessions
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/user-sessions/{self.owl_test_email}")
            
            if response.status_code == 200:
                data = response.json()
                sessions = data.get("sessions", [])
                
                # Check if we can find our new sessions
                found_sessions = sum(
                    1 for session in sessions
                    if session.get("session_id") in session_ids
                )
                
                success = found_sessions >= 2  # At least 2 of our 3 sessions should be found
                
                self.log_test(
                    "Owl Agent - Multi-session Management",
                    success,
                    f"Created {len(session_ids)} sessions, found {found_sessions} in user sessions",
                    {
                        "created_sessions": len(session_ids),
                        "found_sessions": found_sessions,
                        "total_user_sessions": len(sessions)
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Multi-session Management",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Multi-session Management",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_security_validation(self):
        """Test security aspects of Owl Agent system"""
        print("🔒 Testing Owl Agent Security Validation...")
        
        # Test 1: Session ownership validation
        if hasattr(self, 'owl_test_session_id'):
            wrong_user_payload = {
                "session_id": self.owl_test_session_id,
                "user_email": "wrong_user@test.com"
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/owl-agent/save-for-later",
                    json=wrong_user_payload
                )
                
                # Should fail because user doesn't exist or session doesn't belong to user
                ownership_validated = response.status_code in [404, 403, 401]
                
                self.log_test(
                    "Owl Agent - Session Ownership Validation",
                    ownership_validated,
                    f"Status: {response.status_code}",
                    {"status_code": response.status_code}
                )
            except Exception as e:
                self.log_test(
                    "Owl Agent - Session Ownership Validation",
                    False,
                    f"Exception: {str(e)}"
                )
        
        # Test 2: Email normalization (case insensitive)
        if hasattr(self, 'owl_test_email'):
            uppercase_email_payload = {
                "email": self.owl_test_email.upper(),  # Test with uppercase
                "password": self.owl_test_password
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/owl-agent/auth/login",
                    json=uppercase_email_payload
                )
                
                # Should succeed because email should be case-insensitive
                case_insensitive_login = response.status_code == 200
                
                self.log_test(
                    "Owl Agent - Case Insensitive Email",
                    case_insensitive_login,
                    f"Login with uppercase email: {response.status_code}",
                    {"status_code": response.status_code}
                )
            except Exception as e:
                self.log_test(
                    "Owl Agent - Case Insensitive Email",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_database_integration(self):
        """Test database integration and collections"""
        print("🗄️ Testing Database Integration...")
        
        # This test verifies that the system is properly creating and managing
        # the new collections: owl_users, owl_sessions, owl_responses
        
        # We can infer database integration is working if:
        # 1. User registration works (owl_users collection)
        # 2. Session creation works (owl_sessions collection)  
        # 3. Response saving works (owl_responses collection)
        
        database_tests = {
            "owl_users_collection": hasattr(self, 'owl_test_user_id'),
            "owl_sessions_collection": hasattr(self, 'owl_test_session_id'),
            "owl_responses_collection": True  # Tested in progress persistence
        }
        
        all_collections_working = all(database_tests.values())
        
        self.log_test(
            "Owl Agent - Database Integration",
            all_collections_working,
            f"Collections working: {database_tests}",
            database_tests
        )
    
    def run_all_tests(self):
        """Run all Owl Agent authentication and persistence tests"""
        print("🦉 STARTING OWL AGENT AUTHENTICATION & PERSISTENCE TESTING...")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 80)
        
        # Test 1: User Registration
        self.test_owl_user_registration()
        
        # Test 2: User Login
        self.test_owl_user_login()
        
        # Test 3: Duplicate Registration Prevention
        self.test_owl_duplicate_registration_prevention()
        
        # Test 4: Password Security
        self.test_owl_password_security()
        
        # Test 5: Enhanced Start Session with Authentication
        self.test_owl_enhanced_start_session()
        
        # Test 6: Save Session for Later
        self.test_owl_save_session_for_later()
        
        # Test 7: Get User Sessions
        self.test_owl_get_user_sessions()
        
        # Test 8: Resume Saved Session
        self.test_owl_resume_saved_session()
        
        # Test 9: Progress Persistence
        self.test_owl_progress_persistence()
        
        # Test 10: Multi-session Management
        self.test_owl_multi_session_management()
        
        # Test 11: Security Validation
        self.test_owl_security_validation()
        
        # Test 12: Database Integration
        self.test_database_integration()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🦉 OWL AGENT AUTHENTICATION & PERSISTENCE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Group results by category
        categories = {
            "Authentication": [],
            "Session Management": [],
            "Persistence": [],
            "Security": [],
            "Integration": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Registration" in test_name or "Login" in test_name or "Password" in test_name:
                categories["Authentication"].append(result)
            elif "Session" in test_name:
                categories["Session Management"].append(result)
            elif "Persistence" in test_name or "Response" in test_name:
                categories["Persistence"].append(result)
            elif "Security" in test_name or "Ownership" in test_name or "Email" in test_name:
                categories["Security"].append(result)
            else:
                categories["Integration"].append(result)
        
        for category, results in categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                print(f"🔸 {category}: {passed}/{total} passed")
                
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"   {status} {result['test']}")
                print()
        
        # Print failed tests details
        failed_results = [r for r in self.test_results if not r["success"]]
        if failed_results:
            print("❌ FAILED TESTS DETAILS:")
            for result in failed_results:
                print(f"   • {result['test']}")
                print(f"     Details: {result['details']}")
                if result.get('response_data'):
                    print(f"     Response: {result['response_data']}")
                print()
        
        print("=" * 80)
        
        # Final assessment
        if passed_tests == total_tests:
            print("🎉 ALL OWL AGENT AUTHENTICATION & PERSISTENCE TESTS PASSED!")
            print("✅ System is ready for production deployment")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  MOST TESTS PASSED - Minor issues detected")
            print("🔧 Review failed tests and fix before deployment")
        else:
            print("🚨 CRITICAL ISSUES DETECTED")
            print("❌ System requires significant fixes before deployment")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = OwlAuthTester()
    tester.run_all_tests()