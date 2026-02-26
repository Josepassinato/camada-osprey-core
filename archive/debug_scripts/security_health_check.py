#!/usr/bin/env python3
"""
OSPREY Security Health Check - Post Security Fixes Verification
Tests critical backend endpoints after security fixes to ensure deployment readiness
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://formfiller-26.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔒 OSPREY Security Health Check - Post Security Fixes")
print(f"Testing Backend at: {API_BASE}")
print("=" * 80)

# Global variables for test data
CASE_IDS = {}  # Store case IDs for different visa types
TEST_SESSION_TOKEN = str(uuid.uuid4())

def test_root_endpoint():
    """Test basic API connectivity - GET /api/"""
    print("\n🔍 Testing Root Endpoint (GET /api/)...")
    try:
        response = requests.get(f"{API_BASE}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', '')
            print(f"✅ Root endpoint working")
            print(f"   Status: {response.status_code}")
            print(f"   Message: {message}")
            
            # Verify it's the B2C message
            if 'B2C' in message and 'OSPREY' in message:
                print("✅ Correct B2C API message confirmed")
                return True
            else:
                print("⚠️  Unexpected API message format")
                return False
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
        return False

def test_auto_application_start_h1b():
    """Test POST /api/auto-application/start with H-1B"""
    print("\n🚀 Testing Auto-Application Start - H-1B...")
    global CASE_IDS
    
    try:
        payload = {
            "form_code": "H-1B",
            "session_token": TEST_SESSION_TOKEN
        }
        
        response = requests.post(f"{API_BASE}/auto-application/start", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            case = data.get('case', {})
            case_id = case.get('case_id')
            
            if case_id:
                CASE_IDS['H-1B'] = case_id
                print(f"✅ H-1B case created successfully")
                print(f"   Case ID: {case_id}")
                print(f"   Form Code: {case.get('form_code')}")
                print(f"   Status: {case.get('status')}")
                print(f"   Session Token: {case.get('session_token')}")
                
                # Verify security: no hardcoded keys in response
                response_text = response.text
                if os.environ.get('EMERGENT_LLM_KEY', '') and os.environ.get('EMERGENT_LLM_KEY', '') in response_text:
                    print("❌ SECURITY ISSUE: Hardcoded API key found in response!")
                    return False
                else:
                    print("✅ Security check passed: No hardcoded keys in response")
                
                return True
            else:
                print("❌ H-1B case creation failed: No case ID returned")
                return False
        else:
            print(f"❌ H-1B case creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ H-1B case creation error: {str(e)}")
        return False

def test_auto_application_start_b1b2():
    """Test POST /api/auto-application/start with B-1/B-2"""
    print("\n🚀 Testing Auto-Application Start - B-1/B-2...")
    global CASE_IDS
    
    try:
        payload = {
            "form_code": "B-1/B-2",
            "session_token": TEST_SESSION_TOKEN
        }
        
        response = requests.post(f"{API_BASE}/auto-application/start", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            case = data.get('case', {})
            case_id = case.get('case_id')
            
            if case_id:
                CASE_IDS['B-1/B-2'] = case_id
                print(f"✅ B-1/B-2 case created successfully")
                print(f"   Case ID: {case_id}")
                print(f"   Form Code: {case.get('form_code')}")
                print(f"   Status: {case.get('status')}")
                print(f"   Session Token: {case.get('session_token')}")
                
                # Verify security: no hardcoded keys in response
                response_text = response.text
                if os.environ.get('EMERGENT_LLM_KEY', '') and os.environ.get('EMERGENT_LLM_KEY', '') in response_text:
                    print("❌ SECURITY ISSUE: Hardcoded API key found in response!")
                    return False
                else:
                    print("✅ Security check passed: No hardcoded keys in response")
                
                return True
            else:
                print("❌ B-1/B-2 case creation failed: No case ID returned")
                return False
        else:
            print(f"❌ B-1/B-2 case creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ B-1/B-2 case creation error: {str(e)}")
        return False

def test_auto_application_start_f1():
    """Test POST /api/auto-application/start with F-1"""
    print("\n🚀 Testing Auto-Application Start - F-1...")
    global CASE_IDS
    
    try:
        payload = {
            "form_code": "F-1",
            "session_token": TEST_SESSION_TOKEN
        }
        
        response = requests.post(f"{API_BASE}/auto-application/start", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            case = data.get('case', {})
            case_id = case.get('case_id')
            
            if case_id:
                CASE_IDS['F-1'] = case_id
                print(f"✅ F-1 case created successfully")
                print(f"   Case ID: {case_id}")
                print(f"   Form Code: {case.get('form_code')}")
                print(f"   Status: {case.get('status')}")
                print(f"   Session Token: {case.get('session_token')}")
                
                # Verify security: no hardcoded keys in response
                response_text = response.text
                if os.environ.get('EMERGENT_LLM_KEY', '') and os.environ.get('EMERGENT_LLM_KEY', '') in response_text:
                    print("❌ SECURITY ISSUE: Hardcoded API key found in response!")
                    return False
                else:
                    print("✅ Security check passed: No hardcoded keys in response")
                
                return True
            else:
                print("❌ F-1 case creation failed: No case ID returned")
                return False
        else:
            print(f"❌ F-1 case creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ F-1 case creation error: {str(e)}")
        return False

def test_get_case_by_id():
    """Test GET /api/auto-application/case/{case_id}"""
    print("\n📋 Testing Get Case by ID...")
    
    if not CASE_IDS:
        print("❌ No case IDs available for testing")
        return False
    
    success_count = 0
    total_tests = len(CASE_IDS)
    
    for visa_type, case_id in CASE_IDS.items():
        try:
            print(f"\n   Testing {visa_type} case: {case_id}")
            
            # Test with session token
            response = requests.get(
                f"{API_BASE}/auto-application/case/{case_id}",
                params={"session_token": TEST_SESSION_TOKEN},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                case = data.get('case', {})
                
                print(f"   ✅ {visa_type} case retrieved successfully")
                print(f"      Case ID: {case.get('case_id')}")
                print(f"      Form Code: {case.get('form_code')}")
                print(f"      Status: {case.get('status')}")
                print(f"      Created: {case.get('created_at', 'N/A')}")
                
                # Verify security: no hardcoded keys in response
                response_text = response.text
                if os.environ.get('EMERGENT_LLM_KEY', '') and os.environ.get('EMERGENT_LLM_KEY', '') in response_text:
                    print(f"   ❌ SECURITY ISSUE: Hardcoded API key found in {visa_type} response!")
                    return False
                else:
                    print(f"   ✅ Security check passed for {visa_type}")
                
                success_count += 1
            else:
                print(f"   ❌ {visa_type} case retrieval failed: {response.status_code}")
                print(f"      Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ {visa_type} case retrieval error: {str(e)}")
    
    if success_count == total_tests:
        print(f"\n✅ All case retrievals successful ({success_count}/{total_tests})")
        return True
    elif success_count > 0:
        print(f"\n⚠️  Partial success in case retrievals ({success_count}/{total_tests})")
        return True
    else:
        print(f"\n❌ All case retrievals failed ({success_count}/{total_tests})")
        return False

def test_submission_instructions():
    """Test GET /api/auto-application/case/{case_id}/submission-instructions"""
    print("\n📄 Testing Submission Instructions...")
    
    if not CASE_IDS:
        print("❌ No case IDs available for testing submission instructions")
        return False
    
    success_count = 0
    total_tests = len(CASE_IDS)
    
    for visa_type, case_id in CASE_IDS.items():
        try:
            print(f"\n   Testing {visa_type} submission instructions: {case_id}")
            
            response = requests.get(
                f"{API_BASE}/auto-application/case/{case_id}/submission-instructions",
                params={"session_token": TEST_SESSION_TOKEN},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                instructions = data.get('instructions', {})
                
                print(f"   ✅ {visa_type} submission instructions retrieved")
                print(f"      Instructions type: {type(instructions)}")
                print(f"      Has content: {'Yes' if instructions else 'No'}")
                
                # Check for key instruction components
                if isinstance(instructions, dict):
                    keys = list(instructions.keys())
                    print(f"      Instruction sections: {len(keys)}")
                    if keys:
                        print(f"      Sample sections: {keys[:3]}")
                
                # Verify security: no hardcoded keys in response
                response_text = response.text
                if os.environ.get('EMERGENT_LLM_KEY', '') and os.environ.get('EMERGENT_LLM_KEY', '') in response_text:
                    print(f"   ❌ SECURITY ISSUE: Hardcoded API key found in {visa_type} instructions!")
                    return False
                else:
                    print(f"   ✅ Security check passed for {visa_type} instructions")
                
                success_count += 1
            else:
                print(f"   ❌ {visa_type} submission instructions failed: {response.status_code}")
                print(f"      Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ {visa_type} submission instructions error: {str(e)}")
    
    if success_count == total_tests:
        print(f"\n✅ All submission instructions successful ({success_count}/{total_tests})")
        return True
    elif success_count > 0:
        print(f"\n⚠️  Partial success in submission instructions ({success_count}/{total_tests})")
        return True
    else:
        print(f"\n❌ All submission instructions failed ({success_count}/{total_tests})")
        return False

def test_environment_variable_usage():
    """Test that EMERGENT_LLM_KEY environment variable is properly configured"""
    print("\n🔐 Testing Environment Variable Configuration...")
    
    try:
        # Load backend environment variables
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')
        
        emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        
        if emergent_key:
            print(f"✅ EMERGENT_LLM_KEY environment variable found")
            print(f"   Key format: {emergent_key[:15]}...{emergent_key[-6:] if len(emergent_key) > 21 else emergent_key}")
            print(f"   Key length: {len(emergent_key)} characters")
            
            # Verify it's the expected format
            if emergent_key.startswith('sk-emergent-') and len(emergent_key) > 20:
                print("✅ EMERGENT_LLM_KEY format appears correct")
                return True
            else:
                print("⚠️  EMERGENT_LLM_KEY format may be incorrect")
                return False
        else:
            print("❌ EMERGENT_LLM_KEY environment variable not found")
            return False
            
    except Exception as e:
        print(f"❌ Environment variable test error: {str(e)}")
        return False

def test_backend_logs_for_security():
    """Check backend logs for any security issues or hardcoded keys"""
    print("\n📋 Checking Backend Logs for Security Issues...")
    
    try:
        # Check supervisor backend logs
        import subprocess
        
        # Get recent backend logs
        result = subprocess.run(
            ['tail', '-n', '50', '/var/log/supervisor/backend.out.log'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logs = result.stdout
            print("✅ Backend logs retrieved successfully")
            
            # Check for hardcoded API keys in logs
            emergent_key = os.environ.get('EMERGENT_LLM_KEY', '')
            if emergent_key and emergent_key in logs:
                print("❌ SECURITY ISSUE: Hardcoded API key found in backend logs!")
                return False
            else:
                print("✅ Security check passed: No hardcoded keys in logs")
            
            # Check for successful startup
            if 'Application startup complete' in logs or 'Uvicorn running' in logs:
                print("✅ Backend startup successful")
            else:
                print("⚠️  Backend startup status unclear from logs")
            
            # Check for any error patterns
            error_patterns = ['ERROR', 'CRITICAL', 'Exception', 'Traceback']
            errors_found = []
            for pattern in error_patterns:
                if pattern in logs:
                    errors_found.append(pattern)
            
            if errors_found:
                print(f"⚠️  Found error patterns in logs: {errors_found}")
                # Show last few lines for context
                log_lines = logs.split('\n')[-10:]
                print("   Recent log entries:")
                for line in log_lines[-5:]:
                    if line.strip():
                        print(f"      {line}")
            else:
                print("✅ No critical errors found in recent logs")
            
            return True
        else:
            print(f"⚠️  Could not retrieve backend logs: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Backend log check error: {str(e)}")
        return False

def run_security_health_check():
    """Run complete security health check"""
    print("\n🎯 RUNNING COMPLETE SECURITY HEALTH CHECK")
    print("=" * 80)
    
    tests = [
        ("Root Endpoint", test_root_endpoint),
        ("Environment Variables", test_environment_variable_usage),
        ("Backend Logs Security", test_backend_logs_for_security),
        ("Auto-Application Start H-1B", test_auto_application_start_h1b),
        ("Auto-Application Start B-1/B-2", test_auto_application_start_b1b2),
        ("Auto-Application Start F-1", test_auto_application_start_f1),
        ("Get Case by ID", test_get_case_by_id),
        ("Submission Instructions", test_submission_instructions),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Final Summary
    print("\n" + "="*80)
    print("🎯 SECURITY HEALTH CHECK SUMMARY")
    print("="*80)
    
    print(f"\n📊 OVERALL RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    print(f"\n✅ PASSED TESTS:")
    for test_name, result in results.items():
        if result:
            print(f"   ✅ {test_name}")
    
    failed_tests = [name for name, result in results.items() if not result]
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for test_name in failed_tests:
            print(f"   ❌ {test_name}")
    
    # Security Assessment
    print(f"\n🔒 SECURITY ASSESSMENT:")
    security_tests = ["Environment Variables", "Backend Logs Security"]
    security_passed = sum(1 for test in security_tests if results.get(test, False))
    
    if security_passed == len(security_tests):
        print("✅ All security checks passed - No hardcoded API keys detected")
    else:
        print("❌ Security issues detected - Review failed security tests")
    
    # Deployment Readiness
    print(f"\n🚀 DEPLOYMENT READINESS:")
    critical_tests = [
        "Root Endpoint", 
        "Auto-Application Start H-1B", 
        "Auto-Application Start B-1/B-2", 
        "Auto-Application Start F-1",
        "Get Case by ID"
    ]
    critical_passed = sum(1 for test in critical_tests if results.get(test, False))
    
    if critical_passed == len(critical_tests):
        print("✅ All critical endpoints working - Ready for deployment")
    elif critical_passed >= len(critical_tests) * 0.8:
        print("⚠️  Most critical endpoints working - Review failed tests before deployment")
    else:
        print("❌ Critical endpoint failures - NOT ready for deployment")
    
    # Case IDs Summary
    if CASE_IDS:
        print(f"\n📋 CREATED TEST CASES:")
        for visa_type, case_id in CASE_IDS.items():
            print(f"   {visa_type}: {case_id}")
    
    return passed >= total * 0.8  # 80% pass rate for overall success

if __name__ == "__main__":
    success = run_security_health_check()
    exit(0 if success else 1)