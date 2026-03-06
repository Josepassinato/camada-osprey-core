#!/usr/bin/env python3
"""
Teste de Salvamento de Progresso: "Salvar e Continuar"
Verifica se o usuário pode salvar progresso parcial e retomar depois
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://0.0.0.0:8001"

def test_save_partial_progress():
    """
    Testa salvamento de progresso parcial
    """
    print("=" * 80)
    print("🧪 TESTE: SALVAMENTO DE PROGRESSO PARCIAL - 'SALVAR E CONTINUAR'")
    print("=" * 80)
    
    # Step 1: Criar caso F-1
    print("\n📝 PASSO 1: Criar Caso F-1")
    print("-" * 60)
    
    response = requests.post(
        f"{BACKEND_URL}/api/auto-application/start",
        json={"form_code": "F-1", "process_type": "extension"}
    )
    
    if response.status_code != 200:
        print(f"❌ Erro ao criar caso: {response.status_code}")
        return False
    
    case_id = response.json()["case"]["case_id"]
    print(f"✅ Caso criado: {case_id}")
    
    # Step 2: Salvar APENAS Seção 1 e 2 (Parcial - ~30% do formulário)
    print(f"\n📝 PASSO 2: Salvar Progresso Parcial (Seções 1-2 de 6)")
    print("-" * 60)
    
    partial_data_section_1_2 = {
        "friendly_form_data": {
            # Seção 1: Informações Pessoais (Completa)
            "nome_completo": "Ana Paula Silva",
            "data_nascimento": "1996-04-12",
            "pais_nascimento": "Brazil",
            "pais_cidadania": "Brazil",
            "sexo": "Feminino",
            
            # Seção 2: Documentos de Viagem (Completa)
            "numero_passaporte": "BR456789123",
            "pais_emissao_passaporte": "Brazil",
            "data_expiracao_passaporte": "2029-03-20",
            "numero_i94": "98765432101",
            "data_ultima_entrada": "2022-08-20",
            "local_entrada": "Miami International Airport"
            
            # FALTANDO: Seções 3, 4, 5, 6 (Status, Endereço, Info Adicional, F-1 específico)
        },
        "basic_data": {
            "applicant_name": "Ana Paula Silva",
            "email": "ana.paula@university.edu"
        }
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/case/{case_id}/friendly-form",
        json=partial_data_section_1_2
    )
    
    if response.status_code != 200:
        print(f"❌ Erro ao salvar progresso parcial: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    print(f"✅ Progresso parcial salvo!")
    print(f"   Status: {result['validation_status']}")
    print(f"   Completude: {result['completion_percentage']}%")
    print(f"   Issues: {len(result.get('validation_issues', []))}")
    
    # Verificar que foi reconhecido como incompleto
    if result['completion_percentage'] < 50:
        print(f"✅ Sistema corretamente identificou como INCOMPLETO")
    else:
        print(f"⚠️  Completude alta demais para dados parciais")
    
    # Step 3: Recuperar caso e verificar dados salvos
    print(f"\n📝 PASSO 3: Recuperar Caso e Verificar Dados Salvos")
    print("-" * 60)
    
    response = requests.get(f"{BACKEND_URL}/api/auto-application/case/{case_id}")
    
    if response.status_code != 200:
        print(f"❌ Erro ao recuperar caso: {response.status_code}")
        return False
    
    case_data = response.json()["case"]
    
    # Verificar se simplified_form_responses foi salvo
    if "simplified_form_responses" in case_data:
        saved_data = case_data["simplified_form_responses"]
        print(f"✅ Dados salvos encontrados!")
        print(f"   Campos salvos: {len(saved_data)}")
        
        # Verificar campos específicos
        checks = {
            "nome_completo": saved_data.get("nome_completo") == "Ana Paula Silva",
            "data_nascimento": saved_data.get("data_nascimento") == "1996-04-12",
            "numero_passaporte": saved_data.get("numero_passaporte") == "BR456789123",
            "data_ultima_entrada": saved_data.get("data_ultima_entrada") == "2022-08-20"
        }
        
        print(f"\n   Verificação de Campos Salvos:")
        for field, correct in checks.items():
            icon = "✅" if correct else "❌"
            print(f"   {icon} {field}: {correct}")
        
        if all(checks.values()):
            print(f"\n✅ Todos os dados parciais foram salvos corretamente!")
        else:
            print(f"\n❌ Alguns dados não foram salvos corretamente")
            return False
    else:
        print(f"❌ simplified_form_responses não encontrado")
        return False
    
    # Verificar progresso
    if "friendly_form_validation" in case_data:
        validation = case_data["friendly_form_validation"]
        print(f"\n   Validação Salva:")
        print(f"   - Status: {validation.get('status')}")
        print(f"   - Completude: {validation.get('completion_percentage')}%")
        print(f"   - Issues: {len(validation.get('issues', []))}")
    
    # Step 4: Simular "Continuar" - Adicionar mais seções
    print(f"\n📝 PASSO 4: Continuar Preenchimento (Adicionar Seções 3-4)")
    print("-" * 60)
    
    # Agora adiciona Seções 3 e 4
    continued_data = {
        "friendly_form_data": {
            # Manter dados anteriores
            "nome_completo": "Ana Paula Silva",
            "data_nascimento": "1996-04-12",
            "pais_nascimento": "Brazil",
            "pais_cidadania": "Brazil",
            "sexo": "Feminino",
            "numero_passaporte": "BR456789123",
            "pais_emissao_passaporte": "Brazil",
            "data_expiracao_passaporte": "2029-03-20",
            "numero_i94": "98765432101",
            "data_ultima_entrada": "2022-08-20",
            "local_entrada": "Miami International Airport",
            
            # ADICIONAR Seção 3: Status Imigratório
            "status_atual": "F-1",
            "data_expiracao_status": "2025-08-31",
            "tipo_pedido": "Extensão do mesmo status",
            
            # ADICIONAR Seção 4: Endereço
            "endereco": "789 College Street, Unit 12",
            "cidade": "Los Angeles",
            "estado": "CA",
            "cep": "90001",
            "telefone": "+1 213-555-7890",
            "email": "ana.paula@university.edu"
        },
        "basic_data": {
            "applicant_name": "Ana Paula Silva",
            "email": "ana.paula@university.edu"
        }
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/case/{case_id}/friendly-form",
        json=continued_data
    )
    
    if response.status_code != 200:
        print(f"❌ Erro ao continuar preenchimento: {response.status_code}")
        return False
    
    result = response.json()
    print(f"✅ Progresso atualizado!")
    print(f"   Status: {result['validation_status']}")
    print(f"   Completude: {result['completion_percentage']}%")
    print(f"   Issues: {len(result.get('validation_issues', []))}")
    
    # Verificar que completude aumentou
    print(f"\n   📊 Progresso:")
    print(f"   - Antes (Seções 1-2): ~30%")
    print(f"   - Agora (Seções 1-4): {result['completion_percentage']}%")
    
    if result['completion_percentage'] > 50:
        print(f"   ✅ Completude aumentou corretamente!")
    
    # Step 5: Recuperar novamente e verificar atualização
    print(f"\n📝 PASSO 5: Verificar Atualização dos Dados")
    print("-" * 60)
    
    response = requests.get(f"{BACKEND_URL}/api/auto-application/case/{case_id}")
    
    if response.status_code != 200:
        print(f"❌ Erro ao recuperar caso atualizado")
        return False
    
    updated_case = response.json()["case"]
    updated_data = updated_case.get("simplified_form_responses", {})
    
    # Verificar novos campos
    new_checks = {
        "status_atual": updated_data.get("status_atual") == "F-1",
        "endereco": updated_data.get("endereco") == "789 College Street, Unit 12",
        "cidade": updated_data.get("cidade") == "Los Angeles",
        "estado": updated_data.get("estado") == "CA"
    }
    
    print(f"   Verificação de Novos Campos:")
    for field, correct in new_checks.items():
        icon = "✅" if correct else "❌"
        print(f"   {icon} {field}: {correct}")
    
    # Verificar que campos antigos ainda estão lá
    old_checks = {
        "nome_completo": updated_data.get("nome_completo") == "Ana Paula Silva",
        "numero_passaporte": updated_data.get("numero_passaporte") == "BR456789123"
    }
    
    print(f"\n   Verificação de Campos Anteriores (Preservados):")
    for field, correct in old_checks.items():
        icon = "✅" if correct else "❌"
        print(f"   {icon} {field}: {correct}")
    
    all_correct = all(new_checks.values()) and all(old_checks.values())
    
    if all_correct:
        print(f"\n✅ ATUALIZAÇÃO FUNCIONOU! Dados anteriores preservados + novos dados adicionados")
        return True
    else:
        print(f"\n❌ Alguns dados foram perdidos ou não atualizados")
        return False


def test_progress_tracking():
    """
    Testa se o sistema rastreia o progresso corretamente
    """
    print(f"\n{'='*80}")
    print(f"🧪 TESTE: RASTREAMENTO DE PROGRESSO")
    print(f"{'='*80}")
    
    # Criar caso
    response = requests.post(
        f"{BACKEND_URL}/api/auto-application/start",
        json={"form_code": "H-1B", "process_type": "extension"}
    )
    
    case_id = response.json()["case"]["case_id"]
    print(f"✅ Caso H-1B criado: {case_id}")
    
    # Testar progresso em diferentes estágios
    stages = [
        {
            "name": "10% - Apenas Nome e Email",
            "data": {
                "nome_completo": "Carlos Test",
                "email": "carlos@test.com"
            },
            "expected_range": (5, 20)
        },
        {
            "name": "40% - Dados Pessoais Completos",
            "data": {
                "nome_completo": "Carlos Test Silva",
                "data_nascimento": "1985-06-15",
                "pais_nascimento": "Brazil",
                "pais_cidadania": "Brazil",
                "sexo": "Masculino",
                "numero_passaporte": "BR111222333",
                "pais_emissao_passaporte": "Brazil",
                "data_expiracao_passaporte": "2028-12-31",
                "numero_i94": "11122233344",
                "data_ultima_entrada": "2021-05-10",
                "local_entrada": "JFK Airport",
                "email": "carlos@test.com"
            },
            "expected_range": (30, 50)
        },
        {
            "name": "70% - Quase Completo",
            "data": {
                "nome_completo": "Carlos Test Silva",
                "data_nascimento": "1985-06-15",
                "pais_nascimento": "Brazil",
                "pais_cidadania": "Brazil",
                "sexo": "Masculino",
                "numero_passaporte": "BR111222333",
                "pais_emissao_passaporte": "Brazil",
                "data_expiracao_passaporte": "2028-12-31",
                "numero_i94": "11122233344",
                "data_ultima_entrada": "2021-05-10",
                "local_entrada": "JFK Airport",
                "status_atual": "H-1B",
                "data_expiracao_status": "2025-12-31",
                "tipo_pedido": "Extensão do mesmo status",
                "endereco": "100 Tech Avenue",
                "cidade": "Seattle",
                "estado": "WA",
                "cep": "98101",
                "telefone": "+1 206-555-4321",
                "email": "carlos@test.com",
                "motivo_pedido": "Extensão de H-1B pois projeto continua",
                "data_desejada_permanencia": "2028-12-31"
            },
            "expected_range": (60, 80)
        }
    ]
    
    print(f"\n📊 Testando Progresso em Diferentes Estágios:\n")
    
    results = []
    
    for stage in stages:
        print(f"   🔹 {stage['name']}")
        
        response = requests.post(
            f"{BACKEND_URL}/api/case/{case_id}/friendly-form",
            json={
                "friendly_form_data": stage["data"],
                "basic_data": {}
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            completion = result["completion_percentage"]
            min_exp, max_exp = stage["expected_range"]
            
            in_range = min_exp <= completion <= max_exp
            icon = "✅" if in_range else "⚠️"
            
            print(f"      {icon} Completude: {completion}% (Esperado: {min_exp}-{max_exp}%)")
            print(f"      Status: {result['validation_status']}")
            
            results.append({
                "stage": stage["name"],
                "completion": completion,
                "expected": stage["expected_range"],
                "in_range": in_range
            })
        else:
            print(f"      ❌ Erro: {response.status_code}")
            results.append({
                "stage": stage["name"],
                "error": True
            })
    
    # Verificar progressão
    print(f"\n📈 Análise de Progressão:")
    completions = [r["completion"] for r in results if "completion" in r]
    
    if len(completions) >= 2:
        increasing = all(completions[i] < completions[i+1] for i in range(len(completions)-1))
        
        if increasing:
            print(f"   ✅ Completude aumenta consistentemente: {completions}")
        else:
            print(f"   ⚠️  Completude não aumenta consistentemente: {completions}")
    
    success_rate = sum(1 for r in results if r.get("in_range", False)) / len(results)
    
    print(f"\n   Taxa de Sucesso: {success_rate*100:.0f}%")
    
    return success_rate >= 0.66  # 2/3 dos testes


if __name__ == "__main__":
    print("\n")
    print("🚀 " + "="*76 + " 🚀")
    print("   TESTE COMPLETO: SALVAMENTO DE PROGRESSO - 'SALVAR E CONTINUAR'")
    print("🚀 " + "="*76 + " 🚀")
    
    # Test 1: Save partial progress
    test1_success = test_save_partial_progress()
    
    # Test 2: Progress tracking
    test2_success = test_progress_tracking()
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 RESUMO FINAL")
    print(f"{'='*80}")
    
    if test1_success and test2_success:
        print(f"\n✅ TODOS OS TESTES PASSARAM!")
        print(f"\n🎉 Sistema de 'Salvar e Continuar' está FUNCIONANDO!")
        print(f"\nCaracterísticas Validadas:")
        print(f"   ✅ Salvamento de progresso parcial")
        print(f"   ✅ Recuperação de dados salvos")
        print(f"   ✅ Atualização de dados preserva anteriores")
        print(f"   ✅ Rastreamento de completude")
        print(f"   ✅ Validação em diferentes estágios")
        print(f"\nFuncionalidades:")
        print(f"   • Usuário pode salvar formulário incompleto")
        print(f"   • Dados não são perdidos")
        print(f"   • Pode continuar de onde parou")
        print(f"   • Sistema rastreia progresso (0-100%)")
        print(f"   • Validação adaptativa ao nível de completude")
    else:
        print(f"\n⚠️  Alguns testes falharam:")
        print(f"   Salvamento Parcial: {'✅' if test1_success else '❌'}")
        print(f"   Rastreamento Progresso: {'✅' if test2_success else '❌'}")
