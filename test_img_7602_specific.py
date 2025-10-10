#!/usr/bin/env python3
"""
CRITICAL TEST: IMG_7602.png Specific Document Analysis
Testing the specific document reported by the user to verify cache collision is resolved.
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_img_7602_cache_collision():
    """Test the specific IMG_7602.png document for cache collision issues"""
    
    print("🎯 CRITICAL TEST: IMG_7602.png Cache Collision Resolution")
    print("=" * 70)
    print("URL: https://customer-assets.emergentagent.com/job_formfill-aid/artifacts/hka5y6g5_IMG_7602.png")
    print()
    
    # Setup session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'IMG7602Tester/1.0'
    })
    
    # Setup authentication
    try:
        login_data = {
            "email": "test@phase23.com",
            "password": "testpassword123"
        }
        
        login_response = session.post(f"{API_BASE}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            auth_token = login_result.get('token')
            session.headers.update({'Authorization': f'Bearer {auth_token}'})
            print("✅ Authentication successful")
        else:
            print("⚠️ Authentication failed - continuing without auth")
    except Exception as e:
        print(f"⚠️ Auth error: {e}")
    
    try:
        # STEP 1: Download IMG_7602.png
        print("📥 STEP 1: Downloading IMG_7602.png...")
        
        img_url = "https://customer-assets.emergentagent.com/job_formfill-aid/artifacts/hka5y6g5_IMG_7602.png"
        img_response = requests.get(img_url, timeout=30)
        
        if img_response.status_code != 200:
            print(f"❌ Failed to download IMG_7602.png: HTTP {img_response.status_code}")
            return
        
        img_content = img_response.content
        img_size = len(img_content)
        print(f"✅ Downloaded IMG_7602.png: {img_size:,} bytes")
        
        # STEP 2: First analysis of IMG_7602.png
        print("\n📄 STEP 2: First analysis of IMG_7602.png...")
        
        files_1 = {
            'file': ('IMG_7602.png', img_content, 'image/png')
        }
        data_1 = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'IMG-7602-TEST-1'
        }
        
        headers = {k: v for k, v in session.headers.items() if k.lower() != 'content-type'}
        
        response_1 = requests.post(
            f"{API_BASE}/documents/analyze-with-ai",
            files=files_1,
            data=data_1,
            headers=headers
        )
        
        if response_1.status_code != 200:
            print(f"❌ First analysis failed: HTTP {response_1.status_code}")
            print(f"Error: {response_1.text[:200]}")
            return
        
        result_1 = response_1.json()
        extracted_1 = result_1.get('extracted_data', {})
        
        print(f"✅ First analysis complete:")
        print(f"   - Detected type: {extracted_1.get('detected_type', 'unknown')}")
        print(f"   - Completeness: {result_1.get('completeness', 0)}%")
        print(f"   - Valid: {result_1.get('valid', False)}")
        print(f"   - Analysis method: {extracted_1.get('analysis_method', 'unknown')}")
        print(f"   - Confidence: {extracted_1.get('confidence', 0)}")
        
        # STEP 3: Upload a different document to test cache collision
        print("\n📄 STEP 3: Uploading different document (cache collision test)...")
        time.sleep(1)
        
        different_content = """CERTIDÃO DE NASCIMENTO
