#!/usr/bin/env python3
"""
Comprehensive Form Code Test - Test all possible scenarios
"""

import requests
import json
import os
import time
import concurrent.futures

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visabot-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_scenario(scenario_name, steps):
    """Test a specific scenario"""
    print(f"\n🔍 TESTING: {scenario_name}")
    print("-" * 50)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'ComprehensiveFormCodeTester/1.0'
    })
    
    results = []
    case_id = None
    
    for i, step in enumerate(steps, 1):
        print(f"Step {i}: {step['description']}")
        
        try:
            if step['method'] == 'POST':
                response = session.post(f"{API_BASE}{step['endpoint']}", json=step['payload'])
            elif step['method'] == 'PUT':
                response = session.put(f"{API_BASE}{step['endpoint']}", json=step['payload'])
            elif step['method'] == 'GET':
                response = session.get(f"{API_BASE}{step['endpoint']}")
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract case_id if this is a creation step
                if step['method'] == 'POST' and '/auto-application/start' in step['endpoint']:
                    case_data = data.get("case", {})
                    case_id = case_data.get("case_id")
                    print(f"  Case ID: {case_id}")
                
                # Extract form_code
                if "case" in data:
                    form_code = data["case"].get("form_code")
                elif "form_code" in data:
                    form_code = data.get("form_code")
                else:
                    form_code = "NOT_FOUND"
                
                print(f"  Form Code: {form_code}")
                results.append({
                    'step': i,
                    'form_code': form_code,
                    'expected': step.get('expected_form_code'),
                    'success': form_code == step.get('expected_form_code') if step.get('expected_form_code') else True
                })
                
                # Update endpoint for next steps
                if case_id and '{case_id}' in str(steps):
                    for future_step in steps[i:]:
                        if '{case_id}' in future_step['endpoint']:
                            future_step['endpoint'] = future_step['endpoint'].replace('{case_id}', case_id)
            else:
                print(f"  ERROR: {response.text}")
                results.append({
                    'step': i,
                    'form_code': 'ERROR',
                    'expected': step.get('expected_form_code'),
                    'success': False
                })
        
        except Exception as e:
            print(f"  EXCEPTION: {str(e)}")
            results.append({
                'step': i,
                'form_code': 'EXCEPTION',
                'expected': step.get('expected_form_code'),
                'success': False
            })
    
    # Analyze results
    print(f"\n📊 SCENARIO RESULTS:")
    all_success = True
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"  Step {result['step']}: {status} Form Code: {result['form_code']}")
        if not result['success']:
            all_success = False
    
    if all_success:
        print(f"✅ SCENARIO PASSED: {scenario_name}")
    else:
        print(f"❌ SCENARIO FAILED: {scenario_name}")
    
    return all_success, results

