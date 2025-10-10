#!/usr/bin/env python3
"""
TESTE SIMPLES DOS ENDPOINTS AI REVIEW
Teste focado nos endpoints específicos solicitados pelo usuário
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_ai_review_endpoints():
    """Teste simples dos endpoints AI Review"""
    
    print("🚀 TESTE SIMPLES DOS ENDPOINTS AI REVIEW")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'AIReviewTester/1.0'
    })
    
    # TESTE 1: Formulário Incompleto
    print("\n❌ TESTE 1: Formulário Incompleto")
    
    incomplete_form = {
        "case_id": "TEST-INCOMPLETE-001",
        "form_responses": {
            "personal": {
                "full_name": "João Silva"
                # Faltando campos obrigatórios
            },
            "address": {
                "city": "São Paulo"
                # Faltando campos obrigatórios
            }
        },
        "visa_type": "H-1B"
    }
    
    try:
        response = session.post(f"{API_BASE}/ai-review/validate-completeness", json=incomplete_form)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            validation = result.get('validation_result', {})
            
            print(f"✅ Endpoint funcionando")
            print(f"   ready_for_conversion: {validation.get('ready_for_conversion')}")
            print(f"   completeness_score: {validation.get('completeness_score')}%")
            print(f"   critical_issues: {len(validation.get('critical_issues', []))}")
            print(f"   agent: {result.get('agent')}")
            
            # Teste conversão (deve falhar)
            conversion_request = {
                "case_id": "TEST-INCOMPLETE-001",
                "form_responses": incomplete_form["form_responses"],
                "visa_type": "H-1B",
                "force_conversion": False
            }
            
            conv_response = session.post(f"{API_BASE}/ai-review/convert-to-official", json=conversion_request)
            if conv_response.status_code == 200:
                conv_result = conv_response.json()
                print(f"   conversão_falhou: {not conv_result.get('success')} (esperado)")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # TESTE 2: Formulário Completo
    print("\n✅ TESTE 2: Formulário Completo")
    
    complete_form = {
        "case_id": "TEST-COMPLETE-002",
        "form_responses": {
            "personal": {
                "full_name": "João da Silva Santos",
                "date_of_birth": "1990-05-15",
                "place_of_birth": "São Paulo, SP, Brasil", 
                "nationality": "Brasileira"
            },
            "address": {
                "street_address": "Rua das Flores, 123",
                "city": "São Paulo",
                "state": "SP",
                "postal_code": "01234-567",
                "country": "Brasil",
                "phone": "+55 11 99999-9999",
                "email": "joao@email.com"
            },
            "employment": {
                "current_job": "Desenvolvedor de Software",
                "employer_name": "Tech Corp",
                "salary": "R$ 120.000"
            }
        },
        "visa_type": "H-1B"
    }
    
    try:
        response = session.post(f"{API_BASE}/ai-review/validate-completeness", json=complete_form)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            validation = result.get('validation_result', {})
            
            print(f"✅ Endpoint funcionando")
            print(f"   ready_for_conversion: {validation.get('ready_for_conversion')}")
            print(f"   completeness_score: {validation.get('completeness_score')}%")
            print(f"   critical_issues: {len(validation.get('critical_issues', []))}")
            print(f"   agent: {result.get('agent')}")
            
            # Teste conversão (deve funcionar se ready_for_conversion = true)
            if validation.get('ready_for_conversion'):
                conversion_request = {
                    "case_id": "TEST-COMPLETE-002",
                    "form_responses": complete_form["form_responses"],
                    "visa_type": "H-1B",
                    "force_conversion": False
                }
                
                conv_response = session.post(f"{API_BASE}/ai-review/convert-to-official", json=conversion_request)
                if conv_response.status_code == 200:
                    conv_result = conv_response.json()
                    print(f"   conversão_sucesso: {conv_result.get('success')}")
                    print(f"   dados_convertidos: {len(str(conv_result.get('converted_data', {})))} chars")
            else:
                print(f"   ⚠️ Não pronto para conversão - testando conversão forçada")
                forced_conversion = {
                    "case_id": "TEST-COMPLETE-002",
                    "form_responses": complete_form["form_responses"],
                    "visa_type": "H-1B",
                    "force_conversion": True
                }
                
                conv_response = session.post(f"{API_BASE}/ai-review/convert-to-official", json=forced_conversion)
                if conv_response.status_code == 200:
                    conv_result = conv_response.json()
                    print(f"   conversão_forçada: {conv_result.get('success')}")
                    print(f"   dados_convertidos: {len(str(conv_result.get('converted_data', {})))} chars")
        else:
            print(f"❌ Erro: {response.status_code} - {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TESTE SIMPLES CONCLUÍDO")

if __name__ == "__main__":
    test_ai_review_endpoints()