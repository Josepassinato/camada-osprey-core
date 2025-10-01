#!/usr/bin/env python3
"""
CRITICAL DOCUMENT SECURITY INVESTIGATION
Testing document validation system for security vulnerabilities reported by user
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

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://iaimmigration.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DocumentSecurityTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DocumentSecurityTester/1.0'
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
        """Setup authentication for testing"""
        try:
            # Try to create a test user
            test_user_data = {
                "email": "security@test.com",
                "password": "securitytest123",
                "first_name": "Security",
                "last_name": "Tester"
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

    def create_fake_document(self, document_type: str, content: str, size_kb: int = 100) -> bytes:
        """Create a fake document for testing"""
        # Create content that looks like a document but isn't the expected type
        fake_content = f"""
FAKE {document_type.upper()} DOCUMENT - FOR TESTING ONLY
This is not a real {document_type}
Content: {content}
Name: John Doe (NOT the applicant)
Date: {datetime.now().strftime('%Y-%m-%d')}
Document Type: {document_type}
""" + "X" * (size_kb * 1024 - len(content) - 200)  # Pad to desired size
        
        return fake_content.encode('utf-8')

    def test_wrong_document_type_validation(self):
        """Test 1: Document type validation - Upload non-passport as passport"""
        print("🚨 CRITICAL TEST 1: Wrong Document Type Validation")
        
        # Create a fake birth certificate but claim it's a passport
        fake_birth_cert = self.create_fake_document(
            "BIRTH_CERTIFICATE", 
            "This is actually a birth certificate, not a passport. Should be REJECTED.",
            150
        )
        
        files = {
            'file': ('fake_passport.pdf', fake_birth_cert, 'application/pdf')
        }
        data = {
            'document_type': 'passport',  # Claiming it's a passport
            'visa_type': 'H-1B',
            'case_id': 'TEST-SECURITY-WRONG-TYPE'
        }
        
        try:
            # Remove Content-Type header for multipart form data
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if system correctly identified wrong document type
                dr_miguel_validation = result.get('dr_miguel_validation', {})
                ai_analysis = result.get('ai_analysis', {})
                policy_engine = result.get('policy_engine', {})
                
                # Look for rejection indicators
                verdict = dr_miguel_validation.get('verdict', '')
                type_correct = dr_miguel_validation.get('type_correct', True)
                uscis_acceptable = dr_miguel_validation.get('uscis_acceptable', True)
                completeness_score = result.get('completeness_score', 100)
                
                # System should REJECT wrong document type
                should_reject = (
                    verdict == 'REJEITADO' or 
                    type_correct == False or 
                    uscis_acceptable == False or
                    completeness_score < 50
                )
                
                self.log_test(
                    "CRITICAL: Wrong Document Type Detection",
                    should_reject,
                    f"Verdict: {verdict}, Type Correct: {type_correct}, USCIS Acceptable: {uscis_acceptable}, Score: {completeness_score}",
                    {
                        "verdict": verdict,
                        "type_correct": type_correct,
                        "uscis_acceptable": uscis_acceptable,
                        "completeness_score": completeness_score,
                        "should_be_rejected": True,
                        "actually_rejected": should_reject
                    }
                )
                
                # If system approved wrong document type, this is CRITICAL SECURITY ISSUE
                if not should_reject:
                    self.log_test(
                        "🚨 CRITICAL SECURITY VULNERABILITY",
                        False,
                        f"System APPROVED wrong document type with score {completeness_score}% - This is the reported security issue!",
                        {
                            "security_issue": "CONFIRMED",
                            "issue_type": "Wrong document type approved",
                            "expected_behavior": "REJECT non-passport documents",
                            "actual_behavior": f"APPROVED with {completeness_score}%",
                            "risk_level": "CRITICAL"
                        }
                    )
                
            else:
                self.log_test(
                    "Wrong Document Type Detection",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Wrong Document Type Detection",
                False,
                f"Exception: {str(e)}"
            )

    def test_wrong_person_document_validation(self):
        """Test 2: Identity validation - Document belonging to different person"""
        print("🚨 CRITICAL TEST 2: Wrong Person Document Validation")
        
        # Create a document that clearly belongs to someone else
        fake_passport = self.create_fake_document(
            "PASSPORT", 
            """
