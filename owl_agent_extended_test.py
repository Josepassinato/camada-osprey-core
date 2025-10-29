#!/usr/bin/env python3
"""
AGENTE CORUJA (OWL AGENT) EXTENDED TESTING
Tests additional scenarios and edge cases
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

class OwlAgentExtendedTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OwlAgentExtendedTester/1.0'
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
        print()
    
    def test_multi_language_support(self):
        """Test Portuguese and English language support"""
        languages = ["pt", "en"]
        
        for lang in languages:
            try:
                payload = {
                    "case_id": f"TEST-OWL-LANG-{lang.upper()}",
                    "visa_type": "H-1B",
                    "language": lang
                }
                
                response = self.session.post(
                    f"{API_BASE}/owl-agent/start-session",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session_data = data.get("session", {})
                    welcome_msg = session_data.get("welcome_message", {})
                    
                    # Check if language is correctly set
                    success = (
                        session_data.get("language") == lang and
                        welcome_msg.get("language") == lang
                    )
                    
                    self.log_test(
                        f"Multi-Language Support - {lang.upper()}",
                        success,
                        f"Language: {session_data.get('language')}, Welcome message in {lang}",
                        {"session_id": session_data.get("session_id"), "language": lang}
                    )
                else:
                    self.log_test(
                        f"Multi-Language Support - {lang.upper()}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_test(
                    f"Multi-Language Support - {lang.upper()}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_different_visa_types(self):
        """Test different visa types (H-1B, F-1, I-485)"""
        visa_types = ["H-1B", "F-1", "I-485"]
        
        for visa_type in visa_types:
            try:
                payload = {
                    "case_id": f"TEST-OWL-VISA-{visa_type.replace('-', '')}",
                    "visa_type": visa_type,
                    "language": "pt"
                }
                
                response = self.session.post(
                    f"{API_BASE}/owl-agent/start-session",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session_data = data.get("session", {})
                    
                    success = (
                        session_data.get("visa_type") == visa_type and
                        session_data.get("total_fields", 0) > 0
                    )
                    
                    self.log_test(
                        f"Visa Type Support - {visa_type}",
                        success,
                        f"Fields: {session_data.get('total_fields')}, Visa: {visa_type}",
                        {"session_id": session_data.get("session_id"), "visa_type": visa_type}
                    )
                else:
                    self.log_test(
                        f"Visa Type Support - {visa_type}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_test(
                    f"Visa Type Support - {visa_type}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_field_validation_scenarios(self):
        """Test various field validation scenarios"""
        
        # First create a session
        session_payload = {
            "case_id": "TEST-OWL-VALIDATION",
            "visa_type": "H-1B",
            "language": "pt"
        }
        
        session_response = self.session.post(
            f"{API_BASE}/owl-agent/start-session",
            json=session_payload
        )
        
        if session_response.status_code != 200:
            self.log_test("Field Validation Setup", False, "Failed to create session")
            return
        
        session_id = session_response.json().get("session", {}).get("session_id")
        
        # Test scenarios
        validation_scenarios = [
            {
                "name": "Valid Name",
                "field_id": "full_name",
                "input": "João Silva Santos",
                "expected_score_min": 80
            },
            {
                "name": "Invalid Name (Numbers)",
                "field_id": "full_name", 
                "input": "João123 Silva",
                "expected_score_max": 60
            },
            {
                "name": "Valid Email",
                "field_id": "email",
                "input": "joao.silva@email.com",
                "expected_score_min": 80
            },
            {
                "name": "Invalid Email",
                "field_id": "email",
                "input": "invalid-email",
                "expected_score_max": 50
            }
        ]
        
        for scenario in validation_scenarios:
            try:
                payload = {
                    "session_id": session_id,
                    "field_id": scenario["field_id"],
                    "user_input": scenario["input"],
                    "context": {"visa_type": "H-1B"}
                }
                
                response = self.session.post(
                    f"{API_BASE}/owl-agent/validate-field",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    validation = data.get("validation", {})
                    score = validation.get("overall_score", 0)
                    
                    # Check if score meets expectations
                    if "expected_score_min" in scenario:
                        success = score >= scenario["expected_score_min"]
                    else:
                        success = score <= scenario["expected_score_max"]
                    
                    self.log_test(
                        f"Field Validation - {scenario['name']}",
                        success,
                        f"Score: {score}%, Input: '{scenario['input']}'",
                        {"field_id": scenario["field_id"], "score": score}
                    )
                else:
                    self.log_test(
                        f"Field Validation - {scenario['name']}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_test(
                    f"Field Validation - {scenario['name']}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        
        # Test 1: Invalid session ID
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/session/invalid-session-id")
            
            success = response.status_code == 404
            
            self.log_test(
                "Error Handling - Invalid Session ID",
                success,
                f"HTTP {response.status_code} (expected 404)",
                {"expected": 404, "actual": response.status_code}
            )
        except Exception as e:
            self.log_test(
                "Error Handling - Invalid Session ID",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 2: Missing required fields
        try:
            payload = {
                "visa_type": "H-1B",
                "language": "pt"
                # Missing case_id
            }
            
            response = self.session.post(
                f"{API_BASE}/owl-agent/start-session",
                json=payload
            )
            
            success = response.status_code == 400
            
            self.log_test(
                "Error Handling - Missing Required Fields",
                success,
                f"HTTP {response.status_code} (expected 400)",
                {"expected": 400, "actual": response.status_code}
            )
        except Exception as e:
            self.log_test(
                "Error Handling - Missing Required Fields",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test 3: Invalid form ID for download
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/download-form/invalid-form-id")
            
            success = response.status_code in [404, 500]  # Either is acceptable
            
            self.log_test(
                "Error Handling - Invalid Form ID",
                success,
                f"HTTP {response.status_code} (expected 404 or 500)",
                {"expected": "404 or 500", "actual": response.status_code}
            )
        except Exception as e:
            self.log_test(
                "Error Handling - Invalid Form ID",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_complete_workflow(self):
        """Test complete workflow from start to PDF generation"""
        
        workflow_steps = []
        
        try:
            # Step 1: Start session
            session_payload = {
                "case_id": "TEST-OWL-WORKFLOW",
                "visa_type": "F-1",
                "language": "en"
            }
            
            session_response = self.session.post(
                f"{API_BASE}/owl-agent/start-session",
                json=session_payload
            )
            
            if session_response.status_code == 200:
                session_data = session_response.json().get("session", {})
                session_id = session_data.get("session_id")
                workflow_steps.append("✅ Session created")
                
                # Step 2: Get field guidance
                guidance_response = self.session.get(
                    f"{API_BASE}/owl-agent/field-guidance/{session_id}/full_name"
                )
                
                if guidance_response.status_code == 200:
                    workflow_steps.append("✅ Field guidance retrieved")
                    
                    # Step 3: Validate multiple fields
                    fields_to_test = [
                        {"field_id": "full_name", "input": "Maria Silva Santos"},
                        {"field_id": "date_of_birth", "input": "15/08/1995"},
                        {"field_id": "place_of_birth", "input": "São Paulo, SP, Brasil"}
                    ]
                    
                    validated_fields = 0
                    for field_data in fields_to_test:
                        validate_payload = {
                            "session_id": session_id,
                            "field_id": field_data["field_id"],
                            "user_input": field_data["input"],
                            "context": {"visa_type": "F-1"}
                        }
                        
                        validate_response = self.session.post(
                            f"{API_BASE}/owl-agent/validate-field",
                            json=validate_payload
                        )
                        
                        if validate_response.status_code == 200:
                            # Save response
                            save_payload = {
                                "session_id": session_id,
                                "field_id": field_data["field_id"],
                                "user_response": field_data["input"],
                                "validation_score": 85
                            }
                            
                            save_response = self.session.post(
                                f"{API_BASE}/owl-agent/save-response",
                                json=save_payload
                            )
                            
                            if save_response.status_code == 200:
                                validated_fields += 1
                    
                    workflow_steps.append(f"✅ {validated_fields}/{len(fields_to_test)} fields validated and saved")
                    
                    # Step 4: Generate USCIS form
                    form_payload = {"session_id": session_id}
                    
                    form_response = self.session.post(
                        f"{API_BASE}/owl-agent/generate-uscis-form",
                        json=form_payload
                    )
                    
                    if form_response.status_code == 200:
                        form_data = form_response.json()
                        form_id = form_data.get("form_id")
                        workflow_steps.append("✅ USCIS form generated")
                        
                        # Step 5: Download PDF
                        if form_id:
                            download_response = self.session.get(
                                f"{API_BASE}/owl-agent/download-form/{form_id}"
                            )
                            
                            if download_response.status_code == 200:
                                workflow_steps.append("✅ PDF downloaded successfully")
                            else:
                                workflow_steps.append("❌ PDF download failed")
                        else:
                            workflow_steps.append("❌ No form ID returned")
                    else:
                        workflow_steps.append("❌ Form generation failed")
                else:
                    workflow_steps.append("❌ Field guidance failed")
            else:
                workflow_steps.append("❌ Session creation failed")
            
            # Evaluate overall success
            success_count = len([step for step in workflow_steps if step.startswith("✅")])
            total_steps = len(workflow_steps)
            success = success_count >= 4  # At least 4 out of 5 steps should succeed
            
            self.log_test(
                "Complete Workflow Test",
                success,
                f"Steps completed: {success_count}/{total_steps}",
                {"workflow_steps": workflow_steps}
            )
            
        except Exception as e:
            self.log_test(
                "Complete Workflow Test",
                False,
                f"Exception: {str(e)}"
            )

    def run_extended_tests(self):
        """Run all extended tests"""
        print("🦉 AGENTE CORUJA - EXTENDED TESTING SUITE")
        print("=" * 80)
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base: {API_BASE}")
        print("-" * 80)
        
        # Test 1: Multi-language support
        print("\n🌍 Testing Multi-Language Support...")
        self.test_multi_language_support()
        
        # Test 2: Different visa types
        print("\n📋 Testing Different Visa Types...")
        self.test_different_visa_types()
        
        # Test 3: Field validation scenarios
        print("\n✅ Testing Field Validation Scenarios...")
        self.test_field_validation_scenarios()
        
        # Test 4: Error handling
        print("\n❌ Testing Error Handling...")
        self.test_error_handling()
        
        # Test 5: Complete workflow
        print("\n🔄 Testing Complete Workflow...")
        self.test_complete_workflow()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n📊 EXTENDED TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['details']}")
        
        print("\n✅ PASSED TESTS:")
        for test in self.test_results:
            if test["success"]:
                print(f"  - {test['test']}: {test['details']}")

if __name__ == "__main__":
    tester = OwlAgentExtendedTester()
    tester.run_extended_tests()