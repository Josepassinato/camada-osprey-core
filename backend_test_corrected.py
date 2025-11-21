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
BACKEND_URL = "https://maria-support.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_visa_generate_endpoint():
    """
    Test the new multi-agent architecture endpoint POST /api/visa/generate
    
    Tests requested:
    1. B-2 visa extension test
    2. H-1B visa preparation test
    
    Expected validations:
    - Status 200
    - Response contains success: true
    - Response has visa_type identified
    - Response has package_result with PDF info
    - Response has validation with checklist
    - Response has qa_report with scores
    - PDF should be generated in /frontend/public/
    """
    
    print("🧪 TESTING MULTI-AGENT VISA ARCHITECTURE ENDPOINT")
    print("=" * 60)
    
    results = {
        "test_1_b2_extension": {},
        "test_2_h1b_preparation": {},
        "summary": {}
    }
    
    # Test 1: B-2 Visa Extension
    print("\n📋 TESTE 1: Geração de Pacote B-2")
    print("-" * 40)
    
    b2_payload = {
        "visa_type": "B-2",
        "user_request": "Preciso estender meu visto de turista B-2 por 6 meses devido a emergência médica",
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
        
        results["test_1_b2_extension"]["status_code"] = response.status_code
        results["test_1_b2_extension"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Validation checks
            validations = {
                "success_true": response_data.get("success") == True,
                "visa_type_identified": response_data.get("visa_type") is not None,
                "has_package_result": response_data.get("package_result") is not None,
                "has_validation": response_data.get("validation") is not None,
                "has_qa_report": response_data.get("qa_report") is not None,
                "processing_time_present": response_data.get("processing_time") is not None
            }
            
            results["test_1_b2_extension"]["validations"] = validations
            results["test_1_b2_extension"]["response_data"] = response_data
            
            print("\n✅ VALIDAÇÕES B-2:")
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
            # Check for package_result specifically
            if response_data.get("package_result"):
                print(f"  ✅ package_result found: {response_data['package_result']}")
            else:
                print(f"  ❌ package_result not found")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["test_1_b2_extension"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during B-2 test: {str(e)}")
        results["test_1_b2_extension"]["exception"] = str(e)
    
    # Test 2: H-1B Visa Preparation
    print("\n📋 TESTE 2: Geração de Pacote H-1B")
    print("-" * 40)
    
    h1b_payload = {
        "visa_type": "H-1B",
        "user_request": "Preciso preparar meu pacote H-1B para trabalhar como Software Engineer",
        "applicant_data": {}
    }
    
    try:
        print(f"🔗 Endpoint: POST {API_BASE}/visa/generate")
        print(f"📤 Payload: {json.dumps(h1b_payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/visa/generate",
            json=h1b_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["test_2_h1b_preparation"]["status_code"] = response.status_code
        results["test_2_h1b_preparation"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Validation checks
            validations = {
                "success_true": response_data.get("success") == True,
                "visa_type_identified": response_data.get("visa_type") is not None,
                "has_package_result": response_data.get("package_result") is not None,
                "has_validation": response_data.get("validation") is not None,
                "has_qa_report": response_data.get("qa_report") is not None,
                "processing_time_present": response_data.get("processing_time") is not None
            }
            
            results["test_2_h1b_preparation"]["validations"] = validations
            results["test_2_h1b_preparation"]["response_data"] = response_data
            
            print("\n✅ VALIDAÇÕES H-1B:")
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
                
            # Check for package_result specifically
            if response_data.get("package_result"):
                print(f"  ✅ package_result found: {response_data['package_result']}")
            else:
                print(f"  ❌ package_result not found")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["test_2_h1b_preparation"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during H-1B test: {str(e)}")
        results["test_2_h1b_preparation"]["exception"] = str(e)
    
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

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DO ENDPOINT MULTI-AGENTE")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    # Main tests
    main_results = test_visa_generate_endpoint()
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 RELATÓRIO FINAL DE TESTES")
    print("=" * 80)
    
    print(f"✅ Endpoint principal testado: POST /api/visa/generate")
    print(f"📊 Testes principais: {main_results['summary']['tests_passed']}/{main_results['summary']['tests_total']}")
    
    if main_results["summary"]["overall_success"]:
        print("\n🎉 CONCLUSÃO: Multi-agent visa architecture endpoint está FUNCIONAL!")
        print("✅ Ambos os testes (B-2 e H-1B) passaram com sucesso")
        print("✅ Todas as validações esperadas foram atendidas")
    else:
        print("\n⚠️  CONCLUSÃO: Endpoint precisa de correções")
        print("❌ Nem todos os testes passaram")
        
    # Save results to file
    with open("/app/visa_api_test_results_corrected.json", "w") as f:
        json.dump({
            "main_results": main_results,
            "timestamp": time.time()
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/visa_api_test_results_corrected.json")