PASSPORT DOCUMENT
Name: MARIA SILVA (NOT THE APPLICANT)
Passport Number: BR123456789
Date of Birth: 1990-01-01
This document belongs to Maria Silva, not the current applicant.
The system should detect this identity mismatch and REJECT.
""",
            200
        )
        
        files = {
            'file': ('wrong_person_passport.pdf', fake_passport, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-SECURITY-WRONG-PERSON',
            'applicant_name': 'CARLOS SANTOS'  # Different from document name
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if system detected identity mismatch
                dr_miguel_validation = result.get('dr_miguel_validation', {})
                belongs_to_applicant = dr_miguel_validation.get('belongs_to_applicant', True)
                name_validation = dr_miguel_validation.get('name_validation', 'approved')
                verdict = dr_miguel_validation.get('verdict', '')
                completeness_score = result.get('completeness_score', 100)
                
                # System should REJECT document from different person
                should_reject = (
                    belongs_to_applicant == False or
                    name_validation == 'rejected' or
                    verdict == 'REJEITADO' or
                    completeness_score < 50
                )
                
                self.log_test(
                    "CRITICAL: Wrong Person Document Detection",
                    should_reject,
                    f"Belongs to Applicant: {belongs_to_applicant}, Name Validation: {name_validation}, Verdict: {verdict}, Score: {completeness_score}",
                    {
                        "belongs_to_applicant": belongs_to_applicant,
                        "name_validation": name_validation,
                        "verdict": verdict,
                        "completeness_score": completeness_score,
                        "should_be_rejected": True,
                        "actually_rejected": should_reject
                    }
                )
                
                # If system approved document from different person, CRITICAL ISSUE
                if not should_reject:
                    self.log_test(
                        "🚨 CRITICAL IDENTITY SECURITY VULNERABILITY",
                        False,
                        f"System APPROVED document from different person with score {completeness_score}% - MAJOR SECURITY BREACH!",
                        {
                            "security_issue": "CONFIRMED",
                            "issue_type": "Document from different person approved",
                            "expected_behavior": "REJECT documents not belonging to applicant",
                            "actual_behavior": f"APPROVED with {completeness_score}%",
                            "risk_level": "CRITICAL"
                        }
                    )
                
            else:
                self.log_test(
                    "Wrong Person Document Detection",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Wrong Person Document Detection",
                False,
                f"Exception: {str(e)}"
            )

    def test_low_quality_document_validation(self):
        """Test 3: Quality validation - Low quality/illegible documents"""
        print("🚨 CRITICAL TEST 3: Low Quality Document Validation")
        
        # Create a very low quality document
        low_quality_doc = self.create_fake_document(
            "PASSPORT", 
            """
