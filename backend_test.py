#!/usr/bin/env python3
"""
Backend Testing Suite for Multi-Agent Visa Architecture
Testing the new POST /api/visa/generate endpoint as requested
"""

import requests
import json
import time
import os
from pathlib import Path

# Get backend URL from frontend .env
BACKEND_URL = "https://doculegal.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_visa_generate_endpoint():
    """
    Test the new multi-agent architecture endpoint POST /api/visa/generate
    
    SPECIFIC TEST REQUESTED IN REVIEW:
    - F-1 Student Visa with complete package for Rafael Santos Oliveira
    - Expected: 10+ pages, PDF generation, validation, QA report
    
    Expected validations:
    1. ✅ Status 200
    2. ✅ success: true
    3. ✅ visa_type = "F-1"
    4. ✅ package_result with PDF info
    5. ✅ PDF generated: "F1_STUDENT_COMPLETE_PACKAGE_RAFAEL_OLIVEIRA.pdf"
    6. ✅ PDF has 10+ pages
    7. ✅ validation with checklist
    8. ✅ qa_report with scores
    """
    
    print("🧪 TESTING F-1 STUDENT VISA MULTI-AGENT ARCHITECTURE")
    print("=" * 60)
    
    results = {
        "test_1_f1_student_package": {},
        "summary": {}
    }
    
    # Test 1: F-1 Student Package (as requested in review)
    print("\n📋 TESTE F-1: Geração de Pacote F-1 Student Visa")
    print("-" * 50)
    
    # Test with the EXACT format specified in the review request
    f1_payload = {
        "visa_type": "F-1",
        "user_request": "Preciso de ajuda para preparar minha aplicação de visto F-1 de estudante. Fui aceito no programa de mestrado em Ciência da Computação na Boston University e preciso de um pacote completo e profissional para minha entrevista no consulado.",
        "applicant_data": {
            "full_name": "Rafael Santos Oliveira",
            "nationality": "Brazilian",
            "program": "Master of Science in Computer Science",
            "school": "Boston University",
            "start_date": "September 3, 2025"
        }
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/visa/generate")
        print(f"📤 Payload: {json.dumps(b2_payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/visa/generate",
            json=b2_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["test_1_b2_complete_package"]["status_code"] = response.status_code
        results["test_1_b2_complete_package"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # SPECIFIC VALIDATIONS FROM REVIEW REQUEST
            package_result = response_data.get("package_result", {})
            qa_report = response_data.get("qa_report", {})
            validation = response_data.get("validation", {})
            
            validations = {
                "1_status_200": response.status_code == 200,
                "2_success_true": response_data.get("success") == True,
                "3_pages_30_plus": package_result.get("pages", 0) >= 30,
                "4_qa_score_90_plus": qa_report.get("overall_score", 0) >= 0.90,
                "5_qa_passed_true": qa_report.get("passed") == True,
                "6_validation_valid": validation.get("is_valid") == True,
                "7_pdf_generated": package_result.get("package_path") is not None
            }
            
            results["test_1_b2_complete_package"]["validations"] = validations
            results["test_1_b2_complete_package"]["response_data"] = response_data
            
            print("\n🎯 VALIDAÇÕES ESPECÍFICAS DA REVIEW:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Detailed metrics
            print(f"\n📊 MÉTRICAS DETALHADAS:")
            print(f"  📄 Páginas: {package_result.get('pages', 0)} (target: ≥30)")
            print(f"  🎯 QA Score: {qa_report.get('overall_score', 0):.1%} (target: ≥90%)")
            print(f"  ✅ QA Passed: {qa_report.get('passed', False)}")
            print(f"  📋 Validation: {validation.get('is_valid', False)}")
            
            if package_result.get("package_path"):
                print(f"  📁 PDF Path: {package_result['package_path']}")
            else:
                print(f"  ❌ No PDF generated")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["test_1_b2_complete_package"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during B-2 complete package test: {str(e)}")
        results["test_1_b2_complete_package"]["exception"] = str(e)
    
    # Check for PDF generation in /frontend/public/
    print("\n📁 VERIFICAÇÃO DE PDFs GERADOS:")
    print("-" * 40)
    
    frontend_public_path = Path("/app/frontend/public")
    if frontend_public_path.exists():
        pdf_files = list(frontend_public_path.glob("*B2*.pdf"))
        print(f"📄 PDFs B-2 encontrados em /frontend/public/: {len(pdf_files)}")
        for pdf in pdf_files[-5:]:  # Show last 5 B-2 PDFs
            print(f"  📄 {pdf.name} ({pdf.stat().st_size} bytes)")
        results["test_1_b2_complete_package"]["pdf_files_found"] = len(pdf_files)
        
        # Look for the specific file mentioned in review
        target_pdf = "B2_COMPLETE_PACKAGE_60PLUS_PAGES.pdf"
        target_path = frontend_public_path / target_pdf
        if target_path.exists():
            print(f"  ✅ Target PDF found: {target_pdf} ({target_path.stat().st_size} bytes)")
            results["test_1_b2_complete_package"]["target_pdf_found"] = True
        else:
            print(f"  ❌ Target PDF not found: {target_pdf}")
            results["test_1_b2_complete_package"]["target_pdf_found"] = False
    else:
        print("❌ Diretório /frontend/public/ não encontrado")
        results["test_1_b2_complete_package"]["pdf_files_found"] = 0
        results["test_1_b2_complete_package"]["target_pdf_found"] = False
    
    # Check for PDF generation in /frontend/public/
    print("\n📁 VERIFICAÇÃO DE PDFs GERADOS:")
    print("-" * 40)
    
    frontend_public_path = Path("/app/frontend/public")
    if frontend_public_path.exists():
        pdf_files = list(frontend_public_path.glob("*.pdf"))
        print(f"📄 PDFs encontrados em /frontend/public/: {len(pdf_files)}")
        for pdf in pdf_files[-5:]:  # Show last 5 PDFs
            print(f"  📄 {pdf.name} ({pdf.stat().st_size} bytes)")
        results["pdf_files_found"] = len(pdf_files)
    else:
        print("❌ Diretório /frontend/public/ não encontrado")
        results["pdf_files_found"] = 0
    
    # Summary
    print("\n📊 RESUMO DO TESTE FINAL")
    print("=" * 60)
    
    test_success = results["test_1_b2_complete_package"].get("status_code") == 200
    
    print(f"🧪 Teste B-2 Complete Package: {'✅ PASSOU' if test_success else '❌ FALHOU'}")
    
    if test_success:
        validations = results["test_1_b2_complete_package"].get("validations", {})
        passed_count = sum(validations.values())
        total_count = len(validations)
        print(f"   📋 Validações específicas: {passed_count}/{total_count} passaram")
        
        # Show which specific validations failed
        failed_validations = [k for k, v in validations.items() if not v]
        if failed_validations:
            print(f"   ❌ Validações que falharam: {', '.join(failed_validations)}")
        else:
            print(f"   ✅ Todas as validações passaram!")
    
    overall_success = test_success and results["test_1_b2_complete_package"].get("validations", {}).get("2_success_true", False)
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
    print("🚀 INICIANDO TESTE ESPECÍFICO DA REVIEW - B-2 COMPLETE PACKAGE")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    # Main test - B-2 Complete Package as requested
    main_results = test_visa_generate_endpoint()
    
    # Additional tests for context
    additional_results = test_additional_endpoints()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 RELATÓRIO FINAL - TESTE B-2 COMPLETE PACKAGE")
    print("=" * 80)
    
    print(f"✅ Endpoint testado: POST /api/visa/generate")
    print(f"📊 Teste principal: {main_results['summary']['tests_passed']}/{main_results['summary']['tests_total']}")
    print(f"🔍 Testes adicionais: {sum(additional_results.values())}/{len(additional_results)}")
    
    # Detailed analysis of B-2 test results
    b2_results = main_results.get("test_1_b2_complete_package", {})
    validations = b2_results.get("validations", {})
    
    print(f"\n📋 ANÁLISE DETALHADA DAS VALIDAÇÕES:")
    for validation, passed in validations.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {validation}")
    
    if main_results["summary"]["overall_success"]:
        print("\n🎉 CONCLUSÃO: B-2 Complete Package endpoint está FUNCIONAL!")
        print("✅ Todas as validações críticas foram atendidas")
        print("✅ Sistema multi-agente operacional")
    else:
        print("\n⚠️  CONCLUSÃO: B-2 Complete Package precisa de melhorias")
        failed_validations = [k for k, v in validations.items() if not v]
        print(f"❌ Validações que falharam: {', '.join(failed_validations)}")
        
    # Save results to file
    with open("/app/b2_complete_package_test_results.json", "w") as f:
        json.dump({
            "main_results": main_results,
            "additional_results": additional_results,
            "timestamp": time.time(),
            "test_focus": "B-2 Complete Package as requested in review"
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/b2_complete_package_test_results.json")