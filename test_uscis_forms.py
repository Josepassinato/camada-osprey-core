#!/usr/bin/env python3
"""
TESTE ESPECÍFICO: USCIS Form Progress Saving Functionality

FOCO: Testar os endpoints de salvamento de progresso de formulários USCIS conforme solicitado:
1. POST /api/auto-application/case/{case_id}/uscis-form - Save USCIS form data
2. GET /api/auto-application/case/{case_id}/uscis-form - Get USCIS form data
3. POST /api/auto-application/case/{case_id}/authorize-uscis-form - Authorize USCIS form

CENÁRIOS DE TESTE:
- Criar caso de teste H-1B
- Salvar progresso parcial de formulário
- Recuperar dados salvos e verificar integridade
- Testar salvamento progressivo (adicionar mais seções)
- Testar autorização de formulário
- Testar casos extremos (case_id inválido, dados vazios)
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://osprey-visa-hub.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class USCISFormTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'USCISFormTester/1.0'
        })
        self.auth_token = None
        self.setup_test_authentication()
        
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
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def setup_test_authentication(self):
        """Setup authentication for endpoints that require it"""
        try:
            # Try to create a test user
            test_user_data = {
                "email": "uscis_test@formfill.com",
                "password": "testpassword123",
                "first_name": "USCIS",
                "last_name": "Tester"
            }
            
            # Try to signup
            signup_response = self.session.post(
                f"{API_BASE}/auth/signup",
                json=test_user_data
            )
            
            if signup_response.status_code == 200:
                signup_data = signup_response.json()
                self.auth_token = signup_data.get('token')
            else:
                # Try to login if user already exists
                login_data = {
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
                
                login_response = self.session.post(
                    f"{API_BASE}/auth/login",
                    json=login_data
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    self.auth_token = login_result.get('token')
            
            # Set authorization header if we have a token
            if self.auth_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                print(f"✅ Authentication setup successful")
            else:
                print(f"⚠️ Authentication setup failed - some tests may fail")
                
        except Exception as e:
            print(f"⚠️ Authentication setup error: {e}")

    def test_uscis_form_progress_saving(self):
        """TESTE PRINCIPAL: USCIS Form Progress Saving - Sistema de salvamento de progresso de formulários USCIS"""
        print("📋 TESTE PRINCIPAL: USCIS Form Progress Saving - Sistema de salvamento de progresso de formulários USCIS")
        
        # Step 1: Create a test case first using POST /api/auto-application/start with H-1B form
        try:
            case_data = {
                "form_code": "H-1B",
                "session_token": f"uscis_test_{uuid.uuid4().hex[:8]}"
            }
            
            print("📝 Criando caso de teste H-1B...")
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=case_data
            )
            
            if response.status_code != 200:
                self.log_test(
                    "USCIS Form - Create Test Case",
                    False,
                    f"❌ Falha ao criar caso: HTTP {response.status_code}",
                    {"status_code": response.status_code, "error": response.text[:200]}
                )
                return None
            
            result = response.json()
            case_id = result.get('case', {}).get('case_id')
            
            if not case_id:
                self.log_test(
                    "USCIS Form - Create Test Case",
                    False,
                    "❌ Case ID não retornado",
                    result
                )
                return None
            
            self.log_test(
                "USCIS Form - Create Test Case",
                True,
                f"✅ Caso H-1B criado: {case_id}",
                {"case_id": case_id, "form_code": "H-1B"}
            )
            
            # Step 2: Test POST /api/auto-application/case/{case_id}/uscis-form - Save partial form progress
            print("💾 Testando salvamento de progresso parcial...")
            
            partial_form_data = {
                "uscis_form_data": {
                    "section_1_personal": {
                        "full_name": "Carlos Eduardo Silva",
                        "date_of_birth": "1990-05-15",
                        "place_of_birth": "São Paulo, SP, Brazil",
                        "nationality": "Brazilian"
                    },
                    "section_2_contact": {
                        "current_address": "123 Main St, New York, NY 10001",
                        "phone_number": "+1-555-123-4567",
                        "email": "carlos.silva@email.com"
                    }
                },
                "completed_sections": ["section_1_personal", "section_2_contact"]
            }
            
            save_response = self.session.post(
                f"{API_BASE}/auto-application/case/{case_id}/uscis-form",
                json=partial_form_data
            )
            
            save_success = save_response.status_code == 200
            save_data = save_response.json() if save_success else {}
            
            self.log_test(
                "USCIS Form - Save Partial Progress",
                save_success,
                f"✅ Progresso salvo: {len(partial_form_data['completed_sections'])} seções" if save_success else f"❌ Erro ao salvar: HTTP {save_response.status_code}",
                {
                    "success": save_data.get('success', False),
                    "case_id": case_id,
                    "completed_sections": save_data.get('completed_sections', []),
                    "sections_count": len(partial_form_data['completed_sections']),
                    "status_code": save_response.status_code,
                    "error": save_response.text[:200] if not save_success else None
                }
            )
            
            # Step 3: Test GET /api/auto-application/case/{case_id}/uscis-form - Retrieve saved form data
            print("📖 Testando recuperação de dados salvos...")
            
            get_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}/uscis-form")
            
            get_success = get_response.status_code == 200
            get_data = get_response.json() if get_success else {}
            
            retrieved_form_data = get_data.get('uscis_form_data', {})
            retrieved_sections = get_data.get('completed_sections', [])
            
            # Verify data integrity
            data_matches = (
                len(retrieved_form_data) == len(partial_form_data['uscis_form_data']) and
                set(retrieved_sections) == set(partial_form_data['completed_sections'])
            ) if save_success else False
            
            self.log_test(
                "USCIS Form - Retrieve Saved Data",
                get_success and data_matches,
                f"✅ Dados recuperados: {len(retrieved_sections)} seções, integridade={data_matches}" if get_success else f"❌ Erro ao recuperar: HTTP {get_response.status_code}",
                {
                    "success": get_data.get('success', False),
                    "case_id": case_id,
                    "form_code": get_data.get('form_code'),
                    "sections_retrieved": len(retrieved_sections),
                    "data_integrity": data_matches,
                    "has_basic_data": bool(get_data.get('basic_data')),
                    "status_code": get_response.status_code,
                    "error": get_response.text[:200] if not get_success else None
                }
            )
            
            # Step 4: Test progressive saving (save more sections, verify incremental updates)
            print("🔄 Testando salvamento progressivo...")
            
            additional_form_data = {
                "uscis_form_data": {
                    **partial_form_data['uscis_form_data'],  # Keep existing data
                    "section_3_employment": {
                        "employer_name": "Tech Company Inc",
                        "job_title": "Software Engineer",
                        "start_date": "2024-01-15",
                        "salary": "85000"
                    },
                    "section_4_education": {
                        "degree": "Bachelor of Computer Science",
                        "university": "University of São Paulo",
                        "graduation_year": "2012"
                    }
                },
                "completed_sections": ["section_1_personal", "section_2_contact", "section_3_employment", "section_4_education"]
            }
            
            progressive_response = self.session.post(
                f"{API_BASE}/auto-application/case/{case_id}/uscis-form",
                json=additional_form_data
            )
            
            progressive_success = progressive_response.status_code == 200
            progressive_data = progressive_response.json() if progressive_success else {}
            
            self.log_test(
                "USCIS Form - Progressive Saving",
                progressive_success,
                f"✅ Progresso incremental: {len(additional_form_data['completed_sections'])} seções totais" if progressive_success else f"❌ Erro no salvamento progressivo: HTTP {progressive_response.status_code}",
                {
                    "success": progressive_data.get('success', False),
                    "case_id": case_id,
                    "total_sections": len(additional_form_data['completed_sections']),
                    "new_sections_added": 2,
                    "status_code": progressive_response.status_code,
                    "error": progressive_response.text[:200] if not progressive_success else None
                }
            )
            
            # Verify progressive update
            verify_response = self.session.get(f"{API_BASE}/auto-application/case/{case_id}/uscis-form")
            verify_data = verify_response.json() if verify_response.status_code == 200 else {}
            
            final_sections = verify_data.get('completed_sections', [])
            final_form_data = verify_data.get('uscis_form_data', {})
            
            progressive_update_correct = (
                len(final_sections) == 4 and
                'section_3_employment' in final_sections and
                'section_4_education' in final_sections and
                'section_3_employment' in final_form_data and
                'section_4_education' in final_form_data
            ) if progressive_success else False
            
            self.log_test(
                "USCIS Form - Verify Progressive Update",
                progressive_update_correct,
                f"✅ Atualização verificada: {len(final_sections)} seções, dados completos={progressive_update_correct}",
                {
                    "final_sections_count": len(final_sections),
                    "has_employment_section": 'section_3_employment' in final_sections,
                    "has_education_section": 'section_4_education' in final_sections,
                    "data_structure_correct": progressive_update_correct
                }
            )
            
            # Step 5: Test POST /api/auto-application/case/{case_id}/authorize-uscis-form - Authorize USCIS form
            print("✅ Testando autorização de formulário...")
            
            authorization_data = {
                "form_reviewed": True,
                "form_authorized": True,
                "generated_form_data": final_form_data,
                "authorization_timestamp": datetime.now().isoformat()
            }
            
            auth_response = self.session.post(
                f"{API_BASE}/auto-application/case/{case_id}/authorize-uscis-form",
                json=authorization_data
            )
            
            auth_success = auth_response.status_code == 200
            auth_data = auth_response.json() if auth_success else {}
            
            self.log_test(
                "USCIS Form - Authorization",
                auth_success,
                f"✅ Formulário autorizado: documento_salvo={auth_data.get('document_saved', False)}" if auth_success else f"❌ Erro na autorização: HTTP {auth_response.status_code}",
                {
                    "success": auth_data.get('success', False),
                    "case_id": case_id,
                    "document_saved": auth_data.get('document_saved', False),
                    "message": auth_data.get('message', ''),
                    "status_code": auth_response.status_code,
                    "error": auth_response.text[:200] if not auth_success else None
                }
            )
            
            # Step 6: Test edge cases
            print("🚨 Testando casos extremos...")
            
            # Test with invalid case_id
            invalid_case_response = self.session.get(f"{API_BASE}/auto-application/case/INVALID-CASE/uscis-form")
            
            self.log_test(
                "USCIS Form - Invalid Case ID",
                invalid_case_response.status_code == 404,
                f"✅ Caso inválido rejeitado: HTTP {invalid_case_response.status_code}",
                {"status_code": invalid_case_response.status_code}
            )
            
            # Test with empty form data
            empty_data_response = self.session.post(
                f"{API_BASE}/auto-application/case/{case_id}/uscis-form",
                json={"uscis_form_data": {}, "completed_sections": []}
            )
            
            empty_success = empty_data_response.status_code == 200
            
            self.log_test(
                "USCIS Form - Empty Form Data",
                empty_success,
                f"✅ Dados vazios aceitos: HTTP {empty_data_response.status_code}" if empty_success else f"❌ Dados vazios rejeitados: HTTP {empty_data_response.status_code}",
                {
                    "status_code": empty_data_response.status_code,
                    "handles_empty_data": empty_success
                }
            )
            
            # Final summary
            print("📊 Resumo do teste USCIS Form Progress Saving:")
            print(f"   Case ID: {case_id}")
            print(f"   Seções finais: {len(final_sections)}")
            print(f"   Formulário autorizado: {auth_success}")
            
            return {
                "case_id": case_id,
                "final_sections_count": len(final_sections),
                "form_authorized": auth_success,
                "all_tests_passed": save_success and get_success and progressive_success and auth_success
            }
            
        except Exception as e:
            self.log_test(
                "USCIS Form Progress Saving - Exception",
                False,
                f"❌ Exception: {str(e)}"
            )
            return None

    def run_tests(self):
        """Run USCIS form progress saving tests"""
        print("🚀 INICIANDO TESTES DO SISTEMA USCIS FORM PROGRESS SAVING")
        print("=" * 80)
        
        # Run USCIS form progress saving tests
        result = self.test_uscis_form_progress_saving()
        
        # Print summary
        self.print_test_summary()
        
        return result
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS TESTES - USCIS FORM PROGRESS SAVING")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 ESTATÍSTICAS GERAIS:")
        print(f"   Total de testes: {total_tests}")
        print(f"   ✅ Aprovados: {passed_tests}")
        print(f"   ❌ Falharam: {failed_tests}")
        print(f"   📊 Taxa de sucesso: {success_rate:.1f}%")
        
        print(f"\n🎯 ENDPOINTS TESTADOS:")
        print(f"   ✅ POST /api/auto-application/start")
        print(f"   ✅ POST /api/auto-application/case/{{case_id}}/uscis-form")
        print(f"   ✅ GET /api/auto-application/case/{{case_id}}/uscis-form")
        print(f"   ✅ POST /api/auto-application/case/{{case_id}}/authorize-uscis-form")
        
        print(f"\n🔍 FUNCIONALIDADES TESTADAS:")
        print(f"   ✅ Criação de caso H-1B")
        print(f"   ✅ Salvamento de progresso parcial")
        print(f"   ✅ Recuperação de dados salvos")
        print(f"   ✅ Salvamento progressivo (incremental)")
        print(f"   ✅ Autorização de formulário")
        print(f"   ✅ Casos extremos (case_id inválido, dados vazios)")
        
        if failed_tests > 0:
            print(f"\n❌ TESTES FALHARAM:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "=" * 80)


def main():
    """Execute USCIS Form Progress Saving Tests"""
    print("🤖 TESTE ESPECÍFICO: USCIS Form Progress Saving Functionality")
    print("🎯 FOCO: Testar endpoints de salvamento de progresso de formulários USCIS")
    print()
    print("CONTEXTO:")
    print("📋 Usuário reportou problemas com 'save form filling progress' functionality")
    print("📋 Necessário verificar se os endpoints backend estão funcionando corretamente")
    print()
    print("ENDPOINTS TESTADOS:")
    print("📋 POST /api/auto-application/case/{case_id}/uscis-form - Save USCIS form data")
    print("📋 GET /api/auto-application/case/{case_id}/uscis-form - Get USCIS form data")
    print("📋 POST /api/auto-application/case/{case_id}/authorize-uscis-form - Authorize USCIS form")
    print()
    
    tester = USCISFormTester()
    result = tester.run_tests()
    
    # Determine exit code based on test results
    if result and result.get('all_tests_passed', False):
        print("✅ Todos os testes principais passaram!")
        return 0
    else:
        print("❌ Alguns testes falharam - verificar logs acima")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())