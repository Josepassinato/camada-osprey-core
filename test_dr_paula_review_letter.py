#!/usr/bin/env python3
"""
SPECIFIC TEST: Dr. Paula Review Letter Endpoint - JSON Parsing Bug Fix Validation
Tests the /api/llm/dr-paula/review-letter endpoint for the reported JSON parsing issues
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://owlagent.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DrPaulaReviewLetterTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DrPaulaReviewLetterTester/1.0'
        })
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: any = None):
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
    
    def test_review_letter_empty_short(self):
        """Test empty and very short letters that might cause JSON issues"""
        print("📝 Testing Empty/Short Letters...")
        
        test_cases = [
            {"letter": "", "description": "Empty letter"},
            {"letter": "Hi", "description": "Very short letter"},
            {"letter": "I want visa.", "description": "Minimal letter"},
            {"letter": "   ", "description": "Whitespace only"}
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "visa_type": "H1B",
                    "applicant_letter": case["letter"]
                }
                
                response = self.session.post(
                    f"{API_BASE}/llm/dr-paula/review-letter",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify JSON structure is always valid
                    has_review = 'review' in data
                    has_success = 'success' in data
                    
                    if has_review:
                        review = data['review']
                        has_coverage_score = 'coverage_score' in review
                        has_status = 'status' in review
                        has_valid_score = isinstance(review.get('coverage_score'), (int, float))
                        
                        success = has_review and has_coverage_score and has_status and has_valid_score
                        
                        self.log_test(
                            f"Review Letter - {case['description']}",
                            success,
                            f"JSON valid: {success}, Status: {review.get('status')}, Score: {review.get('coverage_score')}",
                            {
                                "test_case": case["description"],
                                "json_structure_valid": success,
                                "response_structure": list(data.keys())
                            }
                        )
                    else:
                        # Check if it's an error response (acceptable for empty letters)
                        has_error = 'error' in data
                        success = has_error and has_success
                        
                        self.log_test(
                            f"Review Letter - {case['description']}",
                            success,
                            f"Proper error handling: {data.get('error', 'No error message')}",
                            {"error_response": success}
                        )
                else:
                    self.log_test(
                        f"Review Letter - {case['description']}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_test(
                    f"Review Letter - {case['description']}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_review_letter_special_characters(self):
        """Test letters with special characters that might break JSON parsing"""
        print("📝 Testing Special Characters...")
        
        test_cases = [
            {
                "letter": 'Minha carta tem "aspas" e \'apostrofes\' e caracteres especiais: ç, ã, õ, é, à.',
                "description": "Portuguese with quotes and accents"
            },
            {
                "letter": "Letter with JSON-breaking chars: {}, [], \", \\, \n, \t, and unicode: 你好, مرحبا",
                "description": "JSON-breaking characters"
            },
            {
                "letter": "Letter with\nmultiple\nlines\nand\ttabs\tand\rcarriage\rreturns",
                "description": "Multiline with control characters"
            }
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "visa_type": "H1B",
                    "applicant_letter": case["letter"]
                }
                
                response = self.session.post(
                    f"{API_BASE}/llm/dr-paula/review-letter",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify JSON structure is valid despite special characters
                    has_review = 'review' in data
                    
                    if has_review:
                        review = data['review']
                        has_valid_structure = all(key in review for key in ['coverage_score', 'status'])
                        
                        self.log_test(
                            f"Review Letter - {case['description']}",
                            has_valid_structure,
                            f"JSON parsed successfully with special chars, Status: {review.get('status')}",
                            {
                                "special_chars_handled": has_valid_structure,
                                "coverage_score": review.get('coverage_score')
                            }
                        )
                    else:
                        self.log_test(
                            f"Review Letter - {case['description']}",
                            'error' in data,
                            f"Error response: {data.get('error', 'No error')}"
                        )
                else:
                    self.log_test(
                        f"Review Letter - {case['description']}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_test(
                    f"Review Letter - {case['description']}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_review_letter_uncommon_visa_types(self):
        """Test uncommon visa types that might cause AI to return non-JSON"""
        print("📝 Testing Uncommon Visa Types...")
        
        test_cases = [
            {
                "visa_type": "I-589",
                "letter": "I am seeking asylum in the United States due to persecution in my home country. I fear for my safety and that of my family.",
                "description": "I-589 Asylum case"
            },
            {
                "visa_type": "O-1",
                "letter": "I am an artist with extraordinary ability. I have won several international awards and have been featured in major publications.",
                "description": "O-1 Extraordinary ability"
            },
            {
                "visa_type": "EB-5",
                "letter": "I am investing $1.8 million in a new commercial enterprise that will create jobs for US workers.",
                "description": "EB-5 Investor visa"
            }
        ]
        
        for case in test_cases:
            try:
                payload = {
                    "visa_type": case["visa_type"],
                    "applicant_letter": case["letter"]
                }
                
                response = self.session.post(
                    f"{API_BASE}/llm/dr-paula/review-letter",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify JSON structure for uncommon visa types
                    has_review = 'review' in data
                    
                    if has_review:
                        review = data['review']
                        correct_visa_type = review.get('visa_type') == case["visa_type"]
                        has_valid_structure = all(key in review for key in ['coverage_score', 'status'])
                        
                        success = has_valid_structure and correct_visa_type
                        
                        self.log_test(
                            f"Review Letter - {case['description']}",
                            success,
                            f"Visa type: {review.get('visa_type')}, Status: {review.get('status')}, Score: {review.get('coverage_score')}",
                            {
                                "visa_type_correct": correct_visa_type,
                                "json_structure_valid": has_valid_structure
                            }
                        )
                    else:
                        self.log_test(
                            f"Review Letter - {case['description']}",
                            'error' in data,
                            f"Error response: {data.get('error', 'No error')}"
                        )
                else:
                    self.log_test(
                        f"Review Letter - {case['description']}",
                        False,
                        f"HTTP {response.status_code}",
                        response.text[:200]
                    )
            except Exception as e:
                self.log_test(
                    f"Review Letter - {case['description']}",
                    False,
                    f"Exception: {str(e)}"
                )
    
    def test_review_letter_json_structure(self):
        """Test that JSON structure is always valid and contains required fields"""
        print("📝 Testing JSON Structure Validation...")
        
        payload = {
            "visa_type": "H1B",
            "applicant_letter": "I am applying for an H-1B visa. I have a computer science degree and 5 years of experience."
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/llm/dr-paula/review-letter",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                required_top_level = ['success', 'agent', 'timestamp']
                has_top_level = all(key in data for key in required_top_level)
                
                # Check review structure
                has_review = 'review' in data
                review_valid = False
                
                if has_review:
                    review = data['review']
                    required_review_fields = ['visa_type', 'coverage_score', 'status']
                    review_valid = all(key in review for key in required_review_fields)
                    
                    # Validate data types
                    coverage_score = review.get('coverage_score')
                    status = review.get('status')
                    
                    score_valid = isinstance(coverage_score, (int, float)) and 0 <= coverage_score <= 1
                    status_valid = status in ['needs_questions', 'complete', 'ready_for_formatting', 'needs_review']
                    
                    # Check questions array if status is needs_questions
                    questions_valid = True
                    if status == 'needs_questions':
                        questions = review.get('questions', [])
                        questions_valid = isinstance(questions, list)
                        if questions:
                            # Check first question structure
                            first_q = questions[0]
                            questions_valid = all(key in first_q for key in ['id', 'question', 'category'])
                    
                    structure_valid = review_valid and score_valid and status_valid and questions_valid
                    
                    self.log_test(
                        "Review Letter - JSON Structure Validation",
                        structure_valid,
                        f"Structure valid: {structure_valid}, Score: {coverage_score}, Status: {status}",
                        {
                            "top_level_valid": has_top_level,
                            "review_valid": review_valid,
                            "score_valid": score_valid,
                            "status_valid": status_valid,
                            "questions_valid": questions_valid,
                            "response_keys": list(data.keys()),
                            "review_keys": list(review.keys()) if has_review else []
                        }
                    )
                else:
                    # Check if it's a valid error response
                    has_error = 'error' in data
                    self.log_test(
                        "Review Letter - JSON Structure Validation",
                        has_error and has_top_level,
                        f"Valid error response structure: {data.get('error', 'No error')}"
                    )
            else:
                self.log_test(
                    "Review Letter - JSON Structure Validation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test(
                "Review Letter - JSON Structure Validation",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_review_letter_fallback_system(self):
        """Test that fallback system works when AI returns invalid JSON"""
        print("📝 Testing Fallback System...")
        
        # Test with a letter that might confuse the AI
        confusing_letter = """
        {This is not JSON but looks like it}
        "I want to apply for visa": true,
        [This might break JSON parsing]
        My experience includes: {"years": 5, "invalid": json}
        """
        
        try:
            payload = {
                "visa_type": "H1B",
                "applicant_letter": confusing_letter
            }
            
            response = self.session.post(
                f"{API_BASE}/llm/dr-paula/review-letter",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # System should ALWAYS return valid JSON, even with fallback
                has_review = 'review' in data
                
                if has_review:
                    review = data['review']
                    has_fallback_indicators = any(key in review for key in ['ai_note', 'error_note', 'raw_response'])
                    has_valid_structure = all(key in review for key in ['coverage_score', 'status'])
                    
                    # Fallback should provide reasonable defaults
                    coverage_score = review.get('coverage_score', 0)
                    status = review.get('status', '')
                    
                    fallback_working = (
                        has_valid_structure and
                        isinstance(coverage_score, (int, float)) and
                        status in ['needs_questions', 'complete', 'ready_for_formatting', 'needs_review']
                    )
                    
                    self.log_test(
                        "Review Letter - Fallback System",
                        fallback_working,
                        f"Fallback working: {fallback_working}, Has indicators: {has_fallback_indicators}, Score: {coverage_score}",
                        {
                            "fallback_working": fallback_working,
                            "has_fallback_indicators": has_fallback_indicators,
                            "coverage_score": coverage_score,
                            "status": status
                        }
                    )
                else:
                    self.log_test(
                        "Review Letter - Fallback System",
                        'error' in data,
                        f"Error response: {data.get('error', 'No error')}"
                    )
            else:
                self.log_test(
                    "Review Letter - Fallback System",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test(
                "Review Letter - Fallback System",
                False,
                f"Exception: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all Dr. Paula review letter tests"""
        print("🔍 TESTING DR. PAULA REVIEW-LETTER ENDPOINT - JSON PARSING BUG FIX...")
        print("=" * 80)
        print()
        
        # Test 1: Empty/Very Short Letter (Edge Case)
        self.test_review_letter_empty_short()
        
        # Test 2: Letter with Special Characters
        self.test_review_letter_special_characters()
        
        # Test 3: Uncommon Visa Types (I-589, O-1)
        self.test_review_letter_uncommon_visa_types()
        
        # Test 4: JSON Structure Validation
        self.test_review_letter_json_structure()
        
        # Test 5: Fallback System Testing
        self.test_review_letter_fallback_system()
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\n📊 DR. PAULA REVIEW LETTER TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  - {test['test']}: {test['details']}")
            print()
        
        # Show critical findings
        print("🔍 CRITICAL FINDINGS:")
        json_parsing_issues = 0
        fallback_working = 0
        structure_valid = 0
        
        for test in self.test_results:
            if "JSON" in test['test'] and test['success']:
                structure_valid += 1
            if "Fallback" in test['test'] and test['success']:
                fallback_working += 1
            if not test['success'] and ("JSON" in test['details'] or "parsing" in test['details']):
                json_parsing_issues += 1
        
        print(f"  - JSON Structure Valid: {structure_valid} tests")
        print(f"  - Fallback System Working: {fallback_working} tests")
        print(f"  - JSON Parsing Issues: {json_parsing_issues} tests")
        print()
        
        # Final verdict
        if json_parsing_issues == 0 and passed_tests >= total_tests * 0.8:
            print("✅ VERDICT: JSON parsing bug appears to be RESOLVED")
            print("   System handles edge cases and provides proper fallbacks")
        else:
            print("❌ VERDICT: JSON parsing issues still present")
            print("   Further investigation and fixes needed")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = DrPaulaReviewLetterTester()
    tester.run_all_tests()