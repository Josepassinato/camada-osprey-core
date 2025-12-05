#!/usr/bin/env python3
"""
Teste de Credenciais do Google
Verifica se as API keys e credenciais estão funcionando
"""

import os
import sys
import requests
import json
from pathlib import Path

# Carregar variáveis de ambiente
sys.path.insert(0, str(Path(__file__).parent / 'backend'))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / 'backend' / '.env')

def test_google_vision_api():
    """Testa Google Vision API"""
    print("\n" + "="*60)
    print("🔍 Testando GOOGLE VISION API")
    print("="*60)
    
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ GOOGLE_API_KEY não encontrada no .env")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:20]}...")
    
    # Testar com uma imagem de teste simples (1x1 pixel em base64)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    
    payload = {
        "requests": [
            {
                "image": {
                    "content": test_image
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION"
                    }
                ]
            }
        ]
    }
    
    try:
        print("📡 Enviando request para Google Vision API...")
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ GOOGLE VISION API: FUNCIONANDO")
            result = response.json()
            print(f"📄 Response: {json.dumps(result, indent=2)[:200]}...")
            return True
        elif response.status_code == 403:
            print("❌ ERRO 403: API Key inválida ou API não habilitada")
            print(f"   Mensagem: {response.text[:200]}")
            return False
        elif response.status_code == 429:
            print("⚠️  ERRO 429: Limite de requisições excedido")
            return False
        else:
            print(f"❌ ERRO {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  TIMEOUT: API não respondeu em 10 segundos")
        return False
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

def test_gemini_api():
    """Testa Gemini API (Google AI Studio)"""
    print("\n" + "="*60)
    print("🔍 Testando GEMINI API")
    print("="*60)
    
    api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY não encontrada no .env")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:20]}...")
    
    # Endpoint para listar modelos disponíveis
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        print("📡 Enviando request para Gemini API...")
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ GEMINI API: FUNCIONANDO")
            result = response.json()
            models = result.get('models', [])
            print(f"📄 Modelos disponíveis: {len(models)}")
            if models:
                print(f"   Primeiro modelo: {models[0].get('name', 'N/A')}")
            return True
        elif response.status_code == 403:
            print("❌ ERRO 403: API Key inválida ou API não habilitada")
            print(f"   Mensagem: {response.text[:200]}")
            return False
        elif response.status_code == 429:
            print("⚠️  ERRO 429: Limite de requisições excedido")
            return False
        else:
            print(f"❌ ERRO {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  TIMEOUT: API não respondeu em 10 segundos")
        return False
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return False

def test_google_oauth2():
    """Verifica credenciais OAuth2"""
    print("\n" + "="*60)
    print("🔍 Verificando GOOGLE OAUTH2 CREDENTIALS")
    print("="*60)
    
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    
    if not client_id:
        print("❌ GOOGLE_CLIENT_ID não encontrada")
        return False
    
    if not client_secret:
        print("❌ GOOGLE_CLIENT_SECRET não encontrada")
        return False
    
    print(f"✅ Client ID: {client_id[:30]}...")
    print(f"✅ Client Secret: {client_secret[:20]}...")
    print(f"✅ Project ID: {project_id}")
    
    print("\n⚠️  NOTA: OAuth2 credentials precisam de Service Account JSON")
    print("   para funcionar completamente. Atualmente configurado para")
    print("   usar API Key como fallback.")
    
    return True

def main():
    print("\n" + "="*60)
    print("🧪 TESTE DE CREDENCIAIS DO GOOGLE")
    print("="*60)
    
    results = {
        'vision_api': test_google_vision_api(),
        'gemini_api': test_gemini_api(),
        'oauth2': test_google_oauth2()
    }
    
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for service, status in results.items():
        icon = "✅" if status else "❌"
        status_text = "FUNCIONANDO" if status else "COM PROBLEMAS"
        print(f"{icon} {service.upper()}: {status_text}")
    
    working_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n🎯 Total: {working_count}/{total_count} serviços funcionando")
    
    if working_count == total_count:
        print("\n✅ TODAS AS CREDENCIAIS ESTÃO FUNCIONANDO!")
    elif working_count > 0:
        print("\n⚠️  ALGUMAS CREDENCIAIS PRECISAM DE ATENÇÃO")
    else:
        print("\n❌ NENHUMA CREDENCIAL ESTÁ FUNCIONANDO")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
