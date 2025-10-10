#!/usr/bin/env python3
"""
Simple test to verify passport document analysis with proper case setup
"""

import requests
import json
import uuid
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_passport_with_proper_case():
    """Test passport document analysis with proper case setup"""
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'PassportTester/1.0'
    })
    
    # Step 1: Create a proper case
    print("📋 Creating test case...")
    case_data = {
        "form_code": "H-1B",
        "session_token": f"test_session_{uuid.uuid4().hex[:8]}"
    }
    
    case_response = session.post(f"{API_BASE}/auto-application/start", json=case_data)
    
    if case_response.status_code != 200:
        print(f"❌ Failed to create case: {case_response.status_code}")
        return False
    
    case_result = case_response.json()
    case_id = case_result.get('case', {}).get('case_id')
    print(f"✅ Case created: {case_id}")
    
    # Step 2: Add basic data to the case
    print("📝 Adding basic data to case...")
    basic_data = {
        "firstName": "Carlos",
        "lastName": "Silva", 
        "email": "carlos.silva@test.com",
        "phone": "+55 11 99999-9999",
        "dateOfBirth": "1990-05-15",
        "placeOfBirth": "São Paulo, SP, Brasil",
        "nationality": "Brazilian"
    }
    
    update_response = session.patch(
        f"{API_BASE}/auto-application/case/{case_id}",
        json={
            "form_data": {"basic_info": basic_data},
            "current_step": "documents"
        }
    )
    
    if update_response.status_code != 200:
        print(f"❌ Failed to update case: {update_response.status_code}")
        return False
    
    print("✅ Basic data added to case")
    
    # Step 3: Test document analysis with the passport image
    print("📥 Testing document analysis with passport image...")
    
    # Download the passport image
    passport_url = "https://customer-assets.emergentagent.com/job_formfill-aid/artifacts/kxf1p849_IMG_5082.jpeg"
    
    try:
        image_response = requests.get(passport_url, timeout=30)
        
        if image_response.status_code == 200:
            print(f"✅ Passport image downloaded: {len(image_response.content)} bytes")
            
            # Analyze the document
            files = {
                'file': ('brazilian_passport.jpeg', image_response.content, 'image/jpeg')
            }
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': case_id
            }
            
            headers = {k: v for k, v in session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✅ Document analysis completed")
                print(f"   Valid: {result.get('valid', False)}")
                print(f"   Legible: {result.get('legible', False)}")
                print(f"   Completeness: {result.get('completeness', 0)}%")
                print(f"   Issues: {len(result.get('issues', []))}")
                print(f"   Policy Score: {result.get('policy_score', 0)}")
                print(f"   Policy Decision: {result.get('policy_decision', 'N/A')}")
                
                # Show assessment preview
                assessment = result.get('dra_paula_assessment', '')
                if assessment:
                    print(f"   Assessment Preview: {assessment[:200]}...")
                
                # Show extracted data keys
                extracted_data = result.get('extracted_data', {})
                if extracted_data:
                    print(f"   Extracted Data Keys: {list(extracted_data.keys())}")
                
                return True
            else:
                print(f"❌ Document analysis failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
        else:
            print(f"❌ Failed to download passport image: {image_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🛂 TESTE SIMPLES: Análise de Passaporte com Caso Válido")
    print("=" * 60)
    
    success = test_passport_with_proper_case()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TESTE CONCLUÍDO: Sistema funcionando corretamente")
    else:
        print("❌ TESTE FALHOU: Verificar logs para detalhes")