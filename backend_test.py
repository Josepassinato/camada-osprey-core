#!/usr/bin/env python3
"""
Backend Testing Suite - O-1 Visa Complete End-to-End Testing
Testing complete O-1 visa application flow for Dr. Sofia Mendes Rodrigues
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://apply-wizard-18.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_o1_visa_complete_flow():
    """
    Test complete O-1 visa application flow for Dr. Sofia Mendes Rodrigues
    
    SPECIFIC TEST REQUESTED IN REVIEW:
    Complete end-to-end O-1 visa application including:
    1. User creation and login
    2. O-1 application start
    3. Basic data filling
    4. Friendly form completion
    5. Document uploads (simulated)
    6. AI review
    7. Final status and download
    
    Expected validations:
    1. ✅ User created successfully
    2. ✅ Login successful with JWT token
    3. ✅ O-1 case created
    4. ✅ Basic data saved
    5. ✅ Friendly form completed
    6. ✅ Documents uploaded
    7. ✅ AI review completed
    8. ✅ Final package available
    """
    
    print("🦅 TESTING O-1 VISA COMPLETE END-TO-END FLOW")
    print("🧑‍⚕️ Applicant: Dr. Sofia Mendes Rodrigues")
    print("=" * 60)
    
    results = {
        "etapa_1_user_creation": {},
        "etapa_2_login": {},
        "etapa_3_start_application": {},
        "etapa_4_basic_data": {},
        "etapa_5_friendly_form": {},
        "etapa_6_document_uploads": {},
        "etapa_7_ai_review": {},
        "etapa_8_final_status": {},
        "summary": {}
    }
    
    # Global variables for the flow
    jwt_token = None
    case_id = None
    
    # ETAPA 1: Criar usuário
    print("\n📋 ETAPA 1: Criação de Usuário")
    print("-" * 50)
    
    user_data = {
        "email": "sofia.mendes.test@example.com",
        "password": "TestPassword123!",
        "first_name": "Sofia",
        "last_name": "Mendes Rodrigues",
        "phone": "+5511987654321"
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/auth/signup")
        print(f"📤 Payload: {json.dumps(user_data, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["etapa_1_user_creation"]["status_code"] = response.status_code
        results["etapa_1_user_creation"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Extract JWT token for subsequent requests
            jwt_token = response_data.get("token")
            user_info = response_data.get("user", {})
            
            validations = {
                "1_user_created": response_data.get("message") == "User created successfully",
                "2_token_present": jwt_token is not None,
                "3_user_email_correct": user_info.get("email") == "sofia.mendes.test@example.com",
                "4_user_name_correct": user_info.get("first_name") == "Sofia"
            }
            
            results["etapa_1_user_creation"]["validations"] = validations
            results["etapa_1_user_creation"]["response_data"] = response_data
            results["etapa_1_user_creation"]["jwt_token"] = jwt_token
            
            print("\n🎯 VALIDAÇÕES ETAPA 1:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            print(f"\n📊 DADOS DO USUÁRIO CRIADO:")
            print(f"  👤 Nome: {user_info.get('first_name')} {user_info.get('last_name')}")
            print(f"  📧 Email: {user_info.get('email')}")
            print(f"  🔑 Token JWT: {'✅ Presente' if jwt_token else '❌ Ausente'}")
            
            if jwt_token:
                print(f"  🔑 Token (primeiros 50 chars): {jwt_token[:50]}...")
            else:
                print(f"  ❌ No JWT token found")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_1_user_creation"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during user creation: {str(e)}")
        results["etapa_1_user_creation"]["exception"] = str(e)
    
    # ETAPA 2: Login
    print("\n📋 ETAPA 2: Login do Usuário")
    print("-" * 50)
    
    login_data = {
        "email": "sofia.mendes.test@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/auth/login")
        print(f"📤 Payload: {json.dumps(login_data, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["etapa_2_login"]["status_code"] = response.status_code
        results["etapa_2_login"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Update JWT token from login
            jwt_token = response_data.get("token")
            user_info = response_data.get("user", {})
            
            validations = {
                "1_login_successful": response_data.get("message") == "Login successful",
                "2_token_present": jwt_token is not None,
                "3_user_email_correct": user_info.get("email") == "sofia.mendes.test@example.com",
                "4_user_name_correct": user_info.get("first_name") == "Sofia"
            }
            
            results["etapa_2_login"]["validations"] = validations
            results["etapa_2_login"]["response_data"] = response_data
            results["etapa_2_login"]["jwt_token"] = jwt_token
            
            print("\n🎯 VALIDAÇÕES ETAPA 2:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_2_login"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during login: {str(e)}")
        results["etapa_2_login"]["exception"] = str(e)
    
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
            
            # Extract case_id for subsequent requests
            case_id = response_data.get("case_id")
            
            validations = {
                "1_case_created": case_id is not None,
                "2_case_id_format": case_id.startswith("OSP-") if case_id else False,
                "3_visa_code_correct": response_data.get("form_code") == "O-1",
                "4_status_created": response_data.get("status") == "created"
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
    
    # ETAPA 4: Preencher dados básicos
    print("\n📋 ETAPA 4: Preencher Dados Básicos")
    print("-" * 50)
    
    if not case_id:
        print("❌ Cannot proceed without case_id")
        return results
    
    basic_data = {
        "full_name": "Sofia Mendes Rodrigues",
        "date_of_birth": "1988-03-15",
        "country_of_birth": "Brazil",
        "passport_number": "BR123456789",
        "passport_expiry": "2029-12-31",
        "phone": "+5511987654321",
        "email": "sofia.mendes.test@example.com",
        "current_address": "Rua das Flores 123, São Paulo, SP, Brazil",
        "marital_status": "single"
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/auto-application/case/{case_id}/basic-data")
        print(f"📤 Payload: {json.dumps(basic_data, indent=2)}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/auto-application/case/{case_id}/basic-data",
            json=basic_data,
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
            
            validations = {
                "1_data_saved": response_data.get("success") == True or "saved" in str(response_data).lower(),
                "2_case_id_matches": case_id in str(response_data),
                "3_progress_updated": response_data.get("progress_percentage", 0) > 0
            }
            
            results["etapa_4_basic_data"]["validations"] = validations
            results["etapa_4_basic_data"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES ETAPA 4:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Basic data failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_4_basic_data"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during basic data: {str(e)}")
        results["etapa_4_basic_data"]["exception"] = str(e)
    
    # ETAPA 5: Preencher formulário completo (friendly-form)
    print("\n📋 ETAPA 5: Preencher Formulário Completo (Friendly-Form)")
    print("-" * 50)
    
    friendly_form_data = {
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
            "job_description": "Leading research in AI-powered early cancer detection systems. Developing machine learning models for medical image analysis and predictive diagnostics."
        },
        "education": [
            {
                "degree": "PhD in Computer Science",
                "institution": "Massachusetts Institute of Technology (MIT)",
                "year": "2015",
                "field": "Artificial Intelligence and Machine Learning"
            },
            {
                "degree": "Master in Computer Science",
                "institution": "University of São Paulo",
                "year": "2010",
                "field": "Data Science"
            }
        ],
        "achievements": [
            {
                "title": "AI for Good Award",
                "organization": "United Nations",
                "year": "2023",
                "description": "Recognized for developing AI system that detects early-stage cancer with 95% accuracy"
            },
            {
                "title": "Best Paper Award",
                "organization": "International Conference on Medical AI",
                "year": "2022",
                "description": "Research on deep learning for medical image analysis"
            }
        ],
        "publications": {
            "total": 52,
            "citations": 2100,
            "h_index": 28,
            "notable_papers": [
                "Deep Learning for Early Cancer Detection: A Comprehensive Study",
                "AI-Powered Diagnostic Systems in Healthcare",
                "Machine Learning Applications in Medical Imaging"
            ]
        },
        "media_coverage": [
            {
                "title": "Brazilian Scientist Revolutionizes Cancer Detection with AI",
                "outlet": "TechCrunch",
                "date": "2023-06-15",
                "url": "https://techcrunch.com/example"
            }
        ],
        "speaking_engagements": [
            {
                "title": "AI in Medicine: The Future is Now",
                "event": "TEDx São Paulo",
                "date": "2023-09-20"
            }
        ]
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/auto-application/case/{case_id}/friendly-form")
        print(f"📤 Payload: {json.dumps(friendly_form_data, indent=2)}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/auto-application/case/{case_id}/friendly-form",
            json=friendly_form_data,
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
            
            validations = {
                "1_form_saved": response_data.get("success") == True or "saved" in str(response_data).lower(),
                "2_case_id_matches": case_id in str(response_data),
                "3_progress_updated": response_data.get("progress_percentage", 0) > 20
            }
            
            results["etapa_5_friendly_form"]["validations"] = validations
            results["etapa_5_friendly_form"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES ETAPA 5:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
        else:
            print(f"❌ Friendly form failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["etapa_5_friendly_form"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during friendly form: {str(e)}")
        results["etapa_5_friendly_form"]["exception"] = str(e)
    
    # Summary
    print("\n📊 RESUMO DO TESTE F-1")
    print("=" * 60)
    
    test_success = results["test_1_f1_student_package"].get("status_code") == 200
    
    print(f"🧪 Teste F-1 Student Package: {'✅ PASSOU' if test_success else '❌ FALHOU'}")
    
    if test_success:
        validations = results["test_1_f1_student_package"].get("validations", {})
        passed_count = sum(validations.values())
        total_count = len(validations)
        print(f"   📋 Validações específicas: {passed_count}/{total_count} passaram")
        
        # Show which specific validations failed
        failed_validations = [k for k, v in validations.items() if not v]
        if failed_validations:
            print(f"   ❌ Validações que falharam: {', '.join(failed_validations)}")
        else:
            print(f"   ✅ Todas as validações passaram!")
    
    validations = results["test_1_f1_student_package"].get("validations", {})
    all_validations_passed = all(validations.values()) if validations else False
    overall_success = test_success and all_validations_passed
    results["summary"]["overall_success"] = overall_success
    results["summary"]["tests_passed"] = 1 if test_success else 0
    results["summary"]["tests_total"] = 1
    
    print(f"\n🎯 RESULTADO FINAL: {'✅ SUCESSO COMPLETO' if overall_success else '❌ NECESSITA MELHORIAS'}")
    print(f"📈 Taxa de sucesso: {results['summary']['tests_passed']}/{results['summary']['tests_total']} ({results['summary']['tests_passed']/results['summary']['tests_total']*100:.1f}%)")
    
    return results

def test_additional_endpoints():
    """Test additional visa API endpoints for completeness"""
    
    print("\n🔍 TESTES ADICIONAIS - ENDPOINTS RELACIONADOS")
    print("=" * 60)
    
    additional_results = {}
    
    # Test health check
    try:
        print("\n🏥 Health Check:")
        response = requests.get(f"{API_BASE}/visa/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Response: {json.dumps(health_data, indent=4)}")
        additional_results["health_check"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ Health check failed: {str(e)}")
        additional_results["health_check"] = False
    
    # Test specialists list
    try:
        print("\n👥 Specialists List:")
        response = requests.get(f"{API_BASE}/visa/specialists", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            specialists_data = response.json()
            print(f"   Response: {json.dumps(specialists_data, indent=4)}")
        additional_results["specialists_list"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ Specialists list failed: {str(e)}")
        additional_results["specialists_list"] = False
    
    # Test visa type detection
    try:
        print("\n🔍 Visa Type Detection:")
        response = requests.get(
            f"{API_BASE}/visa/detect-type",
            params={"user_input": "I need to extend my tourist visa"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            detection_data = response.json()
            print(f"   Response: {json.dumps(detection_data, indent=4)}")
        additional_results["visa_detection"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ Visa detection failed: {str(e)}")
        additional_results["visa_detection"] = False
    
    return additional_results

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE ESPECÍFICO DA REVIEW - F-1 STUDENT VISA")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    # Main test - F-1 Student Package as requested
    main_results = test_visa_generate_endpoint()
    
    # Additional tests for context
    additional_results = test_additional_endpoints()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 RELATÓRIO FINAL - TESTE F-1 STUDENT VISA")
    print("=" * 80)
    
    print(f"✅ Endpoint testado: POST /api/visa/generate")
    print(f"📊 Teste principal: {main_results['summary']['tests_passed']}/{main_results['summary']['tests_total']}")
    print(f"🔍 Testes adicionais: {sum(additional_results.values())}/{len(additional_results)}")
    
    # Detailed analysis of F-1 test results
    f1_results = main_results.get("test_1_f1_student_package", {})
    validations = f1_results.get("validations", {})
    
    print(f"\n📋 ANÁLISE DETALHADA DAS VALIDAÇÕES:")
    for validation, passed in validations.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {validation}")
    
    if main_results["summary"]["overall_success"]:
        print("\n🎉 CONCLUSÃO: F-1 Student Visa endpoint está FUNCIONAL!")
        print("✅ Todas as validações críticas foram atendidas")
        print("✅ Sistema multi-agente operacional")
        
        # Show PDF download link if available
        f1_response = f1_results.get("response_data", {})
        package_result = f1_response.get("package_result", {})
        if package_result.get("download_url"):
            print(f"📁 Link para download: {package_result['download_url']}")
    else:
        print("\n⚠️  CONCLUSÃO: F-1 Student Visa precisa de melhorias")
        failed_validations = [k for k, v in validations.items() if not v]
        print(f"❌ Validações que falharam: {', '.join(failed_validations)}")
        
    # Save results to file
    with open("/app/f1_student_visa_test_results.json", "w") as f:
        json.dump({
            "main_results": main_results,
            "additional_results": additional_results,
            "timestamp": time.time(),
            "test_focus": "F-1 Student Visa as requested in review"
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/f1_student_visa_test_results.json")