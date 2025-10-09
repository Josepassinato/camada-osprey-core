#!/usr/bin/env python3
"""
Form Code Mismatch Investigation - Critical Bug Testing
Tests the reported issue where H-1B selection creates B-1/B-2 cases
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://formfill-pro-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class FormCodeInvestigator:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FormCodeInvestigator/1.0'
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
        if response_data:
            print(f"    Response: {json.dumps(response_data, indent=2)}")
        print()
    
    def test_auto_application_start_h1b(self):
        """Test POST /api/auto-application/start with H-1B form_code"""
        print("🔍 Testing H-1B Case Creation...")
        
        payload = {
            "session_token": "test_h1b_session",
            "form_code": "H-1B"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                case_data = data.get("case", {})
                case_id = case_data.get("case_id")
                form_code = case_data.get("form_code")
                
                # Critical check: form_code should be H-1B, not B-1/B-2
                if form_code == "H-1B":
                    self.log_test(
                        "H-1B Case Creation - Form Code Correct",
                        True,
                        f"✅ Case {case_id} created with correct form_code: {form_code}",
                        {"case_id": case_id, "form_code": form_code}
                    )
                    return case_id, data
                else:
                    self.log_test(
                        "H-1B Case Creation - Form Code MISMATCH",
                        False,
                        f"❌ CRITICAL BUG: Expected 'H-1B', got '{form_code}' for case {case_id}",
                        {"case_id": case_id, "form_code": form_code, "expected": "H-1B"}
                    )
                    return case_id, data
            else:
                self.log_test(
                    "H-1B Case Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                return None, None
        except Exception as e:
            self.log_test(
                "H-1B Case Creation",
                False,
                f"Exception: {str(e)}",
                None
            )
            return None, None
    
    def test_auto_application_start_b1b2(self):
        """Test POST /api/auto-application/start with B-1/B-2 form_code"""
        print("🔍 Testing B-1/B-2 Case Creation...")
        
        payload = {
            "session_token": "test_b1b2_session",
            "form_code": "B-1/B-2"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                case_id = data.get("case_id")
                form_code = data.get("form_code")
                
                # Check: form_code should be B-1/B-2
                if form_code == "B-1/B-2":
                    self.log_test(
                        "B-1/B-2 Case Creation - Form Code Correct",
                        True,
                        f"✅ Case {case_id} created with correct form_code: {form_code}",
                        data
                    )
                    return case_id, data
                else:
                    self.log_test(
                        "B-1/B-2 Case Creation - Form Code Issue",
                        False,
                        f"❌ Expected 'B-1/B-2', got '{form_code}' for case {case_id}",
                        data
                    )
                    return case_id, data
            else:
                self.log_test(
                    "B-1/B-2 Case Creation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
                return None, None
        except Exception as e:
            self.log_test(
                "B-1/B-2 Case Creation",
                False,
                f"Exception: {str(e)}",
                None
            )
            return None, None
    
    def test_case_update_h1b(self, case_id: str):
        """Test PUT /api/auto-application/case/{case_id} with H-1B form_code"""
        if not case_id:
            self.log_test(
                "H-1B Case Update",
                False,
                "No case_id provided",
                None
            )
            return
        
        print(f"🔍 Testing H-1B Case Update for case {case_id}...")
        
        payload = {
            "form_code": "H-1B",
            "session_token": "test_h1b_session"
        }
        
        try:
            response = self.session.put(
                f"{API_BASE}/auto-application/case/{case_id}",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                form_code = data.get("form_code")
                
                # Critical check: form_code should be H-1B after update
                if form_code == "H-1B":
                    self.log_test(
                        "H-1B Case Update - Form Code Correct",
                        True,
                        f"✅ Case {case_id} updated with correct form_code: {form_code}",
                        data
                    )
                else:
                    self.log_test(
                        "H-1B Case Update - Form Code MISMATCH",
                        False,
                        f"❌ CRITICAL BUG: Expected 'H-1B', got '{form_code}' after update",
                        data
                    )
            else:
                self.log_test(
                    "H-1B Case Update",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
        except Exception as e:
            self.log_test(
                "H-1B Case Update",
                False,
                f"Exception: {str(e)}",
                None
            )
    
    def test_case_retrieval(self, case_id: str, expected_form_code: str):
        """Test GET /api/auto-application/case/{case_id} to verify form_code persistence"""
        if not case_id:
            self.log_test(
                f"Case Retrieval - {expected_form_code}",
                False,
                "No case_id provided",
                None
            )
            return
        
        print(f"🔍 Testing Case Retrieval for {case_id} (expecting {expected_form_code})...")
        
        try:
            response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}")
            
            if response.status_code == 200:
                data = response.json()
                form_code = data.get("form_code")
                
                if form_code == expected_form_code:
                    self.log_test(
                        f"Case Retrieval - {expected_form_code} Correct",
                        True,
                        f"✅ Case {case_id} persisted with correct form_code: {form_code}",
                        {"case_id": case_id, "form_code": form_code, "status": data.get("status")}
                    )
                else:
                    self.log_test(
                        f"Case Retrieval - {expected_form_code} MISMATCH",
                        False,
                        f"❌ PERSISTENCE BUG: Expected '{expected_form_code}', got '{form_code}'",
                        data
                    )
            else:
                self.log_test(
                    f"Case Retrieval - {expected_form_code}",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
        except Exception as e:
            self.log_test(
                f"Case Retrieval - {expected_form_code}",
                False,
                f"Exception: {str(e)}",
                None
            )
    
    def test_enum_validation(self):
        """Test USCISForm enum validation with various form codes"""
        print("🔍 Testing USCISForm Enum Validation...")
        
        test_cases = [
            {"form_code": "H-1B", "should_work": True},
            {"form_code": "B-1/B-2", "should_work": True},
            {"form_code": "F-1", "should_work": True},
            {"form_code": "O-1", "should_work": True},
            {"form_code": "INVALID", "should_work": False},
            {"form_code": "h1b", "should_work": False},  # Case sensitive
            {"form_code": "H1B", "should_work": False},  # No dash
        ]
        
        for i, test_case in enumerate(test_cases):
            form_code = test_case["form_code"]
            should_work = test_case["should_work"]
            
            payload = {
                "session_token": f"enum_test_{i}",
                "form_code": form_code
            }
            
            try:
                response = self.session.post(
                    f"{API_BASE}/auto-application/start",
                    json=payload
                )
                
                if should_work:
                    if response.status_code == 200:
                        data = response.json()
                        returned_form_code = data.get("form_code")
                        if returned_form_code == form_code:
                            self.log_test(
                                f"Enum Validation - {form_code} Valid",
                                True,
                                f"✅ {form_code} accepted and returned correctly",
                                {"input": form_code, "output": returned_form_code}
                            )
                        else:
                            self.log_test(
                                f"Enum Validation - {form_code} Transformation",
                                False,
                                f"❌ {form_code} transformed to {returned_form_code}",
                                data
                            )
                    else:
                        self.log_test(
                            f"Enum Validation - {form_code} Rejected",
                            False,
                            f"❌ {form_code} should be valid but was rejected: {response.status_code}",
                            response.text
                        )
                else:
                    if response.status_code != 200:
                        self.log_test(
                            f"Enum Validation - {form_code} Correctly Rejected",
                            True,
                            f"✅ {form_code} correctly rejected with {response.status_code}",
                            None
                        )
                    else:
                        self.log_test(
                            f"Enum Validation - {form_code} Should Be Rejected",
                            False,
                            f"❌ {form_code} should be invalid but was accepted",
                            response.json()
                        )
            except Exception as e:
                self.log_test(
                    f"Enum Validation - {form_code}",
                    False,
                    f"Exception: {str(e)}",
                    None
                )
    
    def test_default_behavior(self):
        """Test default behavior when no form_code is provided"""
        print("🔍 Testing Default Behavior...")
        
        payload = {
            "session_token": "default_test"
            # No form_code provided
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                form_code = data.get("form_code")
                
                if form_code is None:
                    self.log_test(
                        "Default Behavior - No Form Code",
                        True,
                        "✅ No form_code set when none provided",
                        data
                    )
                elif form_code == "B-1/B-2":
                    self.log_test(
                        "Default Behavior - B-1/B-2 Default",
                        False,
                        "❌ POTENTIAL BUG: Default form_code is B-1/B-2 - this might be causing the issue",
                        data
                    )
                else:
                    self.log_test(
                        "Default Behavior - Other Default",
                        True,
                        f"ℹ️ Default form_code is: {form_code}",
                        data
                    )
            else:
                self.log_test(
                    "Default Behavior",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    None
                )
        except Exception as e:
            self.log_test(
                "Default Behavior",
                False,
                f"Exception: {str(e)}",
                None
            )
    
    def test_edge_cases(self):
        """Test edge cases that might reveal the bug"""
        print("🔍 Testing Edge Cases...")
        
        # Test case 1: Empty form_code
        payload1 = {
            "session_token": "edge_test_1",
            "form_code": ""
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=payload1
            )
            
            if response.status_code == 200:
                data = response.json()
                form_code = data.get("form_code")
                
                if form_code == "B-1/B-2":
                    self.log_test(
                        "Edge Case - Empty String Defaults to B-1/B-2",
                        False,
                        "❌ POTENTIAL BUG: Empty form_code defaults to B-1/B-2",
                        data
                    )
                else:
                    self.log_test(
                        "Edge Case - Empty String",
                        True,
                        f"✅ Empty form_code handled correctly: {form_code}",
                        data
                    )
        except Exception as e:
            self.log_test(
                "Edge Case - Empty String",
                False,
                f"Exception: {str(e)}",
                None
            )
        
        # Test case 2: Null form_code
        payload2 = {
            "session_token": "edge_test_2",
            "form_code": None
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=payload2
            )
            
            if response.status_code == 200:
                data = response.json()
                form_code = data.get("form_code")
                
                if form_code == "B-1/B-2":
                    self.log_test(
                        "Edge Case - Null Defaults to B-1/B-2",
                        False,
                        "❌ POTENTIAL BUG: Null form_code defaults to B-1/B-2",
                        data
                    )
                else:
                    self.log_test(
                        "Edge Case - Null",
                        True,
                        f"✅ Null form_code handled correctly: {form_code}",
                        data
                    )
        except Exception as e:
            self.log_test(
                "Edge Case - Null",
                False,
                f"Exception: {str(e)}",
                None
            )
    
    def test_sequential_operations(self):
        """Test sequential operations to see if there's cross-contamination"""
        print("🔍 Testing Sequential Operations for Cross-Contamination...")
        
        # Create B-1/B-2 case first
        payload_b1b2 = {
            "session_token": "seq_test_b1b2",
            "form_code": "B-1/B-2"
        }
        
        try:
            response_b1b2 = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=payload_b1b2
            )
            
            if response_b1b2.status_code == 200:
                data_b1b2 = response_b1b2.json()
                case_id_b1b2 = data_b1b2.get("case_id")
                
                # Now create H-1B case immediately after
                payload_h1b = {
                    "session_token": "seq_test_h1b",
                    "form_code": "H-1B"
                }
                
                response_h1b = self.session.post(
                    f"{API_BASE}/auto-application/start",
                    json=payload_h1b
                )
                
                if response_h1b.status_code == 200:
                    data_h1b = response_h1b.json()
                    case_id_h1b = data_h1b.get("case_id")
                    form_code_h1b = data_h1b.get("form_code")
                    
                    if form_code_h1b == "H-1B":
                        self.log_test(
                            "Sequential Operations - No Cross-Contamination",
                            True,
                            f"✅ H-1B case created correctly after B-1/B-2: {form_code_h1b}",
                            {"b1b2_case": case_id_b1b2, "h1b_case": case_id_h1b}
                        )
                    else:
                        self.log_test(
                            "Sequential Operations - Cross-Contamination Detected",
                            False,
                            f"❌ CROSS-CONTAMINATION BUG: H-1B case got form_code: {form_code_h1b}",
                            {"b1b2_case": case_id_b1b2, "h1b_case": case_id_h1b, "h1b_form_code": form_code_h1b}
                        )
                else:
                    self.log_test(
                        "Sequential Operations - H-1B Creation Failed",
                        False,
                        f"H-1B creation failed: {response_h1b.status_code}",
                        response_h1b.text
                    )
            else:
                self.log_test(
                    "Sequential Operations - B-1/B-2 Creation Failed",
                    False,
                    f"B-1/B-2 creation failed: {response_b1b2.status_code}",
                    response_b1b2.text
                )
        except Exception as e:
            self.log_test(
                "Sequential Operations",
                False,
                f"Exception: {str(e)}",
                None
            )
    
    def run_investigation(self):
        """Run complete form code mismatch investigation"""
        print("🚨 FORM CODE MISMATCH INVESTIGATION")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"API Base: {API_BASE}")
        print("=" * 60)
        print()
        
        # Test 1: Basic case creation
        print("📋 TESTING BASIC CASE CREATION...")
        h1b_case_id, h1b_data = self.test_auto_application_start_h1b()
        b1b2_case_id, b1b2_data = self.test_auto_application_start_b1b2()
        
        # Test 2: Case updates
        print("🔄 TESTING CASE UPDATES...")
        if h1b_case_id:
            self.test_case_update_h1b(h1b_case_id)
        
        # Test 3: Case retrieval and persistence
        print("💾 TESTING CASE PERSISTENCE...")
        if h1b_case_id:
            self.test_case_retrieval(h1b_case_id, "H-1B")
        if b1b2_case_id:
            self.test_case_retrieval(b1b2_case_id, "B-1/B-2")
        
        # Test 4: Enum validation
        print("🔤 TESTING ENUM VALIDATION...")
        self.test_enum_validation()
        
        # Test 5: Default behavior
        print("⚙️ TESTING DEFAULT BEHAVIOR...")
        self.test_default_behavior()
        
        # Test 6: Edge cases
        print("🎯 TESTING EDGE CASES...")
        self.test_edge_cases()
        
        # Test 7: Sequential operations
        print("🔄 TESTING SEQUENTIAL OPERATIONS...")
        self.test_sequential_operations()
        
        # Generate summary
        self.generate_investigation_summary()
    
    def generate_investigation_summary(self):
        """Generate investigation summary"""
        print("\n" + "=" * 60)
        print("📊 FORM CODE MISMATCH INVESTIGATION SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Identify critical issues
        critical_issues = []
        for test in self.test_results:
            if not test["success"] and "CRITICAL BUG" in test["details"]:
                critical_issues.append(test)
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"  - {issue['test']}: {issue['details']}")
            print()
        
        # Identify potential bugs
        potential_bugs = []
        for test in self.test_results:
            if not test["success"] and "POTENTIAL BUG" in test["details"]:
                potential_bugs.append(test)
        
        if potential_bugs:
            print("⚠️ POTENTIAL BUGS IDENTIFIED:")
            for bug in potential_bugs:
                print(f"  - {bug['test']}: {bug['details']}")
            print()
        
        if failed_tests > 0:
            print("❌ ALL FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['details']}")
            print()
        
        print("✅ SUCCESSFUL TESTS:")
        for test in self.test_results:
            if test["success"]:
                print(f"  - {test['test']}")
        
        print("\n" + "=" * 60)
        print("🎯 INVESTIGATION COMPLETED")
        print("=" * 60)
        
        # Save detailed results to file
        with open('/app/form_code_investigation_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Detailed results saved to: /app/form_code_investigation_results.json")

if __name__ == "__main__":
    investigator = FormCodeInvestigator()
    investigator.run_investigation()