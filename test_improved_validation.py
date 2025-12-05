#!/usr/bin/env python3
"""
Test script for improved AI validation
Tests the enhanced validation system with programmatic + AI validation
"""

import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://0.0.0.0:8001"

def test_validation_scenarios():
    """Test multiple validation scenarios"""
    
    print("=" * 80)
    print("🧪 TESTE DE VALIDAÇÃO IA MELHORADA")
    print("=" * 80)
    
    scenarios = [
        {
            "name": "Dados 100% Completos",
            "data": {
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
                    "motivo_mudanca": "Consegui emprego após conclusão dos estudos na minha área de formação",
                    "data_entrada_eua": "2020-08-15",
                    "numero_i94": "1234567890"
                },
                "basic_data": {
                    "applicant_name": "Carlos Eduardo Silva Mendes",
                    "email": "carlos.teste@test.com"
                }
            },
            "expected_completion": ">= 90",
            "expected_status": "approved"
        },
        {
            "name": "Dados 50% Completos",
            "data": {
                "friendly_form_data": {
                    "nome_completo": "Maria Santos Silva",
                    "data_nascimento": "1990-05-15",
                    "email": "maria@test.com",
                    "numero_passaporte": "BR123456789",
                    "pais_nascimento": "Brazil",
                    "status_atual": "F-1",
                    "status_solicitado": "H-1B"
                    # Faltando: endereco, cidade, estado, cep, telefone, data_entrada_eua, numero_i94, motivo_mudanca
                },
                "basic_data": {}
            },
            "expected_completion": "40-60",
            "expected_status": "rejected or needs_review"
        },
        {
            "name": "Dados Mínimos (20%)",
            "data": {
                "friendly_form_data": {
                    "nome_completo": "João Silva",
                    "email": "joao@test.com"
                    # Faltando quase tudo
                },
                "basic_data": {}
            },
            "expected_completion": "< 30",
            "expected_status": "rejected"
        },
        {
            "name": "Dados com Erros de Formato",
            "data": {
                "friendly_form_data": {
                    "nome_completo": "Ana Costa",
                    "data_nascimento": "15/03/1992",  # Formato errado
                    "email": "ana.costa",  # Email inválido
                    "telefone": "abc-def-ghij",  # Telefone inválido
                    "numero_passaporte": "BR123",  # Muito curto
                    "pais_nascimento": "Brazil",
                    "endereco": "123 Main Street",
                    "cidade": "New York",
                    "estado": "NY",
                    "cep": "10001",
                    "status_atual": "F-1",
                    "status_solicitado": "H-1B",
                    "data_entrada_eua": "2020-08-15",
                    "numero_i94": "abcd"  # Deve ser numérico
                },
                "basic_data": {}
            },
            "expected_completion": "60-80",
            "expected_status": "needs_review"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"📋 CENÁRIO {i}: {scenario['name']}")
        print(f"{'='*80}")
        
        # Create test case
        print(f"🔧 Criando caso de teste I-539...")
        case_response = requests.post(
            f"{BACKEND_URL}/api/auto-application/start",
            json={"form_code": "I-539", "process_type": "change_of_status"}
        )
        
        if case_response.status_code != 200:
            print(f"❌ Falha ao criar caso: {case_response.status_code}")
            continue
        
        case_id = case_response.json()["case"]["case_id"]
        print(f"✅ Caso criado: {case_id}")
        
        # Submit friendly form
        print(f"\n🔍 Testando validação...")
        response = requests.post(
            f"{BACKEND_URL}/api/case/{case_id}/friendly-form",
            json=scenario["data"]
        )
        
        if response.status_code == 200:
            result = response.json()
            
            validation_status = result.get("validation_status")
            completion = result.get("completion_percentage", 0)
            issues = result.get("validation_issues", [])
            missing_fields = result.get("missing_fields", [])
            
            print(f"\n📊 RESULTADOS:")
            print(f"   ✓ Status: {validation_status}")
            print(f"   ✓ Completude: {completion}%")
            print(f"   ✓ Issues Detectados: {len(issues)}")
            print(f"   ✓ Campos Faltando: {len(missing_fields)}")
            
            if issues:
                print(f"\n⚠️  Problemas Detectados ({len(issues)}):")
                for issue in issues[:5]:  # Show first 5
                    severity_icon = "🔴" if issue.get("severity") == "error" else "🟡" if issue.get("severity") == "warning" else "🔵"
                    print(f"   {severity_icon} {issue.get('field_label', issue.get('field'))}: {issue.get('issue')}")
            
            if missing_fields:
                print(f"\n❌ Campos Faltando ({len(missing_fields)}):")
                for field in missing_fields[:5]:  # Show first 5
                    print(f"   - {field}")
            
            # Check expectations
            print(f"\n✅ VALIDAÇÃO DO TESTE:")
            print(f"   Esperado: Status = {scenario['expected_status']}, Completude = {scenario['expected_completion']}")
            
            status_correct = scenario['expected_status'].lower() in validation_status.lower() or validation_status.lower() in scenario['expected_status'].lower()
            
            # Parse completion expectation
            if ">=" in scenario['expected_completion']:
                min_completion = int(scenario['expected_completion'].split(">=")[1].strip())
                completion_correct = completion >= min_completion
            elif "<" in scenario['expected_completion']:
                max_completion = int(scenario['expected_completion'].split("<")[1].strip())
                completion_correct = completion < max_completion
            elif "-" in scenario['expected_completion']:
                min_c, max_c = map(int, scenario['expected_completion'].split("-"))
                completion_correct = min_c <= completion <= max_c
            else:
                completion_correct = True
            
            status_icon = "✅" if status_correct else "❌"
            completion_icon = "✅" if completion_correct else "❌"
            
            print(f"   {status_icon} Status: {'CORRETO' if status_correct else 'INCORRETO'}")
            print(f"   {completion_icon} Completude: {'CORRETO' if completion_correct else 'INCORRETO'}")
            
            results.append({
                "scenario": scenario['name'],
                "status_correct": status_correct,
                "completion_correct": completion_correct,
                "validation_status": validation_status,
                "completion_percentage": completion,
                "issues_count": len(issues)
            })
        else:
            print(f"❌ Erro na validação: {response.status_code}")
            print(response.text)
            results.append({
                "scenario": scenario['name'],
                "status_correct": False,
                "completion_correct": False,
                "error": response.text
            })
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 RESUMO GERAL")
    print(f"{'='*80}")
    
    total_scenarios = len(results)
    passed_scenarios = sum(1 for r in results if r.get('status_correct') and r.get('completion_correct'))
    
    print(f"\n✅ Cenários Passados: {passed_scenarios}/{total_scenarios}")
    
    for result in results:
        icon = "✅" if result.get('status_correct') and result.get('completion_correct') else "❌"
        print(f"   {icon} {result['scenario']}")
        if 'validation_status' in result:
            print(f"      → Status: {result['validation_status']}, Completude: {result['completion_percentage']}%, Issues: {result['issues_count']}")
    
    if passed_scenarios == total_scenarios:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! Validação IA está funcionando perfeitamente!")
    elif passed_scenarios >= total_scenarios * 0.75:
        print(f"\n✅ Maioria dos testes passou. Sistema funcionando bem!")
    else:
        print(f"\n⚠️ Alguns testes falharam. Validação precisa de ajustes.")
    
    return results

if __name__ == "__main__":
    test_validation_scenarios()