BLURRY ILLEGIBLE PASSPORT
[UNREADABLE TEXT] ████ ████ ████
[CORRUPTED DATA] ░░░░ ░░░░ ░░░░
Quality: VERY POOR - Should be REJECTED
Text is barely readable, image is blurry
This document should fail quality checks
""",
            80  # Smaller size to simulate poor quality
        )
        
        files = {
            'file': ('low_quality_passport.pdf', low_quality_doc, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-SECURITY-LOW-QUALITY'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check quality analysis
                quality_analysis = result.get('quality_analysis', {})
                quality_issues = result.get('quality_issues', [])
                completeness_score = result.get('completeness_score', 100)
                validity_status = result.get('validity_status', 'valid')
                
                # System should detect quality issues
                has_quality_issues = (
                    len(quality_issues) > 0 or
                    completeness_score < 70 or
                    validity_status in ['invalid', 'unclear']
                )
                
                self.log_test(
                    "CRITICAL: Low Quality Document Detection",
                    has_quality_issues,
                    f"Quality Issues: {len(quality_issues)}, Score: {completeness_score}, Validity: {validity_status}",
                    {
                        "quality_issues": quality_issues,
                        "completeness_score": completeness_score,
                        "validity_status": validity_status,
                        "should_have_issues": True,
                        "actually_has_issues": has_quality_issues
                    }
                )
                
            else:
                self.log_test(
                    "Low Quality Document Detection",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Low Quality Document Detection",
                False,
                f"Exception: {str(e)}"
            )

    def test_dr_miguel_validation_system(self):
        """Test 4: Dr. Miguel validation system functionality"""
        print("🚨 CRITICAL TEST 4: Dr. Miguel Validation System")
        
        # Test with a document that should trigger multiple validation failures
        suspicious_doc = self.create_fake_document(
            "DRIVER_LICENSE", 
            """
DRIVER'S LICENSE (NOT PASSPORT!)
Name: FAKE PERSON
License Number: DL123456
This is clearly NOT a passport document
Dr. Miguel should detect this immediately
Type: DRIVER LICENSE
Expected Document: PASSPORT
Mismatch: CRITICAL
""",
            120
        )
        
        files = {
            'file': ('suspicious_document.pdf', suspicious_doc, 'application/pdf')
        }
        data = {
            'document_type': 'passport',  # Claiming it's passport
            'visa_type': 'H-1B',
            'case_id': 'TEST-DR-MIGUEL-VALIDATION'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check Dr. Miguel specific validation
                dr_miguel_validation = result.get('dr_miguel_validation', {})
                ai_analysis = result.get('ai_analysis', {})
                
                # Dr. Miguel should be working
                dr_miguel_working = bool(dr_miguel_validation or ai_analysis)
                
                if dr_miguel_working:
                    document_type_identified = dr_miguel_validation.get('document_type_identified', '')
                    type_correct = dr_miguel_validation.get('type_correct', True)
                    verdict = dr_miguel_validation.get('verdict', '')
                    critical_issues = dr_miguel_validation.get('critical_issues', [])
                    
                    # Dr. Miguel should detect the mismatch
                    dr_miguel_detected_issue = (
                        type_correct == False or
                        verdict == 'REJEITADO' or
                        len(critical_issues) > 0 or
                        'driver' in document_type_identified.lower()
                    )
                    
                    self.log_test(
                        "CRITICAL: Dr. Miguel Validation Working",
                        dr_miguel_detected_issue,
                        f"Type Identified: {document_type_identified}, Type Correct: {type_correct}, Verdict: {verdict}, Issues: {len(critical_issues)}",
                        {
                            "dr_miguel_working": True,
                            "document_type_identified": document_type_identified,
                            "type_correct": type_correct,
                            "verdict": verdict,
                            "critical_issues": critical_issues,
                            "detected_mismatch": dr_miguel_detected_issue
                        }
                    )
                else:
                    self.log_test(
                        "CRITICAL: Dr. Miguel Validation Working",
                        False,
                        "Dr. Miguel validation system not responding or not integrated",
                        {
                            "dr_miguel_working": False,
                            "dr_miguel_validation_present": bool(dr_miguel_validation),
                            "ai_analysis_present": bool(ai_analysis),
                            "issue": "Dr. Miguel not functioning"
                        }
                    )
                
            else:
                self.log_test(
                    "Dr. Miguel Validation System",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Dr. Miguel Validation System",
                False,
                f"Exception: {str(e)}"
            )

    def test_policy_engine_validation(self):
        """Test 5: Policy Engine validation rules"""
        print("🚨 CRITICAL TEST 5: Policy Engine Validation Rules")
        
        # Test document that should fail policy validation
        policy_test_doc = self.create_fake_document(
            "EXPIRED_PASSPORT", 
            """
