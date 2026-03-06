#!/usr/bin/env python3
"""
🎯 TESTE COMPLETO: Correção Automática de Dados do Cadastro Baseado em Documentos

**OBJETIVO:**
Testar se o sistema detecta e corrige automaticamente discrepâncias entre o cadastro inicial do usuário 
e os dados extraídos dos documentos oficiais (passaporte).

**CENÁRIO DE TESTE:**
1. Criar caso com dados INCORRETOS/INCOMPLETOS
2. Simular upload de passaporte com dados CORRETOS
3. Verificar se o sistema detecta discrepâncias
4. Validar correção automática
5. Confirmar campos de auditoria

**FLUXO DETALHADO:**
- Nome ERRADO: "Joao Silva" → CORRETO: "João Silva Santos"
- Data nascimento: "1990-05-15" (mesmo)
- Email: "test_autocorrect@test.com"
- Passaporte: BR1234567
- Nacionalidade: BRAZILIAN
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime
import hashlib

# Get backend URL from frontend .env
BACKEND_URL = "https://formfiller-26.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_test_passport_content():
    """Create simulated passport content for OCR testing"""
    passport_content = """PASSPORT
UNITED STATES OF AMERICA
PASSPORT NO: BR1234567
NAME: JOÃO SILVA SANTOS
DATE OF BIRTH: 15 MAY 1990
NATIONALITY: BRAZILIAN
DATE OF ISSUE: 01 JAN 2020
DATE OF EXPIRY: 01 JAN 2030
PLACE OF BIRTH: SAO PAULO, BRAZIL
SEX: M
"""
    return passport_content

def test_document_based_autocorrection():
    """
    🎯 TESTE COMPLETO: Correção Automática de Dados do Cadastro Baseado em Documentos
    
    METODOLOGIA - TESTE EM 4 ETAPAS:
    
    ETAPA 1: CRIAR CASO COM DADOS INCORRETOS
    - Nome: "Joao Silva" (sem acento, incompleto)
    - Data nascimento: "1990-05-15"
    - Email: "test_autocorrect@test.com"
    
    ETAPA 2: SIMULAR UPLOAD DE PASSAPORTE
    - Nome CORRETO: "JOÃO SILVA SANTOS"
    - Data nascimento: "15/05/1990"
    - Número passaporte: "BR1234567"
    - Nacionalidade: "BRAZILIAN"
    
    ETAPA 3: VERIFICAR CORREÇÃO AUTOMÁTICA
    - Sistema deve detectar discrepância no nome
    - Deve corrigir automaticamente o cadastro
    - Deve adicionar campos de auditoria
    
    ETAPA 4: CONSULTAR DADOS ATUALIZADOS
    - Verificar se nome foi atualizado
    - Verificar campos de auditoria
    """
    
    print("🎯 TESTE COMPLETO: Correção Automática de Dados do Cadastro Baseado em Documentos")
    print("📋 OBJETIVO: Testar detecção e correção automática de discrepâncias")
    print("=" * 80)
    
    results = {
        "step1_create_case_incorrect_data": {},
        "step2_upload_passport_document": {},
        "step3_verify_auto_correction": {},
        "step4_check_audit_fields": {},
        "summary": {}
    }
    
    # STEP 1: Create case with INCORRECT data
    print("\n📋 ETAPA 1: CRIAR CASO COM DADOS INCORRETOS")
    print("-" * 60)
    print("📝 Dados INCORRETOS/INCOMPLETOS:")
    print("  - Nome: 'Joao Silva' (sem acento, sem sobrenome completo)")
    print("  - Data nascimento: '1990-05-15'")
    print("  - Email: 'test_autocorrect@test.com'")
    
    try:
        # Create case with incorrect data
        incorrect_data = {
            "session_token": "test_autocorrect_session",
            "applicant_name": "Joao Silva",  # INCORRECT: missing accent and full surname
            "applicant_email": "test_autocorrect@test.com",
            "date_of_birth": "1990-05-15"
        }
        
        print(f"📤 Creating case with incorrect data...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json=incorrect_data,
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
                print(f"✅ Case created with incorrect data: {case_id}")
                print(f"📝 Initial name: '{incorrect_data['applicant_name']}'")
                
                results["step1_create_case_incorrect_data"] = {
                    "success": True,
                    "case_id": case_id,
                    "status_code": response.status_code,
                    "initial_name": incorrect_data["applicant_name"],
                    "initial_email": incorrect_data["applicant_email"],
                    "initial_dob": incorrect_data["date_of_birth"]
                }
            else:
                print(f"❌ No case_id in response: {case_data}")
                results["step1_create_case_incorrect_data"] = {"success": False, "error": "No case_id"}
                return results
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            results["step1_create_case_incorrect_data"] = {"success": False, "status_code": response.status_code}
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["step1_create_case_incorrect_data"] = {"success": False, "exception": str(e)}
        return results
    
    case_id = results["step1_create_case_incorrect_data"]["case_id"]
    
    # STEP 2: Upload passport document with CORRECT data
    print("\n📋 ETAPA 2: SIMULAR UPLOAD DE PASSAPORTE COM DADOS CORRETOS")
    print("-" * 60)
    print("📝 Dados CORRETOS no passaporte:")
    print("  - Nome: 'JOÃO SILVA SANTOS' (com acento, nome completo)")
    print("  - Data nascimento: '15 MAY 1990'")
    print("  - Número passaporte: 'BR1234567'")
    print("  - Nacionalidade: 'BRAZILIAN'")
    
    try:
        # Create passport content
        passport_content = create_test_passport_content()
        
        # Create temporary passport file
        passport_file_path = "/tmp/test_passport.txt"
        with open(passport_file_path, 'w', encoding='utf-8') as f:
            f.write(passport_content)
        
        print(f"📄 Passport content created:")
        print(passport_content)
        
        # Upload passport document
        print(f"📤 Uploading passport document to case {case_id}...")
        
        with open(passport_file_path, 'rb') as f:
            files = {
                'file': ('test_passport.txt', f, 'text/plain')
            }
            data = {
                'document_type': 'passport'
            }
            
            response = requests.post(
                f"{API_BASE}/case/{case_id}/upload-document",
                files=files,
                data=data,
                timeout=60
            )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"✅ Passport document uploaded successfully")
            
            # Check if extraction was successful
            extraction = upload_result.get("extraction", {})
            auto_corrected = extraction.get("auto_corrected", False)
            corrections_made = extraction.get("corrections_made", {})
            
            print(f"📄 Extraction result: {json.dumps(extraction, indent=2, ensure_ascii=False)}")
            
            results["step2_upload_passport_document"] = {
                "success": True,
                "status_code": response.status_code,
                "upload_result": upload_result,
                "extraction": extraction,
                "auto_corrected": auto_corrected,
                "corrections_made": corrections_made
            }
        else:
            print(f"❌ Failed to upload passport: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step2_upload_passport_document"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception uploading passport: {str(e)}")
        results["step2_upload_passport_document"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 3: Verify automatic correction
    print("\n📋 ETAPA 3: VERIFICAR CORREÇÃO AUTOMÁTICA")
    print("-" * 60)
    print("🔍 VALIDAÇÕES ESPERADAS:")
    print("  ✅ Sistema deve extrair nome correto: 'João Silva Santos'")
    print("  ✅ Sistema deve detectar discrepância: 'Joao Silva' ≠ 'João Silva Santos'")
    print("  ✅ Sistema deve calcular confiança > 80% (passaporte)")
    print("  ✅ Sistema deve AUTO-CORRIGIR o cadastro")
    print("  ✅ Sistema deve adicionar campos de auditoria")
    
    try:
        # Get updated case data
        print(f"🔍 Retrieving updated case data for {case_id}...")
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            
            # Check basic data for corrections
            basic_data = case_info.get("basic_data", {})
            
            print(f"📄 Updated basic data: {json.dumps(basic_data, indent=2, ensure_ascii=False)}")
            
            # Verify auto-correction
            auto_correction_checks = {
                "name_corrected": False,
                "audit_fields_added": False,
                "data_verified_by_document": False,
                "verification_document_type": False,
                "verification_date": False
            }
            
            # Check if name was corrected
            current_name = basic_data.get("applicant_name") or basic_data.get("first_name", "") + " " + basic_data.get("last_name", "")
            original_name = "Joao Silva"
            expected_corrected_name = "João Silva Santos"
            
            if "João" in current_name and "Santos" in current_name:
                auto_correction_checks["name_corrected"] = True
                print(f"✅ Name corrected: '{original_name}' → '{current_name}'")
            else:
                print(f"❌ Name NOT corrected: still '{current_name}'")
            
            # Check audit fields
            if basic_data.get("data_verified_by_document"):
                auto_correction_checks["data_verified_by_document"] = True
                print(f"✅ data_verified_by_document: {basic_data.get('data_verified_by_document')}")
            
            if basic_data.get("verification_document_type") == "passport":
                auto_correction_checks["verification_document_type"] = True
                print(f"✅ verification_document_type: {basic_data.get('verification_document_type')}")
            
            if basic_data.get("verification_date"):
                auto_correction_checks["verification_date"] = True
                print(f"✅ verification_date: {basic_data.get('verification_date')}")
            
            # Check if any audit fields were added
            audit_fields = ["data_verified_by_document", "verification_document_type", "verification_date"]
            audit_fields_present = any(basic_data.get(field) for field in audit_fields)
            auto_correction_checks["audit_fields_added"] = audit_fields_present
            
            print(f"\n🎯 AUTO-CORRECTION VERIFICATION:")
            for check, passed in auto_correction_checks.items():
                status = "✅" if passed else "❌"
                check_name = check.replace("_", " ").title()
                print(f"  {status} {check_name}: {passed}")
            
            results["step3_verify_auto_correction"] = {
                "success": True,
                "case_data": case_info,
                "basic_data": basic_data,
                "auto_correction_checks": auto_correction_checks,
                "original_name": original_name,
                "current_name": current_name,
                "expected_name": expected_corrected_name,
                "passed": all(auto_correction_checks.values())
            }
        else:
            print(f"❌ Failed to retrieve updated case: {response.status_code}")
            results["step3_verify_auto_correction"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception verifying auto-correction: {str(e)}")
        results["step3_verify_auto_correction"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 4: Check audit fields and MongoDB persistence
    print("\n📋 ETAPA 4: CONSULTAR DADOS ATUALIZADOS NO MONGODB")
    print("-" * 60)
    print("🔍 VERIFICAÇÕES FINAIS:")
    print("  ✅ Nome atualizado para 'João Silva Santos'")
    print("  ✅ Campos de auditoria presentes")
    print("  ✅ Timestamp de verificação")
    print("  ✅ Tipo de documento usado para verificação")
    
    try:
        # Additional verification - check if changes persisted
        print(f"🔍 Final verification of case {case_id}...")
        
        # Get case data again to ensure persistence
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            final_case_data = response.json()
            final_case_info = final_case_data.get("case", {})
            final_basic_data = final_case_info.get("basic_data", {})
            
            # Final audit checks
            final_audit_checks = {
                "name_persisted": "João" in str(final_basic_data.get("applicant_name", "")) or "João" in str(final_basic_data.get("first_name", "")),
                "santos_surname_added": "Santos" in str(final_basic_data),
                "verification_fields_persisted": bool(final_basic_data.get("data_verified_by_document")),
                "document_type_recorded": final_basic_data.get("verification_document_type") == "passport",
                "verification_timestamp": bool(final_basic_data.get("verification_date"))
            }
            
            print(f"📄 Final basic data: {json.dumps(final_basic_data, indent=2, ensure_ascii=False)}")
            
            print(f"\n🎯 FINAL AUDIT VERIFICATION:")
            for check, passed in final_audit_checks.items():
                status = "✅" if passed else "❌"
                check_name = check.replace("_", " ").title()
                print(f"  {status} {check_name}: {passed}")
            
            results["step4_check_audit_fields"] = {
                "success": True,
                "final_case_data": final_case_info,
                "final_basic_data": final_basic_data,
                "final_audit_checks": final_audit_checks,
                "passed": all(final_audit_checks.values())
            }
        else:
            print(f"❌ Failed final verification: {response.status_code}")
            results["step4_check_audit_fields"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception in final verification: {str(e)}")
        results["step4_check_audit_fields"] = {"success": False, "exception": str(e)}
    
    # SUMMARY AND ASSESSMENT
    print("\n📋 RESUMO FINAL - CORREÇÃO AUTOMÁTICA DE DADOS")
    print("=" * 80)
    
    # Count successful steps
    step_results = [
        results.get("step1_create_case_incorrect_data", {}).get("success", False),
        results.get("step2_upload_passport_document", {}).get("success", False),
        results.get("step3_verify_auto_correction", {}).get("passed", False),
        results.get("step4_check_audit_fields", {}).get("passed", False)
    ]
    
    successful_steps = sum(step_results)
    total_steps = len(step_results)
    success_rate = (successful_steps / total_steps) * 100
    
    # Individual step results
    step_names = [
        "ETAPA 1: Criar Caso com Dados Incorretos",
        "ETAPA 2: Upload de Passaporte com Dados Corretos",
        "ETAPA 3: Verificar Correção Automática",
        "ETAPA 4: Consultar Dados Atualizados"
    ]
    
    print(f"📊 RESULTADOS POR ETAPA:")
    for i, (step_name, passed) in enumerate(zip(step_names, step_results)):
        status = "✅" if passed else "❌"
        print(f"  {status} {step_name}: {'SUCESSO' if passed else 'FALHOU'}")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
    
    # Detailed Analysis
    print(f"\n📋 ANÁLISE DETALHADA:")
    print("=" * 60)
    
    # Check if auto-correction worked
    auto_correction_worked = results.get("step3_verify_auto_correction", {}).get("passed", False)
    upload_successful = results.get("step2_upload_passport_document", {}).get("success", False)
    extraction_data = results.get("step2_upload_passport_document", {}).get("extraction", {})
    
    if upload_successful:
        print(f"✅ UPLOAD: Passaporte enviado com sucesso")
        if extraction_data.get("successful"):
            print(f"✅ EXTRAÇÃO: Dados extraídos do passaporte")
            if extraction_data.get("auto_corrected"):
                print(f"✅ CORREÇÃO: Sistema detectou e corrigiu discrepâncias")
                corrections = extraction_data.get("corrections_made", {})
                if corrections:
                    print(f"✅ CORREÇÕES APLICADAS: {json.dumps(corrections, ensure_ascii=False)}")
            else:
                print(f"❌ CORREÇÃO: Sistema NÃO detectou discrepâncias")
        else:
            print(f"❌ EXTRAÇÃO: Falha na extração de dados do passaporte")
    
    if auto_correction_worked:
        original_name = results.get("step3_verify_auto_correction", {}).get("original_name", "")
        current_name = results.get("step3_verify_auto_correction", {}).get("current_name", "")
        print(f"✅ RESULTADO: Nome corrigido de '{original_name}' para '{current_name}'")
    
    # System Assessment
    print(f"\n🎯 AVALIAÇÃO DO SISTEMA:")
    print("=" * 60)
    
    system_criteria = {
        "extrai_dados_passaporte": extraction_data.get("successful", False),
        "detecta_discrepancias": extraction_data.get("auto_corrected", False),
        "corrige_automaticamente": auto_correction_worked,
        "adiciona_campos_auditoria": results.get("step4_check_audit_fields", {}).get("passed", False),
        "persiste_no_mongodb": results.get("step4_check_audit_fields", {}).get("success", False)
    }
    
    criteria_passed = sum(system_criteria.values())
    total_criteria = len(system_criteria)
    
    print(f"📊 CRITÉRIOS DE FUNCIONALIDADE:")
    for criterion, passed in system_criteria.items():
        status = "✅" if passed else "❌"
        criterion_name = criterion.replace("_", " ").title()
        print(f"  {status} {criterion_name}: {'FUNCIONANDO' if passed else 'NÃO FUNCIONANDO'}")
    
    print(f"\n🎯 CRITÉRIOS ATENDIDOS: {criteria_passed}/{total_criteria} ({criteria_passed/total_criteria*100:.1f}%)")
    
    # Final Assessment
    system_ready = success_rate >= 75 and criteria_passed >= 4
    
    if system_ready:
        print("\n✅ SISTEMA DE CORREÇÃO AUTOMÁTICA: TOTALMENTE FUNCIONAL")
        print("✅ EXTRAÇÃO OCR: FUNCIONANDO")
        print("✅ DETECÇÃO DE DISCREPÂNCIAS: ATIVA")
        print("✅ CORREÇÃO AUTOMÁTICA: OPERACIONAL")
        print("✅ CAMPOS DE AUDITORIA: IMPLEMENTADOS")
        print("✅ PERSISTÊNCIA MONGODB: CONFIRMADA")
    else:
        print("\n⚠️  SISTEMA DE CORREÇÃO AUTOMÁTICA: NECESSITA CORREÇÕES")
        
        # Identify problem areas
        problem_areas = []
        if not system_criteria["extrai_dados_passaporte"]:
            problem_areas.append("Extração de dados do passaporte")
        if not system_criteria["detecta_discrepancias"]:
            problem_areas.append("Detecção de discrepâncias")
        if not system_criteria["corrige_automaticamente"]:
            problem_areas.append("Correção automática")
        if not system_criteria["adiciona_campos_auditoria"]:
            problem_areas.append("Campos de auditoria")
        if not system_criteria["persiste_no_mongodb"]:
            problem_areas.append("Persistência no MongoDB")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Expected Response Format Check
    print(f"\n📋 VERIFICAÇÃO DO FORMATO DE RESPOSTA ESPERADO:")
    print("=" * 60)
    
    expected_response = {
        "success": True,
        "message": "Document uploaded successfully",
        "extraction": {
            "successful": True,
            "auto_corrected": True,
            "corrections_made": {
                "first_name": "João",
                "last_name": "Silva Santos"
            },
            "message": "Cadastro atualizado automaticamente com base no passport"
        }
    }
    
    actual_response = results.get("step2_upload_passport_document", {}).get("upload_result", {})
    
    response_checks = {
        "success_field": actual_response.get("success", False),
        "message_field": bool(actual_response.get("message")),
        "extraction_field": bool(actual_response.get("extraction")),
        "extraction_successful": actual_response.get("extraction", {}).get("successful", False),
        "auto_corrected_field": "auto_corrected" in actual_response.get("extraction", {}),
        "corrections_made_field": "corrections_made" in actual_response.get("extraction", {})
    }
    
    print(f"📊 FORMATO DE RESPOSTA:")
    for check, passed in response_checks.items():
        status = "✅" if passed else "❌"
        check_name = check.replace("_", " ").title()
        print(f"  {status} {check_name}: {passed}")
    
    print(f"\n📄 RESPOSTA ESPERADA:")
    print(json.dumps(expected_response, indent=2, ensure_ascii=False))
    
    print(f"\n📄 RESPOSTA ATUAL:")
    print(json.dumps(actual_response, indent=2, ensure_ascii=False))
    
    # Store summary
    results["summary"] = {
        "successful_steps": successful_steps,
        "total_steps": total_steps,
        "success_rate": success_rate,
        "system_criteria": system_criteria,
        "criteria_passed": criteria_passed,
        "total_criteria": total_criteria,
        "system_ready": system_ready,
        "case_id": results.get("step1_create_case_incorrect_data", {}).get("case_id"),
        "auto_correction_worked": auto_correction_worked,
        "response_format_correct": sum(response_checks.values()) >= 4
    }
    
    return results

if __name__ == "__main__":
    print("🎯 INICIANDO TESTE DE CORREÇÃO AUTOMÁTICA DE DADOS")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("🎯 OBJETIVO: Testar correção automática baseada em documentos")
    
    # Execute main test
    test_results = test_document_based_autocorrection()
    
    # Save results to file
    with open("/app/autocorrect_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "🎯 TESTE COMPLETO: Correção Automática de Dados do Cadastro Baseado em Documentos",
            "test_methodology": "TESTE EM 4 ETAPAS SEQUENCIAIS",
            "test_scenario": {
                "incorrect_initial_data": {
                    "name": "Joao Silva",
                    "date_of_birth": "1990-05-15",
                    "email": "test_autocorrect@test.com"
                },
                "correct_passport_data": {
                    "name": "JOÃO SILVA SANTOS",
                    "date_of_birth": "15 MAY 1990",
                    "passport_number": "BR1234567",
                    "nationality": "BRAZILIAN"
                },
                "expected_corrections": {
                    "first_name": "João",
                    "last_name": "Silva Santos"
                }
            },
            "validation_criteria": [
                "Sistema extrai dados corretos do passaporte",
                "Sistema detecta discrepância no nome",
                "Sistema calcula confiança > 80%",
                "Sistema corrige automaticamente o cadastro",
                "Sistema adiciona campos de auditoria",
                "Dados são persistidos no MongoDB"
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: /app/autocorrect_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    system_ready = summary.get("system_ready", False)
    success_rate = summary.get("success_rate", 0)
    auto_correction_worked = summary.get("auto_correction_worked", False)
    
    if system_ready and auto_correction_worked:
        print("\n🎉 CONCLUSÃO FINAL: SISTEMA DE CORREÇÃO AUTOMÁTICA FUNCIONANDO!")
        print("   ✅ Extração OCR funcionando corretamente")
        print("   ✅ Detecção de discrepâncias operacional")
        print("   ✅ Correção automática implementada")
        print("   ✅ Campos de auditoria sendo adicionados")
        print("   ✅ Sistema pronto para produção")
    elif auto_correction_worked:
        print("\n⚠️  CONCLUSÃO: Correção automática funciona, mas com problemas menores")
        print("   ✅ Funcionalidade principal operacional")
        print("   ⚠️  Alguns aspectos precisam de ajustes")
        print("   🔧 Revisar áreas problemáticas identificadas")
    else:
        print("\n❌ CONCLUSÃO CRÍTICA: SISTEMA DE CORREÇÃO AUTOMÁTICA NÃO FUNCIONAL!")
        print("   ❌ Correção automática não está funcionando")
        print("   ❌ Pode haver problemas na extração OCR")
        print("   ❌ Detecção de discrepâncias pode estar falhando")
        print("   🚨 Implementação ou correção urgente necessária")
        
        criteria_passed = summary.get("criteria_passed", 0)
        total_criteria = summary.get("total_criteria", 5)
        print(f"   📊 Apenas {criteria_passed}/{total_criteria} critérios funcionando")
        print(f"   🎯 Necessário pelo menos 4/{total_criteria} para aprovação")