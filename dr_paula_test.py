#!/usr/bin/env python3
"""
TESTE DIRETO E SIMPLES - VALIDAR DRA. PAULA COM CHAVE OPENAI
Direct test of Dr. Paula endpoints as requested in review
"""

import requests
import json
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://validai-imm.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_dr_paula_critical():
    """Test Dr. Paula with the exact I-589 payload from review request"""
    print("🚨 TESTE CRÍTICO - DRA. PAULA I-589 ASYLUM CASE")
    print("=" * 60)
    
    # Exact payload from review request
    i589_payload = {
        "visa_type": "I-589", 
        "applicant_letter": "Meu nome é Maria Silva e estou solicitando asilo político nos Estados Unidos devido à perseguição que sofri no meu país de origem por minhas opiniões políticas e ativismo pelos direitos humanos. Trabalhei como jornalista investigativa e recebi ameaças constantes do governo por expor corrupção.",
        "visa_profile": {
            "title": "I-589 Asylum Application",
            "directives": [
                {"id": "1", "pt": "Descrever perseguição detalhadamente", "en": "Describe persecution in detail", "required": True}
            ]
        }
    }
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'DrPaulaDirectTest/1.0'
    })
    
    print("🔍 TESTE 1: POST /api/llm/dr-paula/review-letter")
    print(f"Payload: {json.dumps(i589_payload, indent=2)}")
    print()
    
    try:
        response = session.post(
            f"{API_BASE}/llm/dr-paula/review-letter",
            json=i589_payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        # VERIFICAÇÕES ESPECÍFICAS conforme solicitado:
        checks = {
            "returns_200_ok": response.status_code == 200,
            "not_500_error": response.status_code != 500,
            "budget_ok": True,
            "dr_paula_available": True,
            "json_valid": False,
            "has_review_field": False,
            "status_valid": False
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                response_text = json.dumps(data, indent=2)
                print(f"Response JSON: {response_text}")
                
                # Check for budget issues
                checks["budget_ok"] = "Budget exceeded" not in response_text and "budget" not in response_text.lower()
                
                # Check for availability
                checks["dr_paula_available"] = "não está disponível" not in response_text
                
                # JSON is valid if we got here
                checks["json_valid"] = True
                
                # Check for review field
                checks["has_review_field"] = "review" in data
                
                # Check status
                review_data = data.get("review", {})
                status = review_data.get("status", "")
                checks["status_valid"] = status in ["needs_questions", "ready_for_formatting", "needs_review", "complete", "incomplete"]
                
                print(f"\nStatus found: '{status}'")
                
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                print(f"Raw Response: {response.text}")
        else:
            print(f"Error Response: {response.text}")
            response_text = response.text
            checks["budget_ok"] = "Budget exceeded" not in response_text
            checks["dr_paula_available"] = "não está disponível" not in response_text
        
        print("\n📊 VERIFICAÇÕES:")
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}: {result}")
        
        all_passed = all(checks.values())
        print(f"\n🎯 RESULTADO FINAL: {'✅ SUCESSO' if all_passed else '❌ FALHA'}")
        
        if all_passed:
            print("✅ O problema está resolvido e usuário pode usar o sistema normalmente")
        else:
            print("❌ Identificar erro específico para correção imediata")
            failed_checks = [k for k, v in checks.items() if not v]
            print(f"❌ Falhas: {failed_checks}")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_dr_paula_backup():
    """Test backup endpoint: generate-directives"""
    print("\n🔍 TESTE DE BACKUP: POST /api/llm/dr-paula/generate-directives")
    print("=" * 60)
    
    backup_payload = {
        "visa_type": "I-589",
        "language": "pt"
    }
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'DrPaulaDirectTest/1.0'
    })
    
    try:
        response = session.post(
            f"{API_BASE}/llm/dr-paula/generate-directives",
            json=backup_payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                directives_text = data.get("directives_text", "")
                print(f"Generated {len(directives_text)} characters of directives")
                print(f"Response keys: {list(data.keys())}")
                
                success = len(directives_text) > 50
                print(f"✅ Backup test: {'PASSED' if success else 'FAILED'}")
                return success
                
            except json.JSONDecodeError:
                print("❌ JSON parsing failed")
                print(f"Raw response: {response.text}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Run the direct Dr. Paula tests"""
    print("🚀 TESTE DIRETO E SIMPLES - VALIDAR DRA. PAULA COM CHAVE OPENAI")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run critical test
    critical_success = test_dr_paula_critical()
    
    # Run backup test
    backup_success = test_dr_paula_backup()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO FINAL:")
    print(f"✅ Teste Crítico (review-letter): {'PASSOU' if critical_success else 'FALHOU'}")
    print(f"✅ Teste Backup (generate-directives): {'PASSOU' if backup_success else 'FALHOU'}")
    
    if critical_success:
        print("\n🎉 CONCLUSÃO: O problema está resolvido!")
        print("✅ Usuário pode usar o sistema normalmente")
        print("✅ Configuração OpenAI funcionando")
    else:
        print("\n❌ CONCLUSÃO: Problema persiste!")
        print("❌ Requer correção imediata")
        print("❌ Verificar configuração OpenAI")

if __name__ == "__main__":
    main()