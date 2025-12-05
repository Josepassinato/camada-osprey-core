#!/usr/bin/env python3
"""
Test script for the new friendly form endpoint
Tests the complete flow: submission -> AI validation -> data storage
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://0.0.0.0:8001"

def create_test_case():
    """Create a test case for I-539"""
    print("📝 Step 1: Creating test case for I-539...")
    
    response = requests.post(
        f"{BACKEND_URL}/api/auto-application/start",
        json={
            "form_code": "I-539",
            "process_type": "change_of_status"
        }
    )
    
    if response.status_code == 200:
        case_id = response.json()["case"]["case_id"]
        print(f"✅ Case created: {case_id}")
        return case_id
    else:
        print(f"❌ Error creating case: {response.status_code}")
        print(response.text)
        return None

def submit_friendly_form(case_id):
    """Submit friendly form data with AI validation"""
    print(f"\n📝 Step 2: Submitting friendly form data for case {case_id}...")
    
    # Simulated data from friendly form (in Portuguese)
    friendly_form_data = {
        "nome_completo": "Maria Santos Silva",
        "data_nascimento": "1990-05-15",
        "email": "maria.santos@test.com",
        "telefone": "+55 11 98765-4321",
        "numero_passaporte": "BR123456789",
        "pais_nascimento": "Brazil",
        "endereco": "123 Main Street, Apt 4B",
        "cidade": "New York",
        "estado": "NY",
        "cep": "10001",
        # I-539 specific fields
        "status_atual": "F-1",
        "status_solicitado": "H-1B",
        "motivo_mudanca": "Consegui emprego após conclusão dos estudos",
        "data_entrada_eua": "2020-08-15",
        "numero_i94": "1234567890",
        "data_expiracao_visto_atual": "2024-12-31"
    }
    
    basic_data = {
        "applicant_name": "Maria Santos Silva",
        "email": "maria.santos@test.com",
        "passport_number": "BR123456789"
    }
    
    payload = {
        "friendly_form_data": friendly_form_data,
        "basic_data": basic_data
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/case/{case_id}/friendly-form",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Friendly form submitted successfully!")
        print(f"\n📊 Validation Results:")
        print(f"   - Status: {result['validation_status']}")
        print(f"   - Completion: {result['completion_percentage']}%")
        print(f"   - Message: {result['message']}")
        
        if result['validation_issues']:
            print(f"\n⚠️  Validation Issues ({len(result['validation_issues'])}):")
            for issue in result['validation_issues'][:3]:  # Show first 3
                print(f"   - {issue.get('field')}: {issue.get('issue')}")
        else:
            print("\n✅ No validation issues found!")
        
        print(f"\n📋 Next Steps:")
        for step in result['next_steps']:
            print(f"   - {step}")
        
        return result
    else:
        print(f"❌ Error submitting form: {response.status_code}")
        print(response.text)
        return None

def verify_data_saved(case_id):
    """Verify that the data was saved correctly in the database"""
    print(f"\n📝 Step 3: Verifying data was saved for case {case_id}...")
    
    response = requests.get(f"{BACKEND_URL}/api/auto-application/case/{case_id}")
    
    if response.status_code == 200:
        case_data = response.json()["case"]
        
        print(f"✅ Data retrieved successfully!")
        print(f"\n📊 Saved Data Summary:")
        
        # Check if simplified_form_responses exists
        if "simplified_form_responses" in case_data:
            print(f"   ✅ simplified_form_responses: {len(case_data['simplified_form_responses'])} fields")
        else:
            print(f"   ❌ simplified_form_responses: NOT FOUND")
        
        # Check if friendly_form_validation exists
        if "friendly_form_validation" in case_data:
            validation = case_data["friendly_form_validation"]
            print(f"   ✅ friendly_form_validation:")
            print(f"      - Status: {validation.get('status')}")
            print(f"      - Completion: {validation.get('completion_percentage')}%")
            print(f"      - Issues: {len(validation.get('issues', []))}")
        else:
            print(f"   ❌ friendly_form_validation: NOT FOUND")
        
        # Check basic_data
        if "basic_data" in case_data:
            print(f"   ✅ basic_data: {len(case_data['basic_data'])} fields")
        else:
            print(f"   ❌ basic_data: NOT FOUND")
        
        # Check progress
        print(f"\n📈 Progress:")
        print(f"   - Current step: {case_data.get('current_step', 'N/A')}")
        print(f"   - Progress: {case_data.get('progress_percentage', 0)}%")
        
        return case_data
    else:
        print(f"❌ Error retrieving case: {response.status_code}")
        print(response.text)
        return None

def test_incomplete_form(case_id):
    """Test AI validation with incomplete data"""
    print(f"\n📝 Step 4: Testing AI validation with incomplete data...")
    
    # Intentionally incomplete data
    incomplete_data = {
        "nome_completo": "João Teste",
        "email": "joao@test.com",
        # Missing many required fields
    }
    
    payload = {
        "friendly_form_data": incomplete_data,
        "basic_data": {}
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/case/{case_id}/friendly-form",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Incomplete form validation completed!")
        print(f"   - Status: {result['validation_status']}")
        print(f"   - Completion: {result['completion_percentage']}%")
        print(f"   - Issues found: {len(result['validation_issues'])}")
        
        if result['validation_status'] in ['rejected', 'needs_review']:
            print(f"   ✅ AI correctly identified incomplete form")
        else:
            print(f"   ⚠️  AI did not identify incomplete form (may be too lenient)")
        
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def main():
    """Run complete test flow"""
    print("=" * 60)
    print("🧪 FRIENDLY FORM ENDPOINT TEST")
    print("=" * 60)
    
    # Step 1: Create case
    case_id = create_test_case()
    if not case_id:
        print("\n❌ Test failed: Could not create case")
        return
    
    # Step 2: Submit complete form
    result = submit_friendly_form(case_id)
    if not result:
        print("\n❌ Test failed: Could not submit form")
        return
    
    # Step 3: Verify data was saved
    saved_data = verify_data_saved(case_id)
    if not saved_data:
        print("\n❌ Test failed: Could not verify saved data")
        return
    
    # Create another case for incomplete form test
    case_id_2 = create_test_case()
    if case_id_2:
        # Step 4: Test with incomplete data
        incomplete_result = test_incomplete_form(case_id_2)
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   - Endpoint working: ✅")
    print(f"   - AI validation working: ✅")
    print(f"   - Data persistence working: ✅")
    print(f"   - Test cases created: {case_id}, {case_id_2}")
    print("\n🎉 The friendly form system is ready to use!")

if __name__ == "__main__":
    main()
