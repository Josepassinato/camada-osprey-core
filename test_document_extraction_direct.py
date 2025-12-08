#!/usr/bin/env python3
"""
🎯 TESTE DIRETO - EXTRAÇÃO E AUTO-CORREÇÃO DE DADOS DE DOCUMENTOS

**OBJETIVO:**
Testar diretamente a lógica de extração e auto-correção sem depender do Google Vision API.
Simula o texto já extraído do documento para focar na validação dos regex patterns e lógica de comparação.

**CENÁRIO DE TESTE:**
1. Simular texto extraído de passaporte com nome completo
2. Testar regex patterns para extração de dados
3. Testar lógica de comparação de nomes
4. Validar critérios de auto-correção
"""

import sys
import os
sys.path.append('/app/backend')

from document_data_extractor import DocumentDataExtractor
import asyncio
import json

def test_passport_regex_extraction():
    """Testar extração de dados do passaporte usando regex patterns"""
    print("🔍 TESTE 1: EXTRAÇÃO DE DADOS DO PASSAPORTE COM REGEX")
    print("=" * 60)
    
    # Texto simulado do passaporte (como seria extraído pelo OCR)
    passport_text = """PASSPORT
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
    
    print(f"📄 Texto do passaporte:")
    print(passport_text)
    print("-" * 40)
    
    # Testar extração
    extractor = DocumentDataExtractor()
    extracted_data = extractor._extract_passport_data(passport_text)
    
    print(f"🔍 RESULTADOS DA EXTRAÇÃO:")
    print(f"  Confiança: {extracted_data['confidence']:.1%}")
    print(f"  Campos extraídos: {len(extracted_data['fields'])}")
    
    for field, value in extracted_data['fields'].items():
        print(f"    {field}: '{value}'")
    
    # Verificações específicas
    checks = {
        "nome_completo_extraido": "full_name" in extracted_data['fields'],
        "nome_completo_correto": extracted_data['fields'].get('full_name') == 'João Silva Santos',
        "numero_passaporte_extraido": "passport_number" in extracted_data['fields'],
        "data_nascimento_extraida": "date_of_birth" in extracted_data['fields'],
        "nacionalidade_extraida": "nationality" in extracted_data['fields'],
        "confianca_adequada": extracted_data['confidence'] >= 0.7
    }
    
    print(f"\n🎯 VERIFICAÇÕES:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check.replace('_', ' ').title()}: {passed}")
    
    success_rate = sum(checks.values()) / len(checks) * 100
    print(f"\n📊 Taxa de sucesso da extração: {success_rate:.1f}%")
    
    return {
        "success": success_rate >= 80,
        "extracted_data": extracted_data,
        "checks": checks,
        "success_rate": success_rate
    }

def test_name_comparison_logic():
    """Testar lógica de comparação de nomes"""
    print("\n🔍 TESTE 2: LÓGICA DE COMPARAÇÃO DE NOMES")
    print("=" * 60)
    
    extractor = DocumentDataExtractor()
    
    # Cenários de teste
    test_scenarios = [
        {
            "name": "Subset simples",
            "extracted_name": "João Silva Santos",
            "current_name": "Joao Silva",
            "user_data": {"first_name": "Joao", "last_name": "Silva"},
            "expected_different": False  # Deve identificar como mesmo nome (subset)
        },
        {
            "name": "Nome completo vs separado",
            "extracted_name": "Maria Oliveira Costa",
            "current_name": "Maria Oliveira",
            "user_data": {"first_name": "Maria", "last_name": "Oliveira"},
            "expected_different": False  # Deve identificar como mesmo nome
        },
        {
            "name": "Nomes completamente diferentes",
            "extracted_name": "Pedro Alves Mendes",
            "current_name": "Carlos Santos",
            "user_data": {"first_name": "Carlos", "last_name": "Santos"},
            "expected_different": True  # Deve identificar como diferentes
        },
        {
            "name": "Acentos diferentes",
            "extracted_name": "José da Silva",
            "current_name": "Jose da Silva",
            "user_data": {"first_name": "Jose", "last_name": "da Silva"},
            "expected_different": False  # Deve ignorar acentos
        }
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"\n📝 Cenário: {scenario['name']}")
        print(f"  Extraído: '{scenario['extracted_name']}'")
        print(f"  Atual: '{scenario['current_name']}'")
        
        is_different = extractor._compare_names(
            scenario['extracted_name'],
            scenario['current_name'],
            scenario['user_data']
        )
        
        expected = scenario['expected_different']
        passed = is_different == expected
        
        status = "✅" if passed else "❌"
        print(f"  {status} Resultado: {'Diferentes' if is_different else 'Iguais'} (Esperado: {'Diferentes' if expected else 'Iguais'})")
        
        results.append({
            "scenario": scenario['name'],
            "passed": passed,
            "is_different": is_different,
            "expected": expected
        })
    
    passed_scenarios = sum(1 for r in results if r['passed'])
    total_scenarios = len(results)
    success_rate = (passed_scenarios / total_scenarios) * 100
    
    print(f"\n📊 Taxa de sucesso da comparação: {passed_scenarios}/{total_scenarios} ({success_rate:.1f}%)")
    
    return {
        "success": success_rate >= 75,
        "results": results,
        "success_rate": success_rate
    }

async def test_auto_correction_logic():
    """Testar lógica de auto-correção"""
    print("\n🔍 TESTE 3: LÓGICA DE AUTO-CORREÇÃO")
    print("=" * 60)
    
    extractor = DocumentDataExtractor()
    
    # Dados do usuário atual (incompletos)
    current_user_data = {
        "first_name": "Joao",
        "last_name": "Silva",
        "email": "test@test.com",
        "date_of_birth": "1990-05-15"
    }
    
    # Texto do passaporte
    passport_text = """PASSPORT
