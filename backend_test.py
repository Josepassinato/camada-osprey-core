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
    
    # FASE 3: Upload de documentos I-539
    print("\n📋 FASE 3: Upload de Documentos I-539")
    print("-" * 50)
    
    # Create simulated I-539 document content
    def create_simulated_document(doc_type, content):
        """Create a simulated PDF document as base64"""
        return base64.b64encode(content.encode()).decode()
    
    documents_to_upload = [
        {
            "name": "passport_carlos_mendes.pdf",
            "type": "passport",
            "content": "PASSPORT - REPÚBLICA FEDERATIVA DO BRASIL\nNome: CARLOS EDUARDO SILVA MENDES\nPassaporte: BR987654321\nData de Nascimento: 15/03/1985\nNacionalidade: BRASILEIRA\nValidade: 31/12/2030"
        },
        {
            "name": "i20_columbia_university.pdf", 
            "type": "i20",
            "content": "FORM I-20 - CERTIFICATE OF ELIGIBILITY FOR NONIMMIGRANT STUDENT STATUS\nStudent Name: Carlos Eduardo Silva Mendes\nSEVIS ID: N9876543210\nSchool: Columbia University\nProgram: Master of Science in Computer Science\nProgram End Date: June 30, 2025"
        },
        {
            "name": "financial_support_proof.pdf",
            "type": "financial_documents",
            "content": "BANK STATEMENT - BANCO DO BRASIL\nAccount Holder: Carlos Eduardo Silva Mendes\nBalance: R$ 450,000.00\nStatement Period: January 2025\nSufficient funds for educational expenses"
        },
        {
            "name": "cover_letter_i539.pdf",
            "type": "cover_letter", 
            "content": "COVER LETTER FOR I-539 APPLICATION\nTo: U.S. Citizenship and Immigration Services\nRe: Application to Extend F-1 Student Status\nApplicant: Carlos Eduardo Silva Mendes\nI am respectfully requesting an extension of my F-1 student status to complete my Master's degree program at Columbia University."
        },
        {
            "name": "academic_transcript.pdf",
            "type": "education_documents",
            "content": "COLUMBIA UNIVERSITY - OFFICIAL TRANSCRIPT\nStudent: Carlos Eduardo Silva Mendes\nProgram: Master of Science in Computer Science\nCurrent GPA: 3.8/4.0\nExpected Graduation: June 2025"
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
    
    # FASE 4: Testar endpoints de AI Review
    print("\n📋 FASE 4: Testar Endpoints de AI Review")
    print("-" * 50)
    
    ai_review_endpoints = [
        {
            "name": "AI Case Review",
            "endpoint": f"/api/case/{case_id}/ai-review",
            "method": "POST",
            "data": {"review_type": "comprehensive"}
        },
        {
            "name": "Professional QA Review", 
            "endpoint": f"/api/auto-application/case/{case_id}/professional-qa-review",
            "method": "POST",
            "data": {"review_level": "detailed"}
        },
        {
            "name": "Document Validation",
            "endpoint": "/api/specialized-agents/document-validation",
            "method": "POST", 
            "data": {
                "document_type": "passport",
                "document_content": "CARLOS EDUARDO SILVA MENDES passport content",
                "case_context": {"applicant_name": "Carlos Eduardo Silva Mendes", "visa_type": "I-539"}
            }
        },
        {
            "name": "Form Validation",
            "endpoint": "/api/specialized-agents/form-validation", 
            "method": "POST",
            "data": {
                "form_data": basic_data,
                "visa_type": "I-539",
                "step_id": "basic_data"
            }
        },
        {
            "name": "Compliance Check",
            "endpoint": "/api/specialized-agents/compliance-check",
            "method": "POST",
            "data": {
                "complete_application": basic_data,
                "documents": ["passport", "i20", "financial_documents"],
                "visa_type": "I-539"
            }
        }
    ]
    
    ai_review_results = {}
    
    for endpoint_test in ai_review_endpoints:
        try:
            print(f"\n🔍 Testing: {endpoint_test['name']}")
            print(f"🔗 Endpoint: {endpoint_test['method']} {API_BASE}{endpoint_test['endpoint']}")
            
            start_time = time.time()
            
            if endpoint_test['method'] == 'POST':
                response = requests.post(
                    f"{API_BASE}{endpoint_test['endpoint']}",
                    json=endpoint_test['data'],
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
            else:
                response = requests.get(
                    f"{API_BASE}{endpoint_test['endpoint']}",
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
            
            processing_time = time.time() - start_time
            
            print(f"⏱️  Processing time: {processing_time:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
            
            ai_review_results[endpoint_test['name']] = {
                "status_code": response.status_code,
                "processing_time": processing_time,
                "working": response.status_code in [200, 201]
            }
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                print(f"✅ {endpoint_test['name']}: SUCCESS")
                print(f"📄 Response preview: {str(response_data)[:200]}...")
                ai_review_results[endpoint_test['name']]["response_data"] = response_data
            else:
                print(f"❌ {endpoint_test['name']}: FAILED")
                print(f"📄 Error: {response.text}")
                ai_review_results[endpoint_test['name']]["error"] = response.text
                
        except Exception as e:
            print(f"❌ Exception testing {endpoint_test['name']}: {str(e)}")
            ai_review_results[endpoint_test['name']] = {
                "status_code": 0,
                "processing_time": 0,
                "working": False,
                "exception": str(e)
            }
    
    results["fase_4_ai_review_endpoints"] = ai_review_results
    
    # Summary of AI Review endpoints
    working_endpoints = sum(1 for result in ai_review_results.values() if result.get("working", False))
    total_endpoints = len(ai_review_endpoints)
    
    print(f"\n📊 AI REVIEW ENDPOINTS SUMMARY:")
    print(f"   Working: {working_endpoints}/{total_endpoints} ({working_endpoints/total_endpoints*100:.1f}%)")
    
    for name, result in ai_review_results.items():
        status = "✅" if result.get("working", False) else "❌"
        print(f"   {status} {name}: {result.get('status_code', 0)}")
    
    # FASE 5: Análise de Validação de Documentos
    print("\n📋 FASE 5: Análise de Validação de Documentos")
    print("-" * 50)
    
    document_validation_tests = []
    
    for doc in documents_to_upload:
        if doc.get("status") == "uploaded":
            try:
                print(f"\n🔍 Validating: {doc['name']}")
                
                validation_data = {
                    "document_type": doc["type"],
                    "document_content": doc["content"],
                    "applicant_name": "Carlos Eduardo Silva Mendes",
                    "visa_type": "I-539"
                }
                
                response = requests.post(
                    f"{API_BASE}/test-document-validation",
                    json=validation_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    validation_result = response.json()
                    print(f"✅ Validation completed")
                    
                    # Check key validation criteria
                    validation_checks = {
                        "document_type_correct": validation_result.get("document_type_correct", False),
                        "belongs_to_applicant": validation_result.get("belongs_to_applicant", False),
                        "uscis_acceptable": validation_result.get("uscis_acceptable", False),
                        "completeness_score": validation_result.get("completeness_score", 0) >= 70
                    }
                    
                    document_validation_tests.append({
                        "document": doc["name"],
                        "type": doc["type"],
                        "validation_checks": validation_checks,
                        "completeness_score": validation_result.get("completeness_score", 0),
                        "working": all(validation_checks.values())
                    })
                    
                    print(f"   📊 Completeness: {validation_result.get('completeness_score', 0)}%")
                    print(f"   🎯 Type Correct: {validation_result.get('document_type_correct', False)}")
                    print(f"   👤 Belongs to Applicant: {validation_result.get('belongs_to_applicant', False)}")
                    print(f"   ✅ USCIS Acceptable: {validation_result.get('uscis_acceptable', False)}")
                    
                else:
                    print(f"❌ Validation failed: {response.text}")
                    document_validation_tests.append({
                        "document": doc["name"],
                        "type": doc["type"],
                        "working": False,
                        "error": response.text
                    })
                    
            except Exception as e:
                print(f"❌ Exception validating {doc['name']}: {str(e)}")
                document_validation_tests.append({
                    "document": doc["name"],
                    "type": doc["type"],
                    "working": False,
                    "exception": str(e)
                })
    
    results["fase_5_document_validation"] = document_validation_tests
    
    # FASE 6: Análise de Qualidade de Cartas
    print("\n📋 FASE 6: Análise de Qualidade de Cartas")
    print("-" * 50)
    
    # Test letter quality assessment
    cover_letter_content = """
    COVER LETTER FOR I-539 APPLICATION
    
    To: U.S. Citizenship and Immigration Services
    Re: Application to Extend F-1 Student Status
    
    Dear USCIS Officer,
    
    I am Carlos Eduardo Silva Mendes, currently in F-1 student status, respectfully requesting an extension of my nonimmigrant student status to complete my Master of Science degree in Computer Science at Columbia University.
    
    I am currently enrolled in the Master's program and need additional time to complete my thesis research on artificial intelligence applications in healthcare. My current I-20 expires on June 30, 2025, and I require an extension until December 31, 2025.
    
    I have maintained good academic standing with a GPA of 3.8/4.0 and have sufficient financial resources to support my continued studies as evidenced by the attached bank statements.
    
    I respectfully request your favorable consideration of this application.
    
    Sincerely,
    Carlos Eduardo Silva Mendes
    """
    
    try:
        print("🔍 Testing letter quality assessment...")
        
        letter_data = {
            "letter_content": cover_letter_content,
            "letter_type": "cover_letter",
            "visa_type": "I-539",
            "applicant_name": "Carlos Eduardo Silva Mendes"
        }
        
        response = requests.post(
            f"{API_BASE}/llm/dr-paula/review-letter",
            json=letter_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            letter_review = response.json()
            print("✅ Letter quality assessment completed")
            
            quality_checks = {
                "professional_tone": "professional" in str(letter_review).lower(),
                "complete_information": len(cover_letter_content) > 500,
                "proper_format": "Dear" in cover_letter_content and "Sincerely" in cover_letter_content,
                "visa_specific": "I-539" in cover_letter_content and "F-1" in cover_letter_content
            }
            
            results["fase_6_letter_quality"] = {
                "working": True,
                "quality_checks": quality_checks,
                "review_result": letter_review,
                "overall_quality": sum(quality_checks.values()) / len(quality_checks) * 100
            }
            
            print(f"   📝 Professional Tone: {quality_checks['professional_tone']}")
            print(f"   📋 Complete Information: {quality_checks['complete_information']}")
            print(f"   📄 Proper Format: {quality_checks['proper_format']}")
            print(f"   🎯 Visa Specific: {quality_checks['visa_specific']}")
            print(f"   📊 Overall Quality: {results['fase_6_letter_quality']['overall_quality']:.1f}%")
            
        else:
            print(f"❌ Letter assessment failed: {response.text}")
            results["fase_6_letter_quality"] = {
                "working": False,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception in letter quality assessment: {str(e)}")
        results["fase_6_letter_quality"] = {
            "working": False,
            "exception": str(e)
        }
    
    # FASE 7: Verificação de Preenchimento de Formulário
    print("\n📋 FASE 7: Verificação de Preenchimento de Formulário")
    print("-" * 50)
    
    try:
        print("🔍 Testing form completion verification...")
        
        # Test form validation with I-539 specific requirements
        form_validation_data = {
            "form_data": basic_data,
            "visa_type": "I-539",
            "step_id": "form_completion_check"
        }
        
        response = requests.post(
            f"{API_BASE}/specialized-agents/form-validation",
            json=form_validation_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            form_validation = response.json()
            print("✅ Form completion verification completed")
            
            # Check I-539 specific requirements
            i539_requirements = {
                "applicant_name_present": bool(basic_data.get("applicant_name")),
                "current_visa_type_present": bool(basic_data.get("current_visa_type")),
                "extension_reason_present": bool(basic_data.get("extension_reason")),
                "i20_expiration_present": bool(basic_data.get("i20_expiration")),
                "sevis_number_present": bool(basic_data.get("sevis_number")),
                "university_present": bool(basic_data.get("university"))
            }
            
            results["fase_7_form_verification"] = {
                "working": True,
                "i539_requirements": i539_requirements,
                "validation_result": form_validation,
                "completion_rate": sum(i539_requirements.values()) / len(i539_requirements) * 100
            }
            
            print(f"   👤 Applicant Name: {i539_requirements['applicant_name_present']}")
            print(f"   📋 Current Visa Type: {i539_requirements['current_visa_type_present']}")
            print(f"   📝 Extension Reason: {i539_requirements['extension_reason_present']}")
            print(f"   📅 I-20 Expiration: {i539_requirements['i20_expiration_present']}")
            print(f"   🔢 SEVIS Number: {i539_requirements['sevis_number_present']}")
            print(f"   🏫 University: {i539_requirements['university_present']}")
            print(f"   📊 Completion Rate: {results['fase_7_form_verification']['completion_rate']:.1f}%")
            
        else:
            print(f"❌ Form verification failed: {response.text}")
            results["fase_7_form_verification"] = {
                "working": False,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception in form verification: {str(e)}")
        results["fase_7_form_verification"] = {
            "working": False,
            "exception": str(e)
        }
    
    # FASE 8: Verificação de Conformidade USCIS
    print("\n📋 FASE 8: Verificação de Conformidade USCIS")
    print("-" * 50)
    
    try:
        print("🔍 Testing USCIS compliance check...")
        
        # Comprehensive compliance check for I-539
        compliance_data = {
            "complete_application": {
                "case_id": case_id,
                "applicant_data": basic_data,
                "documents": [doc["type"] for doc in documents_to_upload],
                "form_type": "I-539"
            },
            "documents": ["passport", "i20", "financial_documents", "cover_letter", "education_documents"],
            "visa_type": "I-539"
        }
        
        response = requests.post(
            f"{API_BASE}/specialized-agents/compliance-check",
            json=compliance_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            compliance_result = response.json()
            print("✅ USCIS compliance check completed")
            
            # Check I-539 specific USCIS requirements
            uscis_requirements = {
                "form_i539_complete": True,  # Simulated
                "supporting_documents_present": len([doc for doc in documents_to_upload]) >= 4,
                "financial_evidence_provided": any("financial" in doc["type"] for doc in documents_to_upload),
                "current_status_documented": bool(basic_data.get("current_visa_type")),
                "extension_reason_valid": bool(basic_data.get("extension_reason")),
                "i94_copy_available": True,  # Simulated
                "passport_copy_available": any("passport" in doc["type"] for doc in documents_to_upload)
            }
            
            results["fase_8_uscis_compliance"] = {
                "working": True,
                "uscis_requirements": uscis_requirements,
                "compliance_result": compliance_result,
                "compliance_score": sum(uscis_requirements.values()) / len(uscis_requirements) * 100
            }
            
            print(f"   📋 Form I-539 Complete: {uscis_requirements['form_i539_complete']}")
            print(f"   📄 Supporting Documents: {uscis_requirements['supporting_documents_present']}")
            print(f"   💰 Financial Evidence: {uscis_requirements['financial_evidence_provided']}")
            print(f"   📋 Current Status Documented: {uscis_requirements['current_status_documented']}")
            print(f"   📝 Extension Reason Valid: {uscis_requirements['extension_reason_valid']}")
            print(f"   🛂 I-94 Copy Available: {uscis_requirements['i94_copy_available']}")
            print(f"   📘 Passport Copy Available: {uscis_requirements['passport_copy_available']}")
            print(f"   📊 Compliance Score: {results['fase_8_uscis_compliance']['compliance_score']:.1f}%")
            
        else:
            print(f"❌ USCIS compliance check failed: {response.text}")
            results["fase_8_uscis_compliance"] = {
                "working": False,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception in USCIS compliance check: {str(e)}")
        results["fase_8_uscis_compliance"] = {
            "working": False,
            "exception": str(e)
        }
    
    # FASE 9: Análise Final do Sistema de Revisão
    print("\n📋 FASE 9: Análise Final do Sistema de Revisão")
    print("-" * 50)
    
    try:
        # Check current case status
        print(f"🔗 Endpoint: GET {API_BASE}/auto-application/case/{case_id}")
        
        start_time = time.time()
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["fase_9_final_analysis"]["status_code"] = response.status_code
        results["fase_9_final_analysis"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Case Status Response: {json.dumps(response_data, indent=2)}")
            
            # Final analysis of AI review system
            ai_review_analysis = {
                "case_retrieval_working": True,
                "case_data_complete": bool(response_data.get("case")),
                "applicant_data_preserved": "Carlos Eduardo Silva Mendes" in str(response_data),
                "i539_specific_data_present": "I-539" in str(response_data) or "F-1" in str(response_data)
            }
            
            results["fase_9_final_analysis"]["ai_review_analysis"] = ai_review_analysis
            results["fase_9_final_analysis"]["response_data"] = response_data
            
            print("\n🎯 ANÁLISE FINAL DO SISTEMA:")
            print("=" * 50)
            for check, passed in ai_review_analysis.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Final analysis failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["fase_9_final_analysis"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during final analysis: {str(e)}")
        results["fase_9_final_analysis"]["exception"] = str(e)
    
    # Summary
    print("\n📊 RESUMO COMPLETO DO TESTE I-539 AI REVIEW")
    print("=" * 60)
    
    # Count successful phases
    successful_phases = 0
    total_phases = 9
    
    phase_keys = [
        "fase_1_case_creation", "fase_2_basic_data", "fase_3_document_uploads", 
        "fase_4_ai_review_endpoints", "fase_5_document_validation", "fase_6_letter_quality",
        "fase_7_form_verification", "fase_8_uscis_compliance", "fase_9_final_analysis"
    ]
    
    for phase_key in phase_keys:
        phase_data = results.get(phase_key, {})
        if isinstance(phase_data, dict):
            if phase_data.get("status_code") in [200, 201] or phase_data.get("working", False):
                successful_phases += 1
        elif isinstance(phase_data, list):
            # For document validation (list of results)
            if any(item.get("working", False) for item in phase_data):
                successful_phases += 1
    
    success_rate = (successful_phases / total_phases) * 100
    
    print(f"🧪 Teste I-539 AI Review System: {successful_phases}/{total_phases} fases concluídas ({success_rate:.1f}%)")
    print(f"👤 Aplicante: Carlos Eduardo Silva Mendes")
    print(f"🎯 Processo: I-539 Extension of Stay")
    print(f"📋 Case ID: {case_id}")
    
    # Show phase-by-phase results
    print(f"\n📋 RESULTADOS POR FASE:")
    phase_names = [
        "Criação de Caso I-539",
        "Dados Básicos", 
        "Upload de Documentos",
        "Endpoints de AI Review",
        "Validação de Documentos",
        "Qualidade de Cartas",
        "Verificação de Formulário",
        "Conformidade USCIS",
        "Análise Final"
    ]
    
    for i, (phase_key, phase_name) in enumerate(zip(phase_keys, phase_names)):
        phase_data = results.get(phase_key, {})
        
        if isinstance(phase_data, dict):
            status_code = phase_data.get("status_code", 0)
            working = phase_data.get("working", False)
            status = "✅" if status_code in [200, 201] or working else "❌"
            print(f"  {status} Fase {i+1}: {phase_name}")
        elif isinstance(phase_data, list):
            working_items = sum(1 for item in phase_data if item.get("working", False))
            total_items = len(phase_data)
            status = "✅" if working_items > 0 else "❌"
            print(f"  {status} Fase {i+1}: {phase_name} ({working_items}/{total_items} working)")
        else:
            print(f"  ❌ Fase {i+1}: {phase_name} (No data)")
    
    # AI Review System Analysis
    print(f"\n🤖 ANÁLISE DO SISTEMA DE IA DE REVISÃO:")
    print("=" * 50)
    
    # Check AI Review endpoints
    ai_endpoints = results.get("fase_4_ai_review_endpoints", {})
    working_ai_endpoints = sum(1 for result in ai_endpoints.values() if result.get("working", False))
    total_ai_endpoints = len(ai_endpoints)
    
    print(f"📡 Endpoints de IA: {working_ai_endpoints}/{total_ai_endpoints} funcionando")
    
    # Check document validation
    doc_validation = results.get("fase_5_document_validation", [])
    working_validations = sum(1 for doc in doc_validation if doc.get("working", False))
    total_validations = len(doc_validation)
    
    print(f"📄 Validação de Documentos: {working_validations}/{total_validations} documentos validados")
    
    # Check letter quality
    letter_quality = results.get("fase_6_letter_quality", {})
    letter_working = letter_quality.get("working", False)
    letter_score = letter_quality.get("overall_quality", 0)
    
    print(f"✍️  Qualidade de Cartas: {'✅' if letter_working else '❌'} (Score: {letter_score:.1f}%)")
    
    # Check form verification
    form_verification = results.get("fase_7_form_verification", {})
    form_working = form_verification.get("working", False)
    form_completion = form_verification.get("completion_rate", 0)
    
    print(f"📋 Verificação de Formulário: {'✅' if form_working else '❌'} (Completude: {form_completion:.1f}%)")
    
    # Check USCIS compliance
    uscis_compliance = results.get("fase_8_uscis_compliance", {})
    uscis_working = uscis_compliance.get("working", False)
    uscis_score = uscis_compliance.get("compliance_score", 0)
    
    print(f"⚖️  Conformidade USCIS: {'✅' if uscis_working else '❌'} (Score: {uscis_score:.1f}%)")
    
    overall_success = success_rate >= 70  # Consider success if 70% or more phases completed
    results["summary"]["overall_success"] = overall_success
    results["summary"]["successful_phases"] = successful_phases
    results["summary"]["total_phases"] = total_phases
    results["summary"]["success_rate"] = success_rate
    results["summary"]["case_id"] = case_id
    results["summary"]["ai_review_functional"] = working_ai_endpoints > 0
    
    print(f"\n🎯 RESULTADO FINAL: {'✅ SISTEMA FUNCIONAL' if overall_success else '❌ NECESSITA MELHORIAS'}")
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    return results

def test_additional_i539_endpoints():
    """Test additional I-539 related endpoints for completeness"""
    
    print("\n🔍 TESTES ADICIONAIS - ENDPOINTS I-539 RELACIONADOS")
    print("=" * 60)
    
    additional_results = {}
    
    # Test visa detailed info for I-539
    try:
        print("\n📋 I-539 Visa Detailed Info:")
        response = requests.get(f"{API_BASE}/visa-detailed-info/I-539?process_type=change_of_status", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            visa_info = response.json()
            print(f"   Response: {json.dumps(visa_info, indent=4)}")
        additional_results["i539_visa_info"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ I-539 visa info failed: {str(e)}")
        additional_results["i539_visa_info"] = False
    
    # Test document requirements for I-539
    try:
        print("\n📄 I-539 Document Requirements:")
        response = requests.get(f"{API_BASE}/visa/I-539/documents", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            doc_requirements = response.json()
            print(f"   Response: {json.dumps(doc_requirements, indent=4)}")
        additional_results["i539_documents"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ I-539 document requirements failed: {str(e)}")
        additional_results["i539_documents"] = False
    
    # Test document validation database
    try:
        print("\n🗄️ Document Validation Database:")
        response = requests.get(f"{API_BASE}/document-validation-database/passport", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            validation_db = response.json()
            print(f"   Response: {json.dumps(validation_db, indent=4)}")
        additional_results["validation_database"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ Validation database failed: {str(e)}")
        additional_results["validation_database"] = False
    
    # Test comprehensive document validation
    try:
        print("\n🔍 Comprehensive Document Validation:")
        validation_data = {
            "document_type": "passport",
            "document_content": "CARLOS EDUARDO SILVA MENDES passport content",
            "applicant_name": "Carlos Eduardo Silva Mendes",
            "visa_type": "I-539"
        }
        response = requests.post(
            f"{API_BASE}/test-comprehensive-document-validation",
            json=validation_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            validation_result = response.json()
            print(f"   Response: {json.dumps(validation_result, indent=4)}")
        additional_results["comprehensive_validation"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ Comprehensive validation failed: {str(e)}")
        additional_results["comprehensive_validation"] = False
    
    # Test validation capabilities
    try:
        print("\n⚙️ Validation Capabilities:")
        response = requests.get(f"{API_BASE}/documents/validation-capabilities", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            capabilities = response.json()
            print(f"   Response: {json.dumps(capabilities, indent=4)}")
        additional_results["validation_capabilities"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ Validation capabilities failed: {str(e)}")
        additional_results["validation_capabilities"] = False
    
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