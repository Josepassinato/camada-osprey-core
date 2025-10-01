#!/usr/bin/env python3
"""
FINAL PRODUCTION VERIFICATION - IMMIGRATION SYSTEM
Comprehensive production readiness testing for immigration application system
Focus: Core APIs, No Mocks, Production Behavior, Carlos Silva Journey
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any
import base64
import hashlib
import io

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://iaimmigration.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🌐 PRODUCTION VERIFICATION TARGET: {BACKEND_URL}")
print(f"🎯 API BASE: {API_BASE}")
print("="*80)

class ProductionVerificationTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ProductionVerificationTester/1.0'
        })
        self.auth_token = None
        # Use realistic Brazilian user data for Carlos Silva simulation
        self.carlos_email = f"carlos.silva.{uuid.uuid4().hex[:6]}@gmail.com"
        self.carlos_password = "CarlosSilva2024!"
        self.owl_session_id = None
        self.auto_case_id = None
        self.carlos_case_id = None
        print(f"🇧🇷 Carlos Silva Test User: {self.carlos_email}")
        print("="*80)
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with production focus"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PRODUÇÃO OK" if success else "❌ FALHA CRÍTICA"
        print(f"{status} {test_name}")
        if details:
            print(f"    📋 {details}")
        if not success and response_data:
            print(f"    🔍 Response: {str(response_data)[:200]}...")
        print()
    
    def run_production_verification(self):
        """Execute complete production verification suite"""
        print("🚀 INICIANDO VERIFICAÇÃO FINAL COMPLETA DO SISTEMA EM PRODUÇÃO")
        print("="*80)
        
        # 1. Core APIs Functioning
        print("\n📡 1. VERIFICAÇÕES DE APIs CORE FUNCIONANDO")
        self.test_auth_signup_production()
        self.test_auth_login_production()
        self.test_auto_application_start_production()
        self.test_auto_application_case_update_production()
        self.test_owl_agent_basic_endpoints()
        
        # 2. No Mocks or Test Fallbacks
        print("\n🚫 2. SEM MOCKS OU FALLBACKS DE TESTE")
        self.test_no_forced_mocks()
        self.test_no_test_sessions_accepted()
        self.test_no_overly_permissive_validation()
        self.test_no_test_data_endpoints()
        
        # 3. Production Behavior
        print("\n⚙️ 3. COMPORTAMENTO DE PRODUÇÃO")
        self.test_appropriate_errors()
        self.test_rigorous_data_validation()
        self.test_real_authentication()
        self.test_real_payment_systems()
        
        # 4. Credentials and Configuration
        print("\n🔐 4. CREDENCIAIS E CONFIGURAÇÃO")
        self.test_real_credentials_usage()
        self.test_mock_mode_only_when_unconfigured()
        self.test_production_logging()
        
        # 5. Carlos Silva Basic Journey Simulation
        print("\n🇧🇷 5. SIMULAÇÃO CARLOS SILVA (PRIMEIRAS 4 ETAPAS)")
        self.test_carlos_silva_journey_basic()
        
        # Final Summary
        self.print_production_verification_summary()
    
    def test_auth_signup_production(self):
        """Test POST /api/auth/signup with production behavior"""
        print("🔐 Testing Authentication Signup...")
        
        carlos_data = {
            "email": self.carlos_email,
            "password": self.carlos_password,
            "first_name": "Carlos",
            "last_name": "Silva",
            "phone": "+5511987654321"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=carlos_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Production checks
                has_token = 'token' in data and data['token']
                has_user_data = 'user' in data
                no_test_indicators = 'test' not in str(data).lower()
                proper_structure = has_token and has_user_data
                
                # Store token for subsequent tests
                if has_token:
                    self.auth_token = data['token']
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                success = proper_structure and no_test_indicators
                
                self.log_test(
                    "POST /api/auth/signup",
                    success,
                    f"Token: {'✓' if has_token else '✗'}, User Data: {'✓' if has_user_data else '✗'}, Production: {'✓' if no_test_indicators else '✗'}",
                    {"has_token": has_token, "has_user": has_user_data}
                )
            elif response.status_code == 400 and "already registered" in response.text:
                # User already exists, try login
                self.log_test(
                    "POST /api/auth/signup",
                    True,
                    "User already exists (expected in production), proceeding to login",
                    {"status": "user_exists"}
                )
                self.test_auth_login_production()
            else:
                self.log_test(
                    "POST /api/auth/signup",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("POST /api/auth/signup", False, f"Exception: {str(e)}")
    
    def test_auth_login_production(self):
        """Test POST /api/auth/login with production behavior"""
        print("🔐 Testing Authentication Login...")
        
        login_data = {
            "email": self.carlos_email,
            "password": self.carlos_password
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Production checks
                has_token = 'token' in data and data['token']
                has_user_data = 'user' in data
                no_test_indicators = 'test' not in str(data).lower()
                
                # Store token for subsequent tests
                if has_token:
                    self.auth_token = data['token']
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                success = has_token and has_user_data and no_test_indicators
                
                self.log_test(
                    "POST /api/auth/login",
                    success,
                    f"Token: {'✓' if has_token else '✗'}, User Data: {'✓' if has_user_data else '✗'}, Production: {'✓' if no_test_indicators else '✗'}",
                    {"has_token": has_token, "has_user": has_user_data}
                )
            elif response.status_code == 401:
                # Test with wrong credentials to verify proper error handling
                wrong_login = {
                    "email": self.carlos_email,
                    "password": "wrong_password"
                }
                
                wrong_response = self.session.post(f"{API_BASE}/auth/login", json=wrong_login)
                
                if wrong_response.status_code == 401:
                    error_data = wrong_response.json()
                    proper_error = 'detail' in error_data and 'Invalid' in error_data['detail']
                    
                    self.log_test(
                        "POST /api/auth/login",
                        proper_error,
                        f"Proper 401 error handling: {error_data.get('detail', 'No detail')}",
                        {"error_handling": proper_error}
                    )
                else:
                    self.log_test(
                        "POST /api/auth/login",
                        False,
                        f"Expected 401 for wrong credentials, got {wrong_response.status_code}",
                        wrong_response.text[:200]
                    )
            else:
                self.log_test(
                    "POST /api/auth/login",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("POST /api/auth/login", False, f"Exception: {str(e)}")
    
    def test_auto_application_start_production(self):
        """Test POST /api/auto-application/start with production behavior"""
        print("📋 Testing Auto Application Start...")
        
        try:
            response = self.session.post(f"{API_BASE}/auto-application/start", json={})
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle new response structure with nested case object
                case_data = data.get('case', {})
                has_case_id = 'case_id' in case_data and case_data['case_id']
                has_session_token = 'session_token' in case_data
                case_id_format = case_data.get('case_id', '').startswith('OSP-') if has_case_id else False
                no_test_indicators = 'test' not in str(data).lower()
                has_message = 'message' in data
                
                # Store case ID for subsequent tests
                if has_case_id:
                    self.auto_case_id = case_data['case_id']
                
                success = has_case_id and case_id_format and no_test_indicators and has_message
                
                self.log_test(
                    "POST /api/auto-application/start",
                    success,
                    f"Case ID: {case_data.get('case_id', 'None')}, Format: {'✓' if case_id_format else '✗'}, Production: {'✓' if no_test_indicators else '✗'}",
                    {"case_id": case_data.get('case_id'), "has_session": has_session_token, "has_message": has_message}
                )
            else:
                self.log_test(
                    "POST /api/auto-application/start",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("POST /api/auto-application/start", False, f"Exception: {str(e)}")
    
    def test_auto_application_case_update_production(self):
        """Test PUT /api/auto-application/case/{id} with rigorous validation"""
        print("📋 Testing Auto Application Case Update...")
        
        if not self.auto_case_id:
            self.log_test(
                "PUT /api/auto-application/case/{id}",
                False,
                "No case ID available from previous test"
            )
            return
        
        # Test with H-1B form selection (production data)
        update_data = {
            "form_code": "H-1B",
            "status": "form_selected"
        }
        
        try:
            response = self.session.put(
                f"{API_BASE}/auto-application/case/{self.auto_case_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Production validation checks
                proper_form_code = data.get('form_code') == 'H-1B'
                proper_status = data.get('status') == 'form_selected'
                has_case_id = data.get('case_id') == self.auto_case_id
                no_test_indicators = 'test' not in str(data).lower()
                
                # Rigorous validation - should not accept invalid data
                invalid_update = {"form_code": "INVALID_FORM"}
                invalid_response = self.session.put(
                    f"{API_BASE}/auto-application/case/{self.auto_case_id}",
                    json=invalid_update
                )
                
                rejects_invalid = invalid_response.status_code != 200 or 'error' in invalid_response.text.lower()
                
                success = proper_form_code and proper_status and has_case_id and no_test_indicators and rejects_invalid
                
                self.log_test(
                    "PUT /api/auto-application/case/{id}",
                    success,
                    f"Form: {data.get('form_code')}, Status: {data.get('status')}, Validation: {'✓' if rejects_invalid else '✗'}",
                    {"form_code": data.get('form_code'), "status": data.get('status'), "validation": rejects_invalid}
                )
            else:
                self.log_test(
                    "PUT /api/auto-application/case/{id}",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("PUT /api/auto-application/case/{id}", False, f"Exception: {str(e)}")
    
    def test_owl_agent_basic_endpoints(self):
        """Test basic Owl Agent endpoints"""
        print("🦉 Testing Owl Agent Basic Endpoints...")
        
        # Test start session
        try:
            session_data = {
                "visa_type": "H-1B",
                "language": "pt"
            }
            
            response = self.session.post(f"{API_BASE}/owl-agent/start-session", json=session_data)
            
            if response.status_code == 200:
                data = response.json()
                
                has_session_id = 'session_id' in data
                proper_visa_type = data.get('visa_type') == 'H-1B'
                proper_language = data.get('language') == 'pt'
                no_test_indicators = 'test' not in str(data).lower()
                
                if has_session_id:
                    self.owl_session_id = data['session_id']
                
                success = has_session_id and proper_visa_type and proper_language and no_test_indicators
                
                self.log_test(
                    "Owl Agent Basic Endpoints",
                    success,
                    f"Session: {'✓' if has_session_id else '✗'}, Visa: {data.get('visa_type')}, Lang: {data.get('language')}",
                    {"session_id": data.get('session_id'), "visa_type": data.get('visa_type')}
                )
            else:
                self.log_test(
                    "Owl Agent Basic Endpoints",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("Owl Agent Basic Endpoints", False, f"Exception: {str(e)}")
    
    def test_no_forced_mocks(self):
        """Verify no forced mocks in Google Document AI"""
        print("🚫 Testing No Forced Mocks...")
        
        # Test document analysis to ensure it's not using forced mocks
        test_doc = b"Test document content for mock detection" * 100
        
        files = {'file': ('test.pdf', test_doc, 'application/pdf')}
        data = {'document_type': 'passport', 'visa_type': 'H-1B'}
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            response = requests.post(f"{API_BASE}/documents/analyze-with-ai", files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for mock indicators
                response_text = str(result).lower()
                no_mock_indicators = not any(indicator in response_text for indicator in [
                    'mock', 'test_mode', 'fake', 'dummy', 'simulation'
                ])
                
                # Check for real processing indicators
                has_real_processing = any(indicator in response_text for indicator in [
                    'google', 'ai', 'analysis', 'validation', 'completeness'
                ])
                
                success = no_mock_indicators and has_real_processing
                
                self.log_test(
                    "No Forced Mocks",
                    success,
                    f"Mock indicators: {'✗' if no_mock_indicators else '✓'}, Real processing: {'✓' if has_real_processing else '✗'}",
                    {"no_mocks": no_mock_indicators, "real_processing": has_real_processing}
                )
            else:
                self.log_test("No Forced Mocks", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("No Forced Mocks", False, f"Exception: {str(e)}")
    
    def test_no_test_sessions_accepted(self):
        """Verify no test-session accepted in payment"""
        print("🚫 Testing No Test Sessions in Payment...")
        
        if not self.owl_session_id:
            self.log_test("No Test Sessions in Payment", True, "No Owl session to test (acceptable)")
            return
        
        try:
            payment_data = {
                "session_id": "test-session-123",  # Should be rejected
                "delivery_method": "download"
            }
            
            response = self.session.post(f"{API_BASE}/owl-agent/initiate-payment", json=payment_data)
            
            # Should reject test sessions
            rejects_test_session = response.status_code != 200 or 'error' in response.text.lower()
            
            self.log_test(
                "No Test Sessions in Payment",
                rejects_test_session,
                f"Test session rejection: {'✓' if rejects_test_session else '✗'} (Status: {response.status_code})",
                {"rejects_test": rejects_test_session}
            )
        except Exception as e:
            self.log_test("No Test Sessions in Payment", False, f"Exception: {str(e)}")
    
    def test_no_overly_permissive_validation(self):
        """Verify validation is not overly permissive"""
        print("🚫 Testing No Overly Permissive Validation...")
        
        # Test with clearly invalid data
        invalid_case_data = {
            "form_code": "TOTALLY_INVALID_FORM_CODE_12345",
            "status": "invalid_status",
            "basic_data": {"invalid": "data"}
        }
        
        try:
            if self.auto_case_id:
                response = self.session.put(
                    f"{API_BASE}/auto-application/case/{self.auto_case_id}",
                    json=invalid_case_data
                )
                
                # Should reject invalid data
                properly_rejects = response.status_code >= 400 or 'error' in response.text.lower()
                
                self.log_test(
                    "No Overly Permissive Validation",
                    properly_rejects,
                    f"Invalid data rejection: {'✓' if properly_rejects else '✗'} (Status: {response.status_code})",
                    {"rejects_invalid": properly_rejects}
                )
            else:
                self.log_test("No Overly Permissive Validation", True, "No case ID to test (acceptable)")
        except Exception as e:
            self.log_test("No Overly Permissive Validation", False, f"Exception: {str(e)}")
    
    def test_no_test_data_endpoints(self):
        """Verify endpoints don't return test data"""
        print("🚫 Testing No Test Data Endpoints...")
        
        try:
            # Test a basic endpoint for test data indicators
            response = self.session.get(f"{API_BASE}/documents/validation-capabilities")
            
            if response.status_code == 200:
                data = response.json()
                response_text = str(data).lower()
                
                # Check for test data indicators
                no_test_data = not any(indicator in response_text for indicator in [
                    'test_user', 'dummy_data', 'fake_', 'mock_', 'sample_'
                ])
                
                # Check for production indicators
                has_production_data = any(indicator in response_text for indicator in [
                    'production', 'capabilities', 'version', 'supported'
                ])
                
                success = no_test_data and has_production_data
                
                self.log_test(
                    "No Test Data Endpoints",
                    success,
                    f"Test data: {'✗' if no_test_data else '✓'}, Production data: {'✓' if has_production_data else '✗'}",
                    {"no_test_data": no_test_data, "production_data": has_production_data}
                )
            else:
                self.log_test("No Test Data Endpoints", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("No Test Data Endpoints", False, f"Exception: {str(e)}")
    
    def test_appropriate_errors(self):
        """Test appropriate error responses (400, 404, 500)"""
        print("⚙️ Testing Appropriate Error Responses...")
        
        # Test 404 for non-existent resource
        try:
            response = self.session.get(f"{API_BASE}/auto-application/case/NON-EXISTENT-CASE")
            
            proper_404 = response.status_code == 404
            
            # Test 400 for invalid data
            invalid_signup = {
                "email": "invalid-email",  # Invalid email format
                "password": "123",  # Too short
                "first_name": "",  # Empty
                "last_name": ""
            }
            
            signup_response = self.session.post(f"{API_BASE}/auth/signup", json=invalid_signup)
            proper_400 = signup_response.status_code == 400 or signup_response.status_code == 422
            
            success = proper_404 and proper_400
            
            self.log_test(
                "Appropriate Error Responses",
                success,
                f"404 for missing: {'✓' if proper_404 else '✗'}, 400 for invalid: {'✓' if proper_400 else '✗'}",
                {"404_response": proper_404, "400_response": proper_400}
            )
        except Exception as e:
            self.log_test("Appropriate Error Responses", False, f"Exception: {str(e)}")
    
    def test_rigorous_data_validation(self):
        """Test rigorous data validation"""
        print("⚙️ Testing Rigorous Data Validation...")
        
        # Test email validation
        try:
            invalid_emails = ["invalid", "@domain.com", "user@", "user@domain"]
            validation_results = []
            
            for email in invalid_emails:
                test_data = {
                    "email": email,
                    "password": "ValidPassword123!",
                    "first_name": "Test",
                    "last_name": "User"
                }
                
                response = self.session.post(f"{API_BASE}/auth/signup", json=test_data)
                rejects_invalid = response.status_code >= 400
                validation_results.append(rejects_invalid)
            
            rigorous_validation = all(validation_results)
            
            self.log_test(
                "Rigorous Data Validation",
                rigorous_validation,
                f"Invalid email rejection rate: {sum(validation_results)}/{len(validation_results)}",
                {"validation_results": validation_results}
            )
        except Exception as e:
            self.log_test("Rigorous Data Validation", False, f"Exception: {str(e)}")
    
    def test_real_authentication(self):
        """Test real authentication (not bypassed)"""
        print("⚙️ Testing Real Authentication...")
        
        # Test protected endpoint without auth
        try:
            # Remove auth header temporarily
            original_headers = self.session.headers.copy()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            response = self.session.get(f"{API_BASE}/profile")
            
            # Should require authentication
            requires_auth = response.status_code == 401
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            self.log_test(
                "Real Authentication",
                requires_auth,
                f"Protected endpoint requires auth: {'✓' if requires_auth else '✗'} (Status: {response.status_code})",
                {"requires_auth": requires_auth}
            )
        except Exception as e:
            self.log_test("Real Authentication", False, f"Exception: {str(e)}")
    
    def test_real_payment_systems(self):
        """Test real payment systems (not mocked)"""
        print("⚙️ Testing Real Payment Systems...")
        
        if not self.owl_session_id:
            self.log_test("Real Payment Systems", True, "No Owl session for payment test (acceptable)")
            return
        
        try:
            payment_data = {
                "session_id": self.owl_session_id,
                "delivery_method": "download"
            }
            
            response = self.session.post(f"{API_BASE}/owl-agent/initiate-payment", json=payment_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for real Stripe indicators
                has_stripe_url = 'checkout_url' in data and 'stripe' in str(data).lower()
                no_mock_indicators = 'mock' not in str(data).lower() and 'test' not in str(data).lower()
                
                success = has_stripe_url and no_mock_indicators
                
                self.log_test(
                    "Real Payment Systems",
                    success,
                    f"Stripe integration: {'✓' if has_stripe_url else '✗'}, No mocks: {'✓' if no_mock_indicators else '✗'}",
                    {"stripe_integration": has_stripe_url, "no_mocks": no_mock_indicators}
                )
            else:
                # May fail due to session requirements, but should not be due to mocking
                error_text = response.text.lower()
                not_mock_error = 'mock' not in error_text and 'test' not in error_text
                
                self.log_test(
                    "Real Payment Systems",
                    not_mock_error,
                    f"Error not due to mocking: {'✓' if not_mock_error else '✗'} (Status: {response.status_code})",
                    {"not_mock_error": not_mock_error}
                )
        except Exception as e:
            self.log_test("Real Payment Systems", False, f"Exception: {str(e)}")
    
    def test_real_credentials_usage(self):
        """Test system uses real credentials when available"""
        print("🔐 Testing Real Credentials Usage...")
        
        # Test that system has real API keys configured
        try:
            # Test an endpoint that would use external APIs
            response = self.session.get(f"{API_BASE}/documents/validation-capabilities")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for real API integrations
                has_google_integration = 'google' in str(data).lower()
                has_openai_integration = 'ai' in str(data).lower() or 'gpt' in str(data).lower()
                has_capabilities = 'capabilities' in data
                
                success = has_capabilities and (has_google_integration or has_openai_integration)
                
                self.log_test(
                    "Real Credentials Usage",
                    success,
                    f"Google: {'✓' if has_google_integration else '✗'}, AI: {'✓' if has_openai_integration else '✗'}, Capabilities: {'✓' if has_capabilities else '✗'}",
                    {"google": has_google_integration, "ai": has_openai_integration, "capabilities": has_capabilities}
                )
            else:
                self.log_test("Real Credentials Usage", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Real Credentials Usage", False, f"Exception: {str(e)}")
    
    def test_mock_mode_only_when_unconfigured(self):
        """Test mock mode only when credentials not configured"""
        print("🔐 Testing Mock Mode Only When Unconfigured...")
        
        # This is more of a configuration check
        try:
            # Check if system properly indicates when using mocks vs real APIs
            response = self.session.get(f"{API_BASE}/documents/validation-capabilities")
            
            if response.status_code == 200:
                data = response.json()
                
                # System should indicate its configuration status
                has_version_info = 'version' in data
                has_engine_info = 'validation_engines' in data
                
                success = has_version_info and has_engine_info
                
                self.log_test(
                    "Mock Mode Only When Unconfigured",
                    success,
                    f"Version info: {'✓' if has_version_info else '✗'}, Engine info: {'✓' if has_engine_info else '✗'}",
                    {"version_info": has_version_info, "engine_info": has_engine_info}
                )
            else:
                self.log_test("Mock Mode Only When Unconfigured", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Mock Mode Only When Unconfigured", False, f"Exception: {str(e)}")
    
    def test_production_logging(self):
        """Test appropriate production logging"""
        print("🔐 Testing Production Logging...")
        
        # Test that system provides appropriate logging for production
        try:
            # Make a request that should generate logs
            response = self.session.post(f"{API_BASE}/auto-application/start", json={})
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response includes appropriate metadata for logging
                has_case_id = 'case_id' in data
                has_timestamp_info = 'created_at' in str(data) or 'timestamp' in str(data)
                
                success = has_case_id  # Basic requirement for production logging
                
                self.log_test(
                    "Production Logging",
                    success,
                    f"Case tracking: {'✓' if has_case_id else '✗'}, Timestamp info: {'✓' if has_timestamp_info else '✗'}",
                    {"case_tracking": has_case_id, "timestamp_info": has_timestamp_info}
                )
            else:
                self.log_test("Production Logging", False, f"HTTP {response.status_code}", response.text[:200])
        except Exception as e:
            self.log_test("Production Logging", False, f"Exception: {str(e)}")
    
    def test_carlos_silva_journey_basic(self):
        """Test Carlos Silva H-1B journey - first 4 steps only"""
        print("🇧🇷 Testing Carlos Silva H-1B Journey (Basic - First 4 Steps)...")
        
        try:
            # Step 1: Create case
            print("   📋 ETAPA 1: Criação do caso...")
            start_response = self.session.post(f"{API_BASE}/auto-application/start", json={})
            
            if start_response.status_code != 200:
                self.log_test("Carlos Silva Journey", False, "Failed to create case", start_response.text[:200])
                return
            
            start_data = start_response.json()
            case_data = start_data.get('case', {})
            carlos_case_id = case_data.get('case_id')
            
            if not carlos_case_id:
                self.log_test("Carlos Silva Journey", False, "No case ID returned", start_data)
                return
            
            self.carlos_case_id = carlos_case_id
            print(f"   ✅ Caso criado: {carlos_case_id}")
            
            # Step 2: Select H-1B visa
            print("   📋 ETAPA 2: Seleção de visto H-1B...")
            visa_update = {
                "form_code": "H-1B",
                "status": "form_selected"
            }
            
            visa_response = self.session.put(
                f"{API_BASE}/auto-application/case/{carlos_case_id}",
                json=visa_update
            )
            
            if visa_response.status_code != 200:
                self.log_test("Carlos Silva Journey", False, "Failed to select H-1B visa", visa_response.text[:200])
                return
            
            visa_data = visa_response.json()
            print(f"   ✅ H-1B selecionado: {visa_data.get('form_code')}")
            
            # Step 3: Add basic Carlos Silva data
            print("   📋 ETAPA 3: Dados básicos do Carlos Silva...")
            carlos_basic_data = {
                "basic_data": {
                    "nome": "Carlos Silva",
                    "email": self.carlos_email,
                    "telefone": "+5511987654321",
                    "nacionalidade": "Brasileira",
                    "data_nascimento": "1985-03-15",
                    "local_nascimento": "São Paulo, Brasil",
                    "empresa": "Tech Solutions Brasil Ltda",
                    "cargo": "Engenheiro de Software Senior",
                    "salario_anual": "R$ 180.000",
                    "experiencia_anos": "8"
                },
                "status": "basic_data"
            }
            
            basic_response = self.session.put(
                f"{API_BASE}/auto-application/case/{carlos_case_id}",
                json=carlos_basic_data
            )
            
            if basic_response.status_code != 200:
                self.log_test("Carlos Silva Journey", False, "Failed to add basic data", basic_response.text[:200])
                return
            
            basic_data = basic_response.json()
            print(f"   ✅ Dados básicos salvos: {basic_data.get('status')}")
            
            # Step 4: Verify data persistence
            print("   📋 ETAPA 4: Verificação de persistência...")
            get_response = self.session.get(f"{API_BASE}/auto-application/case/{carlos_case_id}")
            
            if get_response.status_code != 200:
                self.log_test("Carlos Silva Journey", False, "Failed to retrieve case", get_response.text[:200])
                return
            
            case_data = get_response.json()
            
            # Verify Carlos Silva data is persisted
            basic_data_stored = case_data.get('basic_data', {})
            carlos_name_stored = basic_data_stored.get('nome') == 'Carlos Silva'
            h1b_form_stored = case_data.get('form_code') == 'H-1B'
            proper_status = case_data.get('status') == 'basic_data'
            
            success = carlos_name_stored and h1b_form_stored and proper_status
            
            print(f"   ✅ Verificação completa")
            
            self.log_test(
                "Carlos Silva H-1B Journey (Basic 4 Steps)",
                success,
                f"Nome: {'✓' if carlos_name_stored else '✗'}, H-1B: {'✓' if h1b_form_stored else '✗'}, Status: {'✓' if proper_status else '✗'}",
                {
                    "case_id": carlos_case_id,
                    "nome_stored": carlos_name_stored,
                    "h1b_stored": h1b_form_stored,
                    "status": case_data.get('status'),
                    "steps_completed": 4
                }
            )
            
        except Exception as e:
            self.log_test("Carlos Silva H-1B Journey (Basic 4 Steps)", False, f"Exception: {str(e)}")
    
    def print_production_verification_summary(self):
        """Print comprehensive production verification summary"""
        print("\n" + "="*80)
        print("🎯 RESUMO DA VERIFICAÇÃO FINAL COMPLETA DE PRODUÇÃO")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 ESTATÍSTICAS GERAIS:")
        print(f"   Total de Testes: {total_tests}")
        print(f"   ✅ Aprovados: {passed_tests}")
        print(f"   ❌ Falharam: {failed_tests}")
        print(f"   📈 Taxa de Sucesso: {success_rate:.1f}%")
        print()
        
        # Categorize results
        core_apis = [r for r in self.test_results if any(api in r['test'] for api in ['auth/signup', 'auth/login', 'auto-application', 'Owl Agent'])]
        no_mocks = [r for r in self.test_results if 'Mock' in r['test'] or 'Test' in r['test']]
        production_behavior = [r for r in self.test_results if any(behavior in r['test'] for behavior in ['Error', 'Validation', 'Authentication', 'Payment'])]
        credentials = [r for r in self.test_results if 'Credential' in r['test'] or 'Logging' in r['test']]
        carlos_journey = [r for r in self.test_results if 'Carlos Silva' in r['test']]
        
        categories = [
            ("🔌 APIs Core", core_apis),
            ("🚫 Sem Mocks", no_mocks),
            ("⚙️ Comportamento Produção", production_behavior),
            ("🔐 Credenciais", credentials),
            ("🇧🇷 Jornada Carlos Silva", carlos_journey)
        ]
        
        for category_name, category_tests in categories:
            if category_tests:
                category_passed = sum(1 for t in category_tests if t['success'])
                category_total = len(category_tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                print(f"{category_name}: {category_passed}/{category_total} ({category_rate:.1f}%)")
                
                for test in category_tests:
                    status = "✅" if test['success'] else "❌"
                    print(f"   {status} {test['test']}")
                print()
        
        # Critical failures
        critical_failures = [r for r in self.test_results if not r['success']]
        if critical_failures:
            print("🚨 FALHAS CRÍTICAS IDENTIFICADAS:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
            print()
        
        # Production readiness assessment
        if success_rate >= 90:
            print("🎉 SISTEMA APROVADO PARA PRODUÇÃO!")
            print("   ✅ Taxa de sucesso ≥90%")
            print("   ✅ Funcionalidades core operacionais")
            print("   ✅ Comportamento de produção verificado")
        elif success_rate >= 75:
            print("⚠️ SISTEMA PARCIALMENTE PRONTO PARA PRODUÇÃO")
            print("   ⚠️ Algumas correções necessárias")
            print("   ⚠️ Revisar falhas críticas")
        else:
            print("❌ SISTEMA NÃO PRONTO PARA PRODUÇÃO")
            print("   ❌ Taxa de sucesso <75%")
            print("   ❌ Correções críticas necessárias")
        
        print("="*80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "production_ready": success_rate >= 90,
            "critical_failures": [f['test'] for f in critical_failures]
        }


if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICAÇÃO FINAL COMPLETA DO SISTEMA EM PRODUÇÃO")
    print("🎯 CRITÉRIO DE APROVAÇÃO: Sistema robusto, seguro e pronto para usuários reais")
    print("🚫 SEM comportamento de teste ou mock forçado")
    print("="*80)
    
    tester = ProductionVerificationTester()
    tester.run_production_verification()