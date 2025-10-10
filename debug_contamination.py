#!/usr/bin/env python3
"""
Debug contamination detection in IMG_7602.png analysis
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def debug_contamination():
    """Debug what contamination is being detected"""
    
    print("🔍 DEBUG: Contamination Detection in IMG_7602.png")
    print("=" * 60)
    
    # Setup session
    session = requests.Session()
    
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
            print("⚠️ Authentication failed")
    except Exception as e:
        print(f"⚠️ Auth error: {e}")
    
    try:
        # Download IMG_7602.png
        print("\n📥 Downloading IMG_7602.png...")
        
        img_url = "https://customer-assets.emergentagent.com/job_formfill-aid/artifacts/hka5y6g5_IMG_7602.png"
        img_response = requests.get(img_url, timeout=30)
        
        if img_response.status_code != 200:
            print(f"❌ Failed to download: HTTP {img_response.status_code}")
            return
        
        img_content = img_response.content
        print(f"✅ Downloaded: {len(img_content):,} bytes")
        
        # Analyze IMG_7602.png
        print("\n📄 Analyzing IMG_7602.png...")
        
        files = {
            'file': ('IMG_7602.png', img_content, 'image/png')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'DEBUG-IMG-7602'
        }
        
        headers = {k: v for k, v in session.headers.items() if k.lower() != 'content-type'}
        
        response = requests.post(
            f"{API_BASE}/documents/analyze-with-ai",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Analysis failed: HTTP {response.status_code}")
            print(f"Error: {response.text[:500]}")
            return
        
        result = response.json()
        
        print("✅ Analysis complete. Checking for contamination...")
        
        # Check for birth certificate keywords
        birth_keywords = ['nascimento', 'birth', 'cartório', 'joão', 'silva']
        result_str = str(result).lower()
        
        print(f"\n🔍 Contamination Analysis:")
        print(f"Full result length: {len(str(result))} characters")
        
        found_keywords = []
        for keyword in birth_keywords:
            if keyword in result_str:
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"❌ Contamination detected! Found keywords: {found_keywords}")
            
            # Find where these keywords appear
            for keyword in found_keywords:
                positions = []
                start = 0
                while True:
                    pos = result_str.find(keyword, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
                
                print(f"\n🔍 Keyword '{keyword}' found at positions: {positions}")
                
                # Show context around each occurrence
                for pos in positions[:3]:  # Show first 3 occurrences
                    start_context = max(0, pos - 50)
                    end_context = min(len(result_str), pos + 50)
                    context = result_str[start_context:end_context]
                    print(f"   Context: ...{context}...")
        else:
            print("✅ No contamination detected!")
        
        # Show key parts of the result
        print(f"\n📊 Analysis Result Summary:")
        print(f"   - Valid: {result.get('valid', False)}")
        print(f"   - Legible: {result.get('legible', False)}")
        print(f"   - Completeness: {result.get('completeness', 0)}%")
        print(f"   - Issues count: {len(result.get('issues', []))}")
        
        extracted_data = result.get('extracted_data', {})
        print(f"   - Detected type: {extracted_data.get('detected_type', 'unknown')}")
        print(f"   - Analysis method: {extracted_data.get('analysis_method', 'unknown')}")
        print(f"   - Confidence: {extracted_data.get('confidence', 0)}")
        
        # Show assessment
        assessment = result.get('dra_paula_assessment', '')
        print(f"   - Assessment length: {len(assessment)} chars")
        if assessment:
            print(f"   - Assessment preview: {assessment[:200]}...")
        
        # Show issues
        issues = result.get('issues', [])
        if issues:
            print(f"\n📋 Issues found:")
            for i, issue in enumerate(issues[:5]):  # Show first 5 issues
                print(f"   {i+1}. {issue}")
        
        # Show extracted data details
        if extracted_data:
            print(f"\n📄 Extracted Data Keys: {list(extracted_data.keys())}")
            
            # Show some extracted data (excluding large fields)
            for key, value in extracted_data.items():
                if key not in ['full_text_extracted', 'security_features'] and len(str(value)) < 200:
                    print(f"   - {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        return None

if __name__ == "__main__":
    result = debug_contamination()
    
    if result:
        print("\n" + "=" * 60)
        print("🎯 DEBUG COMPLETE")
        print("Check the contamination analysis above for details.")
    else:
        print("\n" + "=" * 60)
        print("❌ DEBUG FAILED")
    print("=" * 60)