BIRTH CERTIFICATE
CARTÓRIO DO REGISTRO CIVIL
Nome: JOÃO SILVA SANTOS
Data de Nascimento: 15/08/1990
Local: BRASÍLIA - DF
Pai: CARLOS SANTOS
Mãe: MARIA SILVA
""" + "Different document content. " * 3000
        
        files_diff = {
            'file': ('birth_cert_joao.pdf', different_content.encode('utf-8'), 'application/pdf')
        }
        data_diff = {
            'document_type': 'birth_certificate',
            'visa_type': 'H-1B',
            'case_id': 'DIFFERENT-DOC-TEST'
        }
        
        response_diff = requests.post(
            f"{API_BASE}/documents/analyze-with-ai",
            files=files_diff,
            data=data_diff,
            headers=headers
        )
        
        if response_diff.status_code == 200:
            result_diff = response_diff.json()
            extracted_diff = result_diff.get('extracted_data', {})
            print(f"✅ Different document analyzed:")
            print(f"   - Detected type: {extracted_diff.get('detected_type', 'unknown')}")
            print(f"   - Completeness: {result_diff.get('completeness', 0)}%")
        else:
            print(f"⚠️ Different document analysis failed: HTTP {response_diff.status_code}")
        
        # STEP 4: Second analysis of IMG_7602.png (critical test)
        print("\n📄 STEP 4: Second analysis of IMG_7602.png (critical cache test)...")
        time.sleep(1)
        
        files_2 = {
            'file': ('IMG_7602_second.png', img_content, 'image/png')
        }
        data_2 = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'IMG-7602-TEST-2'
        }
        
        response_2 = requests.post(
            f"{API_BASE}/documents/analyze-with-ai",
            files=files_2,
            data=data_2,
            headers=headers
        )
        
        if response_2.status_code != 200:
            print(f"❌ Second analysis failed: HTTP {response_2.status_code}")
            print(f"Error: {response_2.text[:200]}")
            return
        
        result_2 = response_2.json()
        extracted_2 = result_2.get('extracted_data', {})
        
        print(f"✅ Second analysis complete:")
        print(f"   - Detected type: {extracted_2.get('detected_type', 'unknown')}")
        print(f"   - Completeness: {result_2.get('completeness', 0)}%")
        print(f"   - Valid: {result_2.get('valid', False)}")
        print(f"   - Analysis method: {extracted_2.get('analysis_method', 'unknown')}")
        print(f"   - Confidence: {extracted_2.get('confidence', 0)}")
        
        # STEP 5: Compare results for cache collision
        print("\n🔍 STEP 5: Cache collision analysis...")
        
        # Check consistency between first and second analysis
        same_type = extracted_1.get('detected_type') == extracted_2.get('detected_type')
        same_method = extracted_1.get('analysis_method') == extracted_2.get('analysis_method')
        completeness_diff = abs(result_1.get('completeness', 0) - result_2.get('completeness', 0))
        confidence_diff = abs(extracted_1.get('confidence', 0) - extracted_2.get('confidence', 0))
        
        # Check for contamination from different document
        result_1_str = str(result_1).lower()
        result_2_str = str(result_2).lower()
        
        # Birth certificate keywords should NOT appear in IMG_7602 results
        birth_keywords = ['nascimento', 'birth', 'cartório', 'joão', 'silva']
        contamination_1 = any(keyword in result_1_str for keyword in birth_keywords)
        contamination_2 = any(keyword in result_2_str for keyword in birth_keywords)
        
        print(f"📊 Consistency Analysis:")
        print(f"   - Same detected type: {same_type} ({extracted_1.get('detected_type')} vs {extracted_2.get('detected_type')})")
        print(f"   - Same analysis method: {same_method} ({extracted_1.get('analysis_method')} vs {extracted_2.get('analysis_method')})")
        print(f"   - Completeness difference: {completeness_diff}%")
        print(f"   - Confidence difference: {confidence_diff:.3f}")
        print(f"   - Contamination in first: {contamination_1}")
        print(f"   - Contamination in second: {contamination_2}")
        
        # STEP 6: Final assessment
        print("\n🏆 FINAL ASSESSMENT:")
        
        cache_collision_resolved = (
            same_type and 
            same_method and 
            completeness_diff <= 10 and  # Allow 10% variance
            confidence_diff <= 0.2 and   # Allow 20% variance
            not contamination_1 and 
            not contamination_2
        )
        
        if cache_collision_resolved:
            print("✅ CACHE COLLISION RESOLVED!")
            print("   - IMG_7602.png gets consistent analysis")
            print("   - No contamination from other documents")
            print("   - Fresh analysis performed each time")
        else:
            print("❌ CACHE COLLISION ISSUES DETECTED!")
            print("   - Inconsistent results between analyses")
            print("   - Possible contamination from other documents")
            
            if not same_type:
                print(f"   - Type inconsistency: {extracted_1.get('detected_type')} vs {extracted_2.get('detected_type')}")
            if completeness_diff > 10:
                print(f"   - Large completeness difference: {completeness_diff}%")
            if contamination_1 or contamination_2:
                print("   - Birth certificate contamination detected")
        
        # STEP 7: Check for fresh analysis indicators
        print("\n🔄 Fresh Analysis Verification:")
        
        has_real_vision = extracted_2.get('analysis_method') == 'real_vision_native'
        has_confidence = extracted_2.get('confidence', 0) > 0
        has_assessment = len(result_2.get('dra_paula_assessment', '')) > 50
        
        fresh_analysis = has_real_vision and has_confidence and has_assessment
        
        print(f"   - Real vision analysis: {has_real_vision}")
        print(f"   - Confidence score: {extracted_2.get('confidence', 0)}")
        print(f"   - Assessment length: {len(result_2.get('dra_paula_assessment', ''))} chars")
        print(f"   - Fresh analysis confirmed: {fresh_analysis}")
        
        return cache_collision_resolved and fresh_analysis
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_img_7602_cache_collision()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 IMG_7602.png CACHE COLLISION TEST: PASSED")
        print("✅ Cache collision bug appears to be resolved")
    else:
        print("⚠️ IMG_7602.png CACHE COLLISION TEST: NEEDS ATTENTION")
        print("❌ Cache collision issues may still exist")
    print("=" * 70)