def run_comprehensive_tests():
    """Run comprehensive form code tests"""
    print("🧪 COMPREHENSIVE FORM CODE TESTING")
    print("=" * 60)
    
    scenarios = [
        {
            'name': 'Standard H-1B Flow',
            'steps': [
                {
                    'method': 'POST',
                    'endpoint': '/auto-application/start',
                    'payload': {'session_token': 'test_h1b_standard'},
                    'description': 'Start application (no form_code)',
                    'expected_form_code': None
                },
                {
                    'method': 'PUT',
                    'endpoint': '/auto-application/case/{case_id}',
                    'payload': {'form_code': 'H-1B', 'session_token': 'test_h1b_standard'},
                    'description': 'Select H-1B form',
                    'expected_form_code': 'H-1B'
                },
                {
                    'method': 'GET',
                    'endpoint': '/auto-application/case/{case_id}?session_token=test_h1b_standard',
                    'payload': {},
                    'description': 'Retrieve case',
                    'expected_form_code': 'H-1B'
                }
            ]
        },
        {
            'name': 'Direct H-1B Creation',
            'steps': [
                {
                    'method': 'POST',
                    'endpoint': '/auto-application/start',
                    'payload': {'session_token': 'test_h1b_direct', 'form_code': 'H-1B'},
                    'description': 'Start with H-1B form_code',
                    'expected_form_code': 'H-1B'
                },
                {
                    'method': 'GET',
                    'endpoint': '/auto-application/case/{case_id}?session_token=test_h1b_direct',
                    'payload': {},
                    'description': 'Retrieve case',
                    'expected_form_code': 'H-1B'
                }
            ]
        },
        {
            'name': 'B-1/B-2 to H-1B Change',
            'steps': [
                {
                    'method': 'POST',
                    'endpoint': '/auto-application/start',
                    'payload': {'session_token': 'test_change', 'form_code': 'B-1/B-2'},
                    'description': 'Start with B-1/B-2',
                    'expected_form_code': 'B-1/B-2'
                },
                {
                    'method': 'PUT',
                    'endpoint': '/auto-application/case/{case_id}',
                    'payload': {'form_code': 'H-1B', 'session_token': 'test_change'},
                    'description': 'Change to H-1B',
                    'expected_form_code': 'H-1B'
                },
                {
                    'method': 'GET',
                    'endpoint': '/auto-application/case/{case_id}?session_token=test_change',
                    'payload': {},
                    'description': 'Retrieve changed case',
                    'expected_form_code': 'H-1B'
                }
            ]
        },
        {
            'name': 'Multiple Updates',
            'steps': [
                {
                    'method': 'POST',
                    'endpoint': '/auto-application/start',
                    'payload': {'session_token': 'test_multiple'},
                    'description': 'Start application',
                    'expected_form_code': None
                },
                {
                    'method': 'PUT',
                    'endpoint': '/auto-application/case/{case_id}',
                    'payload': {'form_code': 'B-1/B-2', 'session_token': 'test_multiple'},
                    'description': 'Set to B-1/B-2',
                    'expected_form_code': 'B-1/B-2'
                },
                {
                    'method': 'PUT',
                    'endpoint': '/auto-application/case/{case_id}',
                    'payload': {'form_code': 'H-1B', 'session_token': 'test_multiple'},
                    'description': 'Change to H-1B',
                    'expected_form_code': 'H-1B'
                },
                {
                    'method': 'PUT',
                    'endpoint': '/auto-application/case/{case_id}',
                    'payload': {'form_code': 'F-1', 'session_token': 'test_multiple'},
                    'description': 'Change to F-1',
                    'expected_form_code': 'F-1'
                },
                {
                    'method': 'GET',
                    'endpoint': '/auto-application/case/{case_id}?session_token=test_multiple',
                    'payload': {},
                    'description': 'Final retrieval',
                    'expected_form_code': 'F-1'
                }
            ]
        }
    ]
    
    passed_scenarios = 0
    total_scenarios = len(scenarios)
    
    for scenario in scenarios:
        success, results = test_scenario(scenario['name'], scenario['steps'])
        if success:
            passed_scenarios += 1
    
    print(f"\n" + "=" * 60)
    print(f"📊 COMPREHENSIVE TEST SUMMARY")
    print(f"=" * 60)
    print(f"Total Scenarios: {total_scenarios}")
    print(f"✅ Passed: {passed_scenarios}")
    print(f"❌ Failed: {total_scenarios - passed_scenarios}")
    print(f"Success Rate: {(passed_scenarios/total_scenarios*100):.1f}%")
    
    if passed_scenarios == total_scenarios:
        print(f"\n🎉 ALL SCENARIOS PASSED!")
        print(f"The form_code system is working correctly.")
        print(f"The reported bug may be in the frontend code or a specific edge case.")
    else:
        print(f"\n🚨 SOME SCENARIOS FAILED!")
        print(f"There are issues with the form_code system that need investigation.")

if __name__ == "__main__":
    run_comprehensive_tests()