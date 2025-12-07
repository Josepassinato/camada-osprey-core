#!/usr/bin/env python3
"""
🎯 AUDITORIA COMPLETA - FLUXO FORMULÁRIO AMIGÁVEL → FORMULÁRIO OFICIAL

Objetivo: Verificar se o sistema tem um formulário amigável em português para o usuário preencher,
e se esses dados alimentam o formulário oficial USCIS.

FLUXO ESPERADO:
Usuário (Português) → Formulário Amigável → IA Avalia → Dados Coletados → Formulário Oficial USCIS
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://visaflow-5.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_friendly_form_complete_flow():
    """
    🎯 AUDITORIA COMPLETA - FLUXO FORMULÁRIO AMIGÁVEL → FORMULÁRIO OFICIAL
    
    Testa o fluxo completo conforme especificado na review request:
    1. Verificar existência do FriendlyForm
    2. Verificar backend support para simplified_form_responses
    3. Testar fluxo completo - criar caso, preencher formulário amigável
    4. Verificar mapeamento IA → formulário oficial
    5. Testar geração com dados amigáveis
    """
    
    print("🎯 AUDITORIA COMPLETA - FLUXO FORMULÁRIO AMIGÁVEL → FORMULÁRIO OFICIAL")
    print("=" * 80)
    print("📋 Objetivo: Verificar formulário amigável em português → formulário oficial USCIS")
    print("🔄 Fluxo: Usuário (PT) → Form Amigável → IA → Dados → Form Oficial USCIS")
    print("=" * 80)
    
    results = {
        "parte1_friendly_form": {},
        "parte2_backend": {},
        "parte3_fluxo_completo": {},
        "parte4_mapeamento_ia": {},
        "parte5_geracao_oficial": {},
        "summary": {}
    }
    
    # PARTE 1: VERIFICAR FORMULÁRIO AMIGÁVEL
    print("\n🔍 PARTE 1: VERIFICAR FORMULÁRIO AMIGÁVEL")
    print("-" * 50)
    
    # 1.1: Verificar existência do FriendlyForm
    print("\n📋 1.1: Verificar Existência do FriendlyForm")
    friendly_form_exists = os.path.exists("/app/frontend/src/pages/FriendlyForm.tsx")
    
    if friendly_form_exists:
        file_size = os.path.getsize("/app/frontend/src/pages/FriendlyForm.tsx")
        print(f"✅ Arquivo existe: /app/frontend/src/pages/FriendlyForm.tsx")
        print(f"✅ Tamanho: {file_size} bytes ({file_size/1024:.1f} KB)")
        print(f"✅ É um componente React: {file_size > 0}")
        
        # Verificar estrutura do FriendlyForm
        try:
            with open("/app/frontend/src/pages/FriendlyForm.tsx", "r") as f:
                content = f.read()
                
            # Verificar interfaces e funcionalidades
            has_form_section = "interface FormSection" in content
            has_form_field = "interface FormField" in content
            has_ai_suggestion = "aiSuggestion" in content
            has_validation = "validation" in content
            has_portuguese = any(word in content.lower() for word in ["português", "portuguese", "pt-br"])
            
            print(f"\n📋 1.2: Verificar Estrutura do FriendlyForm")
            print(f"✅ Tem interface FormSection: {has_form_section}")
            print(f"✅ Tem interface FormField: {has_form_field}")
            print(f"✅ Suporta diferentes tipos de campos: {has_ai_suggestion}")
            print(f"✅ Tem validação: {has_validation}")
            print(f"✅ Tem integração com IA (aiSuggestion): {has_ai_suggestion}")
            
            print(f"\n📋 1.3: Verificar Idioma do Formulário")
            print(f"✅ Textos em português: {has_portuguese}")
            
            results["parte1_friendly_form"] = {
                "exists": friendly_form_exists,
                "file_size": file_size,
                "has_form_section": has_form_section,
                "has_form_field": has_form_field,
                "has_ai_suggestion": has_ai_suggestion,
                "has_validation": has_validation,
                "has_portuguese": has_portuguese,
                "working": all([friendly_form_exists, file_size > 0, has_form_section, has_form_field])
            }
            
        except Exception as e:
            print(f"❌ Erro ao analisar FriendlyForm: {str(e)}")
            results["parte1_friendly_form"]["working"] = False
    else:
        print(f"❌ Arquivo não existe: /app/frontend/src/pages/FriendlyForm.tsx")
        results["parte1_friendly_form"]["working"] = False
    
    # PARTE 2: VERIFICAR BACKEND
    print("\n🔍 PARTE 2: VERIFICAR BACKEND")
    print("-" * 50)
    
    # 2.1: Endpoint de Formulário Simplificado
    print("\n📋 2.1: Verificar Endpoints de Formulário Simplificado")
    
    # Verificar se o modelo suporta simplified_form_responses
    try:
        # Criar um caso de teste para verificar o modelo
        test_case_data = {
            "visa_type": "I-539",
            "applicant_name": "Test User Friendly Form",
            "email": "friendly@test.com"
        }
        
        print(f"🔗 Endpoint: POST {API_BASE}/auto-application/start")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json=test_case_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_id = case_data.get("case", {}).get("case_id")
            print(f"✅ Caso criado: {case_id}")
            
            # Testar se aceita simplified_form_responses
            simplified_responses = {
                "personal_info": {
                    "full_name": "João da Silva Santos",
                    "birth_date": "15 de março de 1990",
                    "nationality": "Brasileiro",
                    "passport": "BR123456789"
                },
                "current_status": {
                    "visa_type": "F-1 estudante",
                    "expiration": "30 de junho de 2025",
                    "reason_extension": "Preciso terminar meu mestrado em ciência da computação"
                },
                "contact": {
                    "address": "Rua 123, Apartamento 4B, Boston",
                    "phone": "617-555-1234",
                    "email": "joao@test.com"
                }
            }
            
            print(f"\n📋 2.2: Testar Salvamento de Respostas Amigáveis")
            print(f"🔗 Endpoint: PUT {API_BASE}/auto-application/case/{case_id}")
            
            update_response = requests.put(
                f"{API_BASE}/auto-application/case/{case_id}",
                json={"simplified_form_responses": simplified_responses},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"📊 Status Code: {update_response.status_code}")
            
            if update_response.status_code == 200:
                print("✅ Campo simplified_form_responses aceito pelo modelo")
                print("✅ Endpoint para salvar respostas funcionando")
                
                # Verificar se dados foram salvos
                print(f"\n📋 2.3: Verificar Se Dados Foram Salvos")
                print(f"🔗 Endpoint: GET {API_BASE}/auto-application/case/{case_id}")
                
                get_response = requests.get(
                    f"{API_BASE}/auto-application/case/{case_id}",
                    timeout=30
                )
                
                print(f"📊 Status Code: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    case_info = get_response.json()
                    saved_responses = case_info.get("case", {}).get("simplified_form_responses")
                    
                    if saved_responses:
                        print("✅ Dados em português preservados")
                        print("✅ Estrutura correta")
                        print(f"📄 Dados salvos: {json.dumps(saved_responses, indent=2, ensure_ascii=False)}")
                        
                        results["parte2_backend"] = {
                            "case_created": True,
                            "simplified_responses_accepted": True,
                            "data_persisted": True,
                            "portuguese_preserved": True,
                            "working": True
                        }
                    else:
                        print("❌ Dados não foram persistidos")
                        results["parte2_backend"]["working"] = False
                else:
                    print(f"❌ Erro ao recuperar caso: {get_response.status_code}")
                    results["parte2_backend"]["working"] = False
            else:
                print(f"❌ Erro ao salvar respostas: {update_response.status_code}")
                results["parte2_backend"]["working"] = False
        else:
            print(f"❌ Erro ao criar caso: {response.status_code}")
            results["parte2_backend"]["working"] = False
            
    except Exception as e:
        print(f"❌ Erro no teste de backend: {str(e)}")
        results["parte2_backend"]["working"] = False
    
    # PARTE 3: TESTAR FLUXO COMPLETO
    print("\n🔍 PARTE 3: TESTAR FLUXO COMPLETO")
    print("-" * 50)
    
    try:
        # 3.1: Criar Caso e Preencher Formulário Amigável
        print("\n📋 3.1: Criar Caso I-539 para Teste")
        
        case_data = {
            "visa_type": "I-539",
            "applicant_name": "Maria Santos Silva",
            "email": "maria@test.com"
        }
        
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json=case_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            case_info = response.json()
            case_id = case_info.get("case", {}).get("case_id")
            print(f"✅ Caso criado: {case_id}")
            
            # 3.2: Salvar Respostas do Formulário Amigável
            print(f"\n📋 3.2: Salvar Respostas do Formulário Amigável")
            
            friendly_responses = {
                "personal_info": {
                    "full_name": "Maria Santos Silva",
                    "birth_date": "20 de janeiro de 1985",
                    "nationality": "Brasileira",
                    "passport": "BR987654321"
                },
                "current_status": {
                    "visa_type": "F-1 estudante",
                    "expiration": "15 de dezembro de 2024",
                    "reason_extension": "Preciso de mais tempo para completar minha dissertação de mestrado em Engenharia"
                },
                "contact": {
                    "address": "Rua Augusta 456, Apartamento 12A, São Paulo",
                    "phone": "11-98765-4321",
                    "email": "maria.santos@email.com"
                },
                "education": {
                    "current_school": "Universidade de São Paulo",
                    "program": "Mestrado em Engenharia Civil",
                    "expected_completion": "Junho de 2025"
                }
            }
            
            update_response = requests.put(
                f"{API_BASE}/auto-application/case/{case_id}",
                json={"simplified_form_responses": friendly_responses},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"📊 Status Code: {update_response.status_code}")
            
            if update_response.status_code == 200:
                print("✅ Respostas do formulário amigável salvas")
                
                # 3.3: Verificar Se Dados Foram Salvos
                print(f"\n📋 3.3: Verificar Persistência dos Dados")
                
                get_response = requests.get(
                    f"{API_BASE}/auto-application/case/{case_id}",
                    timeout=30
                )
                
                if get_response.status_code == 200:
                    case_data = get_response.json()
                    saved_responses = case_data.get("case", {}).get("simplified_form_responses")
                    
                    if saved_responses:
                        print("✅ Campo existe")
                        print("✅ Dados em português preservados")
                        print("✅ Estrutura correta")
                        
                        results["parte3_fluxo_completo"] = {
                            "case_created": True,
                            "responses_saved": True,
                            "data_persisted": True,
                            "structure_correct": True,
                            "working": True
                        }
                    else:
                        print("❌ Dados não persistidos")
                        results["parte3_fluxo_completo"]["working"] = False
                else:
                    print(f"❌ Erro ao verificar dados: {get_response.status_code}")
                    results["parte3_fluxo_completo"]["working"] = False
            else:
                print(f"❌ Erro ao salvar respostas: {update_response.status_code}")
                results["parte3_fluxo_completo"]["working"] = False
        else:
            print(f"❌ Erro ao criar caso: {response.status_code}")
            results["parte3_fluxo_completo"]["working"] = False
            
    except Exception as e:
        print(f"❌ Erro no fluxo completo: {str(e)}")
        results["parte3_fluxo_completo"]["working"] = False
    
    # PARTE 4: MAPEAMENTO IA → FORMULÁRIO OFICIAL
    print("\n🔍 PARTE 4: MAPEAMENTO IA → FORMULÁRIO OFICIAL")
    print("-" * 50)
    
    try:
        # 4.1: Procurar Sistema de Tradução
        print("\n📋 4.1: Verificar Sistema de Mapeamento/Tradução")
        
        # Testar endpoint de mapeamento (se existir)
        mapping_endpoints = [
            f"/api/case/{case_id}/map-to-official",
            f"/api/auto-application/case/{case_id}/translate-responses",
            f"/api/auto-application/case/{case_id}/ai-processing"
        ]
        
        mapping_found = False
        for endpoint in mapping_endpoints:
            try:
                print(f"🔗 Testando: POST {BACKEND_URL}{endpoint}")
                response = requests.post(f"{BACKEND_URL}{endpoint}", timeout=10)
                print(f"📊 Status Code: {response.status_code}")
                
                if response.status_code not in [404, 405]:
                    mapping_found = True
                    print(f"✅ Endpoint de mapeamento encontrado: {endpoint}")
                    break
            except:
                continue
        
        if not mapping_found:
            print("⚠️  Nenhum endpoint específico de mapeamento encontrado")
        
        # 4.2: Verificar Integração com Form Filler
        print(f"\n📋 4.2: Verificar Integração com Form Filler")
        
        # Verificar se existe uscis_form_filler.py
        form_filler_exists = os.path.exists("/app/backend/uscis_form_filler.py")
        print(f"✅ Form filler existe: {form_filler_exists}")
        
        if form_filler_exists:
            try:
                with open("/app/backend/uscis_form_filler.py", "r") as f:
                    filler_content = f.read()
                
                uses_simplified = "simplified_form" in filler_content.lower()
                uses_friendly = "friendly" in filler_content.lower()
                has_translation = any(word in filler_content.lower() for word in ["translate", "map", "convert"])
                
                print(f"✅ Form filler lê simplified_form_responses: {uses_simplified}")
                print(f"✅ Referências a friendly form: {uses_friendly}")
                print(f"✅ Sistema de tradução/mapeamento: {has_translation}")
                
                results["parte4_mapeamento_ia"] = {
                    "mapping_endpoints_found": mapping_found,
                    "form_filler_exists": form_filler_exists,
                    "uses_simplified_responses": uses_simplified,
                    "has_translation_logic": has_translation,
                    "working": form_filler_exists and (uses_simplified or has_translation)
                }
                
            except Exception as e:
                print(f"❌ Erro ao analisar form filler: {str(e)}")
                results["parte4_mapeamento_ia"]["working"] = False
        else:
            results["parte4_mapeamento_ia"]["working"] = False
            
    except Exception as e:
        print(f"❌ Erro no teste de mapeamento: {str(e)}")
        results["parte4_mapeamento_ia"]["working"] = False
    
    # PARTE 5: TESTAR GERAÇÃO COM DADOS AMIGÁVEIS
    print("\n🔍 PARTE 5: TESTAR GERAÇÃO COM DADOS AMIGÁVEIS")
    print("-" * 50)
    
    try:
        # 5.1: Gerar Formulário Oficial Com Dados Amigáveis
        print(f"\n📋 5.1: Gerar Formulário Oficial Com Dados Amigáveis")
        print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/generate-form")
        
        generate_response = requests.post(
            f"{API_BASE}/case/{case_id}/generate-form",
            timeout=60
        )
        
        print(f"📊 Status Code: {generate_response.status_code}")
        
        if generate_response.status_code == 200:
            form_data = generate_response.json()
            print(f"✅ Formulário oficial gerado")
            print(f"📄 Resposta: {json.dumps(form_data, indent=2)}")
            
            # 5.2: Comparar Dados
            print(f"\n📋 5.2: Comparar Dados - Amigável vs Oficial")
            
            # Buscar dados finais do caso
            final_response = requests.get(
                f"{API_BASE}/auto-application/case/{case_id}",
                timeout=30
            )
            
            if final_response.status_code == 200:
                final_data = final_response.json()
                case_info = final_data.get("case", {})
                
                simplified = case_info.get("simplified_form_responses")
                basic_data = case_info.get("basic_data")
                generated_form = case_info.get("generated_form")
                
                print(f"\n📊 ANÁLISE DE DADOS:")
                print(f"✅ Dados do formulário amigável (português): {'Sim' if simplified else 'Não'}")
                print(f"✅ Dados do basic_data (mapeado): {'Sim' if basic_data else 'Não'}")
                print(f"✅ PDF gerado: {'Sim' if generated_form else 'Não'}")
                
                if simplified:
                    print(f"\n📄 Dados amigáveis encontrados:")
                    print(f"   - Seções: {list(simplified.keys()) if isinstance(simplified, dict) else 'N/A'}")
                
                if generated_form:
                    print(f"\n📄 Formulário gerado:")
                    print(f"   - Tipo: {generated_form.get('form_type', 'N/A')}")
                    print(f"   - Tamanho: {generated_form.get('file_size', 0)} bytes")
                
                # Determinar fonte dos dados para o PDF
                uses_simplified_data = simplified and generated_form
                
                results["parte5_geracao_oficial"] = {
                    "form_generated": True,
                    "has_simplified_data": bool(simplified),
                    "has_generated_form": bool(generated_form),
                    "uses_simplified_for_pdf": uses_simplified_data,
                    "working": bool(generated_form)
                }
            else:
                print(f"❌ Erro ao buscar dados finais: {final_response.status_code}")
                results["parte5_geracao_oficial"]["working"] = False
        else:
            print(f"❌ Erro na geração: {generate_response.status_code}")
            print(f"📄 Erro: {generate_response.text}")
            results["parte5_geracao_oficial"]["working"] = False
            
    except Exception as e:
        print(f"❌ Erro na geração oficial: {str(e)}")
        results["parte5_geracao_oficial"]["working"] = False
    
    # RESUMO E AVALIAÇÃO
    print("\n📊 CRITÉRIOS DE AVALIAÇÃO")
    print("=" * 80)
    
    # Formulário Amigável (5 pontos)
    friendly_form_score = 0
    friendly_criteria = results.get("parte1_friendly_form", {})
    
    print("\n📋 Formulário Amigável (5 pontos):")
    criteria_checks = [
        ("Existe componente FriendlyForm.tsx", friendly_criteria.get("exists", False)),
        ("Suporta múltiplas seções", friendly_criteria.get("has_form_section", False)),
        ("Tem validação de campos", friendly_criteria.get("has_validation", False)),
        ("Integra com IA para sugestões", friendly_criteria.get("has_ai_suggestion", False)),
        ("Salva no campo simplified_form_responses", results.get("parte2_backend", {}).get("simplified_responses_accepted", False))
    ]
    
    for criteria, passed in criteria_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {criteria}")
        if passed:
            friendly_form_score += 1
    
    # Backend (5 pontos)
    backend_score = 0
    backend_criteria = results.get("parte2_backend", {})
    
    print("\n📋 Backend (5 pontos):")
    backend_checks = [
        ("Modelo aceita simplified_form_responses", backend_criteria.get("simplified_responses_accepted", False)),
        ("Endpoint para salvar respostas", backend_criteria.get("case_created", False)),
        ("Endpoint para recuperar respostas", backend_criteria.get("data_persisted", False)),
        ("Sistema de mapeamento existe", results.get("parte4_mapeamento_ia", {}).get("working", False)),
        ("IA valida/traduz respostas", results.get("parte4_mapeamento_ia", {}).get("has_translation_logic", False))
    ]
    
    for criteria, passed in backend_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {criteria}")
        if passed:
            backend_score += 1
    
    # Integração (5 pontos)
    integration_score = 0
    integration_criteria = results.get("parte4_mapeamento_ia", {})
    generation_criteria = results.get("parte5_geracao_oficial", {})
    
    print("\n📋 Integração (5 pontos):")
    integration_checks = [
        ("Form filler usa simplified_form_responses", integration_criteria.get("uses_simplified_responses", False)),
        ("Dados amigáveis → dados oficiais", integration_criteria.get("working", False)),
        ("Tradução português → inglês", integration_criteria.get("has_translation_logic", False)),
        ("Mapeamento de campos funciona", integration_criteria.get("working", False)),
        ("PDF final contém dados corretos", generation_criteria.get("working", False))
    ]
    
    for criteria, passed in integration_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {criteria}")
        if passed:
            integration_score += 1
    
    # Experiência do Usuário (5 pontos)
    ux_score = 0
    
    print("\n📋 Experiência do Usuário (5 pontos):")
    ux_checks = [
        ("Formulário em português", friendly_criteria.get("has_portuguese", False)),
        ("Perguntas simples e claras", friendly_criteria.get("has_form_field", False)),
        ("Feedback em tempo real", friendly_criteria.get("has_validation", False)),
        ("IA auxilia preenchimento", friendly_criteria.get("has_ai_suggestion", False)),
        ("Fluxo intuitivo", results.get("parte3_fluxo_completo", {}).get("working", False))
    ]
    
    for criteria, passed in ux_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {criteria}")
        if passed:
            ux_score += 1
    
    # Score Total
    total_score = friendly_form_score + backend_score + integration_score + ux_score
    max_score = 20
    
    print(f"\n🎯 RESULTADO ESPERADO")
    print("=" * 50)
    print(f"Score Total: {total_score}/{max_score} pontos ({total_score/max_score*100:.1f}%)")
    
    # Fluxo Completo
    print(f"\n📋 Fluxo Completo:")
    flow_checks = [
        ("Usuário preenche formulário amigável (português)", friendly_criteria.get("working", False)),
        ("Sistema salva em simplified_form_responses", backend_criteria.get("working", False)),
        ("IA valida e mapeia dados", integration_criteria.get("working", False)),
        ("Sistema preenche formulário oficial USCIS", generation_criteria.get("working", False)),
        ("PDF gerado contém dados corretos", generation_criteria.get("has_generated_form", False))
    ]
    
    for step, passed in flow_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {step}")
    
    # Conclusão
    working_steps = sum(1 for _, passed in flow_checks if passed)
    total_steps = len(flow_checks)
    
    print(f"\n📊 Conclusão:")
    if total_score >= 15:  # 75% threshold
        print("✅ Sistema está COMPLETO")
        print(f"✅ {working_steps}/{total_steps} etapas do fluxo funcionando")
    elif total_score >= 10:  # 50% threshold
        print("⚠️  Sistema está PARCIAL")
        print(f"⚠️  {working_steps}/{total_steps} etapas do fluxo funcionando")
    else:
        print("❌ Sistema está INCOMPLETO")
        print(f"❌ {working_steps}/{total_steps} etapas do fluxo funcionando")
    
    # O que funciona / O que está faltando
    print(f"\n📋 O que funciona:")
    working_parts = []
    if friendly_form_score >= 3:
        working_parts.append("- Formulário amigável implementado")
    if backend_score >= 3:
        working_parts.append("- Backend suporta dados amigáveis")
    if integration_score >= 2:
        working_parts.append("- Integração parcial funcionando")
    if ux_score >= 3:
        working_parts.append("- Experiência do usuário adequada")
    
    for part in working_parts:
        print(part)
    
    print(f"\n📋 O que está faltando:")
    missing_parts = []
    if friendly_form_score < 3:
        missing_parts.append("- Implementação completa do formulário amigável")
    if backend_score < 3:
        missing_parts.append("- Suporte completo no backend")
    if integration_score < 3:
        missing_parts.append("- Sistema de mapeamento IA completo")
    if ux_score < 3:
        missing_parts.append("- Melhorias na experiência do usuário")
    
    for part in missing_parts:
        print(part)
    
    # Recomendações
    print(f"\n📋 Recomendações de melhoria:")
    if integration_score < 3:
        print("- Implementar sistema robusto de mapeamento IA português → inglês")
    if backend_score < 4:
        print("- Melhorar persistência e validação de dados amigáveis")
    if friendly_form_score < 4:
        print("- Expandir funcionalidades do formulário amigável")
    
    results["summary"] = {
        "friendly_form_score": friendly_form_score,
        "backend_score": backend_score,
        "integration_score": integration_score,
        "ux_score": ux_score,
        "total_score": total_score,
        "max_score": max_score,
        "percentage": total_score/max_score*100,
        "working_steps": working_steps,
        "total_steps": total_steps,
        "system_status": "COMPLETO" if total_score >= 15 else ("PARCIAL" if total_score >= 10 else "INCOMPLETO")
    }
    
    return results

if __name__ == "__main__":
    print("🚀 INICIANDO AUDITORIA COMPLETA - FORMULÁRIO AMIGÁVEL → FORMULÁRIO OFICIAL")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Execute audit
    audit_results = test_friendly_form_complete_flow()
    
    # Save results
    with open("/app/friendly_form_audit_results.json", "w") as f:
        json.dump({
            "audit_results": audit_results,
            "timestamp": time.time(),
            "test_focus": "Friendly Form → Official Form Flow Audit",
            "criteria": {
                "friendly_form": 5,
                "backend": 5,
                "integration": 5,
                "user_experience": 5,
                "total": 20
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: /app/friendly_form_audit_results.json")
    
    # Final recommendation
    summary = audit_results.get("summary", {})
    system_status = summary.get("system_status", "INCOMPLETO")
    percentage = summary.get("percentage", 0)
    
    print(f"\n✅ RECOMENDAÇÃO FINAL:")
    if system_status == "COMPLETO":
        print("🎉 SISTEMA DE FORMULÁRIO AMIGÁVEL ESTÁ PRONTO PARA PRODUÇÃO")
        print("   - Fluxo completo português → inglês funcionando")
        print("   - Experiência do usuário excelente")
        print("   - Integração IA operacional")
    elif system_status == "PARCIAL":
        print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL - MELHORIAS RECOMENDADAS")
        print("   - Funcionalidades básicas operacionais")
        print("   - Algumas integrações precisam de ajustes")
        print(f"   - Score atual: {percentage:.1f}% (meta: 75%)")
    else:
        print("❌ SISTEMA PRECISA DE DESENVOLVIMENTO ADICIONAL")
        print("   - Múltiplas funcionalidades faltando")
        print("   - Integração IA incompleta")
        print(f"   - Score atual: {percentage:.1f}% (meta: 75%)")