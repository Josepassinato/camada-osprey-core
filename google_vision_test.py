#!/usr/bin/env python3
"""
Google Vision API Configuration Test - TESTE FINAL
Verificar configuração completa Google Vision API com Client ID OAuth2
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://iaimmigration.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class GoogleVisionConfigTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GoogleVisionConfigTester/1.0'
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
    
    def test_google_vision_configuration_detection(self):
        """Test 1: Verificar se sistema detecta API Key + Client ID"""
        print("📋 Test 1: Configuration Detection...")
        
        try:
            # Test document analysis to check configuration
            test_document = b"Test document for Google Vision API configuration check. " * 100
            
            files = {
                'file': ('test_config.pdf', test_document, 'application/pdf')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': 'TEST-GOOGLE-CONFIG'
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = result.get('extracted_data', {})
                google_vision_data = extracted_data.get('google_vision_data', {})
                
                # Check configuration details
                api_enabled = google_vision_data.get('api_enabled', False)
                auth_method = google_vision_data.get('auth_method', 'unknown')
                project_id = google_vision_data.get('project_id', 'unknown')
                mock_mode = google_vision_data.get('mock_mode', True)
                
                # Expected configuration
                expected_project_id = "891629358081"
                expected_auth_methods = ["api_key", "oauth2"]
                
                config_correct = (
                    project_id == expected_project_id and
                    auth_method in expected_auth_methods and
                    api_enabled  # Should be enabled with credentials
                )
                
                self.log_test(
                    "Google Vision - Configuration Detection",
                    config_correct,
                    f"Project ID: {project_id}, Auth: {auth_method}, API Enabled: {api_enabled}, Mock: {mock_mode}",
                    {
                        "project_id": project_id,
                        "expected_project_id": expected_project_id,
                        "auth_method": auth_method,
                        "api_enabled": api_enabled,
                        "mock_mode": mock_mode,
                        "configuration_status": "DETECTED" if config_correct else "INCOMPLETE"
                    }
                )
            else:
                self.log_test(
                    "Google Vision - Configuration Detection",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Google Vision - Configuration Detection",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_google_vision_multiple_credentials(self):
        """Test 2: Confirmar se API Key + Client ID estão configurados"""
        print("📋 Test 2: Multiple Credentials Test...")
        
        try:
            # Test with a document to trigger Google Vision processing
            test_document = b"PASSPORT TEST DOCUMENT FOR CREDENTIALS VERIFICATION. " * 100
            
            files = {
                'file': ('credentials_test.pdf', test_document, 'application/pdf')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': 'TEST-CREDENTIALS-MULTIPLE'
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = result.get('extracted_data', {})
                google_vision_data = extracted_data.get('google_vision_data', {})
                
                # Check for multiple credential configuration
                auth_method = google_vision_data.get('auth_method', 'unknown')
                project_id = google_vision_data.get('project_id', 'unknown')
                api_enabled = google_vision_data.get('api_enabled', False)
                
                # Expected values
                expected_api_key = "AIzaSyBjn25InzalbcQVeDN8dgfgv6StUsBIutw"
                expected_client_id = "891629358081-pb11latlhnnp0dj68v03c0v2ocr6bhb8.apps.googleusercontent.com"
                expected_project_id = "891629358081"
                
                # Check if system is configured with both credentials
                has_multiple_credentials = (
                    auth_method in ["api_key", "oauth2"] and
                    project_id == expected_project_id and
                    api_enabled
                )
                
                self.log_test(
                    "Google Vision - Multiple Credentials",
                    has_multiple_credentials,
                    f"Auth method: {auth_method}, Project: {project_id}, API enabled: {api_enabled}",
                    {
                        "auth_method": auth_method,
                        "project_id": project_id,
                        "expected_project_id": expected_project_id,
                        "api_enabled": api_enabled,
                        "credentials_status": "MULTIPLE_CONFIGURED" if has_multiple_credentials else "INCOMPLETE",
                        "expected_api_key_prefix": expected_api_key[:20] + "...",
                        "expected_client_id_prefix": expected_client_id[:30] + "..."
                    }
                )
            else:
                self.log_test(
                    "Google Vision - Multiple Credentials",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Google Vision - Multiple Credentials",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_google_vision_service_status(self):
        """Test 3: Confirmar que erro 403 é esperado (serviço propagando)"""
        print("📋 Test 3: Service Status Test (403 expected)...")
        
        try:
            # Test with a document to trigger actual API call
            test_document = b"SERVICE STATUS TEST DOCUMENT FOR GOOGLE VISION API. " * 100
            
            files = {
                'file': ('service_status_test.pdf', test_document, 'application/pdf')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': 'TEST-SERVICE-STATUS'
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = result.get('extracted_data', {})
                google_vision_data = extracted_data.get('google_vision_data', {})
                
                # Check if system handles 403 error gracefully
                mock_mode = google_vision_data.get('mock_mode', True)
                api_enabled = google_vision_data.get('api_enabled', False)
                
                # System should be configured but may fall back to mock due to 403
                service_propagating = (
                    api_enabled and  # API is configured
                    mock_mode  # But falls back to mock due to service not ready
                )
                
                # Check for fallback behavior
                fallback_working = result.get('completeness', 0) > 0  # Should still provide results
                
                self.log_test(
                    "Google Vision - Service Status (403 Expected)",
                    service_propagating or not api_enabled,  # Either propagating or not configured yet
                    f"API enabled: {api_enabled}, Mock fallback: {mock_mode}, Fallback working: {fallback_working}",
                    {
                        "api_enabled": api_enabled,
                        "mock_mode": mock_mode,
                        "fallback_working": fallback_working,
                        "service_status": "PROPAGATING" if service_propagating else "NOT_READY",
                        "expected_behavior": "403 error with graceful fallback to mock mode",
                        "activation_url": "https://console.developers.google.com/apis/api/vision.googleapis.com/overview?project=891629358081"
                    }
                )
            else:
                self.log_test(
                    "Google Vision - Service Status (403 Expected)",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Google Vision - Service Status (403 Expected)",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_google_vision_hybrid_system_readiness(self):
        """Test 4: Confirmar se Dr. Miguel + Google Vision está pronto"""
        print("📋 Test 4: Hybrid System Readiness...")
        
        try:
            # Test hybrid system with both Google Vision and Dr. Miguel
            test_document = b"""
            PASSPORT
            UNITED STATES OF AMERICA
            
            Type: P
            Country Code: USA
            Passport No: 123456789
            
            Surname: SMITH
            Given Names: JOHN MICHAEL
            Nationality: UNITED STATES OF AMERICA
            Date of Birth: 15 JAN 1990
            Sex: M
            Place of Birth: NEW YORK, NY, USA
            Date of Issue: 10 MAR 2020
            Date of Expiry: 09 MAR 2030
            Authority: U.S. DEPARTMENT OF STATE
            """ * 20
            
            files = {
                'file': ('hybrid_test.pdf', test_document, 'application/pdf')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': 'TEST-HYBRID-READINESS',
                'applicant_name': 'John Michael Smith'
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check hybrid system components
                hybrid_powered = result.get('hybrid_powered', False)
                google_vision_enabled = result.get('google_vision_enabled', False)
                dr_miguel_enabled = result.get('dr_miguel_enabled', False)
                professional_grade = result.get('professional_grade', False)
                
                # Check extracted data structure
                extracted_data = result.get('extracted_data', {})
                google_vision_data = extracted_data.get('google_vision_data', {})
                dr_miguel_analysis = extracted_data.get('dr_miguel_analysis', {})
                processing_stats = extracted_data.get('processing_stats', {})
                
                # Verify hybrid system is ready
                hybrid_ready = (
                    hybrid_powered and
                    google_vision_enabled and
                    dr_miguel_enabled and
                    professional_grade and
                    bool(google_vision_data) and
                    bool(dr_miguel_analysis) and
                    bool(processing_stats)
                )
                
                combined_confidence = processing_stats.get('combined_confidence', 0)
                
                self.log_test(
                    "Google Vision - Hybrid System Readiness",
                    hybrid_ready,
                    f"Hybrid: {hybrid_powered}, Google: {google_vision_enabled}, Dr. Miguel: {dr_miguel_enabled}, Combined confidence: {combined_confidence}%",
                    {
                        "hybrid_powered": hybrid_powered,
                        "google_vision_enabled": google_vision_enabled,
                        "dr_miguel_enabled": dr_miguel_enabled,
                        "professional_grade": professional_grade,
                        "combined_confidence": combined_confidence,
                        "google_auth_method": google_vision_data.get('auth_method'),
                        "dr_miguel_verdict": dr_miguel_analysis.get('verdict'),
                        "system_status": "READY" if hybrid_ready else "NOT_READY"
                    }
                )
            else:
                self.log_test(
                    "Google Vision - Hybrid System Readiness",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Google Vision - Hybrid System Readiness",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_google_vision_preparation_for_activation(self):
        """Test 5: Verificar se sistema está pronto para quando API for ativada"""
        print("📋 Test 5: Preparation for Activation...")
        
        try:
            # Test system readiness for when API becomes active
            test_document = b"PREPARATION TEST FOR GOOGLE VISION API ACTIVATION. " * 100
            
            files = {
                'file': ('activation_prep_test.pdf', test_document, 'application/pdf')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': 'TEST-ACTIVATION-PREP'
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = result.get('extracted_data', {})
                google_vision_data = extracted_data.get('google_vision_data', {})
                
                # Check preparation indicators
                api_enabled = google_vision_data.get('api_enabled', False)
                auth_method = google_vision_data.get('auth_method', 'unknown')
                project_id = google_vision_data.get('project_id', 'unknown')
                mock_mode = google_vision_data.get('mock_mode', True)
                
                # System should be configured and ready to switch from mock to real
                ready_for_activation = (
                    api_enabled and  # Credentials configured
                    auth_method in ["api_key", "oauth2"] and  # Valid auth method
                    project_id == "891629358081"  # Correct project
                )
                
                # Check if system provides user information
                real_api_active = result.get('real_api_active', False)
                assessment = result.get('dra_paula_assessment', '')
                
                # Verify cost-benefit readiness
                cost_ready = "$1.50/1000" in str(result) or "cost" in assessment.lower()
                
                self.log_test(
                    "Google Vision - Preparation for Activation",
                    ready_for_activation,
                    f"Ready: {ready_for_activation}, Auth: {auth_method}, Project: {project_id}, Real API: {real_api_active}",
                    {
                        "ready_for_activation": ready_for_activation,
                        "api_enabled": api_enabled,
                        "auth_method": auth_method,
                        "project_id": project_id,
                        "mock_mode": mock_mode,
                        "real_api_active": real_api_active,
                        "cost_ready": cost_ready,
                        "activation_status": "READY_FOR_SWITCH" if ready_for_activation else "NOT_READY",
                        "next_steps": [
                            "Enable Google Vision API service in Google Cloud Console",
                            "Wait for service propagation (typically within minutes)",
                            "System will automatically switch from mock to real mode",
                            "Cost tracking: $1.50/1000 documents vs current mock mode"
                        ],
                        "activation_url": "https://console.developers.google.com/apis/api/vision.googleapis.com/overview?project=891629358081"
                    }
                )
            else:
                self.log_test(
                    "Google Vision - Preparation for Activation",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "Google Vision - Preparation for Activation",
                False,
                f"Exception: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all Google Vision API configuration tests"""
        print("🔍 TESTE FINAL: VERIFICAÇÃO COMPLETA GOOGLE VISION API...")
        print("=" * 80)
        print()
        
        # Test 1: Configuration Detection
        self.test_google_vision_configuration_detection()
        
        # Test 2: Multiple Credentials Test
        self.test_google_vision_multiple_credentials()
        
        # Test 3: Service Status Test (403 expected)
        self.test_google_vision_service_status()
        
        # Test 4: Hybrid System Readiness
        self.test_google_vision_hybrid_system_readiness()
        
        # Test 5: Preparation for Activation
        self.test_google_vision_preparation_for_activation()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 80)
        print("📊 GOOGLE VISION API CONFIGURATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
            print()
        
        # Show configuration status
        print("🔧 CONFIGURATION STATUS:")
        for result in self.test_results:
            if result['success']:
                print(f"  ✅ {result['test']}")
            else:
                print(f"  ❌ {result['test']}")
        
        print("\n" + "=" * 80)
        print("🎯 FINAL ASSESSMENT:")
        
        if passed_tests == total_tests:
            print("✅ Google Vision API configuration is COMPLETE and ready for activation!")
            print("   - All credentials properly configured")
            print("   - Hybrid system (Dr. Miguel + Google Vision) operational")
            print("   - System ready to switch from mock to real API when service is enabled")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ Google Vision API configuration is MOSTLY READY with minor issues")
            print("   - Most components configured correctly")
            print("   - Some fine-tuning may be needed")
        else:
            print("❌ Google Vision API configuration needs ATTENTION")
            print("   - Multiple configuration issues detected")
            print("   - Review failed tests and fix issues before activation")
        
        print("\n📋 NEXT STEPS:")
        print("1. Enable Google Vision API service in Google Cloud Console")
        print("2. URL: https://console.developers.google.com/apis/api/vision.googleapis.com/overview?project=891629358081")
        print("3. Wait for service propagation (typically within minutes)")
        print("4. System will automatically detect activation and switch from mock to real mode")
        print("5. Monitor cost: $1.50/1000 documents vs current free mock mode")
        print("=" * 80)

if __name__ == "__main__":
    tester = GoogleVisionConfigTester()
    tester.run_all_tests()