EXPIRED PASSPORT DOCUMENT
Name: Test User
Passport Number: EX123456789
Issue Date: 2015-01-01
Expiry Date: 2020-01-01 (EXPIRED!)
Status: EXPIRED - Should be REJECTED
This passport expired in 2020 and should not be accepted
""",
            150
        )
        
        files = {
            'file': ('expired_passport.pdf', policy_test_doc, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-POLICY-ENGINE-VALIDATION'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check Policy Engine components
                policy_engine = result.get('policy_engine', {})
                policy_score = result.get('policy_score', 1.0)
                policy_decision = result.get('policy_decision', 'PASS')
                
                # Check for expiration detection
                expiration_warnings = result.get('expiration_warnings', [])
                validity_status = result.get('validity_status', 'valid')
                
                # Policy Engine should detect issues
                policy_detected_issues = (
                    policy_decision in ['FAIL', 'ALERT'] or
                    policy_score < 0.5 or
                    len(expiration_warnings) > 0 or
                    validity_status in ['expired', 'invalid']
                )
                
                self.log_test(
                    "CRITICAL: Policy Engine Validation Rules",
                    policy_detected_issues,
                    f"Policy Decision: {policy_decision}, Score: {policy_score}, Validity: {validity_status}, Warnings: {len(expiration_warnings)}",
                    {
                        "policy_engine_present": bool(policy_engine),
                        "policy_decision": policy_decision,
                        "policy_score": policy_score,
                        "validity_status": validity_status,
                        "expiration_warnings": expiration_warnings,
                        "detected_issues": policy_detected_issues
                    }
                )
                
            else:
                self.log_test(
                    "Policy Engine Validation Rules",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Policy Engine Validation Rules",
                False,
                f"Exception: {str(e)}"
            )

    def test_confidence_scoring_thresholds(self):
        """Test 6: Confidence scoring and approval thresholds"""
        print("🚨 CRITICAL TEST 6: Confidence Scoring and Thresholds")
        
        # Test with clearly inadequate document
        inadequate_doc = self.create_fake_document(
            "RANDOM_PAPER", 
            """
RANDOM DOCUMENT - NOT OFFICIAL
This is just a random piece of paper
No official seals, no government authority
Not a passport, not any official document
Should receive very low confidence score
Confidence should be < 50%
""",
            90
        )
        
        files = {
            'file': ('random_document.pdf', inadequate_doc, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-CONFIDENCE-SCORING'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check confidence/completeness scoring
                completeness_score = result.get('completeness_score', 100)
                policy_score = result.get('policy_score', 1.0)
                
                # Convert policy_score to percentage if it's 0-1 scale
                if isinstance(policy_score, float) and policy_score <= 1.0:
                    policy_score_pct = policy_score * 100
                else:
                    policy_score_pct = policy_score
                
                # Check if system properly assigns low scores to inadequate documents
                low_confidence_detected = (
                    completeness_score < 70 or
                    policy_score_pct < 70
                )
                
                # CRITICAL: Check if system incorrectly gives high score (like the reported 85%)
                high_score_issue = (
                    completeness_score >= 85 or
                    policy_score_pct >= 85
                )
                
                self.log_test(
                    "CRITICAL: Confidence Scoring Accuracy",
                    low_confidence_detected and not high_score_issue,
                    f"Completeness: {completeness_score}%, Policy: {policy_score_pct}%, Low confidence detected: {low_confidence_detected}, High score issue: {high_score_issue}",
                    {
                        "completeness_score": completeness_score,
                        "policy_score": policy_score,
                        "policy_score_percentage": policy_score_pct,
                        "low_confidence_detected": low_confidence_detected,
                        "high_score_issue": high_score_issue,
                        "threshold_working": low_confidence_detected
                    }
                )
                
                # If system gives high score to inadequate document, this confirms the bug
                if high_score_issue:
                    self.log_test(
                        "🚨 CRITICAL SCORING VULNERABILITY CONFIRMED",
                        False,
                        f"System gave HIGH SCORE ({max(completeness_score, policy_score_pct)}%) to inadequate document - This confirms the reported 85% approval bug!",
                        {
                            "security_issue": "CONFIRMED",
                            "issue_type": "High confidence score for inadequate document",
                            "expected_behavior": "Low score (<50%) for random/inadequate documents",
                            "actual_behavior": f"High score ({max(completeness_score, policy_score_pct)}%)",
                            "risk_level": "CRITICAL",
                            "matches_user_report": True
                        }
                    )
                
            else:
                self.log_test(
                    "Confidence Scoring Thresholds",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Confidence Scoring Thresholds",
                False,
                f"Exception: {str(e)}"
            )

    def test_comprehensive_security_validation(self):
        """Test 7: Comprehensive security validation with multiple issues"""
        print("🚨 CRITICAL TEST 7: Comprehensive Security Validation")
        
        # Create document with MULTIPLE security issues
        multi_issue_doc = self.create_fake_document(
            "FAKE_DOCUMENT", 
            """
