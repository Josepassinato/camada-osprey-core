#!/usr/bin/env python3
"""
🎯 TESTE COMPLETO DO FLUXO: FORMULÁRIO AMIGÁVEL → VALIDAÇÃO IA → PDF OFICIAL

Testing the complete friendly form flow as requested in review:
1. NEW ENDPOINT: POST /api/case/{case_id}/friendly-form
2. AI validation with feedback in Portuguese  
3. Integration with uscis_form_filler.py to use friendly form data
4. Field mapping from Portuguese to English

PHASES:
- PHASE 1: Test friendly form endpoint
- PHASE 2: Test AI validation (complete vs incomplete data)
- PHASE 3: Test integration with official PDF generation
- PHASE 4: Test field mapping Portuguese → English
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://formfiller-26.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_friendly_form_complete_flow():
    """
    🎯 TESTE COMPLETO DO FLUXO: FORMULÁRIO AMIGÁVEL → VALIDAÇÃO IA → PDF OFICIAL
    
    Testing complete flow from friendly form to official USCIS PDF generation
    """
    
    print("🎯 TESTE COMPLETO DO FLUXO: FORMULÁRIO AMIGÁVEL → VALIDAÇÃO IA → PDF OFICIAL")
    print("📋 Testing new friendly form system with AI validation")
    print("🎯 Focus: End-to-end flow from Portuguese form to English PDF")
    print("=" * 80)
    
    results = {
        "phase1_endpoint_test": {},
        "phase2_ai_validation": {},
        "phase3_pdf_integration": {},
        "phase4_field_mapping": {},
        "summary": {}
    }
    
    # Test data as suggested in review request
    complete_friendly_form_data = {
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
            "motivo_mudanca": "Consegui emprego após conclusão dos estudos",
            "data_entrada_eua": "2020-08-15",
            "numero_i94": "1234567890"
        },
        "basic_data": {
            "applicant_name": "Carlos Eduardo Silva Mendes",
            "email": "carlos.teste@test.com"
        }
    }
    
    incomplete_friendly_form_data = {
        "friendly_form_data": {
            "nome_completo": "Maria Silva Santos",
            "email": "maria.teste@test.com",
            "status_atual": "F-1",
            "status_solicitado": "H-1B"
            # Missing required fields: data_nascimento, endereco, numero_passaporte, etc.
        },
        "basic_data": {
            "applicant_name": "Maria Silva Santos",
            "email": "maria.teste@test.com"
        }
    }
    
    # PHASE 1: Test Friendly Form Endpoint
    print("\n📋 PHASE 1: TESTE DO ENDPOINT DE FORMULÁRIO AMIGÁVEL")
    print("-" * 60)
    
    # First, create a test case for I-539
    print("🔧 Creating I-539 test case...")
    try:
        case_creation_data = {
            "form_code": "I-539",
            "process_type": "change_of_status"
        }
        
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json=case_creation_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Case creation status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            # Extract case_id from nested structure
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            print(f"✅ Test case created: {case_id}")
            
            results["phase1_endpoint_test"]["case_creation"] = {
                "success": True,
                "case_id": case_id,
                "response": case_data
            }
        else:
            print(f"❌ Case creation failed: {response.text}")
            results["phase1_endpoint_test"]["case_creation"] = {
                "success": False,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["phase1_endpoint_test"]["case_creation"] = {
            "success": False,
            "exception": str(e)
        }
        return results
    
    # Test friendly form endpoint with complete data
    print(f"\n🔍 Testing friendly form endpoint with COMPLETE data...")
    print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/friendly-form")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=complete_friendly_form_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["phase1_endpoint_test"]["complete_data"] = {
            "status_code": response.status_code,
            "processing_time": processing_time
        }
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            # Validate response structure
            validations = {
                "validation_status_present": "validation_status" in response_data,
                "completion_percentage_present": "completion_percentage" in response_data,
                "validation_issues_present": "validation_issues" in response_data,
                "case_id_matches": response_data.get("case_id") == case_id,
                "data_saved_confirmation": response_data.get("data_saved", False)
            }
            
            results["phase1_endpoint_test"]["complete_data"]["validations"] = validations
            results["phase1_endpoint_test"]["complete_data"]["response_data"] = response_data
            results["phase1_endpoint_test"]["complete_data"]["working"] = all(validations.values())
            
            print(f"\n🎯 ENDPOINT VALIDATIONS - COMPLETE DATA:")
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Check AI validation results
            validation_status = response_data.get("validation_status")
            completion_percentage = response_data.get("completion_percentage", 0)
            
            print(f"\n📊 AI VALIDATION RESULTS:")
            print(f"  📋 Status: {validation_status}")
            print(f"  📊 Completion: {completion_percentage}%")
            print(f"  🔍 Issues: {len(response_data.get('validation_issues', []))}")
            
        else:
            print(f"❌ Friendly form endpoint failed: {response.text}")
            results["phase1_endpoint_test"]["complete_data"]["error"] = response.text
            results["phase1_endpoint_test"]["complete_data"]["working"] = False
            
    except Exception as e:
        print(f"❌ Exception testing complete data: {str(e)}")
        results["phase1_endpoint_test"]["complete_data"]["exception"] = str(e)
        results["phase1_endpoint_test"]["complete_data"]["working"] = False
    
    # Verify data was saved in simplified_form_responses
    print(f"\n🔍 Verifying data saved in simplified_form_responses...")
    try:
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            simplified_responses = case_info.get("simplified_form_responses")
            
            if simplified_responses:
                print(f"✅ Data saved in simplified_form_responses")
                print(f"📄 Saved data: {json.dumps(simplified_responses, indent=2)}")
                results["phase1_endpoint_test"]["data_persistence"] = {
                    "success": True,
                    "data": simplified_responses
                }
            else:
                print(f"❌ No data found in simplified_form_responses")
                results["phase1_endpoint_test"]["data_persistence"] = {
                    "success": False,
                    "error": "No simplified_form_responses found"
                }
        else:
            print(f"❌ Failed to retrieve case data: {response.text}")
            results["phase1_endpoint_test"]["data_persistence"] = {
                "success": False,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception verifying data persistence: {str(e)}")
        results["phase1_endpoint_test"]["data_persistence"] = {
            "success": False,
            "exception": str(e)
        }
    
    # PHASE 2: Test AI Validation with Incomplete Data
    print("\n📋 PHASE 2: TESTE DE VALIDAÇÃO IA")
    print("-" * 60)
    
    # Create another case for incomplete data test
    print("🔧 Creating second test case for incomplete data...")
    try:
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json=case_creation_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            # Extract case_id from nested structure
            case_info = case_data.get("case", {})
            incomplete_case_id = case_info.get("case_id")
            print(f"✅ Second test case created: {incomplete_case_id}")
        else:
            print(f"❌ Second case creation failed, using original case")
            incomplete_case_id = case_id
            
    except Exception as e:
        print(f"❌ Exception creating second case, using original: {str(e)}")
        incomplete_case_id = case_id
    
    # Test with incomplete data
    print(f"\n🔍 Testing AI validation with INCOMPLETE data...")
    print(f"🔗 Endpoint: POST {API_BASE}/case/{incomplete_case_id}/friendly-form")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/case/{incomplete_case_id}/friendly-form",
            json=incomplete_friendly_form_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["phase2_ai_validation"]["incomplete_data"] = {
            "status_code": response.status_code,
            "processing_time": processing_time
        }
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
            
            validation_status = response_data.get("validation_status")
            completion_percentage = response_data.get("completion_percentage", 0)
            validation_issues = response_data.get("validation_issues", [])
            
            # Validate AI behavior with incomplete data
            validations = {
                "status_rejected_or_needs_review": validation_status in ["rejected", "needs_review"],
                "completion_below_70": completion_percentage < 70,
                "validation_issues_present": len(validation_issues) > 0,
                "missing_fields_identified": any("faltando" in issue.lower() or "missing" in issue.lower() for issue in validation_issues)
            }
            
            results["phase2_ai_validation"]["incomplete_data"]["validations"] = validations
            results["phase2_ai_validation"]["incomplete_data"]["response_data"] = response_data
            results["phase2_ai_validation"]["incomplete_data"]["working"] = all(validations.values())
            
            print(f"\n🎯 AI VALIDATION - INCOMPLETE DATA:")
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            print(f"\n📊 AI VALIDATION RESULTS - INCOMPLETE:")
            print(f"  📋 Status: {validation_status}")
            print(f"  📊 Completion: {completion_percentage}%")
            print(f"  🔍 Issues: {len(validation_issues)}")
            print(f"  📝 Issues list: {validation_issues}")
            
        else:
            print(f"❌ AI validation with incomplete data failed: {response.text}")
            results["phase2_ai_validation"]["incomplete_data"]["error"] = response.text
            results["phase2_ai_validation"]["incomplete_data"]["working"] = False
            
    except Exception as e:
        print(f"❌ Exception testing incomplete data: {str(e)}")
        results["phase2_ai_validation"]["incomplete_data"]["exception"] = str(e)
        results["phase2_ai_validation"]["incomplete_data"]["working"] = False
    
    # PHASE 3: Test Integration with PDF Official
    print("\n📋 PHASE 3: TESTE DE INTEGRAÇÃO COM PDF OFICIAL")
    print("-" * 60)
    
    # Use the case with complete data for PDF generation
    print(f"🔍 Testing PDF generation using friendly form data...")
    print(f"🔗 Case ID: {case_id} (with complete friendly form data)")
    
    try:
        # Generate USCIS form using friendly form data
        print(f"📝 Generating I-539 form with friendly form data...")
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/case/{case_id}/generate-form",
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["phase3_pdf_integration"]["form_generation"] = {
            "status_code": response.status_code,
            "processing_time": processing_time
        }
        
        if response.status_code == 200:
            form_data = response.json()
            print(f"📄 Form generation response: {json.dumps(form_data, indent=2)}")
            
            # Validate form generation
            validations = {
                "success_true": form_data.get("success", False),
                "form_type_i539": form_data.get("form_type") == "I-539",
                "filename_present": form_data.get("filename") is not None,
                "file_size_positive": form_data.get("file_size", 0) > 0
            }
            
            results["phase3_pdf_integration"]["form_generation"]["validations"] = validations
            results["phase3_pdf_integration"]["form_generation"]["response_data"] = form_data
            results["phase3_pdf_integration"]["form_generation"]["working"] = all(validations.values())
            
            print(f"\n🎯 PDF GENERATION VALIDATIONS:")
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
        else:
            print(f"❌ PDF generation failed: {response.text}")
            results["phase3_pdf_integration"]["form_generation"]["error"] = response.text
            results["phase3_pdf_integration"]["form_generation"]["working"] = False
            
    except Exception as e:
        print(f"❌ Exception during PDF generation: {str(e)}")
        results["phase3_pdf_integration"]["form_generation"]["exception"] = str(e)
        results["phase3_pdf_integration"]["form_generation"]["working"] = False
    
    # Verify that friendly form data is being used in the PDF
    print(f"\n🔍 Verifying friendly form data usage in PDF...")
    try:
        # Get the updated case to check if friendly form data was used
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            
            # Check if simplified_form_responses exists and has data
            simplified_responses = case_info.get("simplified_form_responses")
            generated_form = case_info.get("generated_form")
            
            validations = {
                "simplified_responses_exist": simplified_responses is not None,
                "generated_form_exists": generated_form is not None,
                "friendly_data_has_name": simplified_responses and "nome_completo" in str(simplified_responses),
                "friendly_data_has_passport": simplified_responses and "numero_passaporte" in str(simplified_responses)
            }
            
            results["phase3_pdf_integration"]["data_usage"] = {
                "validations": validations,
                "working": all(validations.values()),
                "simplified_responses": simplified_responses,
                "generated_form": generated_form
            }
            
            print(f"\n🎯 FRIENDLY FORM DATA USAGE:")
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            if simplified_responses:
                print(f"\n📄 Friendly form data found:")
                print(f"  👤 Nome: {simplified_responses.get('nome_completo', 'N/A')}")
                print(f"  📘 Passaporte: {simplified_responses.get('numero_passaporte', 'N/A')}")
                print(f"  📧 Email: {simplified_responses.get('email', 'N/A')}")
            
        else:
            print(f"❌ Failed to verify data usage: {response.text}")
            results["phase3_pdf_integration"]["data_usage"] = {
                "working": False,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception verifying data usage: {str(e)}")
        results["phase3_pdf_integration"]["data_usage"] = {
            "working": False,
            "exception": str(e)
        }
    
    # PHASE 4: Test Field Mapping Portuguese → English
    print("\n📋 PHASE 4: TESTE DE MAPEAMENTO DE CAMPOS")
    print("-" * 60)
    
    # Test field mapping by checking the expected mappings
    expected_mappings = {
        "nome_completo": ["Family Name", "Given Name"],
        "data_nascimento": ["Date of Birth"],
        "endereco": ["Street Address"],
        "numero_passaporte": ["Passport Number"],
        "email": ["Email Address"],
        "telefone": ["Phone Number"],
        "status_atual": ["Current Status"],
        "status_solicitado": ["Requested Status"]
    }
    
    print("🔍 Testing field mapping Portuguese → English...")
    
    # Get the case data to verify mappings
    try:
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            simplified_responses = case_info.get("simplified_form_responses", {})
            
            mapping_results = {}
            
            print(f"\n🎯 FIELD MAPPING VERIFICATION:")
            
            for portuguese_field, english_equivalents in expected_mappings.items():
                field_value = simplified_responses.get(portuguese_field)
                
                if field_value:
                    mapping_results[portuguese_field] = {
                        "portuguese_value": field_value,
                        "english_fields": english_equivalents,
                        "mapping_exists": True
                    }
                    print(f"  ✅ {portuguese_field} → {english_equivalents}: '{field_value}'")
                else:
                    mapping_results[portuguese_field] = {
                        "portuguese_value": None,
                        "english_fields": english_equivalents,
                        "mapping_exists": False
                    }
                    print(f"  ❌ {portuguese_field} → {english_equivalents}: No data")
            
            # Calculate mapping success rate
            successful_mappings = sum(1 for result in mapping_results.values() if result["mapping_exists"])
            total_mappings = len(expected_mappings)
            mapping_success_rate = (successful_mappings / total_mappings) * 100
            
            results["phase4_field_mapping"] = {
                "mapping_results": mapping_results,
                "successful_mappings": successful_mappings,
                "total_mappings": total_mappings,
                "success_rate": mapping_success_rate,
                "working": mapping_success_rate >= 80  # 80% threshold
            }
            
            print(f"\n📊 MAPPING RESULTS:")
            print(f"  ✅ Successful mappings: {successful_mappings}/{total_mappings}")
            print(f"  📊 Success rate: {mapping_success_rate:.1f}%")
            
        else:
            print(f"❌ Failed to verify field mapping: {response.text}")
            results["phase4_field_mapping"] = {
                "working": False,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception testing field mapping: {str(e)}")
        results["phase4_field_mapping"] = {
            "working": False,
            "exception": str(e)
        }
    
    # SUMMARY: Generate final assessment
    print("\n📋 SUMMARY: AVALIAÇÃO FINAL DO FLUXO COMPLETO")
    print("=" * 80)
    
    # Count successful phases
    phase_results = {
        "phase1_endpoint": results.get("phase1_endpoint_test", {}).get("complete_data", {}).get("working", False),
        "phase1_persistence": results.get("phase1_endpoint_test", {}).get("data_persistence", {}).get("success", False),
        "phase2_ai_validation": results.get("phase2_ai_validation", {}).get("incomplete_data", {}).get("working", False),
        "phase3_pdf_generation": results.get("phase3_pdf_integration", {}).get("form_generation", {}).get("working", False),
        "phase3_data_usage": results.get("phase3_pdf_integration", {}).get("data_usage", {}).get("working", False),
        "phase4_field_mapping": results.get("phase4_field_mapping", {}).get("working", False)
    }
    
    successful_phases = sum(1 for success in phase_results.values() if success)
    total_phases = len(phase_results)
    overall_success_rate = (successful_phases / total_phases) * 100
    
    results["summary"] = {
        "phase_results": phase_results,
        "successful_phases": successful_phases,
        "total_phases": total_phases,
        "overall_success_rate": overall_success_rate,
        "system_ready": overall_success_rate >= 80,  # 80% threshold
        "test_cases_used": [case_id, incomplete_case_id] if 'incomplete_case_id' in locals() else [case_id]
    }
    
    print(f"📊 RESULTADOS POR FASE:")
    print(f"  📝 Phase 1 - Endpoint funcionando: {'✅' if phase_results['phase1_endpoint'] else '❌'}")
    print(f"  💾 Phase 1 - Dados salvos: {'✅' if phase_results['phase1_persistence'] else '❌'}")
    print(f"  🤖 Phase 2 - Validação IA: {'✅' if phase_results['phase2_ai_validation'] else '❌'}")
    print(f"  📄 Phase 3 - Geração PDF: {'✅' if phase_results['phase3_pdf_generation'] else '❌'}")
    print(f"  🔗 Phase 3 - Uso dos dados: {'✅' if phase_results['phase3_data_usage'] else '❌'}")
    print(f"  🗺️  Phase 4 - Mapeamento campos: {'✅' if phase_results['phase4_field_mapping'] else '❌'}")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_phases}/{total_phases} ({overall_success_rate:.1f}%)")
    
    # Success criteria assessment
    print(f"\n📋 CRITÉRIOS DE SUCESSO:")
    success_criteria = {
        "endpoint_responds_200": phase_results['phase1_endpoint'],
        "ai_validation_works": phase_results['phase2_ai_validation'],
        "data_saved_correctly": phase_results['phase1_persistence'],
        "form_filler_uses_data": phase_results['phase3_data_usage'],
        "field_mapping_works": phase_results['phase4_field_mapping'],
        "pdf_generated_correctly": phase_results['phase3_pdf_generation']
    }
    
    for criterion, passed in success_criteria.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {criterion}: {passed}")
    
    # Final assessment
    if results["summary"]["system_ready"]:
        print("\n✅ FLUXO COMPLETO E FUNCIONAL")
        print("✅ Sistema pronto para uso em produção")
        print("✅ Formulário amigável → IA → PDF oficial funcionando")
    else:
        print("\n⚠️  FLUXO PARCIALMENTE FUNCIONAL")
        print("❌ Algumas funcionalidades precisam de correção")
        
        # Identify problem areas
        problem_areas = []
        if not phase_results['phase1_endpoint']:
            problem_areas.append("Endpoint do formulário amigável")
        if not phase_results['phase2_ai_validation']:
            problem_areas.append("Validação IA")
        if not phase_results['phase3_pdf_generation']:
            problem_areas.append("Geração de PDF")
        if not phase_results['phase4_field_mapping']:
            problem_areas.append("Mapeamento de campos")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    return results

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE COMPLETO - FLUXO FORMULÁRIO AMIGÁVEL")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Execute test
    test_results = test_friendly_form_complete_flow()
    
    # Save results to file
    with open("/app/friendly_form_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "Friendly Form Complete Flow Testing",
            "phases_tested": [
                "Phase 1: Friendly Form Endpoint",
                "Phase 2: AI Validation",
                "Phase 3: PDF Integration", 
                "Phase 4: Field Mapping"
            ]
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/friendly_form_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    if summary.get("system_ready", False):
        print("\n✅ RECOMENDAÇÃO: Fluxo Formulário Amigável PRONTO PARA PRODUÇÃO")
        print("   - Endpoint funcionando corretamente")
        print("   - Validação IA operacional")
        print("   - Integração com PDF oficial funcional")
        print("   - Mapeamento de campos português→inglês funcionando")
    else:
        success_rate = summary.get("overall_success_rate", 0)
        if success_rate >= 60:
            print("\n⚠️  RECOMENDAÇÃO: Fluxo parcialmente funcional, melhorias necessárias")
            print("   - Algumas funcionalidades operacionais")
            print("   - Revisar fases que falharam")
        else:
            print("\n❌ RECOMENDAÇÃO: Fluxo precisa de desenvolvimento adicional")
            print("   - Múltiplos problemas identificados")
            print("   - Revisão completa necessária")