#!/usr/bin/env python3
"""
CORRECTED COMPREHENSIVE IMMIGRATION API TESTING SUITE
Tests ALL immigration application APIs with correct endpoint paths
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any
import base64

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CorrectedImmigrationAPITester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ImmigrationAPITester/1.0'
        })
        self.auth_token = None
        self.test_user_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
        self.test_user_password = "TestPassword123!"
        self.owl_session_id = None
        self.auto_case_id = None
        self.setup_test_authentication()
        
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
        print()
    
    def setup_test_authentication(self):
        """Setup authentication for endpoints that require it"""
        try:
            # Try to create a test user
            test_user_data = {
                "email": self.test_user_email,
                "password": self.test_user_password,
                "first_name": "Test",
                "last_name": "User"
            }
            
            # Try to signup
            signup_response = self.session.post(
                f"{API_BASE}/auth/signup",
                json=test_user_data
            )
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                self.auth_token = signup_data.get('token')
            else:
                # Try to login if user already exists
                login_data = {
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
                
                login_response = self.session.post(
                    f"{API_BASE}/auth/login",
                    json=login_data
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    self.auth_token = login_result.get('token')
            
            # Set authorization header if we have a token
            if self.auth_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                print(f"✅ Authentication setup successful")
            else:
                print(f"⚠️ Authentication setup failed - some tests may fail")
                
        except Exception as e:
            print(f"⚠️ Authentication setup error: {e}")
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints"""
        print("🔐 TESTING AUTHENTICATION ENDPOINTS...")
        
        # Test signup
        unique_email = f"signup_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=payload)
            success = response.status_code == 200 and 'token' in response.json()
            self.log_test("POST /api/auth/signup", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/auth/signup", False, f"Exception: {str(e)}")
        
        # Test login
        payload = {"email": self.test_user_email, "password": self.test_user_password}
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=payload)
            success = response.status_code == 200 and 'token' in response.json()
            self.log_test("POST /api/auth/login", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/auth/login", False, f"Exception: {str(e)}")
    
    def test_owl_agent_endpoints(self):
        """Test Owl Agent endpoints with correct paths"""
        print("🦉 TESTING OWL AGENT ENDPOINTS...")
        
        # Test start session - CORRECT PATH: /owl-agent/start-session
        payload = {"visa_type": "H-1B", "language": "pt"}
        try:
            response = self.session.post(f"{API_BASE}/owl-agent/start-session", json=payload)
            success = response.status_code == 200
            if success and 'session_id' in response.json():
                self.owl_session_id = response.json()['session_id']
            self.log_test("POST /api/owl-agent/start-session", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/owl-agent/start-session", False, f"Exception: {str(e)}")
        
        # Test get session
        if self.owl_session_id:
            try:
                response = self.session.get(f"{API_BASE}/owl-agent/session/{self.owl_session_id}")
                success = response.status_code == 200
                self.log_test("GET /api/owl-agent/session/{session_id}", success, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test("GET /api/owl-agent/session/{session_id}", False, f"Exception: {str(e)}")
        
        # Test save response
        payload = {
            "session_id": self.owl_session_id or "test-session-id",
            "field_id": "full_name",
            "response": "João Silva",
            "validation_score": 95
        }
        try:
            response = self.session.post(f"{API_BASE}/owl-agent/save-response", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/owl-agent/save-response", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/owl-agent/save-response", False, f"Exception: {str(e)}")
        
        # Test register
        unique_email = f"owl_{uuid.uuid4().hex[:8]}@test.com"
        payload = {
            "email": unique_email,
            "password": "OwlPassword123!",
            "first_name": "Owl",
            "last_name": "User"
        }
        try:
            response = self.session.post(f"{API_BASE}/owl-agent/auth/register", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/owl-agent/auth/register", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/owl-agent/auth/register", False, f"Exception: {str(e)}")
        
        # Test login
        payload = {"email": self.test_user_email, "password": self.test_user_password}
        try:
            response = self.session.post(f"{API_BASE}/owl-agent/auth/login", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/owl-agent/auth/login", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/owl-agent/auth/login", False, f"Exception: {str(e)}")
        
        # Test my sessions (user sessions)
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/user-sessions/{self.test_user_email}")
            success = response.status_code == 200
            self.log_test("GET /api/owl-agent/user-sessions/{email}", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/owl-agent/user-sessions/{email}", False, f"Exception: {str(e)}")
    
    def test_auto_application_endpoints(self):
        """Test auto-application endpoints"""
        print("🤖 TESTING AUTO-APPLICATION ENDPOINTS...")
        
        # Test start
        payload = {"visa_type": "H-1B"}
        try:
            response = self.session.post(f"{API_BASE}/auto-application/start", json=payload)
            success = response.status_code == 200
            if success and 'case' in response.json():
                case_data = response.json()['case']
                if 'case_id' in case_data:
                    self.auto_case_id = case_data['case_id']
            self.log_test("POST /api/auto-application/start", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/auto-application/start", False, f"Exception: {str(e)}")
        
        # Test get case
        if self.auto_case_id:
            try:
                response = self.session.get(f"{API_BASE}/auto-application/case/{self.auto_case_id}")
                success = response.status_code == 200
                self.log_test("GET /api/auto-application/case/{case_id}", success, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test("GET /api/auto-application/case/{case_id}", False, f"Exception: {str(e)}")
        
        # Test update case
        if self.auto_case_id:
            payload = {
                "status": "in_progress",
                "basic_data": {"full_name": "João Silva", "email": "joao@test.com"}
            }
            try:
                response = self.session.put(f"{API_BASE}/auto-application/case/{self.auto_case_id}", json=payload)
                success = response.status_code == 200
                self.log_test("PUT /api/auto-application/case/{case_id}", success, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test("PUT /api/auto-application/case/{case_id}", False, f"Exception: {str(e)}")
    
    def test_document_endpoints(self):
        """Test document endpoints"""
        print("📄 TESTING DOCUMENT ENDPOINTS...")
        
        # Test analyze with AI
        sample_document = b"""
        PASSPORT
        REPUBLIC OF BRAZIL
        
        Type: P
        Country Code: BRA
        Passport No: BR123456789
        
        Surname: SILVA
        Given Names: JOAO CARLOS
        Nationality: BRAZILIAN
        Date of Birth: 15 JAN 1990
        Sex: M
        Place of Birth: SAO PAULO, BRAZIL
        Date of Issue: 10 MAR 2020
        Date of Expiry: 09 MAR 2030
        Authority: DPF
        """ * 20
        
        files = {'file': ('passport.pdf', sample_document, 'application/pdf')}
        data = {'document_type': 'passport', 'visa_type': 'H-1B', 'case_id': 'TEST-DOC-ANALYSIS'}
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            response = requests.post(f"{API_BASE}/documents/analyze-with-ai", files=files, data=data, headers=headers)
            success = response.status_code == 200
            self.log_test("POST /api/documents/analyze-with-ai", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/documents/analyze-with-ai", False, f"Exception: {str(e)}")
        
        # Test analysis KPIs
        try:
            response = self.session.get(f"{API_BASE}/documents/analysis/kpis")
            success = response.status_code == 200
            self.log_test("GET /api/documents/analysis/kpis", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/documents/analysis/kpis", False, f"Exception: {str(e)}")
        
        # Test analysis performance
        try:
            response = self.session.get(f"{API_BASE}/documents/analysis/performance")
            success = response.status_code == 200
            self.log_test("GET /api/documents/analysis/performance", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/documents/analysis/performance", False, f"Exception: {str(e)}")
    
    def test_dr_paula_llm_endpoints(self):
        """Test Dr. Paula LLM endpoints"""
        print("👩‍⚕️ TESTING DR. PAULA LLM ENDPOINTS...")
        
        # Test generate directives
        payload = {"visa_type": "H1B", "language": "pt"}
        try:
            response = self.session.post(f"{API_BASE}/llm/dr-paula/generate-directives", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/llm/dr-paula/generate-directives", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/llm/dr-paula/generate-directives", False, f"Exception: {str(e)}")
        
        # Test review letter
        payload = {
            "visa_type": "H1B",
            "applicant_letter": "Eu sou um engenheiro de software com 5 anos de experiência. Tenho mestrado em Ciência da Computação e quero trabalhar nos Estados Unidos para uma empresa de tecnologia."
        }
        try:
            response = self.session.post(f"{API_BASE}/llm/dr-paula/review-letter", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/llm/dr-paula/review-letter", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/llm/dr-paula/review-letter", False, f"Exception: {str(e)}")
        
        # Test request complement
        payload = {
            "visa_type": "H1B",
            "current_letter": "Eu quero trabalhar nos EUA.",
            "missing_areas": ["education", "experience", "job_offer"]
        }
        try:
            response = self.session.post(f"{API_BASE}/llm/dr-paula/request-complement", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/llm/dr-paula/request-complement", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/llm/dr-paula/request-complement", False, f"Exception: {str(e)}")
    
    def test_stripe_payment_endpoints(self):
        """Test Stripe payment endpoints with correct paths"""
        print("💳 TESTING STRIPE PAYMENT ENDPOINTS...")
        
        # Test create checkout session (Owl Agent payment)
        payload = {
            "case_id": self.auto_case_id or "TEST-CASE-PAYMENT",
            "delivery_method": "download",
            "amount": 2999
        }
        try:
            response = self.session.post(f"{API_BASE}/owl-agent/initiate-payment", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/owl-agent/initiate-payment", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/owl-agent/initiate-payment", False, f"Exception: {str(e)}")
        
        # Test webhook
        payload = {
            "id": "evt_test_webhook",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session",
                    "payment_status": "paid",
                    "metadata": {"case_id": self.auto_case_id or "TEST-CASE-PAYMENT"}
                }
            }
        }
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'authorization'}
            response = requests.post(f"{API_BASE}/webhook/stripe", json=payload, headers=headers)
            success = response.status_code == 200
            self.log_test("POST /api/webhook/stripe", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/webhook/stripe", False, f"Exception: {str(e)}")
        
        # Test download
        download_id = "test-download-id-123"
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/download/{download_id}")
            success = response.status_code == 200 or response.status_code == 404  # 404 is expected for test ID
            self.log_test("GET /api/owl-agent/download/{download_id}", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("GET /api/owl-agent/download/{download_id}", False, f"Exception: {str(e)}")
    
    def test_other_critical_endpoints(self):
        """Test other critical endpoints"""
        print("🔧 TESTING OTHER CRITICAL ENDPOINTS...")
        
        # Test chat - CORRECT PATH: /chat (POST)
        payload = {"message": "Hello, I need help with my H-1B application", "session_id": "test-session"}
        try:
            response = self.session.post(f"{API_BASE}/chat", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/chat", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/chat", False, f"Exception: {str(e)}")
        
        # Test AI processing step
        payload = {
            "case_id": self.auto_case_id or "TEST-CASE-AI",
            "step_id": "document_analysis",
            "data": {"document_type": "passport"}
        }
        try:
            response = self.session.post(f"{API_BASE}/ai-processing/step", json=payload)
            success = response.status_code == 200
            self.log_test("POST /api/ai-processing/step", success, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("POST /api/ai-processing/step", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all comprehensive immigration API tests"""
        print("🚀 STARTING CORRECTED COMPREHENSIVE IMMIGRATION API TESTING...")
        print(f"🌐 Testing API Base: {API_BASE}")
        print("=" * 80)
        
        # Authentication Tests
        print("\n🔐 AUTHENTICATION ENDPOINTS")
        print("-" * 40)
        self.test_authentication_endpoints()
        
        # Owl Agent Tests
        print("\n🦉 OWL AGENT ENDPOINTS")
        print("-" * 40)
        self.test_owl_agent_endpoints()
        
        # Auto-Application Tests
        print("\n🤖 AUTO-APPLICATION ENDPOINTS")
        print("-" * 40)
        self.test_auto_application_endpoints()
        
        # Document Tests
        print("\n📄 DOCUMENT ENDPOINTS")
        print("-" * 40)
        self.test_document_endpoints()
        
        # Dr. Paula LLM Tests
        print("\n👩‍⚕️ DR. PAULA LLM ENDPOINTS")
        print("-" * 40)
        self.test_dr_paula_llm_endpoints()
        
        # Stripe Payment Tests
        print("\n💳 STRIPE PAYMENT ENDPOINTS")
        print("-" * 40)
        self.test_stripe_payment_endpoints()
        
        # Other Critical Endpoints
        print("\n🔧 OTHER CRITICAL ENDPOINTS")
        print("-" * 40)
        self.test_other_critical_endpoints()
        
        # Generate Final Report
        print("\n" + "=" * 80)
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("📊 FINAL COMPREHENSIVE IMMIGRATION API TEST REPORT")
        print("=" * 80)
        print(f"🎯 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print()
        
        # Group results by category
        categories = {}
        for test in self.test_results:
            endpoint = test['test']
            if '/auth/' in endpoint:
                category = 'Authentication'
            elif '/owl-agent/' in endpoint:
                category = 'Owl Agent'
            elif '/auto-application/' in endpoint:
                category = 'Auto Application'
            elif '/documents/' in endpoint:
                category = 'Documents'
            elif '/llm/dr-paula/' in endpoint:
                category = 'Dr. Paula LLM'
            elif '/webhook/stripe' in endpoint or '/owl-agent/initiate-payment' in endpoint or '/owl-agent/download/' in endpoint:
                category = 'Stripe Payments'
            elif '/chat' in endpoint or '/ai-processing/' in endpoint:
                category = 'Other Critical'
            else:
                category = 'Other'
            
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'tests': []}
            
            if test['success']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
            categories[category]['tests'].append(test)
        
        print("📋 RESULTS BY CATEGORY:")
        print("-" * 40)
        for category, stats in categories.items():
            total_cat = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total_cat * 100) if total_cat > 0 else 0
            status = "✅" if rate >= 80 else "⚠️" if rate >= 60 else "❌"
            print(f"{status} {category}: {stats['passed']}/{total_cat} ({rate:.1f}%)")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            print("-" * 40)
            for test in self.test_results:
                if not test['success']:
                    print(f"• {test['test']}: {test['details']}")
            print()
        
        # Determine overall system status
        if success_rate >= 95:
            status = "🟢 PRODUCTION READY"
        elif success_rate >= 85:
            status = "🟡 NEEDS MINOR FIXES"
        elif success_rate >= 70:
            status = "🟠 NEEDS MAJOR FIXES"
        else:
            status = "🔴 NOT PRODUCTION READY"
        
        print(f"🏆 OVERALL SYSTEM STATUS: {status}")
        print("=" * 80)
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "api_base": API_BASE,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "status": status,
            "categories": categories,
            "detailed_results": self.test_results
        }
        
        with open('/app/corrected_immigration_api_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: /app/corrected_immigration_api_test_report.json")


if __name__ == "__main__":
    tester = CorrectedImmigrationAPITester()
    tester.run_all_tests()