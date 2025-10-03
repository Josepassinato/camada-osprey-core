#!/usr/bin/env python3
"""
OSPREY Case Management Corrections Validation Tests
Tests specific corrections implemented for case update endpoints and AI parameter handling
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visa-wizard-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing OSPREY Case Management Corrections at: {API_BASE}")
print("=" * 80)

# Global variables for test data
TEST_USER = {
    "email": "case_test@osprey.com",
    "password": "CaseTest123",
    "first_name": "Carlos",
    "last_name": "Silva"
}
AUTH_TOKEN = None
USER_ID = None
CASE_ID = None

def setup_test_user():
    """Setup test user for case management tests"""
    print("\n🔧 Setting up test user...")
    global AUTH_TOKEN, USER_ID
    
    # Try login first
    login_payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            USER_ID = data.get('user', {}).get('id')
            print(f"✅ User login successful - User ID: {USER_ID}")
            return True
        else:
            # Try signup if login fails
            signup_payload = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "first_name": TEST_USER["first_name"],
                "last_name": TEST_USER["last_name"],
                "phone": "+55 11 99999-8888"
            }
            
            signup_response = requests.post(f"{API_BASE}/auth/signup", json=signup_payload, timeout=10)
            
            if signup_response.status_code == 200:
                data = signup_response.json()
                AUTH_TOKEN = data.get('token')
                USER_ID = data.get('user', {}).get('id')
                print(f"✅ User signup successful - User ID: {USER_ID}")
                return True
            else:
                print(f"❌ User setup failed: {signup_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ User setup error: {str(e)}")
        return False

def test_case_creation():
    """Test case creation for different visa types"""
    print("\n📋 Testing Case Creation...")
    global CASE_ID
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    # Test H-1B case creation
    test_cases = [
        {"form_code": "H-1B", "description": "H-1B Specialty Occupation"},
        {"form_code": "B-1/B-2", "description": "Business/Tourism Visitor"},
        {"form_code": "F-1", "description": "Student Visa"}
    ]
    
    created_cases = []
    
    for test_case in test_cases:
        try:
            payload = {
                "form_code": test_case["form_code"]
            }
            
            response = requests.post(f"{API_BASE}/auto-application/start", json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                case_id = data.get('case_id')
                created_cases.append(case_id)
                
                print(f"✅ {test_case['description']} case created: {case_id}")
                print(f"   Response data: {data}")
                
                if not CASE_ID and case_id:  # Use first case for subsequent tests
                    CASE_ID = case_id
                    
            else:
                print(f"❌ {test_case['description']} case creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {test_case['description']} case creation error: {str(e)}")
    
    if created_cases:
        print(f"✅ Created {len(created_cases)} test cases successfully")
        return True
    else:
        print("❌ No cases created successfully")
        return False

def test_case_update_endpoints():
    """Test all case update endpoints - PUT, PATCH, and batch-update"""
    print("\n🔄 Testing Case Update Endpoints...")
    
    if not AUTH_TOKEN or not CASE_ID:
        print("❌ No auth token or case ID available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    results = {
        "put_original": False,
        "patch_optimized": False,
        "batch_update": False
    }
    
    # 1. Test PUT endpoint (original)
    print("\n   Testing PUT /api/auto-application/case/{case_id} (original endpoint)...")
    try:
        put_payload = {
            "status": "basic_data",
            "basic_data": {
                "first_name": "Carlos Eduardo",
                "last_name": "Silva Santos",
                "date_of_birth": "1990-03-15",
                "nationality": "Brazilian",
                "passport_number": "BR123456789"
            },
            "progress_percentage": 30
        }
        
        put_response = requests.put(f"{API_BASE}/auto-application/case/{CASE_ID}", json=put_payload, headers=headers, timeout=10)
        
        if put_response.status_code == 200:
            data = put_response.json()
            print(f"   ✅ PUT endpoint working - Status: {data.get('status')}")
            results["put_original"] = True
        else:
            print(f"   ❌ PUT endpoint failed: {put_response.status_code}")
            print(f"      Error: {put_response.text}")
            
    except Exception as e:
        print(f"   ❌ PUT endpoint error: {str(e)}")
    
    # 2. Test PATCH endpoint (new optimized)
    print("\n   Testing PATCH /api/auto-application/case/{case_id} (new optimized endpoint)...")
    try:
        patch_payload = {
            "user_story_text": "Sou engenheiro de software com 5 anos de experiência. Recebi uma oferta de emprego de uma empresa americana para trabalhar como desenvolvedor sênior.",
            "current_step": "story_completed"
        }
        
        patch_response = requests.patch(f"{API_BASE}/auto-application/case/{CASE_ID}", json=patch_payload, headers=headers, timeout=10)
        
        if patch_response.status_code == 200:
            data = patch_response.json()
            print(f"   ✅ PATCH endpoint working - Current step: {data.get('current_step')}")
            results["patch_optimized"] = True
        else:
            print(f"   ❌ PATCH endpoint failed: {patch_response.status_code}")
            print(f"      Error: {patch_response.text}")
            
    except Exception as e:
        print(f"   ❌ PATCH endpoint error: {str(e)}")
    
    # 3. Test batch-update endpoint (new)
    print("\n   Testing POST /api/auto-application/case/{case_id}/batch-update (new batch endpoint)...")
    try:
        batch_payload = {
            "updates": [
                {
                    "field": "simplified_form_responses",
                    "value": {
                        "education_level": "Bachelor's Degree",
                        "field_of_study": "Computer Science",
                        "years_experience": "5"
                    }
                },
                {
                    "field": "progress_percentage",
                    "value": 60
                },
                {
                    "field": "current_step", 
                    "value": "form_filled"
                }
            ]
        }
        
        batch_response = requests.post(f"{API_BASE}/auto-application/case/{CASE_ID}/batch-update", json=batch_payload, headers=headers, timeout=10)
        
        if batch_response.status_code == 200:
            data = batch_response.json()
            print(f"   ✅ Batch-update endpoint working - Updates applied: {data.get('updates_applied', 0)}")
            results["batch_update"] = True
        else:
            print(f"   ❌ Batch-update endpoint failed: {batch_response.status_code}")
            print(f"      Error: {batch_response.text}")
            
    except Exception as e:
        print(f"   ❌ Batch-update endpoint error: {str(e)}")
    
    # Summary
    successful_endpoints = sum(results.values())
    total_endpoints = len(results)
    
    print(f"\n📊 Case Update Endpoints Summary:")
    print(f"   PUT (original): {'✅' if results['put_original'] else '❌'}")
    print(f"   PATCH (optimized): {'✅' if results['patch_optimized'] else '❌'}")
    print(f"   Batch-update (new): {'✅' if results['batch_update'] else '❌'}")
    print(f"   Success rate: {successful_endpoints}/{total_endpoints} ({int(successful_endpoints/total_endpoints*100)}%)")
    
    return successful_endpoints >= 2  # At least 2 out of 3 should work

def test_ai_parameter_structures():
    """Test AI processing with different parameter structures"""
    print("\n🤖 Testing AI Parameter Structures...")
    
    if not AUTH_TOKEN or not CASE_ID:
        print("❌ No auth token or case ID available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    results = {
        "original_structure": False,
        "simplified_structure": False,
        "flexible_structure": False
    }
    
    # 1. Test with original parameter structure
    print("\n   Testing AI processing with original parameter structure...")
    try:
        original_payload = {
            "step": "document_analysis",
            "case_id": CASE_ID,
            "parameters": {
                "user_data": {
                    "first_name": "Carlos Eduardo",
                    "last_name": "Silva Santos",
                    "nationality": "Brazilian"
                },
                "form_responses": {
                    "education_level": "Bachelor's Degree",
                    "field_of_study": "Computer Science"
                }
            }
        }
        
        original_response = requests.post(f"{API_BASE}/ai-processing/step", json=original_payload, headers=headers, timeout=30)
        
        if original_response.status_code == 200:
            data = original_response.json()
            print(f"   ✅ Original structure working - Processing time: {data.get('processing_time_ms', 'N/A')}ms")
            results["original_structure"] = True
        else:
            print(f"   ❌ Original structure failed: {original_response.status_code}")
            print(f"      Error: {original_response.text}")
            
    except Exception as e:
        print(f"   ❌ Original structure error: {str(e)}")
    
    # 2. Test with simplified form responses structure
    print("\n   Testing AI processing with simplified form responses structure...")
    try:
        simplified_payload = {
            "step": "eligibility_check",
            "case_id": CASE_ID,
            "case_data": {
                "simplified_form_responses": {
                    "visa_type": "H-1B",
                    "education": "Bachelor's in Computer Science",
                    "experience_years": "5",
                    "job_offer": "Yes",
                    "employer_name": "TechCorp USA"
                }
            }
        }
        
        simplified_response = requests.post(f"{API_BASE}/ai-processing/step", json=simplified_payload, headers=headers, timeout=30)
        
        if simplified_response.status_code == 200:
            data = simplified_response.json()
            print(f"   ✅ Simplified structure working - Result: {data.get('result', 'N/A')}")
            results["simplified_structure"] = True
        else:
            print(f"   ❌ Simplified structure failed: {simplified_response.status_code}")
            print(f"      Error: {simplified_response.text}")
            
    except Exception as e:
        print(f"   ❌ Simplified structure error: {str(e)}")
    
    # 3. Test with flexible mixed structure
    print("\n   Testing AI processing with flexible mixed structure...")
    try:
        flexible_payload = {
            "step": "form_validation",
            "case_id": CASE_ID,
            "mixed_data": {
                "basic_info": {
                    "name": "Carlos Eduardo Silva Santos",
                    "birth_date": "1990-03-15"
                },
                "case_data": {
                    "simplified_form_responses": {
                        "current_status": "H4 dependent",
                        "desired_status": "H-1B primary"
                    }
                },
                "additional_context": {
                    "priority": "high",
                    "timeline": "urgent"
                }
            }
        }
        
        flexible_response = requests.post(f"{API_BASE}/ai-processing/step", json=flexible_payload, headers=headers, timeout=30)
        
        if flexible_response.status_code == 200:
            data = flexible_response.json()
            print(f"   ✅ Flexible structure working - Analysis: {data.get('analysis', 'N/A')[:100]}...")
            results["flexible_structure"] = True
        else:
            print(f"   ❌ Flexible structure failed: {flexible_response.status_code}")
            print(f"      Error: {flexible_response.text}")
            
    except Exception as e:
        print(f"   ❌ Flexible structure error: {str(e)}")
    
    # Summary
    successful_structures = sum(results.values())
    total_structures = len(results)
    
    print(f"\n📊 AI Parameter Structures Summary:")
    print(f"   Original structure: {'✅' if results['original_structure'] else '❌'}")
    print(f"   Simplified structure: {'✅' if results['simplified_structure'] else '❌'}")
    print(f"   Flexible structure: {'✅' if results['flexible_structure'] else '❌'}")
    print(f"   Success rate: {successful_structures}/{total_structures} ({int(successful_structures/total_structures*100)}%)")
    
    return successful_structures >= 1  # At least 1 structure should work

def test_data_persistence_optimization():
    """Test MongoDB data persistence and performance optimizations"""
    print("\n💾 Testing Data Persistence Optimization...")
    
    if not AUTH_TOKEN or not CASE_ID:
        print("❌ No auth token or case ID available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    results = {
        "crud_operations": False,
        "query_performance": False,
        "data_integrity": False
    }
    
    # 1. Test CRUD operations efficiency
    print("\n   Testing optimized CRUD operations...")
    try:
        start_time = datetime.now()
        
        # Create operation
        create_payload = {"form_code": "H-1B"}
        create_response = requests.post(f"{API_BASE}/auto-application/start", json=create_payload, headers=headers, timeout=10)
        
        if create_response.status_code == 200:
            temp_case_id = create_response.json().get('case_id')
            
            # Read operation
            read_response = requests.get(f"{API_BASE}/auto-application/case/{temp_case_id}", headers=headers, timeout=10)
            
            # Update operation
            update_payload = {"status": "basic_data", "progress_percentage": 25}
            update_response = requests.put(f"{API_BASE}/auto-application/case/{temp_case_id}", json=update_payload, headers=headers, timeout=10)
            
            # Delete operation (if endpoint exists)
            # delete_response = requests.delete(f"{API_BASE}/auto-application/case/{temp_case_id}", headers=headers, timeout=10)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds() * 1000
            
            if read_response.status_code == 200 and update_response.status_code == 200:
                print(f"   ✅ CRUD operations working - Total time: {total_time:.0f}ms")
                results["crud_operations"] = True
            else:
                print(f"   ❌ CRUD operations failed - Read: {read_response.status_code}, Update: {update_response.status_code}")
        else:
            print(f"   ❌ CRUD create operation failed: {create_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ CRUD operations error: {str(e)}")
    
    # 2. Test query performance with indexes
    print("\n   Testing query performance with indexes...")
    try:
        start_time = datetime.now()
        
        # Test multiple queries that should benefit from indexes
        queries = [
            f"{API_BASE}/auto-application/cases",  # List all cases
            f"{API_BASE}/auto-application/case/{CASE_ID}",  # Get specific case
            f"{API_BASE}/auto-application/cases?status=basic_data",  # Filter by status
        ]
        
        query_times = []
        successful_queries = 0
        
        for query_url in queries:
            query_start = datetime.now()
            response = requests.get(query_url, headers=headers, timeout=10)
            query_end = datetime.now()
            
            query_time = (query_end - query_start).total_seconds() * 1000
            query_times.append(query_time)
            
            if response.status_code == 200:
                successful_queries += 1
        
        avg_query_time = sum(query_times) / len(query_times) if query_times else 0
        
        if successful_queries >= 2 and avg_query_time < 2000:  # Under 2 seconds average
            print(f"   ✅ Query performance good - Avg time: {avg_query_time:.0f}ms, Success: {successful_queries}/{len(queries)}")
            results["query_performance"] = True
        else:
            print(f"   ❌ Query performance issues - Avg time: {avg_query_time:.0f}ms, Success: {successful_queries}/{len(queries)}")
            
    except Exception as e:
        print(f"   ❌ Query performance error: {str(e)}")
    
    # 3. Test data integrity between operations
    print("\n   Testing data integrity between operations...")
    try:
        # Update case with specific data
        integrity_payload = {
            "basic_data": {
                "test_field": "integrity_test_value",
                "timestamp": datetime.now().isoformat()
            },
            "status": "form_filled",
            "progress_percentage": 75
        }
        
        update_response = requests.put(f"{API_BASE}/auto-application/case/{CASE_ID}", json=integrity_payload, headers=headers, timeout=10)
        
        if update_response.status_code == 200:
            # Retrieve and verify data
            retrieve_response = requests.get(f"{API_BASE}/auto-application/case/{CASE_ID}", headers=headers, timeout=10)
            
            if retrieve_response.status_code == 200:
                retrieved_data = retrieve_response.json()
                basic_data = retrieved_data.get('basic_data', {})
                
                # Check if our test data persisted correctly
                if (basic_data.get('test_field') == 'integrity_test_value' and 
                    retrieved_data.get('status') == 'form_filled' and
                    retrieved_data.get('progress_percentage') == 75):
                    
                    print(f"   ✅ Data integrity maintained - All fields persisted correctly")
                    results["data_integrity"] = True
                else:
                    print(f"   ❌ Data integrity issues - Some fields not persisted correctly")
            else:
                print(f"   ❌ Data retrieval failed: {retrieve_response.status_code}")
        else:
            print(f"   ❌ Data update failed: {update_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Data integrity error: {str(e)}")
    
    # Summary
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Data Persistence Optimization Summary:")
    print(f"   CRUD operations: {'✅' if results['crud_operations'] else '❌'}")
    print(f"   Query performance: {'✅' if results['query_performance'] else '❌'}")
    print(f"   Data integrity: {'✅' if results['data_integrity'] else '❌'}")
    print(f"   Success rate: {successful_tests}/{total_tests} ({int(successful_tests/total_tests*100)}%)")
    
    return successful_tests >= 2  # At least 2 out of 3 should work

def test_backward_compatibility():
    """Test that existing endpoints still work after corrections"""
    print("\n🔄 Testing Backward Compatibility...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    results = {
        "user_auth": False,
        "profile_management": False,
        "document_operations": False,
        "chat_functionality": False
    }
    
    # 1. Test user authentication still works
    print("\n   Testing user authentication compatibility...")
    try:
        profile_response = requests.get(f"{API_BASE}/profile", headers=headers, timeout=10)
        
        if profile_response.status_code == 200:
            print(f"   ✅ User authentication working")
            results["user_auth"] = True
        else:
            print(f"   ❌ User authentication failed: {profile_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ User authentication error: {str(e)}")
    
    # 2. Test profile management still works
    print("\n   Testing profile management compatibility...")
    try:
        update_payload = {
            "country_of_birth": "Brazil",
            "current_country": "Brazil"
        }
        
        update_response = requests.put(f"{API_BASE}/profile", json=update_payload, headers=headers, timeout=10)
        
        if update_response.status_code == 200:
            print(f"   ✅ Profile management working")
            results["profile_management"] = True
        else:
            print(f"   ❌ Profile management failed: {update_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Profile management error: {str(e)}")
    
    # 3. Test document operations still work
    print("\n   Testing document operations compatibility...")
    try:
        docs_response = requests.get(f"{API_BASE}/documents", headers=headers, timeout=10)
        
        if docs_response.status_code == 200:
            print(f"   ✅ Document operations working")
            results["document_operations"] = True
        else:
            print(f"   ❌ Document operations failed: {docs_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Document operations error: {str(e)}")
    
    # 4. Test chat functionality still works
    print("\n   Testing chat functionality compatibility...")
    try:
        chat_payload = {
            "message": "Teste de compatibilidade do chat",
            "session_id": str(uuid.uuid4())
        }
        
        chat_response = requests.post(f"{API_BASE}/chat", json=chat_payload, headers=headers, timeout=30)
        
        if chat_response.status_code == 200:
            print(f"   ✅ Chat functionality working")
            results["chat_functionality"] = True
        else:
            print(f"   ❌ Chat functionality failed: {chat_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Chat functionality error: {str(e)}")
    
    # Summary
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Backward Compatibility Summary:")
    print(f"   User authentication: {'✅' if results['user_auth'] else '❌'}")
    print(f"   Profile management: {'✅' if results['profile_management'] else '❌'}")
    print(f"   Document operations: {'✅' if results['document_operations'] else '❌'}")
    print(f"   Chat functionality: {'✅' if results['chat_functionality'] else '❌'}")
    print(f"   Success rate: {successful_tests}/{total_tests} ({int(successful_tests/total_tests*100)}%)")
    
    return successful_tests >= 3  # At least 3 out of 4 should work

def run_all_correction_tests():
    """Run all correction validation tests"""
    print("🚀 Starting OSPREY Case Management Corrections Validation Tests")
    print("=" * 80)
    
    test_results = {}
    
    # Setup
    if not setup_test_user():
        print("❌ Test setup failed - cannot continue")
        return False
    
    # Run tests
    test_results["case_creation"] = test_case_creation()
    test_results["case_update_endpoints"] = test_case_update_endpoints()
    test_results["ai_parameter_structures"] = test_ai_parameter_structures()
    test_results["data_persistence"] = test_data_persistence_optimization()
    test_results["backward_compatibility"] = test_backward_compatibility()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏁 FINAL CORRECTION VALIDATION RESULTS")
    print("=" * 80)
    
    successful_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Success Rate: {successful_tests}/{total_tests} ({int(successful_tests/total_tests*100)}%)")
    
    if successful_tests >= 4:  # At least 4 out of 5 should pass
        print("🎉 CORRECTION VALIDATION SUCCESSFUL - Most corrections working properly!")
        return True
    else:
        print("⚠️  CORRECTION VALIDATION ISSUES - Some corrections need attention")
        return False

if __name__ == "__main__":
    success = run_all_correction_tests()
    exit(0 if success else 1)