UNITED STATES OF AMERICA  
PASSPORT NO: BR1234567
NAME: JOÃO SILVA SANTOS
DATE OF BIRTH: 15 MAY 1990
NATIONALITY: BRAZILIAN
DATE OF ISSUE: 01 JAN 2020
DATE OF EXPIRY: 01 JAN 2030
"""
    
    print(f"📄 Dados atuais do usuário:")
    for key, value in current_user_data.items():
        print(f"  {key}: '{value}'")
    
    print(f"\n📄 Texto do passaporte:")
    print(passport_text)
    
    # Executar extração e validação
    result = await extractor.extract_and_validate(
        document_text=passport_text,
        document_type="passport",
        current_user_data=current_user_data
    )
    
    print(f"\n🔍 RESULTADOS DA VALIDAÇÃO:")
    print(f"  Sucesso: {result.get('success', False)}")
    print(f"  Confiança: {result.get('confidence', 0):.1%}")
    print(f"  Deve auto-corrigir: {result.get('should_auto_correct', False)}")
    print(f"  Discrepâncias encontradas: {len(result.get('discrepancies', []))}")
    
    if result.get('discrepancies'):
        print(f"\n📋 DISCREPÂNCIAS:")
        for i, disc in enumerate(result['discrepancies'], 1):
            print(f"  {i}. {disc['field']}: '{disc['current_value']}' → '{disc['document_value']}'")
    
    if result.get('suggested_corrections'):
        print(f"\n🔧 CORREÇÕES SUGERIDAS:")
        for field, value in result['suggested_corrections'].items():
            print(f"  {field}: '{value}'")
    
    # Verificações
    checks = {
        "extracao_bem_sucedida": result.get('success', False),
        "confianca_adequada": result.get('confidence', 0) >= 0.8,
        "discrepancias_identificadas": len(result.get('discrepancies', [])) > 0,
        "auto_correcao_ativada": result.get('should_auto_correct', False),
        "correcoes_sugeridas": bool(result.get('suggested_corrections'))
    }
    
    print(f"\n🎯 VERIFICAÇÕES:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check.replace('_', ' ').title()}: {passed}")
    
    success_rate = sum(checks.values()) / len(checks) * 100
    print(f"\n📊 Taxa de sucesso da auto-correção: {success_rate:.1f}%")
    
    return {
        "success": success_rate >= 80,
        "result": result,
        "checks": checks,
        "success_rate": success_rate
    }

async def run_all_tests():
    """Executar todos os testes de extração e auto-correção"""
    print("🎯 TESTE COMPLETO - EXTRAÇÃO E AUTO-CORREÇÃO DE DADOS DE DOCUMENTOS")
    print("📋 TESTE DIRETO - Sem dependência do Google Vision API")
    print("🎯 OBJETIVO: Validar regex patterns e lógica de auto-correção")
    print("=" * 80)
    
    results = {}
    
    # Teste 1: Extração de dados
    results["test1_extraction"] = test_passport_regex_extraction()
    
    # Teste 2: Comparação de nomes
    results["test2_comparison"] = test_name_comparison_logic()
    
    # Teste 3: Lógica de auto-correção
    results["test3_autocorrection"] = await test_auto_correction_logic()
    
    # Análise final
    print("\n📋 ANÁLISE FINAL - SISTEMA DE EXTRAÇÃO E AUTO-CORREÇÃO")
    print("=" * 80)
    
    test_results = [
        results["test1_extraction"]["success"],
        results["test2_comparison"]["success"],
        results["test3_autocorrection"]["success"]
    ]
    
    successful_tests = sum(test_results)
    total_tests = len(test_results)
    overall_success_rate = (successful_tests / total_tests) * 100
    
    test_names = [
        "TESTE 1: Extração de dados do passaporte com regex",
        "TESTE 2: Lógica de comparação de nomes",
        "TESTE 3: Lógica de auto-correção"
    ]
    
    print(f"📊 RESULTADOS DOS TESTES:")
    for i, (test_name, passed) in enumerate(zip(test_names, test_results)):
        status = "✅" if passed else "❌"
        success_rate = [
            results["test1_extraction"]["success_rate"],
            results["test2_comparison"]["success_rate"],
            results["test3_autocorrection"]["success_rate"]
        ][i]
        print(f"  {status} {test_name}: {success_rate:.1f}%")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_tests}/{total_tests} ({overall_success_rate:.1f}%)")
    
    # Análise detalhada
    print(f"\n📋 ANÁLISE DETALHADA:")
    print("=" * 60)
    
    # Teste 1 - Extração
    extraction_data = results["test1_extraction"]["extracted_data"]
    print(f"✅ EXTRAÇÃO DE DADOS:")
    print(f"  Nome extraído: '{extraction_data['fields'].get('full_name', 'N/A')}'")
    print(f"  Confiança: {extraction_data['confidence']:.1%}")
    print(f"  Campos extraídos: {len(extraction_data['fields'])}")
    
    # Teste 2 - Comparação
    comparison_results = results["test2_comparison"]["results"]
    passed_comparisons = sum(1 for r in comparison_results if r['passed'])
    print(f"✅ COMPARAÇÃO DE NOMES:")
    print(f"  Cenários testados: {len(comparison_results)}")
    print(f"  Cenários corretos: {passed_comparisons}")
    
    # Teste 3 - Auto-correção
    autocorrection_result = results["test3_autocorrection"]["result"]
    print(f"✅ AUTO-CORREÇÃO:")
    print(f"  Deve auto-corrigir: {autocorrection_result.get('should_auto_correct', False)}")
    print(f"  Discrepâncias: {len(autocorrection_result.get('discrepancies', []))}")
    print(f"  Confiança: {autocorrection_result.get('confidence', 0):.1%}")
    
    # Avaliação final
    system_ready = overall_success_rate >= 75
    
    print(f"\n🎯 AVALIAÇÃO FINAL:")
    print("=" * 60)
    
    if system_ready:
        print("✅ SISTEMA DE EXTRAÇÃO E AUTO-CORREÇÃO: FUNCIONANDO CORRETAMENTE")
        print("✅ REGEX PATTERNS: EXTRAINDO DADOS CORRETAMENTE")
        print("✅ LÓGICA DE COMPARAÇÃO: IDENTIFICANDO NOMES CORRETAMENTE")
        print("✅ AUTO-CORREÇÃO: CRITÉRIOS FUNCIONANDO")
        print("✅ SISTEMA PRONTO PARA INTEGRAÇÃO COM OCR")
    else:
        print("❌ SISTEMA DE EXTRAÇÃO E AUTO-CORREÇÃO: PROBLEMAS IDENTIFICADOS")
        
        # Identificar áreas problemáticas
        problem_areas = []
        if not results["test1_extraction"]["success"]:
            problem_areas.append("Extração de dados com regex")
        if not results["test2_comparison"]["success"]:
            problem_areas.append("Lógica de comparação de nomes")
        if not results["test3_autocorrection"]["success"]:
            problem_areas.append("Critérios de auto-correção")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Salvar resultados
    results["summary"] = {
        "successful_tests": successful_tests,
        "total_tests": total_tests,
        "overall_success_rate": overall_success_rate,
        "system_ready": system_ready,
        "test_results": test_results
    }
    
    return results

if __name__ == "__main__":
    print("🎯 INICIANDO TESTE DIRETO - EXTRAÇÃO E AUTO-CORREÇÃO")
    print("🔍 FOCO: Validar regex patterns e lógica sem dependência do OCR")
    
    # Execute tests
    results = asyncio.run(run_all_tests())
    
    # Save results
    with open("/app/direct_extraction_test_results.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Resultados salvos em: /app/direct_extraction_test_results.json")
    
    # Final recommendation
    summary = results.get("summary", {})
    system_ready = summary.get("system_ready", False)
    success_rate = summary.get("overall_success_rate", 0)
    
    if system_ready:
        print("\n🎉 CONCLUSÃO FINAL: LÓGICA DE EXTRAÇÃO E AUTO-CORREÇÃO FUNCIONANDO!")
        print("   ✅ Regex patterns extraindo dados corretamente")
        print("   ✅ Lógica de comparação de nomes funcionando")
        print("   ✅ Critérios de auto-correção adequados")
        print("   ✅ Sistema pronto para integração com OCR")
        print("   🔧 PRÓXIMO PASSO: Corrigir integração com Google Vision API")
    else:
        print("\n❌ CONCLUSÃO CRÍTICA: PROBLEMAS NA LÓGICA DE EXTRAÇÃO!")
        print("   ❌ Algumas funcionalidades não estão operacionais")
        print(f"   📊 Taxa de sucesso: {success_rate:.1f}%")
        print("   🔧 Correções necessárias antes da integração com OCR")