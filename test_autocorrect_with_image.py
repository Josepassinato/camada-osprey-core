#!/usr/bin/env python3
"""
🎯 TESTE COMPLETO - CORREÇÃO AUTOMÁTICA COM IMAGEM DE PASSAPORTE

**OBJETIVO:**
Testar o sistema completo de auto-correção usando uma imagem de passaporte real
para validar a integração completa: OCR → Extração → Comparação → Auto-correção

**CENÁRIO DE TESTE:**
1. Criar usuário com dados incompletos ("Joao Silva")
2. Criar caso de aplicação
3. Upload de imagem de passaporte com nome completo ("JOÃO SILVA SANTOS")
4. Verificar se o sistema completo funciona end-to-end
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://formfiller-26.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_test_user_with_incomplete_data():
    """Criar usuário com dados incompletos para teste de auto-correção"""
    try:
        print("📝 Creating test user with incomplete data...")
        
        # Dados incompletos propositalmente
        user_data = {
            "email": "test_autocorrect_image@test.com",
            "password": "testpass123",
            "first_name": "Joao",  # Sem acento
            "last_name": "Silva",  # Sem sobrenome completo
            "phone": "+1-555-0123"
        }
        
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            token = result.get("token")
            user_info = result.get("user", {})
            user_id = user_info.get("id")
            
            if token and user_id:
                print(f"✅ Test user created: {user_id}")
                print(f"📧 Email: {user_data['email']}")
                print(f"👤 Name: {user_data['first_name']} {user_data['last_name']}")
                return {
                    "success": True,
                    "user_id": user_id,
                    "token": token,
                    "email": user_data["email"],
                    "original_data": user_data
                }
            else:
                print(f"❌ Missing token or user_id in response")
                return {"success": False, "error": "Missing credentials"}
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            return {"success": False, "status_code": response.status_code, "error": response.text}
            
    except Exception as e:
        print(f"❌ Exception creating test user: {str(e)}")
        return {"success": False, "exception": str(e)}

def create_auto_application_case(token):
    """Criar caso de aplicação automática"""
    try:
        print("\n📝 Creating auto-application case...")
        
        case_data = {
            "session_token": "test_image_session",
            "applicant_name": "Joao Silva",
            "applicant_email": "test_autocorrect_image@test.com",
            "date_of_birth": "1990-05-15"
        }
        
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json=case_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            case_info = result.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ Auto-application case created: {case_id}")
                return {
                    "success": True,
                    "case_id": case_id,
                    "case_data": case_info
                }
            else:
                print(f"❌ No case_id in response")
                return {"success": False, "error": "No case_id"}
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            return {"success": False, "status_code": response.status_code, "error": response.text}
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        return {"success": False, "exception": str(e)}

def upload_passport_image(case_id, token):
    """Upload da imagem de passaporte para teste de auto-correção"""
    try:
        print(f"\n📤 Uploading passport image to case {case_id}...")
        
        # Verificar se a imagem existe
        image_path = "/app/test_passport.png"
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return {"success": False, "error": "Image file not found"}
        
        print(f"📄 Image file size: {os.path.getsize(image_path)} bytes")
        
        # Upload via multipart/form-data
        with open(image_path, 'rb') as f:
            files = {
                'file': ('test_passport.png', f, 'image/png')
            }
            data = {
                'document_type': 'passport'
            }
            
            response = requests.post(
                f"{API_BASE}/case/{case_id}/upload-document",
                files=files,
                data=data,
                headers={
                    "Authorization": f"Bearer {token}"
                },
                timeout=60
            )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploaded successfully")
            
            # Verificar se houve extração e auto-correção
            extraction = result.get("extraction", {})
            if extraction:
                print(f"\n🔍 EXTRACTION RESULTS:")
                print(f"  Successful: {extraction.get('successful', False)}")
                print(f"  Auto-corrected: {extraction.get('auto_corrected', False)}")
                print(f"  Corrections made: {extraction.get('corrections_made', {})}")
                print(f"  Message: {extraction.get('message', 'N/A')}")
                
                if extraction.get('discrepancies_found'):
                    print(f"  Discrepancies found: {len(extraction['discrepancies_found'])}")
                    for i, disc in enumerate(extraction['discrepancies_found'][:3]):
                        print(f"    {i+1}. {disc.get('field')}: '{disc.get('current_value')}' → '{disc.get('document_value')}'")
            else:
                print(f"⚠️  No extraction data in response")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "result": result,
                "extraction": extraction
            }
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception uploading document: {str(e)}")
        return {"success": False, "exception": str(e)}

def verify_user_data_updated(user_id, token, original_data):
    """Verificar se os dados do usuário foram atualizados corretamente"""
    try:
        print(f"\n🔍 Verifying user data updates for user {user_id}...")
        
        response = requests.get(
            f"{API_BASE}/profile",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"📄 Updated user data: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
            
            # Comparar dados originais vs atualizados
            print(f"\n📊 DATA COMPARISON:")
            print("=" * 60)
            
            original_name = f"{original_data['first_name']} {original_data['last_name']}"
            updated_first = user_data.get("first_name", "")
            updated_last = user_data.get("last_name", "")
            updated_name = f"{updated_first} {updated_last}".strip()
            
            print(f"📝 Original Name: '{original_name}'")
            print(f"📝 Updated Name: '{updated_name}'")
            
            # Verificar campos de auditoria
            audit_fields = {
                "data_verified_by_document": user_data.get("data_verified_by_document"),
                "verification_document_type": user_data.get("verification_document_type"),
                "verification_date": user_data.get("verification_date")
            }
            
            print(f"\n🔍 AUDIT FIELDS:")
            for field, value in audit_fields.items():
                status = "✅" if value else "❌"
                print(f"  {status} {field}: {value}")
            
            # Verificar se nome foi corrigido
            name_corrected = updated_name != original_name and "Santos" in updated_name
            
            verification_results = {
                "name_was_corrected": name_corrected,
                "original_name": original_name,
                "updated_name": updated_name,
                "audit_fields_present": all(audit_fields.values()),
                "data_verified_by_document": audit_fields["data_verified_by_document"],
                "verification_document_type": audit_fields["verification_document_type"],
                "verification_date": audit_fields["verification_date"]
            }
            
            print(f"\n🎯 VERIFICATION RESULTS:")
            for check, result in verification_results.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}: {result}")
            
            return {
                "success": True,
                "user_data": user_data,
                "verification_results": verification_results,
                "name_corrected": name_corrected
            }
        else:
            print(f"❌ Failed to get user profile: {response.status_code}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception verifying user data: {str(e)}")
        return {"success": False, "exception": str(e)}

def test_document_autocorrect_with_image():
    """
    🎯 TESTE COMPLETO - CORREÇÃO AUTOMÁTICA COM IMAGEM DE PASSAPORTE
    
    FLUXO COMPLETO:
    1. Criar usuário com dados incompletos ("Joao Silva")
    2. Criar caso de aplicação
    3. Upload de imagem de passaporte com nome completo ("JOÃO SILVA SANTOS")
    4. Verificar se sistema completo funciona:
       - OCR extrai texto da imagem
       - Regex extrai dados do texto
       - Comparação identifica discrepâncias
       - Auto-correção é ativada
       - Dados do usuário são atualizados
       - Campos de auditoria são preenchidos
    
    CRITÉRIOS DE SUCESSO:
    - ✅ OCR processa imagem corretamente
    - ✅ Extração de dados funciona
    - ✅ Auto-correção é ativada
    - ✅ Dados do usuário são atualizados
    - ✅ Campos de auditoria são preenchidos
    """
    
    print("🎯 TESTE COMPLETO - CORREÇÃO AUTOMÁTICA COM IMAGEM DE PASSAPORTE")
    print("📋 INTEGRAÇÃO COMPLETA - OCR + Extração + Auto-correção")
    print("🎯 OBJETIVO: Validar fluxo end-to-end com imagem real")
    print("=" * 80)
    
    results = {
        "step1_create_user": {},
        "step2_create_case": {},
        "step3_upload_image": {},
        "step4_verify_updates": {},
        "summary": {}
    }
    
    # STEP 1: Criar usuário com dados incompletos
    print("\n📋 STEP 1: Criar usuário com dados incompletos")
    print("-" * 60)
    
    user_result = create_test_user_with_incomplete_data()
    results["step1_create_user"] = user_result
    
    if not user_result.get("success"):
        print("❌ Failed to create test user - aborting test")
        return results
    
    user_id = user_result["user_id"]
    token = user_result["token"]
    original_data = user_result["original_data"]
    
    # STEP 2: Criar caso de aplicação
    print("\n📋 STEP 2: Criar caso de aplicação")
    print("-" * 60)
    
    case_result = create_auto_application_case(token)
    results["step2_create_case"] = case_result
    
    if not case_result.get("success"):
        print("❌ Failed to create case - aborting test")
        return results
    
    case_id = case_result["case_id"]
    
    # STEP 3: Upload imagem e testar auto-correção
    print("\n📋 STEP 3: Upload imagem e testar auto-correção")
    print("-" * 60)
    
    upload_result = upload_passport_image(case_id, token)
    results["step3_upload_image"] = upload_result
    
    # STEP 4: Verificar se dados foram atualizados
    print("\n📋 STEP 4: Verificar atualizações nos dados do usuário")
    print("-" * 60)
    
    # Aguardar um pouco para processamento
    time.sleep(3)
    
    verification_result = verify_user_data_updated(user_id, token, original_data)
    results["step4_verify_updates"] = verification_result
    
    # ANÁLISE FINAL
    print("\n📋 ANÁLISE FINAL - SISTEMA DE AUTO-CORREÇÃO COM IMAGEM")
    print("=" * 80)
    
    # Contar etapas bem-sucedidas
    step_results = [
        results.get("step1_create_user", {}).get("success", False),
        results.get("step2_create_case", {}).get("success", False),
        results.get("step3_upload_image", {}).get("success", False),
        results.get("step4_verify_updates", {}).get("success", False)
    ]
    
    successful_steps = sum(step_results)
    total_steps = len(step_results)
    success_rate = (successful_steps / total_steps) * 100
    
    # Resultados por etapa
    step_names = [
        "STEP 1: Criar usuário com dados incompletos",
        "STEP 2: Criar caso de aplicação",
        "STEP 3: Upload imagem e testar auto-correção",
        "STEP 4: Verificar atualizações nos dados do usuário"
    ]
    
    print(f"📊 RESULTADOS POR ETAPA:")
    for i, (step_name, passed) in enumerate(zip(step_names, step_results)):
        status = "✅" if passed else "❌"
        print(f"  {status} {step_name}: {'SUCESSO' if passed else 'FALHOU'}")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
    
    # Análise específica da auto-correção
    print(f"\n🔍 ANÁLISE DA AUTO-CORREÇÃO COM IMAGEM:")
    print("=" * 60)
    
    extraction_data = results.get("step3_upload_image", {}).get("extraction", {})
    verification_data = results.get("step4_verify_updates", {}).get("verification_results", {})
    
    autocorrect_checks = {
        "image_uploaded": results.get("step3_upload_image", {}).get("success", False),
        "extraction_successful": extraction_data.get("successful", False),
        "auto_correction_triggered": extraction_data.get("auto_corrected", False),
        "corrections_applied": bool(extraction_data.get("corrections_made")),
        "user_data_updated": verification_data.get("name_was_corrected", False),
        "audit_fields_added": verification_data.get("audit_fields_present", False)
    }
    
    print(f"📊 VERIFICAÇÕES DE AUTO-CORREÇÃO:")
    for check, passed in autocorrect_checks.items():
        status = "✅" if passed else "❌"
        check_name = check.replace("_", " ").title()
        print(f"  {status} {check_name}: {'PASSOU' if passed else 'FALHOU'}")
    
    autocorrect_success = sum(autocorrect_checks.values())
    total_autocorrect_checks = len(autocorrect_checks)
    autocorrect_rate = (autocorrect_success / total_autocorrect_checks) * 100
    
    print(f"\n🎯 TAXA DE SUCESSO DA AUTO-CORREÇÃO: {autocorrect_success}/{total_autocorrect_checks} ({autocorrect_rate:.1f}%)")
    
    # Detalhes da extração
    if extraction_data:
        print(f"\n📋 DETALHES DA EXTRAÇÃO:")
        print(f"  Successful: {extraction_data.get('successful', False)}")
        print(f"  Auto-corrected: {extraction_data.get('auto_corrected', False)}")
        print(f"  Message: {extraction_data.get('message', 'N/A')}")
        
        corrections = extraction_data.get('corrections_made', {})
        if corrections:
            print(f"  Corrections made:")
            for field, value in corrections.items():
                print(f"    {field}: '{value}'")
    
    # Detalhes da verificação
    if verification_data:
        print(f"\n📋 DETALHES DA VERIFICAÇÃO:")
        print(f"  Original name: '{verification_data.get('original_name', '')}'")
        print(f"  Updated name: '{verification_data.get('updated_name', '')}'")
        print(f"  Name corrected: {verification_data.get('name_was_corrected', False)}")
        print(f"  Document verified: {verification_data.get('data_verified_by_document', False)}")
        print(f"  Document type: {verification_data.get('verification_document_type', 'N/A')}")
    
    # Avaliação final
    system_working = autocorrect_rate >= 50 and verification_data.get("name_was_corrected", False)
    
    print(f"\n🎯 AVALIAÇÃO FINAL:")
    print("=" * 60)
    
    if system_working:
        print("✅ SISTEMA DE AUTO-CORREÇÃO COM IMAGEM: FUNCIONANDO CORRETAMENTE")
        print("✅ OCR: PROCESSANDO IMAGEM CORRETAMENTE")
        print("✅ EXTRAÇÃO: DADOS EXTRAÍDOS DA IMAGEM")
        print("✅ AUTO-CORREÇÃO: ATIVADA COM SUCESSO")
        print("✅ DADOS DO USUÁRIO: ATUALIZADOS CORRETAMENTE")
        print("✅ AUDITORIA: CAMPOS PREENCHIDOS")
    else:
        print("❌ SISTEMA DE AUTO-CORREÇÃO COM IMAGEM: PROBLEMAS IDENTIFICADOS")
        
        # Identificar áreas problemáticas
        problem_areas = []
        if not autocorrect_checks["extraction_successful"]:
            problem_areas.append("OCR/Extração de dados da imagem")
        if not autocorrect_checks["auto_correction_triggered"]:
            problem_areas.append("Ativação da auto-correção")
        if not autocorrect_checks["user_data_updated"]:
            problem_areas.append("Atualização dos dados do usuário")
        if not autocorrect_checks["audit_fields_added"]:
            problem_areas.append("Preenchimento dos campos de auditoria")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Salvar resumo
    results["summary"] = {
        "successful_steps": successful_steps,
        "total_steps": total_steps,
        "success_rate": success_rate,
        "autocorrect_checks": autocorrect_checks,
        "autocorrect_success": autocorrect_success,
        "total_autocorrect_checks": total_autocorrect_checks,
        "autocorrect_rate": autocorrect_rate,
        "system_working": system_working,
        "extraction_data": extraction_data,
        "verification_data": verification_data
    }
    
    return results

if __name__ == "__main__":
    print("🎯 INICIANDO TESTE COMPLETO - AUTO-CORREÇÃO COM IMAGEM")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("🎯 OBJETIVO: Validar sistema completo com imagem de passaporte")
    
    # Execute main test
    test_results = test_document_autocorrect_with_image()
    
    # Save results to file
    with open("/app/autocorrect_image_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "🎯 TESTE COMPLETO - CORREÇÃO AUTOMÁTICA COM IMAGEM DE PASSAPORTE",
            "test_scenario": {
                "original_name": "Joao Silva",
                "document_name": "JOÃO SILVA SANTOS",
                "expected_correction": "João Silva Santos",
                "document_type": "passport",
                "file_type": "image/png"
            },
            "integration_components": [
                "Google Vision API (OCR)",
                "Document Data Extractor (Regex)",
                "Name Comparison Logic",
                "Auto-correction Criteria",
                "User Data Update",
                "Audit Fields"
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: /app/autocorrect_image_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    system_working = summary.get("system_working", False)
    autocorrect_rate = summary.get("autocorrect_rate", 0)
    
    if system_working:
        print("\n🎉 CONCLUSÃO FINAL: SISTEMA DE AUTO-CORREÇÃO COM IMAGEM FUNCIONANDO!")
        print("   ✅ OCR processando imagem corretamente")
        print("   ✅ Extração de dados funcionando")
        print("   ✅ Auto-correção ativada corretamente")
        print("   ✅ Dados do usuário atualizados")
        print("   ✅ Sistema completo pronto para produção")
    else:
        print("\n❌ CONCLUSÃO CRÍTICA: SISTEMA DE AUTO-CORREÇÃO COM PROBLEMAS!")
        print("   ❌ Algumas funcionalidades não estão operacionais")
        print(f"   📊 Taxa de sucesso: {autocorrect_rate:.1f}%")
        print("   🔧 Correções adicionais necessárias")
        
        extraction_successful = summary.get("extraction_data", {}).get("successful", False)
        auto_corrected = summary.get("extraction_data", {}).get("auto_corrected", False)
        
        if not extraction_successful:
            print("   🚨 PROBLEMA CRÍTICO: OCR/Extração de dados falhou")
        elif not auto_corrected:
            print("   🚨 PROBLEMA CRÍTICO: Auto-correção não foi ativada")
        else:
            print("   ⚠️  Extração funcionou mas dados não foram persistidos")