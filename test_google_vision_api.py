#!/usr/bin/env python3
"""
Google Vision API + Dr. Miguel Hybrid System Testing
Test the real API key integration vs mock mode
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

class GoogleVisionAPITester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GoogleVisionAPITester/1.0'
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
    
    def test_google_vision_api_connectivity(self):
        """Test Google Vision API connectivity with real API key"""
        print("🔍 TESTING GOOGLE VISION API CONNECTIVITY...")
        
        # Test 1: Check API key configuration
        try:
            api_key = os.environ.get('GOOGLE_API_KEY')
            
            if api_key:
                # Validate API key format
                is_valid_format = api_key.startswith('AIza') and len(api_key) > 30
                
                self.log_test(
                    "Google Vision API Key Configuration",
                    is_valid_format,
                    f"API Key present: {api_key[:10]}...{api_key[-4:]} (length: {len(api_key)})",
                    {"api_key_configured": True, "format_valid": is_valid_format}
                )
            else:
                self.log_test(
                    "Google Vision API Key Configuration",
                    False,
                    "No GOOGLE_API_KEY found in environment",
                    {"api_key_configured": False}
                )
        except Exception as e:
            self.log_test(
                "Google Vision API Key Configuration",
                False,
                f"Exception checking API key: {str(e)}"
            )
        
        # Test 2: Direct API connectivity test
        try:
            # Create a simple test image (1x1 pixel PNG)
            test_image_data = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
            )
            encoded_content = base64.b64encode(test_image_data).decode('utf-8')
            
            api_key = os.environ.get('GOOGLE_API_KEY')
            if api_key:
                vision_endpoint = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
                
                request_data = {
                    "requests": [
                        {
                            "image": {"content": encoded_content},
                            "features": [{"type": "TEXT_DETECTION", "maxResults": 1}]
                        }
                    ]
                }
                
                response = requests.post(vision_endpoint, json=request_data, timeout=10)
                
                success = response.status_code == 200
                
                self.log_test(
                    "Google Vision API Direct Connectivity",
                    success,
                    f"HTTP {response.status_code}: {response.text[:200] if not success else 'API responding correctly'}",
                    {
                        "status_code": response.status_code,
                        "api_responding": success,
                        "endpoint": vision_endpoint[:50] + "..."
                    }
                )
            else:
                self.log_test(
                    "Google Vision API Direct Connectivity",
                    False,
                    "No API key available for testing"
                )
                
        except Exception as e:
            self.log_test(
                "Google Vision API Direct Connectivity",
                False,
                f"Exception testing API: {str(e)}"
            )
    
    def test_hybrid_system_real_vs_mock(self):
        """Test hybrid system with real API vs mock mode"""
        print("🔬 TESTING HYBRID SYSTEM - REAL API VS MOCK...")
        
        # Create a realistic passport document for testing
        passport_content = b"""
        PASSPORT
        REPUBLIC OF BRAZIL
        
        Type: P
        Country Code: BRA
        Passport No: BR987654321
        
        Surname: SANTOS
        Given Names: CARLOS EDUARDO
        Nationality: BRAZILIAN
        Date of Birth: 25 MAR 1985
        Sex: M
        Place of Birth: RIO DE JANEIRO, BRAZIL
        Date of Issue: 15 JUN 2020
        Date of Expiry: 14 JUN 2030
        Authority: DPF
        
        MRZ:
        P<BRASANTOS<<CARLOS<EDUARDO<<<<<<<<<<<<<<<<<<<<<<
        BR9876543210BRA8503259M3006145<<<<<<<<<<<<<<<<<<8
        """ * 100  # Make it larger than 50KB
        
        files = {
            'file': ('passport_carlos_santos.pdf', passport_content, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-HYBRID-REAL-API',
            'applicant_name': 'Carlos Eduardo Santos'
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                timeout=30  # Longer timeout for real API
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if real API is being used
                extracted_data = result.get('extracted_data', {})
                google_vision_data = extracted_data.get('google_vision_data', {})
                api_enabled = google_vision_data.get('api_enabled', False)
                mock_mode = google_vision_data.get('mock_mode', True)
                
                # Check quality metrics
                completeness = result.get('completeness', 0)
                ocr_confidence = google_vision_data.get('ocr_confidence', 0)
                entities_count = google_vision_data.get('entities_count', 0)
                
                # Real API should provide better results
                real_api_working = (
                    api_enabled and 
                    not mock_mode and 
                    completeness > 0 and
                    ocr_confidence > 0
                )
                
                self.log_test(
                    "Hybrid System - Real API Integration",
                    real_api_working,
                    f"API Enabled: {api_enabled}, Mock Mode: {mock_mode}, Completeness: {completeness}%, OCR: {ocr_confidence}%, Entities: {entities_count}",
                    {
                        "api_enabled": api_enabled,
                        "mock_mode": mock_mode,
                        "completeness": completeness,
                        "ocr_confidence": ocr_confidence,
                        "entities_extracted": entities_count,
                        "real_api_active": real_api_working
                    }
                )
                
                # Test performance with real API
                processing_stats = extracted_data.get('processing_stats', {})
                total_time = processing_stats.get('total_time_ms', 0)
                
                performance_acceptable = total_time < 5000  # Less than 5 seconds
                
                self.log_test(
                    "Hybrid System - Real API Performance",
                    performance_acceptable,
                    f"Processing time: {total_time}ms (target: <5000ms)",
                    {
                        "processing_time_ms": total_time,
                        "performance_target_met": performance_acceptable,
                        "google_time_ms": processing_stats.get('google_time_ms'),
                        "combined_confidence": processing_stats.get('combined_confidence')
                    }
                )
                
            else:
                self.log_test(
                    "Hybrid System - Real API Integration",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
                
        except Exception as e:
            self.log_test(
                "Hybrid System - Real API Integration",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_cost_effectiveness_real_vs_mock(self):
        """Test cost-effectiveness: $1.50/1000 docs vs mock mode"""
        print("💰 TESTING COST-EFFECTIVENESS - REAL API VS MOCK...")
        
        # Test multiple documents to simulate cost analysis
        test_documents = [
            {
                "name": "passport_test_1.pdf",
                "content": b"PASSPORT TEST DOCUMENT 1 - JOHN DOE - USA" * 100,
                "type": "passport"
            },
            {
                "name": "birth_cert_test_2.pdf", 
                "content": b"BIRTH CERTIFICATE TEST DOCUMENT 2 - JANE SMITH - CALIFORNIA" * 100,
                "type": "birth_certificate"
            },
            {
                "name": "diploma_test_3.pdf",
                "content": b"DIPLOMA TEST DOCUMENT 3 - BACHELOR OF SCIENCE - UNIVERSITY" * 100,
                "type": "education_diploma"
            }
        ]
        
        successful_analyses = 0
        total_processing_time = 0
        real_api_usage_count = 0
        
        for i, doc in enumerate(test_documents):
            try:
                files = {
                    'file': (doc["name"], doc["content"], 'application/pdf')
                }
                data = {
                    'document_type': doc["type"],
                    'visa_type': 'H-1B',
                    'case_id': f'TEST-COST-ANALYSIS-{i+1}',
                    'applicant_name': 'Test User'
                }
                
                response = requests.post(
                    f"{API_BASE}/documents/analyze-with-ai",
                    files=files,
                    data=data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    result = response.json()
                    successful_analyses += 1
                    
                    # Check if real API was used
                    extracted_data = result.get('extracted_data', {})
                    google_vision_data = extracted_data.get('google_vision_data', {})
                    
                    if google_vision_data.get('api_enabled', False) and not google_vision_data.get('mock_mode', True):
                        real_api_usage_count += 1
                    
                    # Track processing time
                    processing_stats = extracted_data.get('processing_stats', {})
                    total_processing_time += processing_stats.get('total_time_ms', 0)
                    
            except Exception as e:
                print(f"Error processing document {i+1}: {e}")
        
        # Calculate metrics
        success_rate = (successful_analyses / len(test_documents)) * 100
        avg_processing_time = total_processing_time / len(test_documents) if len(test_documents) > 0 else 0
        real_api_usage_rate = (real_api_usage_count / len(test_documents)) * 100
        
        # Estimate cost (Google Vision API pricing)
        estimated_cost_per_1000 = 1.50  # USD
        cost_per_document = estimated_cost_per_1000 / 1000
        estimated_cost = cost_per_document * real_api_usage_count
        
        cost_effectiveness_good = (
            success_rate >= 90 and  # High success rate
            avg_processing_time < 5000 and  # Reasonable processing time
            real_api_usage_rate > 0  # Real API being used
        )
        
        self.log_test(
            "Cost-Effectiveness Analysis",
            cost_effectiveness_good,
            f"Success: {success_rate:.1f}%, Avg Time: {avg_processing_time:.0f}ms, Real API: {real_api_usage_rate:.1f}%, Est. Cost: ${estimated_cost:.4f}",
            {
                "success_rate": success_rate,
                "avg_processing_time_ms": avg_processing_time,
                "real_api_usage_rate": real_api_usage_rate,
                "documents_processed": len(test_documents),
                "successful_analyses": successful_analyses,
                "estimated_cost_usd": estimated_cost,
                "cost_per_1000_docs": estimated_cost_per_1000
            }
        )
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🔬 GOOGLE VISION API + DR. MIGUEL HYBRID SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            test_name = result["test"]
            if "Google Vision API" in test_name:
                category = "Google Vision API"
            elif "Hybrid System" in test_name:
                category = "Hybrid System"
            elif "Cost-Effectiveness" in test_name:
                category = "Cost Analysis"
            else:
                category = "Other"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Print results by category
        for category, results in categories.items():
            print(f"📋 {category.upper()} RESULTS:")
            for result in results:
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {result['test']}")
                if result["details"]:
                    print(f"      {result['details']}")
            print()
        
        # Print key findings
        print("🎯 KEY FINDINGS:")
        
        # Check if real API is working
        real_api_tests = [t for t in self.test_results if "Real API" in t["test"]]
        if real_api_tests:
            real_api_working = any(t["success"] for t in real_api_tests)
            if real_api_working:
                print("   ✅ Google Vision API real key is working")
            else:
                print("   ❌ Google Vision API real key has issues")
        
        # Check hybrid system status
        hybrid_tests = [t for t in self.test_results if "Hybrid System" in t["test"]]
        if hybrid_tests:
            hybrid_working = any(t["success"] for t in hybrid_tests)
            if hybrid_working:
                print("   ✅ Hybrid system is operational")
            else:
                print("   ❌ Hybrid system needs attention")
        
        # Check cost effectiveness
        cost_tests = [t for t in self.test_results if "Cost-Effectiveness" in t["test"]]
        if cost_tests:
            cost_effective = any(t["success"] for t in cost_tests)
            if cost_effective:
                print("   ✅ Cost-effectiveness targets met")
            else:
                print("   ❌ Cost-effectiveness needs improvement")
        
        print("\n" + "=" * 80)
    
    def run_all_tests(self):
        """Run all Google Vision API tests"""
        print("🚀 STARTING GOOGLE VISION API + DR. MIGUEL HYBRID SYSTEM TESTING")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"🔗 API Base: {API_BASE}")
        print("=" * 80)
        
        # Run all tests
        self.test_google_vision_api_connectivity()
        self.test_hybrid_system_real_vs_mock()
        self.test_cost_effectiveness_real_vs_mock()
        
        # Print summary
        self.print_test_summary()

if __name__ == "__main__":
    tester = GoogleVisionAPITester()
    tester.run_all_tests()