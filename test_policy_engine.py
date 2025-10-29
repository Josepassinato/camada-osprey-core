#!/usr/bin/env python3
"""
Simple Policy Engine Test
"""

import requests
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_policy_engine_simple():
    """Simple test of Policy Engine integration"""
    print("🏛️ Testing Policy Engine Integration...")
    
    try:
        # Create a valid test document (larger than 50KB)
        test_content = b'%PDF-1.4\n' + b'x' * 100000  # Valid PDF header + content
        
        files = {
            'file': ('passport_test.pdf', test_content, 'application/pdf')
        }
        
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-POLICY-SIMPLE'
        }
        
        print(f"   Testing endpoint: {API_BASE}/documents/analyze-with-ai")
        print(f"   Document: passport_test.pdf ({len(test_content)} bytes)")
        print(f"   Visa type: H-1B")
        
        response = requests.post(
            f"{API_BASE}/documents/analyze-with-ai", 
            files=files, 
            data=data, 
            timeout=60
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check for Policy Engine components
            policy_engine = result.get('policy_engine')
            standardized_doc_type = result.get('standardized_doc_type')
            quality_analysis = result.get('quality_analysis')
            policy_score = result.get('policy_score')
            policy_decision = result.get('policy_decision')
            
            print(f"\n   📊 Policy Engine Results:")
            print(f"      Policy Engine Present: {'✅ Yes' if policy_engine else '❌ No'}")
            print(f"      Standardized Doc Type: {standardized_doc_type or '❌ Missing'}")
            print(f"      Quality Analysis: {'✅ Present' if quality_analysis else '❌ Missing'}")
            print(f"      Policy Score: {policy_score if policy_score is not None else '❌ Missing'}")
            print(f"      Policy Decision: {policy_decision or '❌ Missing'}")
            
            if policy_engine:
                print(f"\n   🔍 Policy Engine Details:")
                print(f"      Status: {policy_engine.get('status', 'N/A')}")
                print(f"      Document Type: {policy_engine.get('doc_type', 'N/A')}")
                print(f"      Overall Score: {policy_engine.get('overall_score', 'N/A')}")
                print(f"      Decision: {policy_engine.get('decision', 'N/A')}")
                
                # Check quality analysis
                quality = policy_engine.get('quality', {})
                if quality:
                    print(f"      Quality Status: {quality.get('status', 'N/A')}")
                    print(f"      Quality Checks: {len(quality.get('checks', {}))}")
                
                # Check policy checks
                policy_checks = policy_engine.get('policy_checks', [])
                print(f"      Policy Checks: {len(policy_checks)}")
                
                if policy_checks:
                    print(f"      Sample Checks:")
                    for i, check in enumerate(policy_checks[:3]):
                        print(f"         {i+1}. {check.get('rule', 'N/A')}: {check.get('result', 'N/A')}")
                
                return True
            else:
                print(f"   ❌ Policy Engine not integrated")
                return False
        else:
            print(f"   ❌ API call failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Policy Engine test error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_policy_engine_simple()
    if success:
        print("\n✅ Policy Engine integration working!")
    else:
        print("\n❌ Policy Engine integration needs fixes")