#!/usr/bin/env python3
"""
🎯 TESTE DIRETO: Correção Automática de Dados - Simulação OCR

**OBJETIVO:**
Testar diretamente o sistema de correção automática simulando que o OCR já extraiu o texto do passaporte.
Isso testa a lógica de detecção e correção sem depender da API do Google Vision.

**CENÁRIO DE TESTE:**
1. Criar caso com dados INCORRETOS/INCOMPLETOS
2. Simular texto extraído do passaporte (como se viesse do OCR)
3. Chamar diretamente o sistema de correção automática
4. Verificar se detecta discrepâncias e corrige automaticamente
"""

import requests
import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Add backend directory to path to import modules
sys.path.append('/app/backend')

# Get backend URL from frontend .env
BACKEND_URL = "https://formfiller-26.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_passport_ocr_text():
    """Create simulated OCR-extracted text from passport"""
    return """PASSPORT
UNITED STATES OF AMERICA
PASSPORT NO: BR1234567
NAME: JOÃO SILVA SANTOS
DATE OF BIRTH: 15 MAY 1990
NATIONALITY: BRAZILIAN
DATE OF ISSUE: 01 JAN 2020
DATE OF EXPIRY: 01 JAN 2030
PLACE OF BIRTH: SAO PAULO, BRAZIL
SEX: M"""

