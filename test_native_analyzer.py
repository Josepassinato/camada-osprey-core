#!/usr/bin/env python3
"""
Test Native Document Analyzer with Real Image
"""

import requests
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_native_analyzer_with_real_image():
    """Test native analyzer with IMG_7602.png"""
    
    print("🎯 Testing Native Document Analyzer with Real Image")
    print("=" * 60)
    
    # Download the real image
    img_url = "https://customer-assets.emergentagent.com/job_formfill-aid/artifacts/hka5y6g5_IMG_7602.png"
    
    try:
        print("📥 Downloading IMG_7602.png...")
        img_response = requests.get(img_url, timeout=30)
        if img_response.status_code == 200:
            img_content = img_response.content
            img_size = len(img_content)
            print(f"✅ Downloaded IMG_7602.png: {img_size} bytes")
            
            # Upload for analysis
            files = {
                'file': ('IMG_7602.png', img_content, 'image/png')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': 'NATIVE-ANALYZER-TEST'
            }
            
            print("📄 Uploading for native analysis...")
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_data = result.get('extracted_data', {})
                
                print("✅ Analysis completed!")
                print(f"📊 Response structure: {list(result.keys())}")
                print(f"📊 Extracted data keys: {list(extracted_data.keys())}")
                print(f"📊 Analysis method: {extracted_data.get('analysis_method', 'NOT_SET')}")
                print(f"📊 Detected type: {extracted_data.get('detected_type', 'NOT_SET')}")
                print(f"📊 Confidence: {extracted_data.get('confidence', 'NOT_SET')}")
                print(f"📊 Valid: {result.get('valid', 'NOT_SET')}")
                print(f"📊 Completeness: {result.get('completeness', 'NOT_SET')}%")
                print(f"📊 Assessment: {result.get('dra_paula_assessment', 'NOT_SET')[:100]}...")
                
                # Check if native analyzer is working
                analysis_method = extracted_data.get('analysis_method', '')
                if 'native' in analysis_method.lower():
                    print("✅ NATIVE ANALYZER IS WORKING!")
                else:
                    print(f"❌ NATIVE ANALYZER NOT DETECTED: method='{analysis_method}'")
                    
            else:
                print(f"❌ Upload failed: HTTP {response.status_code}")
                print(f"Error: {response.text[:200]}")
                
        else:
            print(f"❌ Download failed: HTTP {img_response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_native_analyzer_with_real_image()