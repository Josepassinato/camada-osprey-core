#!/usr/bin/env python3
"""
Script de teste para integração dos agentes com jornada do usuário
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from backend.visa_api import transform_case_data_for_agent, generate_package_from_case, FORM_CODE_TO_VISA_TYPE

def test_data_transformation():
    """Testa transformação de dados"""
    print("="*80)
    print("🧪 TESTE 1: Transformação de Dados")
    print("="*80)
    
    # Simular dados do caso como viriam do MongoDB
    mock_case_data = {
        'case_id': 'TEST-001',
        'form_code': 'I-539',  # B-2 Extension
        'process_type': 'change_of_status',
        'basic_data': {
            'firstName': 'João',
            'middleName': 'Carlos',
            'lastName': 'Silva',
            'dateOfBirth': '1990-05-15',
            'countryOfBirth': 'Brazil',
            'gender': 'Male',
            'currentAddress': '123 Main St, Apt 4B',
            'city': 'Miami',
            'state': 'FL',
            'zipCode': '33101',
            'phoneNumber': '+1-305-555-1234',
            'email': 'joao.silva@email.com',
            'alienNumber': 'A123456789',
            'socialSecurityNumber': '',
            'currentStatus': 'B-2',
            'statusExpiration': '2025-08-15'
        },
        'simplified_form_responses': {
            'extension_reason': 'I would like to extend my tourist visa to visit more national parks and spend additional time with my family in the United States.',
            'requested_duration': '6 months',
            'arrival_date': '2025-02-15'
        },
        'user_story_text': 'I arrived in the United States as a tourist and have been enjoying my visit. I would like to extend my stay to complete my travel plans and spend more time with my relatives who live here.'
    }
    
    try:
        # Testar transformação
        transformed = transform_case_data_for_agent(mock_case_data)
        
        print("\n✅ Transformação bem-sucedida!")
        print(f"   Visa Type: {transformed['visa_type']}")
        print(f"   Applicant Name: {transformed['applicant_data']['personal_info']['full_name']}")
        print(f"   Country: {transformed['applicant_data']['personal_info']['country_of_birth']}")
        print(f"   Extension Reason: {transformed['applicant_data'].get('extension_details', {}).get('reason_for_extension', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"\n❌ Erro na transformação: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_mapping():
    """Testa mapeamento de formulários para agentes"""
    print("\n" + "="*80)
    print("🧪 TESTE 2: Mapeamento Formulário → Agente")
    print("="*80)
    
    for form_code, visa_type in FORM_CODE_TO_VISA_TYPE.items():
        status = "✅ DISPONÍVEL" if visa_type in ['B-2', 'F-1', 'H-1B'] else "⏳ PENDENTE"
        print(f"   {form_code:15} → {visa_type:15} {status}")
    
    return True


def test_b2_package_generation():
    """Testa geração de pacote B-2"""
    print("\n" + "="*80)
    print("🧪 TESTE 3: Geração de Pacote B-2")
    print("="*80)
    
    mock_case_data = {
        'case_id': 'TEST-B2-001',
        'form_code': 'I-539',
        'basic_data': {
            'firstName': 'Maria',
            'middleName': 'Luiza',
            'lastName': 'Santos',
            'dateOfBirth': '1985-03-20',
            'countryOfBirth': 'Portugal',
            'gender': 'Female',
            'currentAddress': '456 Ocean Drive',
            'city': 'Los Angeles',
            'state': 'CA',
            'zipCode': '90001',
            'phoneNumber': '+1-213-555-5678',
            'email': 'maria.santos@email.com',
            'currentStatus': 'B-2',
            'statusExpiration': '2025-09-01'
        },
        'simplified_form_responses': {
            'extension_reason': 'Medical treatment and family support',
            'requested_duration': '6 months',
            'arrival_date': '2025-03-01'
        },
        'user_story_text': 'I am visiting the United States for medical treatment and would like to extend my stay to complete my treatment and recovery with family support.'
    }
    
    try:
        print("\n📝 Gerando pacote B-2...")
        result = generate_package_from_case(mock_case_data, enable_qa=True)
        
        if result.get('success'):
            print("\n✅ Pacote B-2 gerado com sucesso!")
            print(f"   Visa Type: {result.get('visa_type')}")
            print(f"   Package Path: {result.get('package_result', {}).get('output_pdf')}")
            print(f"   Pages: {result.get('package_result', {}).get('pages', 0)}")
            print(f"   Size: {result.get('package_result', {}).get('size_kb', 0):.2f} KB")
            
            if result.get('qa_report'):
                print(f"   QA Score: {result['qa_report'].get('overall_score', 'N/A')}")
            
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
            return True
        else:
            print(f"\n❌ Erro ao gerar pacote: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Exceção durante geração: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_f1_package_generation():
    """Testa geração de pacote F-1"""
    print("\n" + "="*80)
    print("🧪 TESTE 4: Geração de Pacote F-1")
    print("="*80)
    
    mock_case_data = {
        'case_id': 'TEST-F1-001',
        'form_code': 'F-1',
        'basic_data': {
            'firstName': 'Carlos',
            'middleName': 'Alberto',
            'lastName': 'Rodriguez',
            'dateOfBirth': '2002-07-10',
            'countryOfBirth': 'Mexico',
            'gender': 'Male',
            'currentAddress': '789 University Ave',
            'city': 'Boston',
            'state': 'MA',
            'zipCode': '02101',
            'phoneNumber': '+1-617-555-9999',
            'email': 'carlos.rodriguez@email.com',
        },
        'simplified_form_responses': {
            'school_name': 'Massachusetts Institute of Technology',
            'program_name': 'Computer Science',
            'degree_level': 'Bachelor',
            'program_start_date': '2025-09-01',
            'program_end_date': '2029-05-31',
            'sevis_id': 'N0012345678',
            'i20_issue_date': '2025-04-15',
            'funding_source': 'Personal and family funds',
            'annual_expenses': '$75,000'
        },
        'user_story_text': 'I have been accepted to study Computer Science at MIT. This has been my dream for many years and I am fully prepared academically and financially.'
    }
    
    try:
        print("\n📝 Gerando pacote F-1...")
        result = generate_package_from_case(mock_case_data, enable_qa=True)
        
        if result.get('success'):
            print("\n✅ Pacote F-1 gerado com sucesso!")
            print(f"   Visa Type: {result.get('visa_type')}")
            print(f"   School: {mock_case_data['simplified_form_responses']['school_name']}")
            print(f"   Package Path: {result.get('package_result', {}).get('output_pdf')}")
            print(f"   Pages: {result.get('package_result', {}).get('pages', 0)}")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
            return True
        else:
            print(f"\n❌ Erro ao gerar pacote: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Exceção durante geração: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n" + "🚀 TESTE DE INTEGRAÇÃO DOS AGENTES" + "\n")
    
    results = []
    
    # Executar testes
    results.append(("Transformação de Dados", test_data_transformation()))
    results.append(("Mapeamento de Formulários", test_agent_mapping()))
    results.append(("Geração Pacote B-2", test_b2_package_generation()))
    results.append(("Geração Pacote F-1", test_f1_package_generation()))
    
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
        print("\n🎉 Todos os testes passaram! Sistema pronto para uso.")
        sys.exit(0)
    else:
        print("\n⚠️  Alguns testes falharam. Revisar antes de usar em produção.")
        sys.exit(1)
