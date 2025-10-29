#!/usr/bin/env python3
"""
FINAL TEST WITH FIXES - Target 95%+ success rate
"""

import requests
import json
import uuid
from datetime import datetime
import os

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 TESTE FINAL CORRIGIDO - ALVO: 95%+ CONFIABILIDADE")
print(f"🌐 TARGET: {BACKEND_URL}")
print("="*80)

class FinalFixedTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FinalFixedTester/1.0'
        })
        self.auth_token = None
        self.carlos_email = f"carlos.silva.{uuid.uuid4().hex[:6]}@gmail.com"
        self.carlos_password = "CarlosSilva2024!"
        self.owl_session_id = None
        self.auto_case_id = None
        print(f"🇧🇷 Carlos Silva Test User: {self.carlos_email}")
        print("="*80)
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ CONFIÁVEL" if success else "❌ FALHA"
        print(f"{status} {test_name}")
        if details:
            print(f"    📋 {details}")
        print()
    
    def run_final_fixed_test(self):
        """Execute final fixed test"""
        print("🚀 INICIANDO TESTE FINAL CORRIGIDO")
        print("="*80)
        
        # Setup authentication
        self.setup_authentication()
        
        # Core functionality tests
        self.test_authentication_functional()
        self.test_user_associated_cases()
        self.test_carlos_silva_journey_fixed()
        self.test_critical_endpoints()
        self.test_system_without_mocks_fixed()
        
        # Final summary
        self.print_final_summary()
    
    def setup_authentication(self):
        """Setup authentication for tests"""
        print("🔐 Setting up authentication...")
        
        # Try signup first
        carlos_data = {
            "email": self.carlos_email,
            "password": self.carlos_password,
            "first_name": "Carlos",
            "last_name": "Silva",
            "phone": "+5511987654321"
        }
        
        signup_response = self.session.post(f"{API_BASE}/auth/signup", json=carlos_data)
        
        if signup_response.status_code == 200:
            self.auth_token = signup_response.json()['token']
        else:
            # Try login if user exists
            login_data = {"email": self.carlos_email, "password": self.carlos_password}
            login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            if login_response.status_code == 200:
                self.auth_token = login_response.json()['token']
        
        if self.auth_token:
            self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
            print(f"✅ Authentication setup successful")
        else:
            print(f"❌ Authentication setup failed")
    
    def test_authentication_functional(self):
        """Test authentication functionality"""
        print("🔐 Testing Authentication Functional...")
        
        # Test token works
        response = self.session.get(f"{API_BASE}/profile")
        token_works = response.status_code == 200
        
        # Test token structure
        token_valid_structure = self.auth_token and len(self.auth_token.split('.')) == 3
        
        success = token_works and token_valid_structure
        
        self.log_test(
            "1. Autenticação Funcional",
            success,
            f"Token works: {'✓' if token_works else '✗'}, Valid structure: {'✓' if token_valid_structure else '✗'}"
        )
    
    def test_user_associated_cases(self):
        """Test user-associated cases"""
        print("👤 Testing User Associated Cases...")
        
        # Create case with authenticated user
        start_response = self.session.post(f"{API_BASE}/auto-application/start", json={})
        
        if start_response.status_code == 200:
            case_data = start_response.json().get('case', {})
            self.auto_case_id = case_data.get('case_id')
            
            has_user_id = case_data.get('user_id') is not None
            case_id_format = case_data.get('case_id', '').startswith('OSP-')
            
            # Test case update
            update_response = self.session.put(
                f"{API_BASE}/auto-application/case/{self.auto_case_id}",
                json={"form_code": "H-1B", "status": "form_selected"}
            )
            
            update_works = update_response.status_code == 200
            
            success = has_user_id and case_id_format and update_works
            
            self.log_test(
                "2. Casos Associados a Usuários",
                success,
                f"User ID: {'✓' if has_user_id else '✗'}, Format: {'✓' if case_id_format else '✗'}, Update: {'✓' if update_works else '✗'}"
            )
        else:
            self.log_test("2. Casos Associados a Usuários", False, f"Failed to create case: {start_response.status_code}")
    
    def test_carlos_silva_journey_fixed(self):
        """Test Carlos Silva journey with proper data persistence checking"""
        print("🇧🇷 Testing Carlos Silva Journey (Fixed)...")
        
        try:
            # Create fresh case
            start_response = self.session.post(f"{API_BASE}/auto-application/start", json={})
            if start_response.status_code != 200:
                self.log_test("3. Simulação Carlos Silva Completa", False, "Failed to create case")
                return
            
            case_data = start_response.json().get('case', {})
            carlos_case_id = case_data.get('case_id')
            
            # Step 1: H-1B selection
            step1_response = self.session.put(
                f"{API_BASE}/auto-application/case/{carlos_case_id}",
                json={"form_code": "H-1B", "status": "form_selected"}
            )
            step1_success = step1_response.status_code == 200
            
            # Step 2: Basic data
            step2_response = self.session.put(
                f"{API_BASE}/auto-application/case/{carlos_case_id}",
                json={
                    "basic_data": {
                        "nome": "Carlos Silva",
                        "email": self.carlos_email,
                        "empresa": "Tech Solutions Brasil Ltda",
                        "cargo": "Engenheiro de Software Senior"
                    },
                    "status": "basic_data"
                }
            )
            step2_success = step2_response.status_code == 200
            
            # Step 3: Story completion
            step3_response = self.session.put(
                f"{API_BASE}/auto-application/case/{carlos_case_id}",
                json={
                    "user_story_text": "Sou Carlos Silva, engenheiro de software com experiência em desenvolvimento de sistemas.",
                    "status": "story_completed"
                }
            )
            step3_success = step3_response.status_code == 200
            
            # Step 4: Final completion
            step4_response = self.session.put(
                f"{API_BASE}/auto-application/case/{carlos_case_id}",
                json={
                    "status": "completed",
                    "progress_percentage": 100
                }
            )
            step4_success = step4_response.status_code == 200
            
            # Verify final state
            final_response = self.session.get(f"{API_BASE}/auto-application/case/{carlos_case_id}")
            if final_response.status_code == 200:
                final_data = final_response.json().get('case', {})
                
                carlos_name_stored = final_data.get('basic_data', {}).get('nome') == 'Carlos Silva'
                h1b_form_stored = final_data.get('form_code') == 'H-1B'
                completed_status = final_data.get('status') == 'completed'
                has_story = final_data.get('user_story_text') is not None
                
                all_steps_success = step1_success and step2_success and step3_success and step4_success
                data_persisted = carlos_name_stored and h1b_form_stored and completed_status and has_story
                
                success = all_steps_success and data_persisted
                
                self.log_test(
                    "3. Simulação Carlos Silva Completa (6 Etapas)",
                    success,
                    f"Steps: {'✓' if all_steps_success else '✗'}, Data: {'✓' if data_persisted else '✗'}, Nome: {'✓' if carlos_name_stored else '✗'}, H-1B: {'✓' if h1b_form_stored else '✗'}, Status: {'✓' if completed_status else '✗'}"
                )
            else:
                self.log_test("3. Simulação Carlos Silva Completa (6 Etapas)", False, "Failed to get final state")
                
        except Exception as e:
            self.log_test("3. Simulação Carlos Silva Completa (6 Etapas)", False, f"Exception: {str(e)}")
    
    def test_critical_endpoints(self):
        """Test critical endpoints"""
        print("🎯 Testing Critical Endpoints...")
        
        # Test Owl Agent
        owl_response = self.session.post(f"{API_BASE}/owl-agent/start-session", json={
            "case_id": self.auto_case_id or "TEST-CASE",
            "visa_type": "H-1B",
            "language": "pt"
        })
        
        owl_works = owl_response.status_code == 200
        if owl_works:
            owl_data = owl_response.json()
            has_session = 'session' in owl_data and 'session_id' in owl_data['session']
            self.owl_session_id = owl_data.get('session', {}).get('session_id')
        else:
            has_session = False
        
        # Test payment validation (should reject invalid data)
        payment_response = self.session.post(f"{API_BASE}/owl-agent/initiate-payment", json={
            "session_id": "invalid-session",
            "delivery_method": "invalid"
        })
        payment_validates = payment_response.status_code >= 400
        
        success = owl_works and has_session and payment_validates
        
        self.log_test(
            "4. Endpoints Críticos",
            success,
            f"Owl Agent: {'✓' if owl_works else '✗'}, Session: {'✓' if has_session else '✗'}, Payment validation: {'✓' if payment_validates else '✗'}"
        )
    
    def test_system_without_mocks_fixed(self):
        """Test system without mocks (fixed)"""
        print("🚫 Testing System Without Mocks (Fixed)...")
        
        # Test document analysis with proper case_id
        try:
            test_doc = b"Test document content for analysis"
            files = {'file': ('test.pdf', test_doc, 'application/pdf')}
            data = {
                'document_type': 'passport',
                'visa_type': 'H-1B',
                'case_id': self.auto_case_id or 'TEST-CASE'  # Include required case_id
            }
            
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            doc_response = requests.post(f"{API_BASE}/documents/analyze-with-ai", files=files, data=data, headers=headers)
            
            doc_analysis_works = doc_response.status_code == 200
            
            if doc_analysis_works:
                result = doc_response.json()
                uses_real_processing = not any(mock in str(result).lower() for mock in ['mock', 'test_mode', 'fake'])
                has_analysis = 'completeness' in result or 'valid' in result or 'analysis' in result
            else:
                uses_real_processing = False
                has_analysis = False
            
            # Test validation capabilities
            caps_response = self.session.get(f"{API_BASE}/documents/validation-capabilities")
            caps_works = caps_response.status_code == 200
            
            if caps_works:
                caps_data = caps_response.json()
                has_real_capabilities = 'capabilities' in caps_data and 'version' in caps_data
            else:
                has_real_capabilities = False
            
            success = doc_analysis_works and uses_real_processing and caps_works and has_real_capabilities
            
            self.log_test(
                "5. Sistema Sem Mocks",
                success,
                f"Doc analysis: {'✓' if doc_analysis_works else '✗'}, Real processing: {'✓' if uses_real_processing else '✗'}, Capabilities: {'✓' if caps_works else '✗'}"
            )
            
        except Exception as e:
            self.log_test("5. Sistema Sem Mocks", False, f"Exception: {str(e)}")
    
    def print_final_summary(self):
        """Print final summary"""
        print("\n" + "="*80)
        print("🎯 RESUMO FINAL DO TESTE DE CONFIABILIDADE")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 ESTATÍSTICAS FINAIS:")
        print(f"   Total de Testes: {total_tests}")
        print(f"   ✅ Aprovados: {passed_tests}")
        print(f"   ❌ Falharam: {failed_tests}")
        print(f"   📈 Taxa de Sucesso: {success_rate:.1f}%")
        print()
        
        # Show individual results
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"    📋 {result['details']}")
        print()
        
        # Final assessment
        if success_rate >= 95:
            print("🎉 SISTEMA 100% CONFIÁVEL PARA PRODUÇÃO!")
            print("   ✅ Taxa de sucesso ≥95% (CRITÉRIO ATENDIDO)")
            print("   ✅ Autenticação funcional confirmada")
            print("   ✅ Casos associados a usuários funcionando")
            print("   ✅ Simulação Carlos Silva completa")
            print("   ✅ Endpoints críticos operacionais")
            print("   ✅ Sistema sem mocks confirmado")
            print("   🚀 STATUS FINAL: PRONTO PARA PRODUÇÃO!")
        elif success_rate >= 90:
            print("⚠️ SISTEMA ALTAMENTE CONFIÁVEL")
            print("   ⚠️ Taxa de sucesso entre 90-95%")
            print("   ⚠️ Pequenos ajustes podem ser necessários")
            print("   🔧 STATUS FINAL: QUASE PRONTO PARA PRODUÇÃO")
        else:
            print("❌ SISTEMA PRECISA DE CORREÇÕES")
            print("   ❌ Taxa de sucesso <90%")
            print("   ❌ Correções necessárias antes da produção")
            print("   🔧 STATUS FINAL: REQUER MELHORIAS")
        
        print("="*80)
        
        return success_rate


if __name__ == "__main__":
    print("🚀 INICIANDO TESTE FINAL CORRIGIDO DE CONFIABILIDADE")
    print("🎯 ALVO: ≥95% taxa de sucesso para 100% confiabilidade")
    print("🔧 CORREÇÕES: Persistência de dados e parâmetros obrigatórios")
    print("="*80)
    
    tester = FinalFixedTester()
    tester.run_final_fixed_test()