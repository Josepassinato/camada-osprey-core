#!/usr/bin/env python3
"""
DEBUG I-765 EAD Test - Focused debugging of data persistence issues
"""

import requests
import json
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://formcraft-43.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔍 DEBUG I-765 EAD TEST")
print(f"🌐 API BASE: {API_BASE}")
print("="*80)

def debug_case_data_persistence():
    """Debug why EAD data is not persisting correctly"""
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'DebugTester/1.0'
    })
    
    try:
        # Step 1: Create case
        print("\n🔍 STEP 1: Create I-765 case")
        case_data = {
            "form_code": "I-765",
            "process_type": "ead_application"
        }
        
        start_response = session.post(f"{API_BASE}/auto-application/start", json=case_data)
        print(f"Status: {start_response.status_code}")
        print(f"Response: {json.dumps(start_response.json(), indent=2)}")
        
        if start_response.status_code != 200:
            print("❌ Failed to create case")
            return
        
        start_data = start_response.json()
        case_info = start_data.get('case', {})
        case_id = case_info.get('case_id')
        
        if not case_id:
            print("❌ No case ID returned")
            return
        
        print(f"✅ Case created: {case_id}")
        
        # Step 2: Add EAD data
        print(f"\n🔍 STEP 2: Add EAD data to case {case_id}")
        ead_data = {
            "ead_data": {
                "eligibility_category": "(c)(3)(B) F-1 OPT",
                "school_name": "Massachusetts Institute of Technology",
                "sevis_number": "N5544332211",
                "degree_completed": "Master of Science in Computer Science",
                "completion_date": "2025-05-15",
                "opt_start_date": "2025-06-15",
                "opt_end_date": "2026-06-14",
                "employer_name": "TechCorp Inc.",
                "employer_address": "500 Tech Park, Boston, MA 02115",
                "job_title": "Software Engineer",
                "job_description": "Develop software applications using Python, Java, and cloud technologies"
            },
            "progress_percentage": 50
        }
        
        ead_response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=ead_data)
        print(f"Status: {ead_response.status_code}")
        print(f"Response: {json.dumps(ead_response.json(), indent=2)}")
        
        # Step 3: Verify data persistence
        print(f"\n🔍 STEP 3: Verify data persistence for case {case_id}")
        get_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
        print(f"Status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            get_data = get_response.json()
            print(f"Full response: {json.dumps(get_data, indent=2)}")
            
            # Check if EAD data is present
            case_data = get_data.get('case', get_data)
            ead_data_stored = case_data.get('ead_data', {})
            
            print(f"\n🔍 EAD Data Analysis:")
            print(f"EAD data present: {'✓' if ead_data_stored else '✗'}")
            if ead_data_stored:
                print(f"School name: {ead_data_stored.get('school_name', 'NOT FOUND')}")
                print(f"SEVIS number: {ead_data_stored.get('sevis_number', 'NOT FOUND')}")
                print(f"Eligibility category: {ead_data_stored.get('eligibility_category', 'NOT FOUND')}")
            else:
                print("❌ No EAD data found in stored case")
                print("Available fields in case:")
                for key in case_data.keys():
                    print(f"  - {key}: {type(case_data[key])}")
        else:
            print(f"❌ Failed to retrieve case: {get_response.text}")
        
        # Step 4: Test user story
        print(f"\n🔍 STEP 4: Add user story to case {case_id}")
        story_data = {
            "user_story_text": "Completei meu mestrado em Ciência da Computação no MIT em maio de 2025. Agora desejo aplicar para OPT (Optional Practical Training) para trabalhar nos Estados Unidos por 12 meses em minha área de estudo. Tenho uma oferta de emprego da empresa TechCorp em Boston para posição de Software Engineer.",
            "simplified_form_responses": {
                "reason_application": "OPT após conclusão do mestrado - MIT",
                "employment": "Oferta da TechCorp Inc. - Software Engineer",
                "relation_to_study": "Trabalho diretamente relacionado à Ciência da Computação",
                "duration": "12 meses (período padrão OPT)"
            },
            "progress_percentage": 70
        }
        
        story_response = session.put(f"{API_BASE}/auto-application/case/{case_id}", json=story_data)
        print(f"Status: {story_response.status_code}")
        print(f"Response: {json.dumps(story_response.json(), indent=2)}")
        
        # Step 5: Final verification
        print(f"\n🔍 STEP 5: Final verification for case {case_id}")
        final_response = session.get(f"{API_BASE}/auto-application/case/{case_id}")
        
        if final_response.status_code == 200:
            final_data = final_response.json()
            case_data = final_data.get('case', final_data)
            
            print(f"\n🔍 Final Data Analysis:")
            print(f"Case ID: {case_data.get('case_id')}")
            print(f"Form code: {case_data.get('form_code')}")
            print(f"Process type: {case_data.get('process_type')}")
            print(f"Progress: {case_data.get('progress_percentage')}%")
            print(f"Status: {case_data.get('status')}")
            
            # Check all data fields
            print(f"\n🔍 Data Fields Present:")
            print(f"Basic data: {'✓' if case_data.get('basic_data') else '✗'}")
            print(f"EAD data: {'✓' if case_data.get('ead_data') else '✗'}")
            print(f"User story: {'✓' if case_data.get('user_story_text') else '✗'}")
            print(f"Simplified responses: {'✓' if case_data.get('simplified_form_responses') else '✗'}")
            
            if case_data.get('user_story_text'):
                story = case_data.get('user_story_text', '')
                print(f"Story contains MIT: {'✓' if 'MIT' in story else '✗'}")
                print(f"Story contains OPT: {'✓' if 'OPT' in story else '✗'}")
                print(f"Story contains TechCorp: {'✓' if 'TechCorp' in story else '✗'}")
            
            if case_data.get('simplified_form_responses'):
                responses = case_data.get('simplified_form_responses', {})
                employment = responses.get('employment', '')
                print(f"Employment contains TechCorp: {'✓' if 'TechCorp' in employment else '✗'}")
        
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")

if __name__ == "__main__":
    debug_case_data_persistence()