MULTIPLE SECURITY ISSUES DOCUMENT
1. WRONG TYPE: This is a birth certificate, not passport
2. WRONG PERSON: Belongs to Maria Santos, not applicant
3. EXPIRED: Document expired in 2019
4. LOW QUALITY: Blurry, illegible text
5. SUSPICIOUS: Contains fake information
6. NOT OFFICIAL: No government seals or authority

Name: MARIA SANTOS (DIFFERENT PERSON)
Document Type: BIRTH CERTIFICATE (NOT PASSPORT)
Expiry: 2019-01-01 (EXPIRED)
Quality: POOR/ILLEGIBLE
Authority: NONE (FAKE)

This document should be IMMEDIATELY REJECTED on multiple grounds.
""",
            180
        )
        
        files = {
            'file': ('multi_issue_document.pdf', multi_issue_doc, 'application/pdf')
        }
        data = {
            'document_type': 'passport',  # Wrong claim
            'visa_type': 'H-1B',
            'case_id': 'TEST-COMPREHENSIVE-SECURITY',
            'applicant_name': 'CARLOS SILVA'  # Different from document
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Comprehensive validation check
                dr_miguel_validation = result.get('dr_miguel_validation', {})
                completeness_score = result.get('completeness_score', 100)
                validity_status = result.get('validity_status', 'valid')
                quality_issues = result.get('quality_issues', [])
                critical_issues = dr_miguel_validation.get('critical_issues', [])
                verdict = dr_miguel_validation.get('verdict', '')
                
                # Count detected issues
                issues_detected = 0
                issue_details = []
                
                if verdict == 'REJEITADO':
                    issues_detected += 1
                    issue_details.append("Verdict: REJECTED")
                
                if completeness_score < 50:
                    issues_detected += 1
                    issue_details.append(f"Low score: {completeness_score}%")
                
                if validity_status in ['invalid', 'expired', 'unclear']:
                    issues_detected += 1
                    issue_details.append(f"Invalid status: {validity_status}")
                
                if len(quality_issues) > 0:
                    issues_detected += 1
                    issue_details.append(f"Quality issues: {len(quality_issues)}")
                
                if len(critical_issues) > 0:
                    issues_detected += 1
                    issue_details.append(f"Critical issues: {len(critical_issues)}")
                
                # System should detect multiple issues (at least 3 out of 6)
                comprehensive_validation_working = issues_detected >= 3
                
                self.log_test(
                    "CRITICAL: Comprehensive Security Validation",
                    comprehensive_validation_working,
                    f"Detected {issues_detected}/6 expected issues: {', '.join(issue_details)}",
                    {
                        "issues_detected": issues_detected,
                        "expected_issues": 6,
                        "issue_details": issue_details,
                        "completeness_score": completeness_score,
                        "validity_status": validity_status,
                        "verdict": verdict,
                        "comprehensive_working": comprehensive_validation_working
                    }
                )
                
                # Final security assessment
                if completeness_score >= 85:
                    self.log_test(
                        "🚨 FINAL SECURITY ASSESSMENT: CRITICAL VULNERABILITY",
                        False,
                        f"System APPROVED document with multiple security issues at {completeness_score}% - SECURITY SYSTEM COMPROMISED!",
                        {
                            "final_assessment": "CRITICAL SECURITY FAILURE",
                            "approval_score": completeness_score,
                            "security_issues_ignored": 6 - issues_detected,
                            "system_status": "COMPROMISED",
                            "immediate_action_required": True
                        }
                    )
                else:
                    self.log_test(
                        "✅ FINAL SECURITY ASSESSMENT: System Working",
                        True,
                        f"System correctly identified security issues and gave low score: {completeness_score}%",
                        {
                            "final_assessment": "SECURITY SYSTEM WORKING",
                            "approval_score": completeness_score,
                            "security_issues_detected": issues_detected,
                            "system_status": "SECURE"
                        }
                    )
                
            else:
                self.log_test(
                    "Comprehensive Security Validation",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Comprehensive Security Validation",
                False,
                f"Exception: {str(e)}"
            )

    def run_all_security_tests(self):
        """Run all security tests"""
        print("🚨 STARTING CRITICAL DOCUMENT SECURITY INVESTIGATION")
        print("=" * 80)
        print("INVESTIGATING: System incorrectly approving inadequate documents with 85% confidence")
        print("REPORTED ISSUE: Non-passport document from different person was approved")
        print("=" * 80)
        print()
        
        # Run all security tests
        self.test_wrong_document_type_validation()
        self.test_wrong_person_document_validation()
        self.test_low_quality_document_validation()
        self.test_dr_miguel_validation_system()
        self.test_policy_engine_validation()
        self.test_confidence_scoring_thresholds()
        self.test_comprehensive_security_validation()
        
        # Generate summary
        self.generate_security_summary()

    def generate_security_summary(self):
        """Generate comprehensive security test summary"""
        print("\n" + "=" * 80)
        print("🚨 CRITICAL DOCUMENT SECURITY INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Security Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Critical findings
        critical_issues = []
        security_vulnerabilities = []
        
        for result in self.test_results:
            if not result['success']:
                if 'CRITICAL' in result['test'] or 'SECURITY' in result['test']:
                    critical_issues.append(result)
                if 'VULNERABILITY' in result['test']:
                    security_vulnerabilities.append(result)
        
        if critical_issues:
            print("🚨 CRITICAL SECURITY ISSUES FOUND:")
            for issue in critical_issues:
                print(f"   ❌ {issue['test']}: {issue['details']}")
            print()
        
        if security_vulnerabilities:
            print("🚨 CONFIRMED SECURITY VULNERABILITIES:")
            for vuln in security_vulnerabilities:
                print(f"   ⚠️ {vuln['test']}: {vuln['details']}")
            print()
        
        # Recommendations
        print("🔧 SECURITY RECOMMENDATIONS:")
        if failed_tests > 0:
            print("   1. IMMEDIATE: Fix document type validation - reject non-passport documents")
            print("   2. URGENT: Implement identity validation - reject documents from different persons")
            print("   3. CRITICAL: Fix confidence scoring - inadequate documents should score <50%")
            print("   4. ESSENTIAL: Enhance Dr. Miguel validation rules")
            print("   5. REQUIRED: Strengthen Policy Engine validation policies")
        else:
            print("   ✅ All security tests passed - system appears secure")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    tester = DocumentSecurityTester()
    tester.run_all_security_tests()