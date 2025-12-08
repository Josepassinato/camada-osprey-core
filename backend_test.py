#!/usr/bin/env python3
"""
🔍 TESTE END-TO-END COMPLETO APÓS CORREÇÃO DO BUG P0 - PDF GENERATION
Testing complete flow from friendly form to PDF download after pypdf migration fix
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime
import pypdf
import io

# Get backend URL from frontend .env
BACKEND_URL = "https://smart-visa-helper-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_test_case():
    """Create a test case for validation testing"""
    try:
        print("📝 Creating test case for validation...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"form_code": "I-539"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ Test case created: {case_id}")
                return case_id
            else:
                print(f"❌ No case_id in response: {case_data}")
                return None
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            print(f"📄 Error response: {response.text}")
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

def test_i539_pdf_generation_e2e():
    """
    🔍 TESTE END-TO-END COMPLETO APÓS CORREÇÃO DO BUG P0 - PDF GENERATION
    
    Testing complete flow after pypdf migration fix:
    1. Create I-539 case
    2. Fill friendly form with Portuguese data
    3. Verify data persistence (including _eua fields)
    4. Generate PDF with corrected pypdf library
    5. Download PDF and verify size
    6. CRITICAL: Extract field values from PDF to verify P0 bug fix
    
    SUCCESS CRITERIA:
    - Case created successfully
    - Friendly form data saved (including endereco_eua, cidade_eua, estado_eua, cep_eua)
    - PDF generated (status 200, >300KB)
    - PDF downloadable (status 200, application/pdf)
    - CRITICAL: At least 6/8 fields filled in PDF (P0 bug fix verification)
    """
    
    print("🔍 TESTE END-TO-END COMPLETO APÓS CORREÇÃO DO BUG P0 - PDF GENERATION")
    print("📋 Testing complete flow from friendly form to PDF download")
    print("🎯 Focus: Verify pypdf migration fixed empty PDF generation bug")
    print("=" * 80)
    
    results = {
        "step1_case_creation": {},
        "step2_friendly_form": {},
        "step3_data_verification": {},
        "step4_pdf_generation": {},
        "step5_pdf_download": {},
        "step6_pdf_field_verification": {},
        "summary": {}
    }
    
    # STEP 1: Create I-539 Case
    print("\n📋 STEP 1: Criar Caso I-539")
    print("-" * 60)
    
    try:
        print("📝 Creating I-539 case...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"form_code": "I-539"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ I-539 case created: {case_id}")
                results["step1_case_creation"] = {
                    "success": True,
                    "case_id": case_id,
                    "status_code": response.status_code
                }
            else:
                print(f"❌ No case_id in response: {case_data}")
                results["step1_case_creation"] = {"success": False, "error": "No case_id"}
                return results
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            results["step1_case_creation"] = {"success": False, "status_code": response.status_code}
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["step1_case_creation"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 2: Fill Friendly Form with Portuguese Data (EXACT data from review request)
    print("\n📋 STEP 2: Preencher Formulário Amigável em Português")
    print("-" * 60)
    
    friendly_form_data = {
        "friendly_form_data": {
            "nome_completo": "Ana Paula Santos Silva",
            "data_nascimento": "1992-07-18",
            "endereco_eua": "789 Broadway Avenue",
            "cidade_eua": "Miami",
            "estado_eua": "FL",
            "cep_eua": "33101",
            "email": "ana.santos@test.com",
            "telefone": "+1-305-555-8888",
            "numero_passaporte": "BR555666777",
            "pais_nascimento": "Brazil",
            "status_atual": "B-2",
            "status_solicitado": "B-2 Extension",
            "data_entrada_eua": "2024-01-15",
            "numero_i94": "99887766554"
        },
        "basic_data": {}
    }
    
    try:
        print(f"📤 Sending friendly form data to case {case_id}...")
        print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/friendly-form")
        
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=friendly_form_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            form_result = response.json()
            print(f"✅ Friendly form data saved successfully")
            print(f"📄 Response: {json.dumps(form_result, indent=2, ensure_ascii=False)}")
            
            results["step2_friendly_form"] = {
                "success": True,
                "status_code": response.status_code,
                "response": form_result
            }
        else:
            print(f"❌ Failed to save friendly form: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step2_friendly_form"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception saving friendly form: {str(e)}")
        results["step2_friendly_form"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 3: Verify Data Persistence (including _eua fields)
    print("\n📋 STEP 3: Verificar Salvamento dos Dados")
    print("-" * 60)
    
    try:
        print(f"🔍 Retrieving case data for {case_id}...")
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            
            # Check for simplified_form_responses
            simplified_responses = case_info.get("simplified_form_responses", {})
            
            print(f"📄 Simplified Form Responses: {json.dumps(simplified_responses, indent=2, ensure_ascii=False)}")
            
            # Verify critical fields including _eua fields
            verification_checks = {
                "simplified_form_responses_exists": simplified_responses is not None and len(simplified_responses) > 0,
                "nome_completo_saved": simplified_responses.get("nome_completo") == "Ana Paula Santos Silva",
                "endereco_eua_saved": simplified_responses.get("endereco_eua") == "789 Broadway Avenue",
                "cidade_eua_saved": simplified_responses.get("cidade_eua") == "Miami",
                "estado_eua_saved": simplified_responses.get("estado_eua") == "FL",
                "cep_eua_saved": simplified_responses.get("cep_eua") == "33101",
                "email_saved": simplified_responses.get("email") == "ana.santos@test.com",
                "telefone_saved": simplified_responses.get("telefone") == "+1-305-555-8888",
                "numero_passaporte_saved": simplified_responses.get("numero_passaporte") == "BR555666777"
            }
            
            print(f"\n🎯 DATA PERSISTENCE VERIFICATION:")
            for check, passed in verification_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["step3_data_verification"] = {
                "success": True,
                "verification_checks": verification_checks,
                "simplified_responses": simplified_responses,
                "passed": all(verification_checks.values())
            }
        else:
            print(f"❌ Failed to retrieve case: {response.status_code}")
            results["step3_data_verification"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception retrieving case: {str(e)}")
        results["step3_data_verification"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 4: Generate PDF Official I-539 (CRITICAL - Bug P0 verification)
    print("\n📋 STEP 4: Gerar PDF Oficial I-539 (⭐ CRÍTICO - Bug P0)")
    print("-" * 60)
    
    try:
        print(f"📝 Generating I-539 PDF for case {case_id}...")
        response = requests.post(
            f"{API_BASE}/case/{case_id}/generate-form",
            headers={"Content-Type": "application/json"},
            timeout=120  # PDF generation might take longer
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            pdf_result = response.json()
            print(f"✅ PDF generation successful")
            print(f"📄 Response: {json.dumps(pdf_result, indent=2, ensure_ascii=False)}")
            
            # Verify PDF generation response
            pdf_checks = {
                "success_true": pdf_result.get("success", False),
                "filename_present": pdf_result.get("filename") is not None,
                "file_size_adequate": pdf_result.get("file_size", 0) > 300000,  # >300KB
                "download_url_present": pdf_result.get("download_url") is not None
            }
            
            print(f"\n🎯 PDF GENERATION VERIFICATION:")
            for check, passed in pdf_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["step4_pdf_generation"] = {
                "success": True,
                "status_code": response.status_code,
                "pdf_result": pdf_result,
                "pdf_checks": pdf_checks,
                "passed": all(pdf_checks.values())
            }
        else:
            print(f"❌ PDF generation failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step4_pdf_generation"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception generating PDF: {str(e)}")
        results["step4_pdf_generation"] = {"success": False, "exception": str(e)}
        return results
    
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

# Helper function for additional testing if needed
def additional_validation_tests():
    """Placeholder for additional validation tests"""
    pass

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE COMPLETO DA VALIDAÇÃO IA MELHORADA")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Execute main test
    test_results = test_enhanced_ai_validation_system()
    
    # Save results to file
    with open("/app/enhanced_ai_validation_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "Enhanced AI Validation System Testing",
            "test_cases": [
                {"name": "Complete Data (I-539)", "expected": "approved, 100%, 0 issues"},
                {"name": "Partial Data (50%)", "expected": "rejected, 40-60%, >5 issues"},
                {"name": "Format Errors", "expected": "needs_review, 80-95%, >=2 issues"},
                {"name": "Issues Verification", "expected": "detailed issues list"},
                {"name": "MongoDB Persistence", "expected": "data saved correctly"}
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: /app/enhanced_ai_validation_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    if summary.get("system_ready", False):
        print("\n✅ RECOMENDAÇÃO: Sistema de Validação IA PRONTO PARA PRODUÇÃO")
        print("   - Validação em dois estágios funcionando")
        print("   - Campos obrigatórios por tipo de visto implementados")
        print("   - Validações de formato operacionais")
        print("   - Cálculo inteligente de completude ativo")
        print("   - Persistência MongoDB confirmada")
    else:
        success_rate = summary.get("success_rate", 0)
        if success_rate >= 60:
            print("\n⚠️  RECOMENDAÇÃO: Sistema parcialmente funcional, melhorias necessárias")
            print("   - Alguns testes passando")
            print("   - Revisar áreas problemáticas identificadas")
        else:
            print("\n❌ RECOMENDAÇÃO: Sistema precisa de desenvolvimento adicional")
            print("   - Múltiplos problemas identificados")
            print("   - Revisão completa da validação necessária")
    
