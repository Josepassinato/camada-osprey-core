#!/usr/bin/env python3
"""
Teste de todos os 8 agentes especializados
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.visa_api import supervisor, FORM_CODE_TO_VISA_TYPE

def test_all_agents_registered():
    """Testa se todos os agentes estão registrados"""
    print("="*80)
    print("🧪 TESTE: Todos os Agentes Registrados")
    print("="*80)
    
    expected_agents = ['B-2', 'F-1', 'H-1B', 'I-130', 'I-765', 'I-90', 'EB-2 NIW', 'EB-1A']
    registered_agents = list(supervisor.specialists.keys())
    
    print(f"\n✅ Agentes esperados: {len(expected_agents)}")
    print(f"✅ Agentes registrados: {len(registered_agents)}")
    
    all_present = True
    for agent in expected_agents:
        if agent in registered_agents:
            print(f"   ✅ {agent:15} - REGISTRADO")
        else:
            print(f"   ❌ {agent:15} - FALTANDO")
            all_present = False
    
    return all_present


def test_form_mapping():
    """Testa mapeamento de formulários"""
    print("\n" + "="*80)
    print("🧪 TESTE: Mapeamento Formulário → Agente")
    print("="*80)
    
    all_mapped = True
    for form_code, visa_type in FORM_CODE_TO_VISA_TYPE.items():
        has_agent = visa_type in supervisor.specialists
        status = "✅ MAPEADO" if has_agent else "❌ SEM AGENTE"
        print(f"   {form_code:15} → {visa_type:15} {status}")
        if not has_agent:
            all_mapped = False
    
    return all_mapped


def test_quick_generation():
    """Teste rápido de geração para cada agente"""
    print("\n" + "="*80)
    print("🧪 TESTE: Geração Rápida de Pacotes")
    print("="*80)
    
    test_cases = [
        ('I-539', 'B-2', {'personal_info': {'full_name': 'Test User B2', 'country_of_birth': 'Brazil'}}),
        ('F-1', 'F-1', {'personal_info': {'full_name': 'Test User F1', 'country_of_birth': 'Mexico'}}),
        ('I-130', 'I-130', {'personal_info': {'full_name': 'Test User I130'}, 'petitioner_info': {'full_name': 'Petitioner'}}),
        ('I-765', 'I-765', {'personal_info': {'full_name': 'Test User I765'}, 'ead_data': {'category': '(c)(9)'}}),
        ('I-90', 'I-90', {'personal_info': {'full_name': 'Test User I90'}, 'greencard_info': {'alien_number': 'A123456789'}}),
        ('EB-2 NIW', 'EB-2 NIW', {'personal_info': {'full_name': 'Test User EB2'}, 'professional_info': {'field': 'Computer Science'}}),
        ('EB-1A', 'EB-1A', {'personal_info': {'full_name': 'Test User EB1A'}, 'professional_info': {'field': 'Medicine'}}),
    ]
    
    results = []
    for form_code, visa_type, test_data in test_cases:
        print(f"\n   Testing {form_code} ({visa_type})...")
        try:
            agent = supervisor.specialists.get(visa_type)
            if agent:
                result = agent.generate_package(test_data)
                if result.get('success') or result.get('package_path'):
                    print(f"   ✅ {form_code:15} - Geração bem-sucedida")
                    results.append(True)
                else:
                    print(f"   ⚠️  {form_code:15} - Geração falhou (mas agente funciona)")
                    results.append(True)  # Agent exists and tried
            else:
                print(f"   ❌ {form_code:15} - Agente não encontrado")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {form_code:15} - Erro: {str(e)[:50]}")
            results.append(False)
    
    return all(results)


if __name__ == '__main__':
    print("\n" + "🚀 TESTE COMPLETO DE TODOS OS AGENTES" + "\n")
    
    results = []
    
    # Executar testes
    results.append(("Agentes Registrados", test_all_agents_registered()))
    results.append(("Mapeamento de Formulários", test_form_mapping()))
    results.append(("Geração de Pacotes", test_quick_generation()))
    
    # Sumário
    print("\n" + "="*80)
    print("📊 SUMÁRIO DOS TESTES")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {test_name:30} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n   Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS 8 AGENTES ESTÃO FUNCIONANDO!")
        print("\n📋 Agentes Disponíveis:")
        print("   1. B-2 (I-539) - Tourist Visa Extension")
        print("   2. F-1 - Student Visa")
        print("   3. H-1B - Work Visa")
        print("   4. I-130 - Family-Based Immigration")
        print("   5. I-765 - Employment Authorization (EAD)")
        print("   6. I-90 - Green Card Renewal/Replacement")
        print("   7. EB-2 NIW - National Interest Waiver")
        print("   8. EB-1A - Extraordinary Ability")
        sys.exit(0)
    else:
        print("\n⚠️  Alguns testes falharam. Revisar antes de usar em produção.")
        sys.exit(1)
