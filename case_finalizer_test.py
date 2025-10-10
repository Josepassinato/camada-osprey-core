#!/usr/bin/env python3
"""
CASE FINALIZER EXPANDIDO (VERSÃO COMPLETA) - TESTE CRÍTICO
Tests the expanded Case Finalizer system with 10 scenarios, PDF merging, and new endpoints
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CaseFinalizerExpandedTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CaseFinalizerExpandedTester/1.0'
        })
        self.auth_token = None
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
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def setup_test_authentication(self):
        """Setup authentication for endpoints that require it"""
        try:
            # Try to create a test user
            test_user_data = {
                "email": "casefinalizer@test.com",
                "password": "testpassword123",
                "first_name": "Case",
                "last_name": "Finalizer"
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
    
    def test_case_finalizer_capabilities(self):
        """Test GET /api/cases/{case_id}/finalize/capabilities"""
        print("🔍 TESTING CASE FINALIZER CAPABILITIES...")
        
        test_case_id = "TEST-CAPABILITIES"
        
        try:
            response = self.session.get(f"{API_BASE}/cases/{test_case_id}/finalize/capabilities")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for 10 scenarios suportados
                scenarios = data.get("supported_scenarios", [])
                expected_scenarios = [
                    "H-1B_basic", "F-1_basic", "I-485_employment", 
                    "I-130_family", "I-589_asylum", "N-400_naturalization",
                    "I-765_work_auth", "I-90_green_card", "I-751_conditions", "O-1_extraordinary"
                ]
                
                # Check features
                features = data.get("features", {})
                pdf_merging = features.get("pdf_merging", False)
                instruction_templates = features.get("instruction_templates", False)
                
                scenarios_count = len(scenarios)
                has_10_scenarios = scenarios_count >= 10
                
                self.log_test(
                    "Case Finalizer Capabilities - 10 Scenarios",
                    has_10_scenarios,
                    f"Found {scenarios_count} scenarios (expected ≥10): {scenarios[:5]}...",
                    {
                        "scenarios_count": scenarios_count,
                        "scenarios": scenarios,
                        "pdf_merging": pdf_merging,
                        "instruction_templates": instruction_templates
                    }
                )
                
                self.log_test(
                    "Case Finalizer Capabilities - PDF Merging",
                    pdf_merging,
                    f"PDF merging enabled: {pdf_merging}",
                    {"pdf_merging": pdf_merging}
                )
                
                self.log_test(
                    "Case Finalizer Capabilities - Instruction Templates",
                    instruction_templates,
                    f"Instruction templates enabled: {instruction_templates}",
                    {"instruction_templates": instruction_templates}
                )
                
                return data
                
            else:
                self.log_test(
                    "Case Finalizer Capabilities",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Case Finalizer Capabilities",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_h1b_basic_scenario(self):
        """Test H-1B_basic scenario with FedEx postage"""
        print("🚀 TESTING H-1B_basic SCENARIO...")
        
        test_case_id = "TEST-H1B-BASIC"
        
        payload = {
            "scenario_key": "H-1B_basic",
            "postage": "FedEx",
            "language": "pt"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/cases/{test_case_id}/finalize/start",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                
                if job_id:
                    # Test status polling
                    status_response = self.session.get(f"{API_BASE}/cases/finalize/{job_id}/status")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        # Check for expected H-1B fees
                        expected_fees = ["$460", "$2805"]  # I-129 and Premium Processing
                        fees_mentioned = any(fee in str(status_data) for fee in expected_fees)
                        
                        # Check for FedEx address
                        fedex_mentioned = "FedEx" in str(status_data) or "fedex" in str(status_data).lower()
                        
                        self.log_test(
                            "H-1B Basic Scenario - Fees",
                            fees_mentioned,
                            f"H-1B fees detected: {fees_mentioned}",
                            {"expected_fees": expected_fees, "status": status_data.get("status")}
                        )
                        
                        self.log_test(
                            "H-1B Basic Scenario - FedEx Postage",
                            fedex_mentioned,
                            f"FedEx postage method detected: {fedex_mentioned}",
                            {"postage": "FedEx", "status": status_data.get("status")}
                        )
                        
                        return job_id
                    else:
                        self.log_test(
                            "H-1B Basic Scenario",
                            False,
                            f"Status polling failed: HTTP {status_response.status_code}",
                            status_response.text
                        )
                else:
                    self.log_test(
                        "H-1B Basic Scenario",
                        False,
                        "No job_id in response",
                        data
                    )
            else:
                self.log_test(
                    "H-1B Basic Scenario",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "H-1B Basic Scenario",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_i485_employment_scenario(self):
        """Test I-485_employment scenario"""
        print("💼 TESTING I-485_employment SCENARIO...")
        
        test_case_id = "TEST-I485-EMPLOYMENT"
        
        payload = {
            "scenario_key": "I-485_employment",
            "postage": "USPS",
            "language": "en"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/cases/{test_case_id}/finalize/start",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                
                if job_id:
                    # Test status polling
                    status_response = self.session.get(f"{API_BASE}/cases/finalize/{job_id}/status")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        # Check for I-485 specific content
                        i485_mentioned = "I-485" in str(status_data) or "adjustment" in str(status_data).lower()
                        employment_mentioned = "employment" in str(status_data).lower()
                        
                        self.log_test(
                            "I-485 Employment Scenario",
                            i485_mentioned and employment_mentioned,
                            f"I-485 employment content detected: I-485={i485_mentioned}, Employment={employment_mentioned}",
                            {"scenario": "I-485_employment", "status": status_data.get("status")}
                        )
                        
                        return job_id
                    else:
                        self.log_test(
                            "I-485 Employment Scenario",
                            False,
                            f"Status polling failed: HTTP {status_response.status_code}",
                            status_response.text
                        )
                else:
                    self.log_test(
                        "I-485 Employment Scenario",
                        False,
                        "No job_id in response",
                        data
                    )
            else:
                self.log_test(
                    "I-485 Employment Scenario",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "I-485 Employment Scenario",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_i589_asylum_scenario(self):
        """Test I-589_asylum scenario"""
        print("🛡️ TESTING I-589_asylum SCENARIO...")
        
        test_case_id = "TEST-I589-ASYLUM"
        
        payload = {
            "scenario_key": "I-589_asylum",
            "postage": "USPS",
            "language": "pt"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/cases/{test_case_id}/finalize/start",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                
                if job_id:
                    # Test status polling
                    status_response = self.session.get(f"{API_BASE}/cases/finalize/{job_id}/status")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        # Check for I-589 asylum specific content
                        i589_mentioned = "I-589" in str(status_data)
                        asylum_mentioned = "asylum" in str(status_data).lower() or "asilo" in str(status_data).lower()
                        
                        self.log_test(
                            "I-589 Asylum Scenario",
                            i589_mentioned or asylum_mentioned,
                            f"I-589 asylum content detected: I-589={i589_mentioned}, Asylum={asylum_mentioned}",
                            {"scenario": "I-589_asylum", "status": status_data.get("status")}
                        )
                        
                        return job_id
                    else:
                        self.log_test(
                            "I-589 Asylum Scenario",
                            False,
                            f"Status polling failed: HTTP {status_response.status_code}",
                            status_response.text
                        )
                else:
                    self.log_test(
                        "I-589 Asylum Scenario",
                        False,
                        "No job_id in response",
                        data
                    )
            else:
                self.log_test(
                    "I-589 Asylum Scenario",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "I-589 Asylum Scenario",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_n400_naturalization_scenario(self):
        """Test N-400_naturalization scenario"""
        print("🇺🇸 TESTING N-400_naturalization SCENARIO...")
        
        test_case_id = "TEST-N400-NATURALIZATION"
        
        payload = {
            "scenario_key": "N-400_naturalization",
            "postage": "FedEx",
            "language": "en"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/cases/{test_case_id}/finalize/start",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                
                if job_id:
                    # Test status polling
                    status_response = self.session.get(f"{API_BASE}/cases/finalize/{job_id}/status")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        # Check for N-400 naturalization specific content
                        n400_mentioned = "N-400" in str(status_data)
                        naturalization_mentioned = "naturalization" in str(status_data).lower() or "citizenship" in str(status_data).lower()
                        
                        self.log_test(
                            "N-400 Naturalization Scenario",
                            n400_mentioned or naturalization_mentioned,
                            f"N-400 naturalization content detected: N-400={n400_mentioned}, Naturalization={naturalization_mentioned}",
                            {"scenario": "N-400_naturalization", "status": status_data.get("status")}
                        )
                        
                        return job_id
                    else:
                        self.log_test(
                            "N-400 Naturalization Scenario",
                            False,
                            f"Status polling failed: HTTP {status_response.status_code}",
                            status_response.text
                        )
                else:
                    self.log_test(
                        "N-400 Naturalization Scenario",
                        False,
                        "No job_id in response",
                        data
                    )
            else:
                self.log_test(
                    "N-400 Naturalization Scenario",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "N-400 Naturalization Scenario",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_download_instructions(self, job_id: str):
        """Test GET /api/download/instructions/{job_id}"""
        print(f"📄 TESTING DOWNLOAD INSTRUCTIONS for job_id: {job_id}...")
        
        try:
            response = self.session.get(f"{API_BASE}/download/instructions/{job_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for instruction content
                has_content = "content" in data or "instructions" in data
                has_language = "language" in data
                
                self.log_test(
                    "Download Instructions",
                    has_content,
                    f"Instructions downloaded successfully: content={has_content}, language={has_language}",
                    {"job_id": job_id, "has_content": has_content}
                )
                
                return data
            else:
                self.log_test(
                    "Download Instructions",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Download Instructions",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_download_checklist(self, job_id: str):
        """Test GET /api/download/checklist/{job_id}"""
        print(f"📋 TESTING DOWNLOAD CHECKLIST for job_id: {job_id}...")
        
        try:
            response = self.session.get(f"{API_BASE}/download/checklist/{job_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for checklist content
                has_content = "content" in data or "checklist" in data
                has_status = "status" in data
                
                self.log_test(
                    "Download Checklist",
                    has_content,
                    f"Checklist downloaded successfully: content={has_content}, status={has_status}",
                    {"job_id": job_id, "has_content": has_content}
                )
                
                return data
            else:
                self.log_test(
                    "Download Checklist",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Download Checklist",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_download_master_packet(self, job_id: str):
        """Test GET /api/download/master-packet/{job_id}"""
        print(f"📦 TESTING DOWNLOAD MASTER PACKET for job_id: {job_id}...")
        
        try:
            response = self.session.get(f"{API_BASE}/download/master-packet/{job_id}")
            
            if response.status_code == 200:
                # Check if it's a PDF or JSON response
                content_type = response.headers.get('content-type', '')
                
                if 'application/pdf' in content_type:
                    # PDF response
                    pdf_size = len(response.content)
                    has_pdf = pdf_size > 1000  # At least 1KB
                    
                    self.log_test(
                        "Download Master Packet - PDF",
                        has_pdf,
                        f"PDF master packet downloaded: size={pdf_size} bytes",
                        {"job_id": job_id, "content_type": content_type, "size": pdf_size}
                    )
                else:
                    # JSON response
                    try:
                        data = response.json()
                        has_content = "content" in data or "packet" in data or "download_url" in data
                        
                        self.log_test(
                            "Download Master Packet - JSON",
                            has_content,
                            f"Master packet info downloaded: {list(data.keys())}",
                            {"job_id": job_id, "content_type": content_type, "data_keys": list(data.keys())}
                        )
                    except json.JSONDecodeError:
                        self.log_test(
                            "Download Master Packet",
                            False,
                            "Invalid JSON response",
                            {"content_type": content_type}
                        )
                
                return True
            else:
                self.log_test(
                    "Download Master Packet",
                    False,
                    f"HTTP {response.status_code}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Download Master Packet",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_knowledge_base_complete(self):
        """Test Knowledge Base Completo with fees and addresses"""
        print("📚 TESTING KNOWLEDGE BASE COMPLETO...")
        
        # Test different scenarios to verify knowledge base
        scenarios_to_test = [
            {
                "scenario": "H-1B_basic",
                "expected_fees": ["$460", "$1500", "$2500"],  # I-129, H1B_CAP, PREMIUM
                "expected_address": "Texas Service Center"
            },
            {
                "scenario": "F-1_basic", 
                "expected_fees": ["$350"],  # SEVIS
                "expected_address": "Student Exchange"
            },
            {
                "scenario": "I-485_employment",
                "expected_fees": ["$1140", "$85"],  # I-485 fee and biometrics
                "expected_address": "Chicago Lockbox"
            }
        ]
        
        knowledge_base_working = 0
        total_scenarios = len(scenarios_to_test)
        
        for scenario_info in scenarios_to_test:
            test_case_id = f"TEST-KB-{scenario_info['scenario'].replace('_', '-').upper()}"
            
            payload = {
                "scenario_key": scenario_info["scenario"],
                "postage": "USPS",
                "language": "pt"
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/cases/{test_case_id}/finalize/start",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    job_id = data.get("job_id")
                    
                    if job_id:
                        # Get status to check knowledge base content
                        status_response = self.session.get(f"{API_BASE}/cases/finalize/{job_id}/status")
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status_str = str(status_data)
                            
                            # Check for expected fees
                            fees_found = sum(1 for fee in scenario_info["expected_fees"] if fee in status_str)
                            fees_ratio = fees_found / len(scenario_info["expected_fees"])
                            
                            # Check for expected address
                            address_found = scenario_info["expected_address"].lower() in status_str.lower()
                            
                            scenario_working = fees_ratio >= 0.5 or address_found  # At least 50% fees or address
                            
                            if scenario_working:
                                knowledge_base_working += 1
                            
                            self.log_test(
                                f"Knowledge Base - {scenario_info['scenario']}",
                                scenario_working,
                                f"Fees: {fees_found}/{len(scenario_info['expected_fees'])}, Address: {address_found}",
                                {
                                    "scenario": scenario_info["scenario"],
                                    "expected_fees": scenario_info["expected_fees"],
                                    "fees_found": fees_found,
                                    "address_expected": scenario_info["expected_address"],
                                    "address_found": address_found
                                }
                            )
            except Exception as e:
                self.log_test(
                    f"Knowledge Base - {scenario_info['scenario']}",
                    False,
                    f"Exception: {str(e)}"
                )
        
        # Overall knowledge base assessment
        kb_success_rate = knowledge_base_working / total_scenarios
        kb_working = kb_success_rate >= 0.6  # At least 60% working
        
        self.log_test(
            "Knowledge Base Complete Assessment",
            kb_working,
            f"Knowledge base working for {knowledge_base_working}/{total_scenarios} scenarios ({kb_success_rate:.1%})",
            {
                "scenarios_working": knowledge_base_working,
                "total_scenarios": total_scenarios,
                "success_rate": kb_success_rate
            }
        )
    
    def run_all_tests(self):
        """Run all Case Finalizer Expandido tests"""
        print("🚀 STARTING CASE FINALIZER EXPANDIDO (VERSÃO COMPLETA) TESTS")
        print("=" * 80)
        
        # Test 1: Capabilities endpoint
        self.test_case_finalizer_capabilities()
        
        # Test 2: Core scenarios
        h1b_job_id = self.test_h1b_basic_scenario()
        i485_job_id = self.test_i485_employment_scenario()
        i589_job_id = self.test_i589_asylum_scenario()
        n400_job_id = self.test_n400_naturalization_scenario()
        
        # Test 3: Download endpoints (if we have job IDs)
        if h1b_job_id:
            self.test_download_instructions(h1b_job_id)
            self.test_download_checklist(h1b_job_id)
            self.test_download_master_packet(h1b_job_id)
        
        # Test 4: Knowledge base complete
        self.test_knowledge_base_complete()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 CASE FINALIZER EXPANDIDO TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests:.1%}")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests/total_tests,
            "results": self.test_results
        }

if __name__ == "__main__":
    tester = CaseFinalizerExpandedTester()
    results = tester.run_all_tests()