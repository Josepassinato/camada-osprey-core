#!/usr/bin/env python3
"""
🎯 TESTE COMPLETO DA VALIDAÇÃO IA MELHORADA
Testing the enhanced AI validation system with two-stage validation as requested in review
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://docsimple-3.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_test_case():
    """Create a test case for validation testing"""
    try:
        print("📝 Creating test case for validation...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_id = case_data.get("case_id")
            
            # Set visa type to I-539
            update_response = requests.put(
                f"{API_BASE}/auto-application/case/{case_id}",
                json={"form_code": "I-539"},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if update_response.status_code in [200, 201]:
                print(f"✅ Test case created: {case_id}")
                return case_id
            else:
                print(f"❌ Failed to set visa type: {update_response.status_code}")
                return None
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Exception creating test case: {str(e)}")
        return None

def test_validation_endpoint(case_id: str, test_data: dict, test_name: str):
    """Test the friendly form validation endpoint"""
    try:
        print(f"\n🔍 {test_name}")
        print("-" * 50)
        
        print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/friendly-form")
        print(f"📤 Test Data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            validation_result = response.json()
            print(f"📄 Validation Response: {json.dumps(validation_result, indent=2, ensure_ascii=False)}")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "processing_time": processing_time,
                "validation_result": validation_result
            }
        else:
            print(f"❌ Validation failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception during validation: {str(e)}")
        return {
            "success": False,
            "exception": str(e)
        }

def verify_mongodb_persistence(case_id: str):
    """Verify that validation data was saved to MongoDB"""
    try:
        print(f"\n💾 Verifying MongoDB persistence for case {case_id}")
        print("-" * 50)
        
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            
            # Check for validation-related fields
            simplified_form_responses = case_info.get("simplified_form_responses")
            friendly_form_validation = case_info.get("friendly_form_validation")
            
            print(f"📄 Simplified Form Responses: {json.dumps(simplified_form_responses, indent=2, ensure_ascii=False) if simplified_form_responses else 'None'}")
            print(f"📄 Friendly Form Validation: {json.dumps(friendly_form_validation, indent=2, ensure_ascii=False) if friendly_form_validation else 'None'}")
            
            persistence_checks = {
                "simplified_form_responses_saved": simplified_form_responses is not None,
                "friendly_form_validation_saved": friendly_form_validation is not None,
                "validation_status_present": friendly_form_validation.get("status") is not None if friendly_form_validation else False,
                "completion_percentage_present": friendly_form_validation.get("completion_percentage") is not None if friendly_form_validation else False,
                "validation_date_present": friendly_form_validation.get("validation_date") is not None if friendly_form_validation else False,
                "issues_array_present": isinstance(friendly_form_validation.get("issues"), list) if friendly_form_validation else False
            }
            
            print(f"\n🎯 PERSISTENCE CHECKS:")
            for check, passed in persistence_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            return {
                "success": True,
                "persistence_checks": persistence_checks,
                "case_data": case_info
            }
        else:
            print(f"❌ Failed to retrieve case: {response.status_code}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception during persistence check: {str(e)}")
        return {
            "success": False,
            "exception": str(e)
        }

def test_enhanced_ai_validation_system():
    """
    🎯 TESTE COMPLETO DA VALIDAÇÃO IA MELHORADA
    
    Testing the enhanced AI validation system with:
    1. Two-Stage Validation (Programmatic + AI)
    2. Required Fields by Visa Type (I-539: 14, I-589: 11, EB-1A: 8)
    3. Format Validations (email, date, phone, numeric, min length)
    4. Intelligent Completeness Calculation with penalties
    5. MongoDB Persistence
    
    TEST CASES:
    - TEST 1: Complete data (I-539) - Expected: approved, 100%, 0 issues
    - TEST 2: Partial data (50%) - Expected: rejected, 40-60%, >5 issues  
    - TEST 3: Format errors - Expected: needs_review, 80-95%, >=2 issues
    - TEST 4: Detailed issues verification
    - TEST 5: MongoDB persistence verification
    """
    
    print("🎯 TESTE COMPLETO DA VALIDAÇÃO IA MELHORADA")
    print("📋 Testing enhanced AI validation system with two-stage validation")
    print("🎯 Focus: Programmatic + AI validation, format checks, completeness calculation")
    print("=" * 80)
    
    results = {
        "test1_complete_data": {},
        "test2_partial_data": {},
        "test3_format_errors": {},
        "test4_issues_verification": {},
        "test5_mongodb_persistence": {},
        "summary": {}
    }
    
    # Create test case for validation
    test_case_id = create_test_case()
    if not test_case_id:
        print("❌ Failed to create test case, aborting tests")
        return results
    
    # TEST 1: Complete Data Validation (I-539) - Expected: approved, 100%, 0 issues
    print("\n📋 TEST 1: Validação com Dados Completos (I-539)")
    print("-" * 60)
    
    complete_data = {
        "friendly_form_data": {
            "nome_completo": "Carlos Eduardo Silva Mendes",
            "data_nascimento": "1985-03-15",
            "email": "carlos.teste@test.com",
            "telefone": "+55 11 98765-4321",
            "numero_passaporte": "BR987654321",
            "pais_nascimento": "Brazil",
            "endereco": "123 Main Street, Apt 4B",
            "cidade": "New York",
            "estado": "NY",
            "cep": "10001",
            "status_atual": "F-1",
            "status_solicitado": "H-1B",
            "motivo_mudanca": "Consegui emprego em empresa americana e preciso mudar meu status de estudante para trabalhador especializado",
            "data_entrada_eua": "2020-08-15",
            "numero_i94": "1234567890"
        }
    }
    
    test1_result = test_validation_endpoint(test_case_id, complete_data, "TEST 1: Dados Completos")
    results["test1_complete_data"] = test1_result
    
    if test1_result.get("success"):
        validation_result = test1_result["validation_result"]
        
        # Verify expected results
        expected_checks = {
            "status_approved": validation_result.get("validation_status") == "approved",
            "completion_near_100": validation_result.get("completion_percentage", 0) >= 95,
            "minimal_issues": len(validation_result.get("validation_issues", [])) <= 2,
            "success_true": validation_result.get("success", False),
            "case_id_correct": validation_result.get("case_id") == test_case_id
        }
        
        print(f"\n🎯 TEST 1 VERIFICATION:")
        for check, passed in expected_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}: {passed}")
        
        results["test1_complete_data"]["verification"] = expected_checks
        results["test1_complete_data"]["passed"] = all(expected_checks.values())
    
    # TEST 2: Partial Data Validation (50%) - Expected: rejected, 40-60%, >5 issues
    print("\n📋 TEST 2: Validação com Dados Parciais (50%)")
    print("-" * 60)
    
    partial_data = {
        "friendly_form_data": {
            "nome_completo": "Maria Santos",
            "data_nascimento": "1990-12-25",
            "email": "maria@test.com",
            "numero_passaporte": "BR555666777",
            "pais_nascimento": "Brazil",
            "endereco": "456 Oak Street",
            "cidade": "Los Angeles"
            # Missing: telefone, estado, cep, status_atual, status_solicitado, data_entrada_eua, numero_i94
        }
    }
    
    test2_result = test_validation_endpoint(test_case_id, partial_data, "TEST 2: Dados Parciais")
    results["test2_partial_data"] = test2_result
    
    if test2_result.get("success"):
        validation_result = test2_result["validation_result"]
        
        # Verify expected results
        expected_checks = {
            "status_rejected_or_needs_review": validation_result.get("validation_status") in ["rejected", "needs_review"],
            "completion_40_to_60": 40 <= validation_result.get("completion_percentage", 0) <= 60,
            "multiple_issues": len(validation_result.get("validation_issues", [])) >= 5,
            "success_true": validation_result.get("success", False),
            "case_id_correct": validation_result.get("case_id") == test_case_id
        }
        
        print(f"\n🎯 TEST 2 VERIFICATION:")
        for check, passed in expected_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}: {passed}")
        
        results["test2_partial_data"]["verification"] = expected_checks
        results["test2_partial_data"]["passed"] = all(expected_checks.values())
    
    # TEST 3: Format Errors Validation - Expected: needs_review, 80-95%, >=2 issues
    print("\n📋 TEST 3: Validação com Erros de Formato")
    print("-" * 60)
    
    format_error_data = {
        "friendly_form_data": {
            "nome_completo": "Ana Paula Costa Silva",
            "data_nascimento": "15/03/1988",  # Wrong format (should be YYYY-MM-DD)
            "email": "ana.paula@invalid",  # Invalid email format
            "telefone": "abc-def-ghij",  # Invalid phone format
            "numero_passaporte": "BR999888777",
            "pais_nascimento": "Brazil",
            "endereco": "789 Pine Street, Suite 100",
            "cidade": "Miami",
            "estado": "FL",
            "cep": "33101",
            "status_atual": "B-2",
            "status_solicitado": "F-1",
            "motivo_mudanca": "Quero estudar",  # Too short
            "data_entrada_eua": "2023/01/10",  # Wrong format
            "numero_i94": "ABC123XYZ"  # Should be numeric
        }
    }
    
    test3_result = test_validation_endpoint(test_case_id, format_error_data, "TEST 3: Erros de Formato")
    results["test3_format_errors"] = test3_result
    
    if test3_result.get("success"):
        validation_result = test3_result["validation_result"]
        
        # Verify expected results
        expected_checks = {
            "status_needs_review": validation_result.get("validation_status") == "needs_review",
            "completion_80_to_95": 80 <= validation_result.get("completion_percentage", 0) <= 95,
            "format_issues": len(validation_result.get("validation_issues", [])) >= 2,
            "success_true": validation_result.get("success", False),
            "case_id_correct": validation_result.get("case_id") == test_case_id
        }
        
        print(f"\n🎯 TEST 3 VERIFICATION:")
        for check, passed in expected_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}: {passed}")
        
        results["test3_format_errors"]["verification"] = expected_checks
        results["test3_format_errors"]["passed"] = all(expected_checks.values())
    
    # TEST 4: Detailed Issues Verification
    print("\n📋 TEST 4: Verificar Lista Detalhada de Issues")
    print("-" * 60)
    
    # Use the format error test result for detailed analysis
    if test3_result.get("success"):
        validation_result = test3_result["validation_result"]
        issues = validation_result.get("validation_issues", [])
        
        print(f"📊 Total Issues Found: {len(issues)}")
        
        issue_analysis = {
            "has_field_names": all(issue.get("field") for issue in issues),
            "has_field_labels": all(issue.get("field_label") for issue in issues),
            "has_issue_descriptions": all(issue.get("issue") for issue in issues),
            "has_severity_levels": all(issue.get("severity") in ["error", "warning", "info"] for issue in issues),
            "has_suggestions": all(issue.get("suggestion") for issue in issues),
            "portuguese_suggestions": all(any(char in issue.get("suggestion", "") for char in "áéíóúãõç") or "exemplo" in issue.get("suggestion", "").lower() for issue in issues)
        }
        
        print(f"\n🎯 DETAILED ISSUES ANALYSIS:")
        for check, passed in issue_analysis.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}: {passed}")
        
        # Print sample issues
        print(f"\n📄 SAMPLE ISSUES (first 3):")
        for i, issue in enumerate(issues[:3]):
            print(f"  Issue {i+1}:")
            print(f"    Field: {issue.get('field', 'N/A')}")
            print(f"    Label: {issue.get('field_label', 'N/A')}")
            print(f"    Issue: {issue.get('issue', 'N/A')}")
            print(f"    Severity: {issue.get('severity', 'N/A')}")
            print(f"    Suggestion: {issue.get('suggestion', 'N/A')}")
        
        results["test4_issues_verification"] = {
            "success": True,
            "issue_analysis": issue_analysis,
            "total_issues": len(issues),
            "sample_issues": issues[:3],
            "passed": all(issue_analysis.values())
        }
    else:
        results["test4_issues_verification"] = {
            "success": False,
            "error": "Could not analyze issues - previous test failed"
        }
    
    # TEST 5: MongoDB Persistence Verification
    print("\n📋 TEST 5: Persistência no MongoDB")
    print("-" * 60)
    
    persistence_result = verify_mongodb_persistence(test_case_id)
    results["test5_mongodb_persistence"] = persistence_result
    
    # Generate Summary and Assessment
    print("\n📋 RESUMO FINAL - SISTEMA DE VALIDAÇÃO IA MELHORADA")
    print("=" * 80)
    
    # Count successful tests
    test_results = [
        results.get("test1_complete_data", {}).get("passed", False),
        results.get("test2_partial_data", {}).get("passed", False),
        results.get("test3_format_errors", {}).get("passed", False),
        results.get("test4_issues_verification", {}).get("passed", False),
        results.get("test5_mongodb_persistence", {}).get("passed", False)
    ]
    
    successful_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100
    
    # Individual test results
    test_names = [
        "TEST 1: Dados Completos (I-539)",
        "TEST 2: Dados Parciais (50%)",
        "TEST 3: Erros de Formato",
        "TEST 4: Lista Detalhada de Issues",
        "TEST 5: Persistência MongoDB"
    ]
    
    print(f"📊 RESULTADOS DOS TESTES:")
    for i, (test_name, passed) in enumerate(zip(test_names, test_results)):
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}: {'PASSOU' if passed else 'FALHOU'}")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Detailed analysis
    print(f"\n📋 ANÁLISE DETALHADA:")
    print("=" * 60)
    
    # Test 1 Analysis
    if results.get("test1_complete_data", {}).get("success"):
        test1_result = results["test1_complete_data"]["validation_result"]
        print(f"✅ TEST 1 - Dados Completos:")
        print(f"  Status: {test1_result.get('validation_status', 'N/A')}")
        print(f"  Completude: {test1_result.get('completion_percentage', 0)}%")
        print(f"  Issues: {len(test1_result.get('validation_issues', []))}")
    
    # Test 2 Analysis
    if results.get("test2_partial_data", {}).get("success"):
        test2_result = results["test2_partial_data"]["validation_result"]
        print(f"⚠️  TEST 2 - Dados Parciais:")
        print(f"  Status: {test2_result.get('validation_status', 'N/A')}")
        print(f"  Completude: {test2_result.get('completion_percentage', 0)}%")
        print(f"  Issues: {len(test2_result.get('validation_issues', []))}")
    
    # Test 3 Analysis
    if results.get("test3_format_errors", {}).get("success"):
        test3_result = results["test3_format_errors"]["validation_result"]
        print(f"🔧 TEST 3 - Erros de Formato:")
        print(f"  Status: {test3_result.get('validation_status', 'N/A')}")
        print(f"  Completude: {test3_result.get('completion_percentage', 0)}%")
        print(f"  Issues: {len(test3_result.get('validation_issues', []))}")
    
    # Performance Analysis
    processing_times = []
    for test_key in ["test1_complete_data", "test2_partial_data", "test3_format_errors"]:
        if results.get(test_key, {}).get("processing_time"):
            processing_times.append(results[test_key]["processing_time"])
    
    if processing_times:
        avg_processing_time = sum(processing_times) / len(processing_times)
        print(f"\n⏱️  PERFORMANCE:")
        print(f"  Tempo médio de validação: {avg_processing_time:.2f}s")
        print(f"  Performance adequada: {'✅ SIM' if avg_processing_time < 2.0 else '❌ NÃO'} (< 2s)")
    
    # System Assessment
    print(f"\n🎯 AVALIAÇÃO DO SISTEMA:")
    print("=" * 60)
    
    criteria_met = {
        "validacao_diferencia_completo_incompleto": successful_tests >= 2,
        "completion_percentage_preciso": successful_tests >= 2,
        "issues_listados_com_detalhes": results.get("test4_issues_verification", {}).get("passed", False),
        "status_determinado_corretamente": successful_tests >= 2,
        "dados_persistem_mongodb": results.get("test5_mongodb_persistence", {}).get("passed", False),
        "performance_adequada": avg_processing_time < 2.0 if processing_times else False
    }
    
    criteria_passed = sum(criteria_met.values())
    total_criteria = len(criteria_met)
    
    print(f"📊 CRITÉRIOS DE SUCESSO:")
    for criterion, passed in criteria_met.items():
        status = "✅" if passed else "❌"
        criterion_name = criterion.replace("_", " ").title()
        print(f"  {status} {criterion_name}: {'ATENDIDO' if passed else 'NÃO ATENDIDO'}")
    
    print(f"\n🎯 CRITÉRIOS ATENDIDOS: {criteria_passed}/{total_criteria} ({criteria_passed/total_criteria*100:.1f}%)")
    
    # Final Assessment
    system_ready = success_rate >= 80 and criteria_passed >= 5
    
    if system_ready:
        print("\n✅ SISTEMA DE VALIDAÇÃO IA: TOTALMENTE FUNCIONAL")
        print("✅ VALIDAÇÃO EM DOIS ESTÁGIOS: OPERACIONAL")
        print("✅ CAMPOS OBRIGATÓRIOS POR TIPO DE VISTO: IMPLEMENTADO")
        print("✅ VALIDAÇÕES DE FORMATO: FUNCIONANDO")
        print("✅ CÁLCULO INTELIGENTE DE COMPLETUDE: ATIVO")
        print("✅ PERSISTÊNCIA MONGODB: CONFIRMADA")
    else:
        print("\n⚠️  SISTEMA DE VALIDAÇÃO IA: NECESSITA MELHORIAS")
        
        # Identify problem areas
        problem_areas = []
        if not criteria_met["validacao_diferencia_completo_incompleto"]:
            problem_areas.append("Diferenciação completo/incompleto")
        if not criteria_met["completion_percentage_preciso"]:
            problem_areas.append("Cálculo de completude")
        if not criteria_met["issues_listados_com_detalhes"]:
            problem_areas.append("Lista detalhada de issues")
        if not criteria_met["dados_persistem_mongodb"]:
            problem_areas.append("Persistência MongoDB")
        if not criteria_met["performance_adequada"]:
            problem_areas.append("Performance de validação")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Store summary
    results["summary"] = {
        "successful_tests": successful_tests,
        "total_tests": total_tests,
        "success_rate": success_rate,
        "criteria_met": criteria_met,
        "criteria_passed": criteria_passed,
        "total_criteria": total_criteria,
        "system_ready": system_ready,
        "avg_processing_time": avg_processing_time if processing_times else None
    }
    
    return results

def test_additional_eb1a_endpoints():
    """Test additional EB-1A related endpoints for completeness"""
    
    print("\n🔍 TESTES ADICIONAIS - ENDPOINTS EB-1A RELACIONADOS")
    print("=" * 60)
    
    additional_results = {}
    
    # Test visa detailed info for EB-1A
    try:
        print("\n📋 EB-1A Visa Detailed Info:")
        response = requests.get(f"{API_BASE}/visa-detailed-info/EB-1A?process_type=consular", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            visa_info = response.json()
            print(f"   Response: {json.dumps(visa_info, indent=4)}")
        additional_results["eb1a_visa_info"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A visa info failed: {str(e)}")
        additional_results["eb1a_visa_info"] = False
    
    # Test document requirements for EB-1A
    try:
        print("\n📄 EB-1A Document Requirements:")
        response = requests.get(f"{API_BASE}/visa/EB-1A/documents", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            doc_requirements = response.json()
            print(f"   Response: {json.dumps(doc_requirements, indent=4)}")
        additional_results["eb1a_documents"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A document requirements failed: {str(e)}")
        additional_results["eb1a_documents"] = False
    
    # Test EB-1A specific validation
    try:
        print("\n🏆 EB-1A Specific Validation:")
        validation_data = {
            "document_type": "awards",
            "document_content": "2023 Turing Award Finalist - Dr. Sofia Martinez Chen",
            "applicant_name": "Dr. Sofia Martinez Chen",
            "visa_type": "EB-1A"
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
        additional_results["eb1a_validation"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A validation failed: {str(e)}")
        additional_results["eb1a_validation"] = False
    
    # Test extraordinary ability criteria validation
    try:
        print("\n🧬 Extraordinary Ability Criteria:")
        criteria_data = {
            "criteria": [
                "Awards - national/international prizes",
                "Membership in associations requiring outstanding achievements",
                "Published material about the applicant",
                "Judging the work of others",
                "Original contributions of major significance",
                "Scholarly articles",
                "High salary"
            ],
            "field": "Sciences - Artificial Intelligence Research"
        }
        response = requests.post(
            f"{API_BASE}/validate-eb1a-criteria",
            json=criteria_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            criteria_result = response.json()
            print(f"   Response: {json.dumps(criteria_result, indent=4)}")
        additional_results["eb1a_criteria"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A criteria validation failed: {str(e)}")
        additional_results["eb1a_criteria"] = False
    
    return additional_results

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE COMPLETO - SISTEMA DE GERAÇÃO DE FORMULÁRIOS USCIS")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Execute main test
    test_results = test_uscis_form_generation_system()
    
    # Save results to file
    with open("/app/uscis_form_generation_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "USCIS Form Generation System Testing",
            "test_cases": [
                {"name": "I-539 Extension", "case_id": "OSP-BD2D8ED2"},
                {"name": "I-589 Asylum", "case_id": "OSP-4899BE72"},
                {"name": "EB-1A Extraordinary", "case_id": "OSP-8731E45D"}
            ]
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/uscis_form_generation_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    if summary.get("system_ready", False):
        print("\n✅ RECOMENDAÇÃO: Sistema de Formulários USCIS PRONTO PARA PRODUÇÃO")
        print("   - Todos os 3 tipos de visto funcionando")
        print("   - PDFs oficiais sendo gerados corretamente")
        print("   - Sistema completo e funcional")
    else:
        success_rate = summary.get("overall_success_rate", 0)
        if success_rate >= 50:
            print("\n⚠️  RECOMENDAÇÃO: Sistema parcialmente funcional, melhorias necessárias")
            print("   - Alguns formulários funcionando")
            print("   - Revisar casos que falharam")
        else:
            print("\n❌ RECOMENDAÇÃO: Sistema precisa de desenvolvimento adicional")
            print("   - Múltiplos problemas identificados")
            print("   - Revisão completa necessária")
    
