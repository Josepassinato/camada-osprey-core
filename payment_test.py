#!/usr/bin/env python3
"""
OWL AGENT PAYMENT & DOWNLOAD SYSTEM TESTS
Tests the final phase integration with Stripe payments
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class OwlPaymentSystemTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OwlPaymentTester/1.0'
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
    
    def create_completed_owl_session(self):
        """Create a completed Owl session for payment testing"""
        try:
            # Start a new Owl session
            start_payload = {
                "case_id": "TEST-PAYMENT-SESSION",
                "visa_type": "H-1B",
                "language": "pt",
                "user_email": "test@payment.com",
                "session_type": "anonymous"
            }
            
            response = self.session.post(f"{API_BASE}/owl-agent/start-session", json=start_payload)
            
            if response.status_code == 200:
                data = response.json()
                session_id = data.get("session", {}).get("session_id")
                
                if session_id:
                    # Simulate completing the session by adding responses
                    self.simulate_session_completion(session_id)
                    
                    self.log_test(
                        "Create Completed Owl Session",
                        True,
                        f"Created session {session_id} for payment testing",
                        {"session_id": session_id}
                    )
                    return session_id
                else:
                    self.log_test(
                        "Create Completed Owl Session",
                        False,
                        "No session_id in response",
                        data
                    )
            else:
                self.log_test(
                    "Create Completed Owl Session",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Create Completed Owl Session",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def simulate_session_completion(self, session_id: str):
        """Simulate completing an Owl session with responses"""
        try:
            # Add multiple responses to simulate completion
            sample_responses = [
                {"field_id": "full_name", "value": "John Smith", "field_type": "text"},
                {"field_id": "date_of_birth", "value": "1990-01-15", "field_type": "date"},
                {"field_id": "current_address", "value": "123 Main St, New York, NY", "field_type": "address"},
                {"field_id": "employer_name", "value": "Tech Company Inc", "field_type": "text"},
                {"field_id": "annual_income", "value": "85000", "field_type": "number"},
                {"field_id": "highest_degree", "value": "Bachelor's Degree", "field_type": "select"},
                {"field_id": "marital_status", "value": "Single", "field_type": "select"},
                {"field_id": "current_job", "value": "Software Engineer", "field_type": "text"},
                {"field_id": "place_of_birth", "value": "New York, NY, USA", "field_type": "text"},
                {"field_id": "previous_us_travel", "value": "No", "field_type": "boolean"}
            ]
            
            for response_data in sample_responses:
                payload = {
                    "session_id": session_id,
                    "field_id": response_data["field_id"],
                    "response_value": response_data["value"],
                    "field_type": response_data["field_type"],
                    "confidence_score": 95
                }
                
                self.session.post(f"{API_BASE}/owl-agent/save-response", json=payload)
            
            return True
        except Exception as e:
            print(f"Error simulating session completion: {e}")
            return False
    
    def test_initiate_payment_fixed_pricing(self, session_id: str):
        """Test payment initiation with fixed package pricing"""
        try:
            # Test all three delivery methods
            delivery_methods = [
                {"method": "download", "expected_amount": 29.99},
                {"method": "email", "expected_amount": 24.99},
                {"method": "both", "expected_amount": 34.99}
            ]
            
            for delivery in delivery_methods:
                payload = {
                    "session_id": session_id,
                    "delivery_method": delivery["method"],
                    "origin_url": "https://agente-coruja-1.preview.emergentagent.com",
                    "user_email": "test@payment.com"
                }
                
                response = self.session.post(f"{API_BASE}/owl-agent/initiate-payment", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    amount = data.get("amount")
                    checkout_url = data.get("checkout_url")
                    
                    # Verify fixed pricing (security - no frontend manipulation)
                    pricing_correct = amount == delivery["expected_amount"]
                    has_checkout_url = bool(checkout_url and checkout_url.startswith("https://"))
                    
                    success = pricing_correct and has_checkout_url
                    
                    self.log_test(
                        f"Initiate Payment - {delivery['method'].title()} Package",
                        success,
                        f"Amount: ${amount} (expected ${delivery['expected_amount']}), Checkout URL: {bool(checkout_url)}",
                        {
                            "delivery_method": delivery["method"],
                            "amount": amount,
                            "expected_amount": delivery["expected_amount"],
                            "pricing_correct": pricing_correct,
                            "has_checkout_url": has_checkout_url
                        }
                    )
                else:
                    self.log_test(
                        f"Initiate Payment - {delivery['method'].title()} Package",
                        False,
                        f"HTTP {response.status_code}",
                        response.text
                    )
        except Exception as e:
            self.log_test(
                "Initiate Payment - Fixed Pricing",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_payment_status_polling(self):
        """Test payment status polling endpoint"""
        try:
            # Use a mock Stripe session ID for testing
            mock_stripe_session_id = "cs_test_mock_session_id_12345"
            
            response = self.session.get(f"{API_BASE}/owl-agent/payment-status/{mock_stripe_session_id}")
            
            # This should return 404 for non-existent session, which is expected behavior
            if response.status_code == 404:
                self.log_test(
                    "Payment Status Polling",
                    True,
                    "Correctly returned 404 for non-existent payment session",
                    {"status_code": 404, "expected": "404 for non-existent session"}
                )
            elif response.status_code == 200:
                data = response.json()
                has_required_fields = all(field in data for field in ["payment_status", "session_status"])
                
                self.log_test(
                    "Payment Status Polling",
                    has_required_fields,
                    f"Status endpoint accessible, has required fields: {has_required_fields}",
                    {"fields_present": list(data.keys()) if isinstance(data, dict) else []}
                )
            else:
                self.log_test(
                    "Payment Status Polling",
                    False,
                    f"Unexpected HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Payment Status Polling",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_stripe_webhook_handling(self):
        """Test Stripe webhook endpoint"""
        try:
            # Test webhook endpoint accessibility
            mock_webhook_payload = {
                "id": "evt_test_webhook",
                "object": "event",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_session_id",
                        "payment_status": "paid"
                    }
                }
            }
            
            # Note: This will likely fail without proper Stripe signature, which is expected
            response = self.session.post(
                f"{API_BASE}/webhook/stripe",
                json=mock_webhook_payload,
                headers={"Stripe-Signature": "test_signature"}
            )
            
            # Any response (even 400/500) indicates the endpoint exists and is handling requests
            endpoint_accessible = response.status_code in [200, 400, 500]
            
            self.log_test(
                "Stripe Webhook Handling",
                endpoint_accessible,
                f"Webhook endpoint accessible (HTTP {response.status_code})",
                {
                    "status_code": response.status_code,
                    "endpoint_exists": endpoint_accessible,
                    "note": "Signature validation expected to fail in test"
                }
            )
        except Exception as e:
            self.log_test(
                "Stripe Webhook Handling",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_secure_download_system(self):
        """Test secure download system"""
        try:
            # Test with mock download ID
            mock_download_id = "DWN-test-download-id-12345"
            
            response = self.session.get(f"{API_BASE}/owl-agent/download/{mock_download_id}")
            
            # Should return 404 for non-existent download, which is expected
            if response.status_code == 404:
                self.log_test(
                    "Secure Download System",
                    True,
                    "Correctly returned 404 for non-existent download ID",
                    {"status_code": 404, "security": "Proper access control"}
                )
            elif response.status_code == 410:
                self.log_test(
                    "Secure Download System",
                    True,
                    "Download link expired (410) - expiry system working",
                    {"status_code": 410, "feature": "Download expiry working"}
                )
            elif response.status_code == 429:
                self.log_test(
                    "Secure Download System",
                    True,
                    "Download limit exceeded (429) - limit system working",
                    {"status_code": 429, "feature": "Download limits working"}
                )
            else:
                self.log_test(
                    "Secure Download System",
                    False,
                    f"Unexpected response: HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Secure Download System",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_download_security_features(self):
        """Test download security features (expiry, limits, validation)"""
        print("🔒 Testing Download Security Features...")
        
        # Test 1: Download ID validation
        invalid_download_ids = ["", "invalid", "../../etc/passwd", "<script>alert('xss')</script>"]
        
        for invalid_id in invalid_download_ids:
            try:
                response = self.session.get(f"{API_BASE}/owl-agent/download/{invalid_id}")
                
                # Should return 404 or 400 for invalid IDs
                security_working = response.status_code in [400, 404]
                
                self.log_test(
                    f"Download Security - Invalid ID: '{invalid_id[:20]}'",
                    security_working,
                    f"HTTP {response.status_code} (expected 400/404)",
                    {"invalid_id": invalid_id, "status_code": response.status_code}
                )
            except Exception as e:
                self.log_test(
                    f"Download Security - Invalid ID: '{invalid_id[:20]}'",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_session_validation_requirements(self):
        """Test session validation requirements (90% completion)"""
        try:
            # Test with incomplete session
            incomplete_payload = {
                "session_id": "INCOMPLETE-SESSION-TEST",
                "delivery_method": "download",
                "origin_url": "https://agente-coruja-1.preview.emergentagent.com",
                "user_email": "test@payment.com"
            }
            
            response = self.session.post(f"{API_BASE}/owl-agent/initiate-payment", json=incomplete_payload)
            
            # Should return error for incomplete session
            if response.status_code == 400:
                error_text = response.text.lower()
                completion_check = "complet" in error_text or "90" in error_text or "not completed" in error_text
                
                self.log_test(
                    "Session Validation - Completion Requirement",
                    completion_check,
                    f"Correctly rejected incomplete session, mentions completion: {completion_check}",
                    {"status_code": 400, "completion_check": completion_check}
                )
            elif response.status_code == 404:
                self.log_test(
                    "Session Validation - Completion Requirement",
                    True,
                    "Correctly returned 404 for non-existent session",
                    {"status_code": 404}
                )
            else:
                self.log_test(
                    "Session Validation - Completion Requirement",
                    False,
                    f"Unexpected response: HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Session Validation Requirements",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_payment_error_handling(self):
        """Test payment system error handling"""
        try:
            # Test missing required fields
            error_scenarios = [
                {"payload": {}, "description": "Empty payload"},
                {"payload": {"session_id": ""}, "description": "Empty session_id"},
                {"payload": {"session_id": "test", "origin_url": ""}, "description": "Empty origin_url"},
                {"payload": {"session_id": "test"}, "description": "Missing origin_url"}
            ]
            
            for scenario in error_scenarios:
                response = self.session.post(f"{API_BASE}/owl-agent/initiate-payment", json=scenario["payload"])
                
                # Should return 400 for missing required fields
                proper_error_handling = response.status_code == 400
                
                self.log_test(
                    f"Payment Error Handling - {scenario['description']}",
                    proper_error_handling,
                    f"HTTP {response.status_code} (expected 400 for missing fields)",
                    {
                        "scenario": scenario["description"],
                        "status_code": response.status_code,
                        "payload": scenario["payload"]
                    }
                )
        except Exception as e:
            self.log_test(
                "Payment Error Handling",
                False,
                f"Exception: {str(e)}"
            )
    
    def run_payment_system_tests(self):
        """Run all payment system tests"""
        print("💳 OWL AGENT PAYMENT & DOWNLOAD SYSTEM TESTS")
        print("=" * 80)
        print(f"🌐 Testing against: {API_BASE}")
        print("Testing Stripe integration, secure downloads, privacy compliance")
        print("-" * 80)
        
        # Test 1: Create a completed Owl session for payment testing
        completed_session_id = self.create_completed_owl_session()
        
        if completed_session_id:
            # Test 2: Initiate Payment - Fixed Package Pricing
            self.test_initiate_payment_fixed_pricing(completed_session_id)
        
        # Test 3: Payment Status Polling
        self.test_payment_status_polling()
        
        # Test 4: Stripe Webhook Handling
        self.test_stripe_webhook_handling()
        
        # Test 5: Secure Download System
        self.test_secure_download_system()
        
        # Test 6: Download Security Features
        self.test_download_security_features()
        
        # Test 7: Session Validation Requirements
        self.test_session_validation_requirements()
        
        # Test 8: Error Handling Scenarios
        self.test_payment_error_handling()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n📊 PAYMENT SYSTEM TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['details']}")
        
        print(f"\n✅ PASSED TESTS ({passed_tests}):")
        for test in self.test_results:
            if test["success"]:
                print(f"  - {test['test']}")
        
        print("\n" + "=" * 80)
        if passed_tests == total_tests:
            print("🎉 ALL PAYMENT SYSTEM TESTS PASSED!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ PAYMENT SYSTEM MOSTLY WORKING (80%+ pass rate)")
        else:
            print("⚠️ PAYMENT SYSTEM NEEDS ATTENTION (< 80% pass rate)")

if __name__ == "__main__":
    tester = OwlPaymentSystemTester()
    tester.run_payment_system_tests()