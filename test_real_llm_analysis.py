#!/usr/bin/env python3
"""
Test Real LLM Analysis vs Fallback
"""

import requests
import os
import json

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://formfill-aid.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_real_vs_fallback_analysis():
    """Test to determine if real LLM analysis is working or using fallback"""
    
    print("🎯 Testing Real LLM Analysis vs Fallback")
    print("=" * 60)
    
    # Test 1: Real image (PNG) - should work with real LLM
    print("📄 Test 1: Real PNG Image (IMG_7602.png)")
    img_url = "https://customer-assets.emergentagent.com/job_formfill-aid/artifacts/hka5y6g5_IMG_7602.png"
    
    try:
        img_response = requests.get(img_url, timeout=30)
        if img_response.status_code == 200:
            img_content = img_response.content
            
            files = {
                'file': ('IMG_7602.png', img_content, 'image/png')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': 'REAL-LLM-TEST-PNG'
            }
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = result.get('extracted_data', {})
                
                print(f"✅ PNG Analysis completed")
                print(f"   Analysis method: {extracted_data.get('analysis_method', 'NOT_SET')}")
                print(f"   Confidence: {extracted_data.get('confidence', 'NOT_SET')}")
                print(f"   Detected type: {extracted_data.get('detected_type', 'NOT_SET')}")
                print(f"   Has error field: {'error' in extracted_data}")
                print(f"   Full text length: {len(extracted_data.get('full_text_extracted', ''))}")
                
                # Check if it's real analysis or fallback
                if 'error' in extracted_data:
                    print(f"   🔍 FALLBACK DETECTED: {extracted_data.get('error', '')}")
                elif extracted_data.get('analysis_method') == 'native_llm_restored':
                    print(f"   ✅ REAL LLM ANALYSIS WORKING!")
                else:
                    print(f"   ⚠️ UNKNOWN STATUS")
                    
            else:
                print(f"❌ PNG test failed: HTTP {response.status_code}")
                
    except Exception as e:
        print(f"❌ PNG test exception: {str(e)}")
    
    print()
    
    # Test 2: PDF file - should fail with real LLM and use fallback
    print("📄 Test 2: PDF File (should use fallback)")
    
    pdf_content = b"PDF test content for fallback analysis" + b"x" * 60000  # Make it large enough
    
    files = {
        'file': ('test_document.pdf', pdf_content, 'application/pdf')
    }
    data = {
        'document_type': 'passport',
        'visa_type': 'H-1B',
        'case_id': 'REAL-LLM-TEST-PDF'
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/documents/analyze-with-ai",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            extracted_data = result.get('extracted_data', {})
            
            print(f"✅ PDF Analysis completed")
            print(f"   Analysis method: {extracted_data.get('analysis_method', 'NOT_SET')}")
            print(f"   Confidence: {extracted_data.get('confidence', 'NOT_SET')}")
            print(f"   Detected type: {extracted_data.get('detected_type', 'NOT_SET')}")
            print(f"   Has error field: {'error' in extracted_data}")
            
            # Check if it's fallback (expected for PDF)
            if 'error' in extracted_data:
                print(f"   ✅ EXPECTED FALLBACK: {extracted_data.get('error', '')}")
            elif extracted_data.get('analysis_method') == 'fallback_native':
                print(f"   ✅ EXPECTED FALLBACK ANALYSIS")
            else:
                print(f"   ⚠️ UNEXPECTED: PDF should use fallback")
                
        else:
            print(f"❌ PDF test failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ PDF test exception: {str(e)}")

if __name__ == "__main__":
    test_real_vs_fallback_analysis()