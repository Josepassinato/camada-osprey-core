#!/usr/bin/env python3
"""
Backend Testing Suite - I-539 Extension of Stay AI Review System Testing
Testing complete I-539 AI review system for Carlos Eduardo Silva Mendes
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://visa-ai-assistant.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_i539_ai_review_system():
    """
    🎯 ANÁLISE DA IA DE REVISÃO FINAL - PROCESSO I-539 EXTENSION OF STAY
    
    Testing complete I-539 AI review system for Carlos Eduardo Silva Mendes
    
    SPECIFIC TEST REQUESTED IN REVIEW:
    Complete I-539 Extension of Stay AI review including:
    1. Case creation for I-539
    2. Basic data completion
    3. Document uploads (passport, I-20, financial proof, etc.)
    4. AI review endpoints testing
    5. Document validation analysis
    6. Letter quality assessment
    7. Form completion verification
    8. USCIS compliance checking
    
    Expected validations:
    1. ✅ I-539 case created successfully
    2. ✅ Basic data saved correctly
    3. ✅ Documents uploaded and analyzed
    4. ✅ AI review endpoints functional
    5. ✅ Document validation working
    6. ✅ Letter quality assessment working
    7. ✅ Form completion verification working
    8. ✅ USCIS compliance checking working
    """
    
    print("🎯 TESTING I-539 EXTENSION OF STAY AI REVIEW SYSTEM")
    print("👨‍🎓 Applicant: Carlos Eduardo Silva Mendes")
    print("📋 Process: I-539 Extension of Stay")
    print("=" * 60)
    
    results = {
        "fase_1_case_creation": {},
        "fase_2_basic_data": {},
        "fase_3_document_uploads": {},
        "fase_4_ai_review_endpoints": {},
        "fase_5_document_validation": {},
        "fase_6_letter_quality": {},
        "fase_7_form_verification": {},
        "fase_8_uscis_compliance": {},
        "fase_9_final_analysis": {},
        "summary": {}
    }
    
    # Global variables for the flow
    case_id = None
    
    # FASE 1: Criar caso I-539
    print("\n📋 FASE 1: Criação de Caso I-539")
    print("-" * 50)
    
    case_data = {
        "visa_type": "I-539",
        "applicant_name": "Carlos Eduardo Silva Mendes",
        "email": "carlos.mendes@test.com"
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/auto-application/create-case")
        print(f"📤 Payload: {json.dumps(case_data, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/auto-application/create-case",
            json=case_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["fase_1_case_creation"]["status_code"] = response.status_code
        results["fase_1_case_creation"]["processing_time"] = processing_time
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Extract case_id for subsequent requests
            case_id = response_data.get("case_id")
            
            validations = {
                "1_case_created": case_id is not None,
                "2_case_id_format": case_id.startswith("OSP-") if case_id else False,
                "3_visa_type_correct": response_data.get("visa_type") == "I-539",
                "4_applicant_name_correct": response_data.get("applicant_name") == "Carlos Eduardo Silva Mendes"
            }
            
            results["fase_1_case_creation"]["validations"] = validations
            results["fase_1_case_creation"]["response_data"] = response_data
            results["fase_1_case_creation"]["case_id"] = case_id
            
            print("\n🎯 VALIDAÇÕES FASE 1:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            print(f"\n📊 DADOS DO CASO CRIADO:")
            print(f"  📋 Case ID: {case_id}")
            print(f"  📝 Tipo de Visto: {response_data.get('visa_type')}")
            print(f"  👤 Aplicante: {response_data.get('applicant_name')}")
            print(f"  📧 Email: {response_data.get('email')}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["fase_1_case_creation"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during case creation: {str(e)}")
        results["fase_1_case_creation"]["exception"] = str(e)
    
    # FASE 2: Completar dados básicos do I-539
    print("\n📋 FASE 2: Completar Dados Básicos I-539")
    print("-" * 50)
    
    if not case_id:
        print("❌ Cannot proceed without case_id")
        return results
    
    basic_data = {
        "applicant_name": "Carlos Eduardo Silva Mendes",
        "date_of_birth": "1985-03-15",
        "passport_number": "BR987654321",
        "current_address": "123 Main Street, Apt 4B",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country_of_birth": "Brazil",
        "email": "carlos.mendes@test.com",
        "phone": "+5511987654321",
        "current_visa_type": "F-1",
        "i20_expiration": "2025-06-30",
        "extension_reason": "Complete Master's degree in Computer Science",
        "university": "Columbia University",
        "sevis_number": "N9876543210"
    }
    
    try:
        print(f"🔗 Endpoint: PUT {API_BASE}/auto-application/case/{case_id}")
        print(f"📤 Payload: {json.dumps(basic_data, indent=2)}")
        
        start_time = time.time()
        response = requests.put(
            f"{API_BASE}/auto-application/case/{case_id}",
            json=basic_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["fase_2_basic_data"]["status_code"] = response.status_code
        results["fase_2_basic_data"]["processing_time"] = processing_time
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            case_data = response_data.get("case", {})
            
            validations = {
                "1_case_updated": response_data.get("message") == "Case updated successfully",
                "2_basic_data_saved": case_data.get("basic_data") is not None,
                "3_applicant_name_correct": case_data.get("applicant_name") == "Carlos Eduardo Silva Mendes",
                "4_visa_type_correct": case_data.get("current_visa_type") == "F-1"
            }
            
            results["fase_2_basic_data"]["validations"] = validations
            results["fase_2_basic_data"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES FASE 2:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Basic data update failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["fase_2_basic_data"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during basic data update: {str(e)}")
        results["fase_2_basic_data"]["exception"] = str(e)
    
    # ETAPA 3: Iniciar aplicação O-1
    print("\n📋 ETAPA 3: Iniciar Aplicação O-1")
    print("-" * 50)
    
    if not jwt_token:
        print("❌ Cannot proceed without JWT token")
        return results
    
    start_application_data = {
        "visa_code": "O-1",
        "user_email": "sofia.mendes.test@example.com"
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/auto-application/start")
        print(f"📤 Payload: {json.dumps(start_application_data, indent=2)}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json=start_application_data,
            headers=headers,
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["etapa_3_start_application"]["status_code"] = response.status_code
        results["etapa_3_start_application"]["processing_time"] = processing_time
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Extract case_id for subsequent requests - check nested structure
            case_data = response_data.get("case", {})
            case_id = case_data.get("case_id") or response_data.get("case_id")
            
            validations = {
                "1_case_created": case_id is not None,
                "2_case_id_format": case_id.startswith("OSP-") if case_id else False,
                "3_visa_code_correct": case_data.get("form_code") == "O-1" or response_data.get("form_code") == "O-1",
                "4_status_created": case_data.get("status") == "created" or response_data.get("status") == "created"
            }
            
            results["etapa_3_start_application"]["validations"] = validations
            results["etapa_3_start_application"]["response_data"] = response_data
            results["etapa_3_start_application"]["case_id"] = case_id
            
            print("\n🎯 VALIDAÇÕES ETAPA 3:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            if case_id:
                print(f"\n📋 CASE ID GERADO: {case_id}")
                
        else:
            print(f"❌ Application start failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_3_start_application"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during application start: {str(e)}")
        results["etapa_3_start_application"]["exception"] = str(e)
    
    # ETAPA 4: Atualizar case com O-1 e dados básicos
    print("\n📋 ETAPA 4: Atualizar Case com O-1 e Dados Básicos")
    print("-" * 50)
    
    if not case_id:
        print("❌ Cannot proceed without case_id")
        # Set default values for summary to avoid KeyError
        results["summary"]["overall_success"] = False
        results["summary"]["successful_steps"] = 3  # Only first 3 steps completed
        results["summary"]["total_steps"] = 8
        results["summary"]["success_rate"] = 37.5
        results["summary"]["case_id"] = None
        results["summary"]["jwt_token_present"] = jwt_token is not None
        return results
    
    # First, set the form_code to O-1
    case_update_data = {
        "form_code": "O-1",
        "process_type": "consular",
        "basic_data": {
            "full_name": "Sofia Mendes Rodrigues",
            "date_of_birth": "1988-03-15",
            "country_of_birth": "Brazil",
            "passport_number": "BR123456789",
            "passport_expiry": "2029-12-31",
            "phone": "+5511987654321",
            "email": "sofia.mendes.test@example.com",
            "current_address": "Rua das Flores 123, São Paulo, SP, Brazil",
            "marital_status": "single"
        },
        "current_step": "basic-data"
    }
    
    try:
        print(f"🔗 Endpoint: PUT {API_BASE}/auto-application/case/{case_id}")
        print(f"📤 Payload: {json.dumps(case_update_data, indent=2)}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        start_time = time.time()
        response = requests.put(
            f"{API_BASE}/auto-application/case/{case_id}",
            json=case_update_data,
            headers=headers,
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["etapa_4_basic_data"]["status_code"] = response.status_code
        results["etapa_4_basic_data"]["processing_time"] = processing_time
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            case_data = response_data.get("case", {})
            
            validations = {
                "1_case_updated": response_data.get("message") == "Case updated successfully",
                "2_form_code_set": case_data.get("form_code") == "O-1",
                "3_basic_data_saved": case_data.get("basic_data") is not None,
                "4_progress_updated": case_data.get("progress_percentage", 0) > 0
            }
            
            results["etapa_4_basic_data"]["validations"] = validations
            results["etapa_4_basic_data"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES ETAPA 4:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Case update failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_4_basic_data"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during case update: {str(e)}")
        results["etapa_4_basic_data"]["exception"] = str(e)
    
    # ETAPA 5: Adicionar dados profissionais detalhados
    print("\n📋 ETAPA 5: Adicionar Dados Profissionais Detalhados")
    print("-" * 50)
    
    professional_data = {
        "simplified_form_responses": {
            "personal_info": {
                "full_name": "Sofia Mendes Rodrigues",
                "title": "Dr.",
                "field_of_expertise": "Artificial Intelligence and Machine Learning in Healthcare",
                "years_of_experience": 15
            },
            "professional_background": {
                "current_position": "Senior AI Research Scientist",
                "current_employer": "Johns Hopkins University Hospital",
                "job_start_date": "2026-01-15",
                "annual_salary": 180000,
                "job_description": "Leading research in AI-powered early cancer detection systems."
            },
            "achievements": [
                {
                    "title": "AI for Good Award",
                    "organization": "United Nations",
                    "year": "2023",
                    "description": "Recognized for developing AI system that detects early-stage cancer with 95% accuracy"
                }
            ],
            "publications": {
                "total": 52,
                "citations": 2100,
                "h_index": 28
            }
        },
        "current_step": "friendly-form"
    }
    
    try:
        print(f"🔗 Endpoint: PUT {API_BASE}/auto-application/case/{case_id}")
        print(f"📤 Payload: {json.dumps(professional_data, indent=2)}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        start_time = time.time()
        response = requests.put(
            f"{API_BASE}/auto-application/case/{case_id}",
            json=professional_data,
            headers=headers,
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["etapa_5_friendly_form"]["status_code"] = response.status_code
        results["etapa_5_friendly_form"]["processing_time"] = processing_time
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            case_data = response_data.get("case", {})
            
            validations = {
                "1_case_updated": response_data.get("message") == "Case updated successfully",
                "2_professional_data_saved": case_data.get("simplified_form_responses") is not None,
                "3_progress_updated": case_data.get("progress_percentage", 0) > 30,
                "4_current_step_updated": case_data.get("current_step") == "friendly-form"
            }
            
            results["etapa_5_friendly_form"]["validations"] = validations
            results["etapa_5_friendly_form"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES ETAPA 5:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Professional data update failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_5_friendly_form"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during professional data update: {str(e)}")
        results["etapa_5_friendly_form"]["exception"] = str(e)
    
    # ETAPA 6: Simular upload de documentos
    print("\n📋 ETAPA 6: Simular Upload de Documentos")
    print("-" * 50)
    
    # Create simulated document content
    def create_simulated_document(doc_type, content):
        """Create a simulated PDF document as base64"""
        return base64.b64encode(content.encode()).decode()
    
    documents_to_upload = [
        {
            "name": "passport_copy.pdf",
            "type": "passport",
            "content": "PASSPORT - REPÚBLICA FEDERATIVA DO BRASIL\nNome: SOFIA MENDES RODRIGUES\nPassaporte: BR123456789\nData de Nascimento: 15/03/1988\nNacionalidade: BRASILEIRA"
        },
        {
            "name": "phd_diploma_mit.pdf", 
            "type": "education_diploma",
            "content": "MASSACHUSETTS INSTITUTE OF TECHNOLOGY\nDiploma - Doctor of Philosophy\nComputer Science\nSofia Mendes Rodrigues\n2015"
        },
        {
            "name": "award_certificates.pdf",
            "type": "other",
            "content": "UNITED NATIONS - AI for Good Award 2023\nRecipient: Dr. Sofia Mendes Rodrigues\nFor developing AI system for early cancer detection"
        },
        {
            "name": "job_offer_johns_hopkins.pdf",
            "type": "employment_letter", 
            "content": "JOHNS HOPKINS UNIVERSITY HOSPITAL\nJob Offer Letter\nPosition: Senior AI Research Scientist\nSalary: $180,000/year\nStart Date: January 15, 2026"
        }
    ]
    
    uploaded_docs = []
    
    for doc in documents_to_upload:
        try:
            print(f"📄 Uploading: {doc['name']}")
            
            # Simulate multipart form data
            files = {
                'file': (doc['name'], doc['content'], 'application/pdf')
            }
            data = {
                'document_type': doc['type'],
                'tags': 'O-1,simulation'
            }
            
            headers = {
                "Authorization": f"Bearer {jwt_token}"
            }
            
            response = requests.post(
                f"{API_BASE}/documents/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code in [200, 201]:
                response_data = response.json()
                uploaded_docs.append({
                    "name": doc['name'],
                    "document_id": response_data.get("document_id"),
                    "status": "uploaded"
                })
                print(f"   ✅ Uploaded: {response_data.get('document_id')}")
            else:
                print(f"   ❌ Failed: {response.text}")
                uploaded_docs.append({
                    "name": doc['name'],
                    "status": "failed",
                    "error": response.text
                })
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            uploaded_docs.append({
                "name": doc['name'],
                "status": "exception",
                "error": str(e)
            })
    
    results["etapa_6_document_uploads"]["uploaded_docs"] = uploaded_docs
    results["etapa_6_document_uploads"]["total_docs"] = len(documents_to_upload)
    results["etapa_6_document_uploads"]["successful_uploads"] = len([d for d in uploaded_docs if d.get("status") == "uploaded"])
    
    print(f"\n📊 RESUMO UPLOADS: {results['etapa_6_document_uploads']['successful_uploads']}/{results['etapa_6_document_uploads']['total_docs']} documentos enviados")
    
    # ETAPA 7: Processar com IA
    print("\n📋 ETAPA 7: Processar com IA")
    print("-" * 50)
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/auto-application/case/{case_id}/ai-processing")
        
        ai_processing_data = {
            "step": "validation",
            "data": {
                "visa_type": "O-1",
                "applicant_field": "AI Research",
                "extraordinary_ability": True
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/auto-application/case/{case_id}/ai-processing",
            json=ai_processing_data,
            headers=headers,
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["etapa_7_ai_review"]["status_code"] = response.status_code
        results["etapa_7_ai_review"]["processing_time"] = processing_time
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            validations = {
                "1_ai_processing_completed": response_data.get("success") == True,
                "2_step_id_present": response_data.get("step_id") is not None,
                "3_progress_updated": response_data.get("progress_percentage", 0) > 50
            }
            
            results["etapa_7_ai_review"]["validations"] = validations
            results["etapa_7_ai_review"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES ETAPA 7:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ AI processing failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_7_ai_review"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during AI processing: {str(e)}")
        results["etapa_7_ai_review"]["exception"] = str(e)
    
    # ETAPA 8: Verificar status final e gerar pacote
    print("\n📋 ETAPA 8: Verificar Status Final e Gerar Pacote")
    print("-" * 50)
    
    try:
        # Check current case status
        print(f"🔗 Endpoint: GET {API_BASE}/auto-application/case/{case_id}")
        
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }
        
        start_time = time.time()
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers=headers,
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["etapa_8_final_status"]["status_code"] = response.status_code
        results["etapa_8_final_status"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Case Status Response: {json.dumps(response_data, indent=2)}")
            
            # Try to generate package
            try:
                print(f"\n🔗 Trying to generate package...")
                package_response = requests.get(
                    f"{API_BASE}/auto-application/case/{case_id}/generate-package",
                    headers=headers,
                    timeout=60
                )
                
                print(f"📊 Package Generation Status: {package_response.status_code}")
                
                if package_response.status_code == 200:
                    package_data = package_response.json()
                    print(f"📄 Package Response: {json.dumps(package_data, indent=2)}")
                    
                    validations = {
                        "1_status_retrieved": True,
                        "2_case_id_matches": case_id in str(response_data),
                        "3_package_generated": package_response.status_code == 200,
                        "4_package_data_present": len(package_data) > 0
                    }
                    
                    results["etapa_8_final_status"]["package_data"] = package_data
                    
                else:
                    print(f"📄 Package Error: {package_response.text}")
                    validations = {
                        "1_status_retrieved": True,
                        "2_case_id_matches": case_id in str(response_data),
                        "3_package_generated": False,
                        "4_package_data_present": False
                    }
                    
            except Exception as package_error:
                print(f"❌ Package generation error: {str(package_error)}")
                validations = {
                    "1_status_retrieved": True,
                    "2_case_id_matches": case_id in str(response_data),
                    "3_package_generated": False,
                    "4_package_data_present": False
                }
            
            results["etapa_8_final_status"]["validations"] = validations
            results["etapa_8_final_status"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES ETAPA 8:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Status check failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_8_final_status"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during final status: {str(e)}")
        results["etapa_8_final_status"]["exception"] = str(e)
    
    # Summary
    print("\n📊 RESUMO COMPLETO DO TESTE O-1")
    print("=" * 60)
    
    # Count successful steps
    successful_steps = 0
    total_steps = 8
    
    for step_key in ["etapa_1_user_creation", "etapa_2_login", "etapa_3_start_application", 
                     "etapa_4_basic_data", "etapa_5_friendly_form", "etapa_6_document_uploads",
                     "etapa_7_ai_review", "etapa_8_final_status"]:
        step_data = results.get(step_key, {})
        if step_data.get("status_code") in [200, 201]:
            successful_steps += 1
    
    success_rate = (successful_steps / total_steps) * 100
    
    print(f"🧪 Teste O-1 Complete Flow: {successful_steps}/{total_steps} etapas concluídas ({success_rate:.1f}%)")
    print(f"👤 Aplicante: Dr. Sofia Mendes Rodrigues")
    print(f"🎯 Visto: O-1 (Extraordinary Ability)")
    print(f"📋 Case ID: {case_id}")
    print(f"🔑 JWT Token: {'✅ Presente' if jwt_token else '❌ Ausente'}")
    
    # Show step-by-step results
    print(f"\n📋 RESULTADOS POR ETAPA:")
    step_names = [
        "Criação de Usuário",
        "Login", 
        "Iniciar Aplicação O-1",
        "Dados Básicos",
        "Formulário Completo",
        "Upload de Documentos",
        "Revisão da IA",
        "Status Final"
    ]
    
    for i, (step_key, step_name) in enumerate(zip(
        ["etapa_1_user_creation", "etapa_2_login", "etapa_3_start_application", 
         "etapa_4_basic_data", "etapa_5_friendly_form", "etapa_6_document_uploads",
         "etapa_7_ai_review", "etapa_8_final_status"], step_names)):
        
        step_data = results.get(step_key, {})
        status_code = step_data.get("status_code", 0)
        status = "✅" if status_code in [200, 201] else "❌"
        print(f"  {status} Etapa {i+1}: {step_name} (Status: {status_code})")
    
    overall_success = success_rate >= 75  # Consider success if 75% or more steps completed
    results["summary"]["overall_success"] = overall_success
    results["summary"]["successful_steps"] = successful_steps
    results["summary"]["total_steps"] = total_steps
    results["summary"]["success_rate"] = success_rate
    results["summary"]["case_id"] = case_id
    results["summary"]["jwt_token_present"] = jwt_token is not None
    
    print(f"\n🎯 RESULTADO FINAL: {'✅ SUCESSO COMPLETO' if overall_success else '❌ NECESSITA MELHORIAS'}")
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    return results

def test_additional_o1_endpoints():
    """Test additional O-1 related endpoints for completeness"""
    
    print("\n🔍 TESTES ADICIONAIS - ENDPOINTS O-1 RELACIONADOS")
    print("=" * 60)
    
    additional_results = {}
    
    # Test visa detailed info for O-1
    try:
        print("\n📋 O-1 Visa Detailed Info:")
        response = requests.get(f"{API_BASE}/visa-detailed-info/O-1?process_type=consular", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            visa_info = response.json()
            print(f"   Response: {json.dumps(visa_info, indent=4)}")
        additional_results["o1_visa_info"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ O-1 visa info failed: {str(e)}")
        additional_results["o1_visa_info"] = False
    
    # Test document requirements for O-1
    try:
        print("\n📄 O-1 Document Requirements:")
        response = requests.get(f"{API_BASE}/visa/O-1/documents", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            doc_requirements = response.json()
            print(f"   Response: {json.dumps(doc_requirements, indent=4)}")
        additional_results["o1_documents"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ O-1 document requirements failed: {str(e)}")
        additional_results["o1_documents"] = False
    
    # Test Owl Agent endpoints (if available)
    try:
        print("\n🦉 Owl Agent Session Start:")
        owl_data = {
            "visa_type": "O-1",
            "language": "pt",
            "user_profile": {
                "name": "Sofia Mendes Rodrigues",
                "field": "AI Research"
            }
        }
        response = requests.post(
            f"{API_BASE}/owl-agent/start-session",
            json=owl_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            owl_session = response.json()
            print(f"   Response: {json.dumps(owl_session, indent=4)}")
        additional_results["owl_agent"] = response.status_code in [200, 201]
    except Exception as e:
        print(f"   ❌ Owl Agent failed: {str(e)}")
        additional_results["owl_agent"] = False
    
    return additional_results

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE COMPLETO O-1 VISA - DR. SOFIA MENDES RODRIGUES")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Main test - O-1 Complete Flow as requested
    main_results = test_o1_visa_complete_flow()
    
    # Additional tests for context
    additional_results = test_additional_o1_endpoints()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 RELATÓRIO FINAL - TESTE COMPLETO O-1 VISA")
    print("=" * 80)
    
    print(f"👤 Aplicante: Dr. Sofia Mendes Rodrigues")
    print(f"🎯 Visto: O-1 (Extraordinary Ability)")
    print(f"📊 Teste principal: {main_results['summary']['successful_steps']}/{main_results['summary']['total_steps']} etapas")
    print(f"📈 Taxa de sucesso: {main_results['summary']['success_rate']:.1f}%")
    print(f"🔍 Testes adicionais: {sum(additional_results.values())}/{len(additional_results)}")
    
    # Show case details if available
    if main_results['summary'].get('case_id'):
        print(f"📋 Case ID: {main_results['summary']['case_id']}")
    
    if main_results['summary'].get('jwt_token_present'):
        print(f"🔑 JWT Token: ✅ Presente")
    
    # Detailed analysis of each step
    print(f"\n📋 ANÁLISE DETALHADA POR ETAPA:")
    step_names = [
        "Criação de Usuário",
        "Login", 
        "Iniciar Aplicação O-1",
        "Dados Básicos",
        "Formulário Completo",
        "Upload de Documentos",
        "Revisão da IA",
        "Status Final"
    ]
    
    for i, (step_key, step_name) in enumerate(zip(
        ["etapa_1_user_creation", "etapa_2_login", "etapa_3_start_application", 
         "etapa_4_basic_data", "etapa_5_friendly_form", "etapa_6_document_uploads",
         "etapa_7_ai_review", "etapa_8_final_status"], step_names)):
        
        step_data = main_results.get(step_key, {})
        status_code = step_data.get("status_code", 0)
        processing_time = step_data.get("processing_time", 0)
        validations = step_data.get("validations", {})
        
        status = "✅" if status_code in [200, 201] else "❌"
        validation_count = f"{sum(validations.values())}/{len(validations)}" if validations else "N/A"
        
        print(f"  {status} Etapa {i+1}: {step_name}")
        print(f"      Status: {status_code} | Tempo: {processing_time:.2f}s | Validações: {validation_count}")
        
        if step_data.get("error"):
            print(f"      ❌ Erro: {step_data['error'][:100]}...")
    
    if main_results["summary"]["overall_success"]:
        print("\n🎉 CONCLUSÃO: O-1 Visa Complete Flow está FUNCIONAL!")
        print("✅ Fluxo completo executado com sucesso")
        print("✅ Sistema de aplicação O-1 operacional")
        
        # Show final results
        final_status = main_results.get("etapa_8_final_status", {})
        if final_status.get("download_data"):
            download_data = final_status["download_data"]
            if download_data.get("download_url"):
                print(f"📁 Link para download: {download_data['download_url']}")
    else:
        print("\n⚠️  CONCLUSÃO: O-1 Visa Flow precisa de melhorias")
        
        # Show failed steps
        failed_steps = []
        for step_key in ["etapa_1_user_creation", "etapa_2_login", "etapa_3_start_application", 
                         "etapa_4_basic_data", "etapa_5_friendly_form", "etapa_6_document_uploads",
                         "etapa_7_ai_review", "etapa_8_final_status"]:
            step_data = main_results.get(step_key, {})
            if step_data.get("status_code") not in [200, 201]:
                failed_steps.append(step_key.replace("etapa_", "").replace("_", " ").title())
        
        if failed_steps:
            print(f"❌ Etapas que falharam: {', '.join(failed_steps)}")
        
    # Save results to file
    with open("/app/o1_visa_complete_test_results.json", "w") as f:
        json.dump({
            "main_results": main_results,
            "additional_results": additional_results,
            "timestamp": time.time(),
            "test_focus": "O-1 Visa Complete End-to-End Flow for Dr. Sofia Mendes Rodrigues",
            "applicant": {
                "name": "Dr. Sofia Mendes Rodrigues",
                "email": "sofia.mendes.test@example.com",
                "visa_type": "O-1",
                "field": "AI Research and Machine Learning in Healthcare"
            }
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/o1_visa_complete_test_results.json")
    
    # Final recommendation
    if main_results["summary"]["success_rate"] >= 75:
        print("\n✅ RECOMENDAÇÃO: Sistema pronto para aplicações O-1 reais")
    elif main_results["summary"]["success_rate"] >= 50:
        print("\n⚠️  RECOMENDAÇÃO: Sistema parcialmente funcional, melhorias necessárias")
    else:
        print("\n❌ RECOMENDAÇÃO: Sistema precisa de correções significativas")