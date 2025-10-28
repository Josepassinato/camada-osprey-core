#!/usr/bin/env python3
"""
AGENTE CORUJA (OWL AGENT) TESTING - Focused Test Suite
Tests the new intelligent questionnaire system endpoints
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class OwlAgentTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'OwlAgentTester/1.0'
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
    
    def test_owl_agent_start_session(self):
        """Test POST /api/owl-agent/start-session"""
        try:
            payload = {
                "case_id": "TEST-OWL-CASE-001",
                "visa_type": "H-1B",
                "language": "pt"
            }
            
            response = self.session.post(
                f"{API_BASE}/owl-agent/start-session",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                success = (
                    data.get("success") is True and
                    "session" in data and
                    "session_id" in data.get("session", {})
                )
                
                self.log_test(
                    "Owl Agent - Start Session",
                    success,
                    f"Session ID: {data.get('session', {}).get('session_id', 'N/A')}",
                    {
                        "agent": data.get("agent"),
                        "session_id": data.get("session", {}).get("session_id"),
                        "total_fields": data.get("session", {}).get("total_fields")
                    }
                )
                return data
            else:
                self.log_test(
                    "Owl Agent - Start Session",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500]
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Start Session",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_owl_agent_get_session(self, session_id: str):
        """Test GET /api/owl-agent/session/{session_id}"""
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/session/{session_id}")
            
            if response.status_code == 200:
                data = response.json()
                success = (
                    data.get("success") is True and
                    "session_data" in data and
                    "progress" in data
                )
                
                self.log_test(
                    "Owl Agent - Get Session",
                    success,
                    f"Status: {data.get('session_data', {}).get('status', 'N/A')}",
                    {
                        "session_id": session_id,
                        "progress": data.get("progress"),
                        "completed_fields": len(data.get("session_data", {}).get("completed_fields", []))
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Get Session",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500]
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Get Session",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_agent_field_guidance(self, session_id: str):
        """Test GET /api/owl-agent/field-guidance/{session_id}/{field_id}"""
        try:
            field_id = "full_name"
            response = self.session.get(
                f"{API_BASE}/owl-agent/field-guidance/{session_id}/{field_id}",
                params={"current_value": "João Silva"}
            )
            
            if response.status_code == 200:
                data = response.json()
                success = (
                    data.get("success") is True and
                    "field_guidance" in data
                )
                
                guidance = data.get("field_guidance", {})
                self.log_test(
                    "Owl Agent - Field Guidance",
                    success,
                    f"Field: {field_id}, Guidance available: {bool(guidance)}",
                    {
                        "session_id": session_id,
                        "field_id": field_id,
                        "guidance_keys": list(guidance.keys()) if guidance else []
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Field Guidance",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500]
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Field Guidance",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_agent_validate_field(self, session_id: str):
        """Test POST /api/owl-agent/validate-field"""
        try:
            payload = {
                "session_id": session_id,
                "field_id": "full_name",
                "user_input": "João Silva Santos",
                "context": {
                    "passport_name": "João Silva Santos",
                    "visa_type": "H-1B"
                }
            }
            
            response = self.session.post(
                f"{API_BASE}/owl-agent/validate-field",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                success = (
                    data.get("success") is True and
                    "validation" in data
                )
                
                validation = data.get("validation", {})
                overall_score = validation.get("overall_score", 0)
                
                self.log_test(
                    "Owl Agent - Validate Field",
                    success,
                    f"Validation score: {overall_score}%",
                    {
                        "session_id": session_id,
                        "field_id": payload["field_id"],
                        "overall_score": overall_score,
                        "validation_keys": list(validation.keys()) if validation else []
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Validate Field",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500]
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Validate Field",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_agent_save_response(self, session_id: str):
        """Test POST /api/owl-agent/save-response"""
        try:
            payload = {
                "session_id": session_id,
                "field_id": "full_name",
                "user_response": "João Silva Santos",
                "validation_score": 85
            }
            
            response = self.session.post(
                f"{API_BASE}/owl-agent/save-response",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                success = (
                    data.get("success") is True and
                    data.get("message") == "Response saved successfully"
                )
                
                self.log_test(
                    "Owl Agent - Save Response",
                    success,
                    f"Response saved for field: {payload['field_id']}",
                    {
                        "session_id": session_id,
                        "field_id": payload["field_id"],
                        "validation_score": payload["validation_score"]
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Save Response",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500]
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Save Response",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_owl_agent_generate_uscis_form(self, session_id: str):
        """Test POST /api/owl-agent/generate-uscis-form"""
        try:
            payload = {
                "session_id": session_id
            }
            
            response = self.session.post(
                f"{API_BASE}/owl-agent/generate-uscis-form",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                success = (
                    data.get("success") is True and
                    "form_id" in data and
                    data.get("pdf_available") is True
                )
                
                form_id = data.get("form_id")
                
                self.log_test(
                    "Owl Agent - Generate USCIS Form",
                    success,
                    f"Form generated: {data.get('visa_type', 'N/A')} - ID: {form_id}",
                    {
                        "session_id": session_id,
                        "form_id": form_id,
                        "visa_type": data.get("visa_type"),
                        "pdf_available": data.get("pdf_available")
                    }
                )
                return form_id
            else:
                self.log_test(
                    "Owl Agent - Generate USCIS Form",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500]
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Generate USCIS Form",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_owl_agent_download_form(self, form_id: str):
        """Test GET /api/owl-agent/download-form/{form_id}"""
        try:
            response = self.session.get(f"{API_BASE}/owl-agent/download-form/{form_id}")
            
            if response.status_code == 200:
                # Check if response is PDF
                content_type = response.headers.get('content-type', '')
                is_pdf = content_type == 'application/pdf'
                has_content = len(response.content) > 0
                
                success = is_pdf and has_content
                
                self.log_test(
                    "Owl Agent - Download Form",
                    success,
                    f"PDF size: {len(response.content)} bytes, Content-Type: {content_type}",
                    {
                        "form_id": form_id,
                        "content_type": content_type,
                        "content_size": len(response.content),
                        "is_pdf": is_pdf
                    }
                )
            else:
                self.log_test(
                    "Owl Agent - Download Form",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:500]
                )
        except Exception as e:
            self.log_test(
                "Owl Agent - Download Form",
                False,
                f"Exception: {str(e)}"
            )

    def run_comprehensive_test(self):
        """Run comprehensive Owl Agent test"""
        print("🦉 TESTING AGENTE CORUJA - INTELLIGENT QUESTIONNAIRE SYSTEM")
        print("=" * 80)
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base: {API_BASE}")
        print("-" * 80)
        
        # Test 1: Start Session
        session_data = self.test_owl_agent_start_session()
        
        if session_data:
            session_id = session_data.get("session", {}).get("session_id")
            
            if session_id:
                # Test 2: Get Session Status
                self.test_owl_agent_get_session(session_id)
                
                # Test 3: Field Guidance
                self.test_owl_agent_field_guidance(session_id)
                
                # Test 4: Validate Field
                self.test_owl_agent_validate_field(session_id)
                
                # Test 5: Save Response
                self.test_owl_agent_save_response(session_id)
                
                # Test 6: Generate USCIS Form
                form_id = self.test_owl_agent_generate_uscis_form(session_id)
                
                # Test 7: Download Form
                if form_id:
                    self.test_owl_agent_download_form(form_id)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n📊 OWL AGENT TEST SUMMARY")
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
    tester = OwlAgentTester()
    tester.run_comprehensive_test()