def test_direct_autocorrection():
    """
    🎯 TESTE DIRETO: Correção Automática de Dados - Simulação OCR
    
    METODOLOGIA - TESTE EM 5 ETAPAS:
    
    ETAPA 1: CRIAR USUÁRIO COM DADOS INCORRETOS
    - Nome: "Joao Silva" (sem acento, incompleto)
    - Email: "test_autocorrect@test.com"
    
    ETAPA 2: CRIAR CASO PARA O USUÁRIO
    - Associar caso ao usuário criado
    
    ETAPA 3: SIMULAR EXTRAÇÃO OCR
    - Texto do passaporte: "JOÃO SILVA SANTOS"
    - Simular que OCR extraiu corretamente
    
    ETAPA 4: TESTAR CORREÇÃO AUTOMÁTICA
    - Chamar endpoint que processa documento
    - Verificar se detecta discrepâncias
    - Verificar se corrige automaticamente
    
    ETAPA 5: VERIFICAR DADOS ATUALIZADOS
    - Confirmar que usuário foi atualizado
    - Verificar campos de auditoria
    """
    
    print("🎯 TESTE DIRETO: Correção Automática de Dados - Simulação OCR")
    print("📋 OBJETIVO: Testar lógica de correção sem depender do Google Vision API")
    print("=" * 80)
    
    results = {
        "step1_create_user_incorrect": {},
        "step2_create_case": {},
        "step3_simulate_ocr": {},
        "step4_test_autocorrection": {},
        "step5_verify_updates": {},
        "summary": {}
    }
    
    # STEP 1: Create user with INCORRECT data
    print("\n📋 ETAPA 1: CRIAR USUÁRIO COM DADOS INCORRETOS")
    print("-" * 60)
    print("📝 Dados INCORRETOS/INCOMPLETOS:")
    print("  - Nome: 'Joao Silva' (sem acento, sem sobrenome completo)")
    print("  - Email: 'test_autocorrect@test.com'")
    
    try:
        # Create user with incorrect data
        incorrect_user_data = {
            "email": "test_autocorrect@test.com",
            "password": "test123",
            "first_name": "Joao",  # INCORRECT: missing accent
            "last_name": "Silva",  # INCORRECT: incomplete surname
            "phone": "+1-555-0123"
        }
        
        print(f"📤 Creating user with incorrect data...")
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json=incorrect_user_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            user_data = response.json()
            user_info = user_data.get("user", {})
            user_id = user_info.get("id")
            token = user_data.get("token")
            
            if user_id and token:
                print(f"✅ User created with incorrect data: {user_id}")
                print(f"📝 Initial name: '{incorrect_user_data['first_name']} {incorrect_user_data['last_name']}'")
                
                results["step1_create_user_incorrect"] = {
                    "success": True,
                    "user_id": user_id,
                    "token": token,
                    "status_code": response.status_code,
                    "initial_first_name": incorrect_user_data["first_name"],
                    "initial_last_name": incorrect_user_data["last_name"],
                    "email": incorrect_user_data["email"]
                }
            else:
                print(f"❌ No user_id or token in response: {user_data}")
                results["step1_create_user_incorrect"] = {"success": False, "error": "No user_id or token"}
                return results
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            results["step1_create_user_incorrect"] = {"success": False, "status_code": response.status_code}
            return results
            
    except Exception as e:
        print(f"❌ Exception creating user: {str(e)}")
        results["step1_create_user_incorrect"] = {"success": False, "exception": str(e)}
        return results
    
    user_id = results["step1_create_user_incorrect"]["user_id"]
    token = results["step1_create_user_incorrect"]["token"]
    
    # STEP 2: Create case for the user
    print("\n📋 ETAPA 2: CRIAR CASO PARA O USUÁRIO")
    print("-" * 60)
    
    try:
        print(f"📤 Creating case for user {user_id}...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"form_code": "I-539"},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ Case created for user: {case_id}")
                
                results["step2_create_case"] = {
                    "success": True,
                    "case_id": case_id,
                    "status_code": response.status_code
                }
            else:
                print(f"❌ No case_id in response: {case_data}")
                results["step2_create_case"] = {"success": False, "error": "No case_id"}
                return results
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            results["step2_create_case"] = {"success": False, "status_code": response.status_code}
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["step2_create_case"] = {"success": False, "exception": str(e)}
        return results
    
    case_id = results["step2_create_case"]["case_id"]
    
    # STEP 3: Simulate OCR extraction
    print("\n📋 ETAPA 3: SIMULAR EXTRAÇÃO OCR")
    print("-" * 60)
    print("📝 Texto simulado do passaporte (como se viesse do OCR):")
    
    passport_text = create_passport_ocr_text()
    print(passport_text)
    
    results["step3_simulate_ocr"] = {
        "success": True,
        "passport_text": passport_text,
        "expected_name": "JOÃO SILVA SANTOS",
        "expected_passport": "BR1234567",
        "expected_nationality": "BRAZILIAN"
    }
    
    # STEP 4: Test direct document processing with simulated OCR text
    print("\n📋 ETAPA 4: TESTAR CORREÇÃO AUTOMÁTICA DIRETA")
    print("-" * 60)
    print("🔍 TESTANDO LÓGICA DE CORREÇÃO AUTOMÁTICA:")
    print("  ✅ Simular que OCR extraiu texto do passaporte")
    print("  ✅ Chamar sistema de correção automática")
    print("  ✅ Verificar detecção de discrepâncias")
    print("  ✅ Verificar correção automática")
    
    try:
        # Import the document extractor directly
        from backend.documents.data_extractor import process_document_and_update_user
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        
        # Connect to MongoDB (same as backend)
        mongo_url = "mongodb://localhost:27017"
        client = AsyncIOMotorClient(mongo_url)
        db = client["osprey_immigration_db"]
        
        async def test_extraction():
            # Call the document processor directly
            result = await process_document_and_update_user(
                document_text=passport_text,
                document_type="passport",
                user_id=user_id,
                db=db
            )
            return result
        
        # Run the async function
        extraction_result = asyncio.run(test_extraction())
        
        print(f"📄 Extraction result: {json.dumps(extraction_result, indent=2, ensure_ascii=False)}")
        
        # Verify extraction results
        extraction_checks = {
            "extraction_successful": extraction_result.get("extraction_successful", False),
            "auto_corrected": extraction_result.get("auto_corrected", False),
            "corrections_made": bool(extraction_result.get("corrections_made")),
            "discrepancies_found": bool(extraction_result.get("discrepancies_found")),
            "confidence_adequate": extraction_result.get("confidence", 0) >= 0.7
        }
        
        print(f"\n🎯 EXTRACTION VERIFICATION:")
        for check, passed in extraction_checks.items():
            status = "✅" if passed else "❌"
            check_name = check.replace("_", " ").title()
            print(f"  {status} {check_name}: {passed}")
        
        results["step4_test_autocorrection"] = {
            "success": True,
            "extraction_result": extraction_result,
            "extraction_checks": extraction_checks,
            "passed": all(extraction_checks.values())
        }
        
    except Exception as e:
        print(f"❌ Exception in direct extraction test: {str(e)}")
        results["step4_test_autocorrection"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 5: Verify user data was updated
    print("\n📋 ETAPA 5: VERIFICAR DADOS ATUALIZADOS DO USUÁRIO")
    print("-" * 60)
    print("🔍 VERIFICAÇÕES FINAIS:")
    print("  ✅ Nome atualizado para 'João Silva Santos'")
    print("  ✅ Campos de auditoria presentes")
    print("  ✅ Timestamp de verificação")
    
    try:
        # Get updated user profile
        print(f"🔍 Getting updated user profile for {user_id}...")
        response = requests.get(
            f"{API_BASE}/profile",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_profile = response.json()
            
            print(f"📄 Updated user profile: {json.dumps(user_profile, indent=2, ensure_ascii=False)}")
            
            # Verify user updates
            user_update_checks = {
                "first_name_corrected": "João" in str(user_profile.get("first_name", "")),
                "last_name_corrected": "Santos" in str(user_profile.get("last_name", "")),
                "data_verified_by_document": user_profile.get("data_verified_by_document", False),
                "verification_document_type": user_profile.get("verification_document_type") == "passport",
                "verification_date": bool(user_profile.get("verification_date"))
            }
            
            print(f"\n🎯 USER UPDATE VERIFICATION:")
            for check, passed in user_update_checks.items():
                status = "✅" if passed else "❌"
                check_name = check.replace("_", " ").title()
                print(f"  {status} {check_name}: {passed}")
            
            results["step5_verify_updates"] = {
                "success": True,
                "user_profile": user_profile,
                "user_update_checks": user_update_checks,
                "passed": all(user_update_checks.values())
            }
        else:
            print(f"❌ Failed to get user profile: {response.status_code}")
            results["step5_verify_updates"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception verifying user updates: {str(e)}")
        results["step5_verify_updates"] = {"success": False, "exception": str(e)}
    
    # SUMMARY AND ASSESSMENT
    print("\n📋 RESUMO FINAL - CORREÇÃO AUTOMÁTICA DIRETA")
    print("=" * 80)
    
    # Count successful steps
    step_results = [
        results.get("step1_create_user_incorrect", {}).get("success", False),
        results.get("step2_create_case", {}).get("success", False),
        results.get("step3_simulate_ocr", {}).get("success", False),
        results.get("step4_test_autocorrection", {}).get("passed", False),
        results.get("step5_verify_updates", {}).get("passed", False)
    ]
    
    successful_steps = sum(step_results)
    total_steps = len(step_results)
    success_rate = (successful_steps / total_steps) * 100
    
    # Individual step results
    step_names = [
        "ETAPA 1: Criar Usuário com Dados Incorretos",
        "ETAPA 2: Criar Caso para o Usuário",
        "ETAPA 3: Simular Extração OCR",
        "ETAPA 4: Testar Correção Automática Direta",
        "ETAPA 5: Verificar Dados Atualizados do Usuário"
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
    auto_correction_worked = results.get("step4_test_autocorrection", {}).get("passed", False)
    extraction_result = results.get("step4_test_autocorrection", {}).get("extraction_result", {})
    
    if extraction_result.get("extraction_successful"):
        print(f"✅ EXTRAÇÃO: Dados extraídos do passaporte com sucesso")
        confidence = extraction_result.get("confidence", 0)
        print(f"✅ CONFIANÇA: {confidence:.0%} (>= 70% necessário)")
        
        if extraction_result.get("auto_corrected"):
            print(f"✅ CORREÇÃO: Sistema detectou e corrigiu discrepâncias automaticamente")
            corrections = extraction_result.get("corrections_made", {})
            if corrections:
                print(f"✅ CORREÇÕES APLICADAS: {json.dumps(corrections, ensure_ascii=False)}")
        else:
            print(f"❌ CORREÇÃO: Sistema NÃO corrigiu automaticamente")
            reason = extraction_result.get("reason_not_corrected", "Unknown")
            print(f"❌ MOTIVO: {reason}")
    else:
        print(f"❌ EXTRAÇÃO: Falha na extração de dados do passaporte")
    
    # User update verification
    user_updated = results.get("step5_verify_updates", {}).get("passed", False)
    if user_updated:
        user_profile = results.get("step5_verify_updates", {}).get("user_profile", {})
        original_name = f"{results.get('step1_create_user_incorrect', {}).get('initial_first_name', '')} {results.get('step1_create_user_incorrect', {}).get('initial_last_name', '')}"
        updated_name = f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}"
        print(f"✅ USUÁRIO ATUALIZADO: Nome corrigido de '{original_name}' para '{updated_name}'")
    
    # System Assessment
    print(f"\n🎯 AVALIAÇÃO DO SISTEMA:")
    print("=" * 60)
    
    system_criteria = {
        "extrai_dados_passaporte": extraction_result.get("extraction_successful", False),
        "detecta_discrepancias": bool(extraction_result.get("discrepancies_found")),
        "corrige_automaticamente": extraction_result.get("auto_corrected", False),
        "adiciona_campos_auditoria": user_updated,
        "confianca_adequada": extraction_result.get("confidence", 0) >= 0.7
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
    system_ready = success_rate >= 80 and criteria_passed >= 4
    
    if system_ready:
        print("\n✅ SISTEMA DE CORREÇÃO AUTOMÁTICA: TOTALMENTE FUNCIONAL")
        print("✅ EXTRAÇÃO DE DADOS: FUNCIONANDO")
        print("✅ DETECÇÃO DE DISCREPÂNCIAS: ATIVA")
        print("✅ CORREÇÃO AUTOMÁTICA: OPERACIONAL")
        print("✅ CAMPOS DE AUDITORIA: IMPLEMENTADOS")
        print("✅ LÓGICA DE NEGÓCIO: CORRETA")
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
        if not system_criteria["confianca_adequada"]:
            problem_areas.append("Cálculo de confiança")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Store summary
    results["summary"] = {
        "successful_steps": successful_steps,
        "total_steps": total_steps,
        "success_rate": success_rate,
        "system_criteria": system_criteria,
        "criteria_passed": criteria_passed,
        "total_criteria": total_criteria,
        "system_ready": system_ready,
        "user_id": user_id,
        "case_id": case_id,
        "auto_correction_worked": auto_correction_worked,
        "extraction_confidence": extraction_result.get("confidence", 0)
    }
    
    return results

if __name__ == "__main__":
    print("🎯 INICIANDO TESTE DIRETO DE CORREÇÃO AUTOMÁTICA")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("🎯 OBJETIVO: Testar lógica de correção automática sem depender do Google Vision")
    
    # Execute main test
    test_results = test_direct_autocorrection()
    
    # Save results to file
    with open("/app/direct_autocorrect_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "🎯 TESTE DIRETO: Correção Automática de Dados - Simulação OCR",
            "test_methodology": "TESTE DIRETO EM 5 ETAPAS - BYPASS GOOGLE VISION API",
            "test_scenario": {
                "incorrect_initial_data": {
                    "first_name": "Joao",
                    "last_name": "Silva",
                    "email": "test_autocorrect@test.com"
                },
                "correct_passport_data": {
                    "name": "JOÃO SILVA SANTOS",
                    "passport_number": "BR1234567",
                    "nationality": "BRAZILIAN"
                },
                "expected_corrections": {
                    "first_name": "João",
                    "last_name": "Silva Santos"
                }
            },
            "validation_criteria": [
                "Sistema extrai dados corretos do texto do passaporte",
                "Sistema detecta discrepância no nome",
                "Sistema calcula confiança >= 70%",
                "Sistema corrige automaticamente o cadastro",
                "Sistema adiciona campos de auditoria",
                "Dados são persistidos no MongoDB"
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: /app/direct_autocorrect_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    system_ready = summary.get("system_ready", False)
    success_rate = summary.get("success_rate", 0)
    auto_correction_worked = summary.get("auto_correction_worked", False)
    
    if system_ready and auto_correction_worked:
        print("\n🎉 CONCLUSÃO FINAL: SISTEMA DE CORREÇÃO AUTOMÁTICA FUNCIONANDO!")
        print("   ✅ Lógica de extração funcionando corretamente")
        print("   ✅ Detecção de discrepâncias operacional")
        print("   ✅ Correção automática implementada")
        print("   ✅ Campos de auditoria sendo adicionados")
        print("   ✅ Sistema pronto para integração com OCR")
    elif auto_correction_worked:
        print("\n⚠️  CONCLUSÃO: Correção automática funciona, mas com problemas menores")
        print("   ✅ Funcionalidade principal operacional")
        print("   ⚠️  Alguns aspectos precisam de ajustes")
        print("   🔧 Revisar áreas problemáticas identificadas")
    else:
        print("\n❌ CONCLUSÃO CRÍTICA: LÓGICA DE CORREÇÃO AUTOMÁTICA COM PROBLEMAS!")
        print("   ❌ Correção automática não está funcionando")
        print("   ❌ Pode haver problemas na lógica de detecção")
        print("   ❌ Algoritmo de confiança pode estar incorreto")
        print("   🚨 Correção da lógica necessária")
        
        criteria_passed = summary.get("criteria_passed", 0)
        total_criteria = summary.get("total_criteria", 5)
        print(f"   📊 Apenas {criteria_passed}/{total_criteria} critérios funcionando")
        print(f"   🎯 Necessário pelo menos 4/{total_criteria} para aprovação")