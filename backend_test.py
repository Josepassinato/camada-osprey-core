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
    - B-2 visa extension with complete package
    - Expected: 30+ pages, 90%+ QA score, valid PDF generation
    
    Expected validations:
    1. ✅ Status 200
    2. ✅ success: true
    3. ✅ package_result.pages >= 30 páginas
    4. ✅ qa_report.overall_score >= 90%
    5. ✅ qa_report.passed = true
    6. ✅ validation.is_valid = true
    7. ✅ Arquivo PDF gerado: B2_COMPLETE_PACKAGE_60PLUS_PAGES.pdf
    """
    
    print("🧪 TESTING MULTI-AGENT VISA ARCHITECTURE ENDPOINT")
    print("=" * 60)
    
    results = {
        "test_1_b2_complete_package": {},
        "summary": {}
    }
    
    # Test 1: B-2 Complete Package (as requested in review)
    print("\n📋 TESTE FINAL: Geração de Pacote B-2 Completo")
    print("-" * 50)
    
    # Test with the EXACT format specified in the review request
    b2_payload = {
        "visa_type": "B-2",
        "user_request": "Preciso estender meu visto de turista B-2 por 6 meses devido a emergência médica. Quero um pacote completo e profissional.",
        "applicant_data": {}
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
    print("\n📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    test1_success = results["test_1_b2_extension"].get("status_code") == 200
    test2_success = results["test_2_h1b_preparation"].get("status_code") == 200
    
    print(f"🧪 Teste 1 (B-2): {'✅ PASSOU' if test1_success else '❌ FALHOU'}")
    print(f"🧪 Teste 2 (H-1B): {'✅ PASSOU' if test2_success else '❌ FALHOU'}")
    
    if test1_success:
        b2_validations = results["test_1_b2_extension"].get("validations", {})
        b2_passed = sum(b2_validations.values())
        b2_total = len(b2_validations)
        print(f"   📋 Validações B-2: {b2_passed}/{b2_total} passaram")
    
    if test2_success:
        h1b_validations = results["test_2_h1b_preparation"].get("validations", {})
        h1b_passed = sum(h1b_validations.values())
        h1b_total = len(h1b_validations)
        print(f"   📋 Validações H-1B: {h1b_passed}/{h1b_total} passaram")
    
    overall_success = test1_success and test2_success
    results["summary"]["overall_success"] = overall_success
    results["summary"]["tests_passed"] = sum([test1_success, test2_success])
    results["summary"]["tests_total"] = 2
    
    print(f"\n🎯 RESULTADO GERAL: {'✅ SUCESSO' if overall_success else '❌ FALHA'}")
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
    print("🚀 INICIANDO TESTES DO ENDPOINT MULTI-AGENTE")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    # Main tests
    main_results = test_visa_generate_endpoint()
    
    # Additional tests
    additional_results = test_additional_endpoints()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 RELATÓRIO FINAL DE TESTES")
    print("=" * 80)
    
    print(f"✅ Endpoint principal testado: POST /api/visa/generate")
    print(f"📊 Testes principais: {main_results['summary']['tests_passed']}/{main_results['summary']['tests_total']}")
    print(f"🔍 Testes adicionais: {sum(additional_results.values())}/{len(additional_results)}")
    
    if main_results["summary"]["overall_success"]:
        print("\n🎉 CONCLUSÃO: Multi-agent visa architecture endpoint está FUNCIONAL!")
        print("✅ Ambos os testes (B-2 e H-1B) passaram com sucesso")
        print("✅ Todas as validações esperadas foram atendidas")
    else:
        print("\n⚠️  CONCLUSÃO: Endpoint precisa de correções")
        print("❌ Nem todos os testes passaram")
        
    # Save results to file
    with open("/app/visa_api_test_results.json", "w") as f:
        json.dump({
            "main_results": main_results,
            "additional_results": additional_results,
            "timestamp": time.time()
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/visa_api_test_results.json")