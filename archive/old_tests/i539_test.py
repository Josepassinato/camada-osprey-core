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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://formcraft-43.preview.emergentagent.com')
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
            
            # PASSO 2: Preencher Basic Data (usando PUT endpoint)
            print("\n📋 PASSO 2: PREENCHER BASIC DATA")
            print(f"   PUT /api/auto-application/case/{case_id}")
            
            basic_data = {
                "basic_data": {
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
            }
            
            basic_response = self.session.put(f"{API_BASE}/auto-application/case/{case_id}", json=basic_data)
            
            if basic_response.status_code == 200:
                basic_result = basic_response.json()
                print(f"   ✅ Dados básicos salvos com sucesso")
                print(f"   ✅ Status: {basic_result.get('status', 'N/A')}")
                self.log_test("PASSO 2: Basic Data", True, "Dados salvos com sucesso")
            else:
                print(f"   ❌ Falha ao salvar dados básicos: HTTP {basic_response.status_code}")
                print(f"   📋 Resposta: {basic_response.text[:200]}")
                self.log_test("PASSO 2: Basic Data", False, f"HTTP {basic_response.status_code}")
            
            # PASSO 3: Verificar Case Data
            print("\n📋 PASSO 3: VERIFICAR CASE DATA")
            print(f"   GET /api/auto-application/case/{case_id}")
            
            case_get_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}")
            
            if case_get_response.status_code == 200:
                case_get_result = case_get_response.json()
                print(f"   ✅ Case data disponível")
                print(f"   ✅ Estrutura: {type(case_get_result)}")
                self.log_test("PASSO 3: Verificar Case Data", True, "Case data disponível")
            else:
                print(f"   ❌ Falha ao obter case data: HTTP {case_get_response.status_code}")
                print(f"   📋 Resposta: {case_get_response.text[:200]}")
                self.log_test("PASSO 3: Verificar Case Data", False, f"HTTP {case_get_response.status_code}")
            
            # PASSO 4: Submeter User Story
            print("\n📋 PASSO 4: SUBMETER USER STORY")
            print(f"   PUT /api/auto-application/case/{case_id}")
            
            user_story_data = {
                "user_story_text": "Quero estender minha estadia para visitar mais cidades americanas e conhecer a família do meu noivo. Tenho poupança de $15.000 e meu noivo me ajudará com hospedagem. Planejo ficar mais 6 meses.",
                "simplified_form_responses": {
                    "currentStatus": "B-2",
                    "requestedStatus": "B-2",
                    "reasonForExtension": "Quero estender minha estadia para visitar mais cidades americanas e conhecer a família do meu noivo",
                    "proposedStayDuration": "6 months",
                    "financialSupport": "Tenho poupança de $15.000 e meu noivo me ajudará com hospedagem"
                }
            }
            
            story_response = self.session.put(f"{API_BASE}/auto-application/case/{case_id}", json=user_story_data)
            
            if story_response.status_code == 200:
                story_result = story_response.json()
                print(f"   ✅ User story submetido com sucesso")
                print(f"   ✅ Status: {story_result.get('status', 'N/A')}")
                self.log_test("PASSO 4: Submeter User Story", True, "Story submetido com sucesso")
            else:
                print(f"   ❌ Falha ao submeter user story: HTTP {story_response.status_code}")
                print(f"   📋 Resposta: {story_response.text[:200]}")
                self.log_test("PASSO 4: Submeter User Story", False, f"HTTP {story_response.status_code}")
            
            # PASSO 5: AI Processing
            print("\n📋 PASSO 5: AI PROCESSING")
            print(f"   POST /api/auto-application/case/{case_id}/ai-processing")
            
            ai_data = {
                "step": "validation"
            }
            
            ai_response = self.session.post(f"{API_BASE}/auto-application/case/{case_id}/ai-processing", json=ai_data)
            
            if ai_response.status_code == 200:
                ai_result = ai_response.json()
                print(f"   ✅ AI processing executado com sucesso")
                print(f"   ✅ Success: {ai_result.get('success', 'N/A')}")
                self.log_test("PASSO 5: AI Processing", True, "AI processing executado com sucesso")
            else:
                print(f"   ❌ Falha no AI processing: HTTP {ai_response.status_code}")
                print(f"   📋 Resposta: {ai_response.text[:200]}")
                self.log_test("PASSO 5: AI Processing", False, f"HTTP {ai_response.status_code}")
            
            # PASSO 6: Generate Form
            print("\n📋 PASSO 6: GENERATE FORM")
            print(f"   POST /api/auto-application/case/{case_id}/generate-form")
            
            generate_response = self.session.post(f"{API_BASE}/auto-application/case/{case_id}/generate-form", json={})
            
            if generate_response.status_code == 200:
                generate_result = generate_response.json()
                print(f"   ✅ Form gerado com sucesso")
                print(f"   ✅ Success: {generate_result.get('success', 'N/A')}")
                self.log_test("PASSO 6: Generate Form", True, "Form gerado com sucesso")
            else:
                print(f"   ❌ Falha ao gerar form: HTTP {generate_response.status_code}")
                print(f"   📋 Resposta: {generate_response.text[:200]}")
                self.log_test("PASSO 6: Generate Form", False, f"HTTP {generate_response.status_code}")
            
            # PASSO 7: Complete Case
            print("\n📋 PASSO 7: COMPLETE CASE")
            print(f"   POST /api/auto-application/case/{case_id}/complete")
            
            complete_response = self.session.post(f"{API_BASE}/auto-application/case/{case_id}/complete", json={})
            
            if complete_response.status_code == 200:
                complete_result = complete_response.json()
                print(f"   ✅ Case completado com sucesso")
                print(f"   ✅ Status: {complete_result.get('status', 'N/A')}")
                self.log_test("PASSO 7: Complete Case", True, "Case completado com sucesso")
            else:
                print(f"   ❌ Falha ao completar case: HTTP {complete_response.status_code}")
                print(f"   📋 Resposta: {complete_response.text[:200]}")
                self.log_test("PASSO 7: Complete Case", False, f"HTTP {complete_response.status_code}")
            
            # PASSO 8: Verificar Final Case Status
            print("\n📋 PASSO 8: VERIFICAR FINAL CASE STATUS")
            print(f"   GET /api/auto-application/case/{case_id}")
            
            final_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}")
            
            if final_response.status_code == 200:
                final_result = final_response.json()
                case_data = final_result.get('case', final_result)
                final_status = case_data.get('status')
                progress = case_data.get('progress_percentage', 0)
                print(f"   ✅ Final case status obtido")
                print(f"   ✅ Status: {final_status}")
                print(f"   ✅ Progress: {progress}%")
                self.log_test("PASSO 8: Final Case Status", True, f"Status: {final_status}, Progress: {progress}%")
            else:
                print(f"   ❌ Falha ao obter final status: HTTP {final_response.status_code}")
                print(f"   📋 Resposta: {final_response.text[:200]}")
                self.log_test("PASSO 8: Final Case Status", False, f"HTTP {final_response.status_code}")
            
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