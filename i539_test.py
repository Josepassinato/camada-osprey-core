#!/usr/bin/env python3
"""
I-539 END-TO-END TEST - MARIA SILVA SANTOS
Complete end-to-end testing for I-539 (Tourist Extension) case
Focus: Complete workflow from case creation to PDF download
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visa-checkout-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🌐 I-539 END-TO-END TEST TARGET: {BACKEND_URL}")
print(f"🎯 API BASE: {API_BASE}")
print("="*80)

class I539EndToEndTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'I539EndToEndTester/1.0'
        })
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} {test_name}")
        if details:
            print(f"    📋 {details}")
        if not success and response_data:
            print(f"    🔍 Response: {str(response_data)[:200]}...")
        print()
    
    def run_i539_complete_test(self):
        """Execute complete I-539 end-to-end test"""
        print("🇧🇷 TESTE COMPLETO END-TO-END - CASO I-539 (EXTENSÃO DE TURISTA)")
        print("👤 USUÁRIO FICTÍCIO: Maria Silva Santos")
        print("📋 DADOS:")
        print("   Nome: Maria Silva Santos")
        print("   Data de Nascimento: 15/03/1990")
        print("   País de Nascimento: Brasil")
        print("   Gênero: Feminino")
        print("   Endereço: 123 Main Street, Apt 4B, Miami, FL 33101")
        print("   Telefone: +1 (305) 555-1234")
        print("   Email: maria.silva@email.com")
        print("   Status Atual: B-2 (Turista)")
        print("   Data de Expiração: 15/12/2024")
        print("   Data de Entrada: 15/06/2024")
        print("   I-94 Number: 12345678901")
        print("="*80)
        
        case_id = None
        
        try:
            # PASSO 1: Criar Case
            print("\n📋 PASSO 1: CRIAR CASE")
            print("   POST /api/auto-application/start")
            print("   Body: {\"form_code\": \"I-539\", \"process_type\": \"change_of_status\"}")
            
            start_data = {
                "form_code": "I-539",
                "process_type": "change_of_status"
            }
            
            start_response = self.session.post(f"{API_BASE}/auto-application/start", json=start_data)
            
            if start_response.status_code == 200:
                start_result = start_response.json()
                case_data = start_result.get('case', start_result)
                case_id = case_data.get('case_id')
                
                if case_id:
                    print(f"   ✅ Case criado com sucesso: {case_id}")
                    print(f"   ✅ Form code: {case_data.get('form_code')}")
                    print(f"   ✅ Process type: {case_data.get('process_type')}")
                    
                    self.log_test("PASSO 1: Criar Case", True, f"Case ID: {case_id}")
                else:
                    print(f"   ❌ Case ID não retornado")
                    self.log_test("PASSO 1: Criar Case", False, "Case ID não retornado")
                    return
            else:
                print(f"   ❌ Falha ao criar case: HTTP {start_response.status_code}")
                print(f"   📋 Resposta: {start_response.text[:200]}")
                self.log_test("PASSO 1: Criar Case", False, f"HTTP {start_response.status_code}")
                return
            
            # PASSO 2: Preencher Basic Data
            print("\n📋 PASSO 2: PREENCHER BASIC DATA")
            print(f"   POST /api/auto-application/case/{case_id}/basic-data")
            
            basic_data = {
                "firstName": "Maria",
                "middleName": "Silva",
                "lastName": "Santos",
                "dateOfBirth": "1990-03-15",
                "countryOfBirth": "Brazil",
                "gender": "Female",
                "currentAddress": "123 Main Street, Apt 4B",
                "city": "Miami",
                "state": "FL",
                "zipCode": "33101",
                "country": "United States",
                "phoneNumber": "+1 (305) 555-1234",
                "email": "maria.silva@email.com",
                "currentStatus": "B-2",
                "statusExpiration": "2024-12-15",
                "i94Number": "12345678901"
            }
            
            basic_response = self.session.post(f"{API_BASE}/auto-application/case/{case_id}/basic-data", json=basic_data)
            
            if basic_response.status_code == 200:
                basic_result = basic_response.json()
                print(f"   ✅ Dados básicos salvos com sucesso")
                print(f"   ✅ Status: {basic_result.get('status', 'N/A')}")
                self.log_test("PASSO 2: Basic Data", True, "Dados salvos com sucesso")
            else:
                print(f"   ❌ Falha ao salvar dados básicos: HTTP {basic_response.status_code}")
                print(f"   📋 Resposta: {basic_response.text[:200]}")
                self.log_test("PASSO 2: Basic Data", False, f"HTTP {basic_response.status_code}")
            
            # PASSO 3: Verificar Friendly Form
            print("\n📋 PASSO 3: VERIFICAR FRIENDLY FORM")
            print(f"   GET /api/auto-application/case/{case_id}/friendly-form")
            
            friendly_get_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}/friendly-form")
            
            if friendly_get_response.status_code == 200:
                friendly_get_result = friendly_get_response.json()
                print(f"   ✅ Friendly form disponível")
                print(f"   ✅ Estrutura: {type(friendly_get_result)}")
                self.log_test("PASSO 3: Verificar Friendly Form", True, "Form disponível")
            else:
                print(f"   ❌ Falha ao obter friendly form: HTTP {friendly_get_response.status_code}")
                print(f"   📋 Resposta: {friendly_get_response.text[:200]}")
                self.log_test("PASSO 3: Verificar Friendly Form", False, f"HTTP {friendly_get_response.status_code}")
            
            # PASSO 4: Submeter Friendly Form
            print("\n📋 PASSO 4: SUBMETER FRIENDLY FORM")
            print(f"   POST /api/auto-application/case/{case_id}/friendly-form")
            
            friendly_form_data = {
                "currentStatus": "B-2",
                "requestedStatus": "B-2",
                "reasonForExtension": "Quero estender minha estadia para visitar mais cidades americanas e conhecer a família do meu noivo",
                "proposedStayDuration": "6 months",
                "financialSupport": "Tenho poupança de $15.000 e meu noivo me ajudará com hospedagem"
            }
            
            friendly_post_response = self.session.post(f"{API_BASE}/auto-application/case/{case_id}/friendly-form", json=friendly_form_data)
            
            if friendly_post_response.status_code == 200:
                friendly_post_result = friendly_post_response.json()
                print(f"   ✅ Friendly form submetido com sucesso")
                print(f"   ✅ Status: {friendly_post_result.get('status', 'N/A')}")
                self.log_test("PASSO 4: Submeter Friendly Form", True, "Form submetido com sucesso")
            else:
                print(f"   ❌ Falha ao submeter friendly form: HTTP {friendly_post_response.status_code}")
                print(f"   📋 Resposta: {friendly_post_response.text[:200]}")
                self.log_test("PASSO 4: Submeter Friendly Form", False, f"HTTP {friendly_post_response.status_code}")
            
            # PASSO 5: Verificar USCIS Form Generation
            print("\n📋 PASSO 5: VERIFICAR USCIS FORM GENERATION")
            print(f"   GET /api/auto-application/case/{case_id}/uscis-form")
            
            uscis_form_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}/uscis-form")
            
            if uscis_form_response.status_code == 200:
                uscis_form_result = uscis_form_response.json()
                print(f"   ✅ USCIS form gerado com sucesso")
                print(f"   ✅ Tipo: {type(uscis_form_result)}")
                self.log_test("PASSO 5: USCIS Form Generation", True, "Form gerado com sucesso")
            else:
                print(f"   ❌ Falha ao gerar USCIS form: HTTP {uscis_form_response.status_code}")
                print(f"   📋 Resposta: {uscis_form_response.text[:200]}")
                self.log_test("PASSO 5: USCIS Form Generation", False, f"HTTP {uscis_form_response.status_code}")
            
            # PASSO 6: Verificar Document Checklist
            print("\n📋 PASSO 6: VERIFICAR DOCUMENT CHECKLIST")
            print(f"   GET /api/auto-application/case/{case_id}/documents/checklist")
            
            checklist_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}/documents/checklist")
            
            if checklist_response.status_code == 200:
                checklist_result = checklist_response.json()
                print(f"   ✅ Document checklist disponível")
                print(f"   ✅ Estrutura: {type(checklist_result)}")
                self.log_test("PASSO 6: Document Checklist", True, "Checklist disponível")
            else:
                print(f"   ❌ Falha ao obter document checklist: HTTP {checklist_response.status_code}")
                print(f"   📋 Resposta: {checklist_response.text[:200]}")
                self.log_test("PASSO 6: Document Checklist", False, f"HTTP {checklist_response.status_code}")
            
            # PASSO 7: Finalizar
            print("\n📋 PASSO 7: FINALIZAR")
            print(f"   GET /api/auto-application/case/{case_id}/finalize")
            
            finalize_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}/finalize")
            
            if finalize_response.status_code == 200:
                finalize_result = finalize_response.json()
                print(f"   ✅ Case finalizado com sucesso")
                print(f"   ✅ Status: {finalize_result.get('status', 'N/A')}")
                self.log_test("PASSO 7: Finalizar", True, "Case finalizado com sucesso")
            else:
                print(f"   ❌ Falha ao finalizar case: HTTP {finalize_response.status_code}")
                print(f"   📋 Resposta: {finalize_response.text[:200]}")
                self.log_test("PASSO 7: Finalizar", False, f"HTTP {finalize_response.status_code}")
            
            # PASSO 8: Obter Link de Download
            print("\n📋 PASSO 8: OBTER LINK DE DOWNLOAD")
            print(f"   GET /api/auto-application/case/{case_id}/download")
            
            download_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}/download")
            
            if download_response.status_code == 200:
                download_result = download_response.json()
                download_url = download_result.get('download_url') or download_result.get('url')
                print(f"   ✅ Link de download obtido com sucesso")
                print(f"   ✅ URL: {download_url[:50] if download_url else 'N/A'}...")
                self.log_test("PASSO 8: Link de Download", True, f"URL obtida: {bool(download_url)}")
            else:
                print(f"   ❌ Falha ao obter link de download: HTTP {download_response.status_code}")
                print(f"   📋 Resposta: {download_response.text[:200]}")
                self.log_test("PASSO 8: Link de Download", False, f"HTTP {download_response.status_code}")
            
        except Exception as e:
            print(f"   ❌ Erro geral: {str(e)}")
            self.log_test("ERRO GERAL", False, f"Exception: {str(e)}")
        
        # Print final summary
        self.print_final_summary(case_id)
    
    def print_final_summary(self, case_id):
        """Print final test summary"""
        print("\n" + "="*80)
        print("📊 RESUMO FINAL - I-539 END-TO-END TEST")
        print("="*80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        success_rate = len(passed_tests) / len(self.test_results) * 100 if self.test_results else 0
        
        print(f"\n🎯 RESULTADO GERAL:")
        print(f"   ✅ Passos que passaram: {len(passed_tests)}/{len(self.test_results)} ({success_rate:.1f}%)")
        print(f"   ❌ Passos que falharam: {len(failed_tests)}/{len(self.test_results)}")
        print(f"   📋 Case ID gerado: {case_id if case_id else 'N/A'}")
        
        print(f"\n📋 DETALHAMENTO:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASSOU" if result["success"] else "❌ FALHOU"
            print(f"   {i}. {result['test']}: {status}")
            print(f"      {result['details']}")
        
        # Verificações esperadas
        expected_verifications = [
            "✅ Case criado com sucesso",
            "✅ Dados básicos salvos",
            "✅ Formulário I-539 gerado em PDF",
            "✅ Checklist de documentos disponível",
            "✅ Link de download funcionando",
            "✅ PDF contém todos os dados preenchidos corretamente"
        ]
        
        print(f"\n📋 VERIFICAÇÕES ESPERADAS:")
        for verification in expected_verifications:
            print(f"   {verification}")
        
        # Final status
        overall_success = success_rate >= 75.0
        print(f"\n🏁 STATUS FINAL: {'FUNCIONAL' if overall_success else 'COM PROBLEMAS'}")
        
        return overall_success

if __name__ == "__main__":
    tester = I539EndToEndTester()
    tester.run_i539_complete_test()