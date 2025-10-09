#!/usr/bin/env python3
"""
TESTE FOCADO DO SISTEMA INTELIGENTE DE PREENCHIMENTO DE FORMULÁRIOS
Testa especificamente as correções implementadas conforme solicitado pelo usuário
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://formfill-pro-2.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class FocusedIntelligentFormsTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FocusedFormsTester/1.0'
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
                "email": "focused_test@forms.com",
                "password": "testpassword123",
                "first_name": "Focused",
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

    def test_case_a_no_validated_documents(self):
        """CASO A: Sem documentos validados - deve usar dados de demonstração"""
        print("🎯 CASO A: Sem documentos validados")
        
        try:
            # Create a test case without documents
            case_data = {
                "form_code": "H-1B",
                "session_token": f"test_session_{uuid.uuid4().hex[:8]}"
            }
            
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=case_data
            )
            
            if response.status_code == 200:
                result = response.json()
                case_id = result.get('case', {}).get('case_id')
                
                # Add only basic data (no documents)
                basic_data = {
                    "firstName": "João",
                    "lastName": "Silva",
                    "email": "joao.silva@test.com"
                }
                
                # Update case with basic data only
                update_response = self.session.patch(
                    f"{API_BASE}/auto-application/case/{case_id}",
                    json={
                        "basic_data": basic_data,
                        "current_step": "documents"
                    }
                )
                
                # Test suggestions endpoint
                request_data = {
                    "case_id": case_id,
                    "form_code": "H-1B",
                    "current_form_data": {}
                }
                
                suggestions_response = self.session.post(
                    f"{API_BASE}/intelligent-forms/suggestions",
                    json=request_data
                )
                
                if suggestions_response.status_code == 200:
                    suggestions_result = suggestions_response.json()
                    suggestions = suggestions_result.get('suggestions', [])
                    
                    # Check if demo data is used
                    has_demo_suggestions = len(suggestions) > 0
                    
                    # Look for expected demo data
                    demo_name_found = False
                    demo_nationality_found = False
                    
                    for suggestion in suggestions:
                        if suggestion.get('field_id') == 'full_name':
                            suggested_value = suggestion.get('suggested_value', '')
                            if 'José da Silva Santos' in suggested_value:
                                demo_name_found = True
                        elif suggestion.get('field_id') == 'nationality':
                            suggested_value = suggestion.get('suggested_value', '')
                            if 'BRASILEIRO' in suggested_value:
                                demo_nationality_found = True
                    
                    self.log_test(
                        "Caso A - Sugestões com Dados Demo",
                        has_demo_suggestions,
                        f"Geradas {len(suggestions)} sugestões usando dados de demonstração",
                        {
                            "total_suggestions": len(suggestions),
                            "demo_name_found": demo_name_found,
                            "demo_nationality_found": demo_nationality_found,
                            "sample_suggestions": suggestions[:3] if suggestions else []
                        }
                    )
                    
                    # Check for expected demo values
                    expected_demo_found = demo_name_found or demo_nationality_found
                    
                    self.log_test(
                        "Caso A - Dados Demo Esperados (José da Silva Santos / BRASILEIRO)",
                        expected_demo_found,
                        f"Nome demo: {demo_name_found}, Nacionalidade demo: {demo_nationality_found}",
                        {
                            "demo_name_found": demo_name_found,
                            "demo_nationality_found": demo_nationality_found
                        }
                    )
                    
                    return suggestions_result
                else:
                    self.log_test(
                        "Caso A - Status 200 OK",
                        False,
                        f"HTTP {suggestions_response.status_code}: {suggestions_response.text[:200]}"
                    )
                    return None
            else:
                self.log_test(
                    "Caso A - Criação de Caso",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Caso A - Exception",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_case_b_with_validated_documents(self):
        """CASO B: Com documentos validados - deve extrair dados reais"""
        print("🎯 CASO B: Com documentos validados")
        
        try:
            # Create a test case with documents
            case_data = {
                "form_code": "H-1B",
                "session_token": f"test_session_{uuid.uuid4().hex[:8]}"
            }
            
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=case_data
            )
            
            if response.status_code == 200:
                result = response.json()
                case_id = result.get('case', {}).get('case_id')
                
                # Add basic data
                basic_data = {
                    "firstName": "Carlos",
                    "lastName": "Silva",
                    "email": "carlos.silva@test.com"
                }
                
                # Update case with basic data
                update_response = self.session.patch(
                    f"{API_BASE}/auto-application/case/{case_id}",
                    json={
                        "basic_data": basic_data,
                        "current_step": "documents"
                    }
                )
                
                # Now create a document in the documents collection for this case
                # This simulates having validated documents
                document_data = {
                    "case_id": case_id,
                    "document_type": "passport",
                    "ai_analysis": {
                        "extracted_data": {
                            "full_name": "CARLOS EDUARDO SILVA",
                            "nationality": "BRASILEIRO",
                            "passport_number": "YC792396",
                            "place_of_birth": "CANOAS, RS",
                            "issue_date": "2018-09-13",
                            "expiry_date": "2028-09-13",
                            "issuing_authority": "POLÍCIA FEDERAL"
                        },
                        "valid": True,
                        "completeness": 95
                    },
                    "status": "approved",
                    "created_at": datetime.now().isoformat()
                }
                
                # Insert document directly into database (simulating validated document)
                # Since we can't access the database directly, we'll simulate this by adding
                # document_analysis_results to the case
                document_analysis = [
                    {
                        "document_type": "passport",
                        "valid": True,
                        "extracted_data": {
                            "full_name": "CARLOS EDUARDO SILVA",
                            "nationality": "BRASILEIRO",
                            "passport_number": "YC792396",
                            "place_of_birth": "CANOAS, RS",
                            "issue_date": "2018-09-13",
                            "expiry_date": "2028-09-13",
                            "issuing_authority": "POLÍCIA FEDERAL"
                        }
                    }
                ]
                
                # Add document analysis to case
                self.session.patch(
                    f"{API_BASE}/auto-application/case/{case_id}",
                    json={
                        "document_analysis_results": document_analysis
                    }
                )
                
                # Test suggestions endpoint
                request_data = {
                    "case_id": case_id,
                    "form_code": "H-1B",
                    "current_form_data": {}
                }
                
                suggestions_response = self.session.post(
                    f"{API_BASE}/intelligent-forms/suggestions",
                    json=request_data
                )
                
                if suggestions_response.status_code == 200:
                    suggestions_result = suggestions_response.json()
                    suggestions = suggestions_result.get('suggestions', [])
                    
                    # Check if real document data is extracted
                    has_suggestions = len(suggestions) > 0
                    
                    # Look for expected real data
                    real_name_found = False
                    real_nationality_found = False
                    real_passport_found = False
                    
                    for suggestion in suggestions:
                        field_id = suggestion.get('field_id', '')
                        suggested_value = suggestion.get('suggested_value', '')
                        
                        if field_id == 'full_name' and 'CARLOS EDUARDO SILVA' in suggested_value:
                            real_name_found = True
                        elif field_id == 'nationality' and 'BRASILEIRO' in suggested_value:
                            real_nationality_found = True
                        elif field_id == 'passport_number' and 'YC792396' in suggested_value:
                            real_passport_found = True
                    
                    self.log_test(
                        "Caso B - Sugestões com Dados Reais",
                        has_suggestions,
                        f"Geradas {len(suggestions)} sugestões baseadas em documentos validados",
                        {
                            "total_suggestions": len(suggestions),
                            "real_name_found": real_name_found,
                            "real_nationality_found": real_nationality_found,
                            "real_passport_found": real_passport_found,
                            "sample_suggestions": suggestions[:3] if suggestions else []
                        }
                    )
                    
                    # Check for expected real values
                    expected_real_found = real_name_found or real_nationality_found or real_passport_found
                    
                    self.log_test(
                        "Caso B - Dados Reais Extraídos (CARLOS EDUARDO SILVA / BRASILEIRO / YC792396)",
                        expected_real_found,
                        f"Nome: {real_name_found}, Nacionalidade: {real_nationality_found}, Passaporte: {real_passport_found}",
                        {
                            "real_name_found": real_name_found,
                            "real_nationality_found": real_nationality_found,
                            "real_passport_found": real_passport_found
                        }
                    )
                    
                    return suggestions_result
                else:
                    self.log_test(
                        "Caso B - Status 200 OK",
                        False,
                        f"HTTP {suggestions_response.status_code}: {suggestions_response.text[:200]}"
                    )
                    return None
            else:
                self.log_test(
                    "Caso B - Criação de Caso",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Caso B - Exception",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_auto_fill_endpoint(self):
        """Teste específico do endpoint auto-fill"""
        print("🚀 TESTE: Auto-Fill com Documentos")
        
        try:
            # Create case with documents (reuse logic from Case B)
            case_data = {
                "form_code": "H-1B",
                "session_token": f"test_session_{uuid.uuid4().hex[:8]}"
            }
            
            response = self.session.post(
                f"{API_BASE}/auto-application/start",
                json=case_data
            )
            
            if response.status_code == 200:
                result = response.json()
                case_id = result.get('case', {}).get('case_id')
                
                # Add document analysis
                document_analysis = [
                    {
                        "document_type": "passport",
                        "valid": True,
                        "extracted_data": {
                            "full_name": "MARIA SANTOS OLIVEIRA",
                            "nationality": "BRASILEIRO",
                            "passport_number": "AB123456",
                            "place_of_birth": "RIO DE JANEIRO, RJ"
                        }
                    }
                ]
                
                self.session.patch(
                    f"{API_BASE}/auto-application/case/{case_id}",
                    json={
                        "document_analysis_results": document_analysis,
                        "basic_data": {"firstName": "Maria", "lastName": "Santos"}
                    }
                )
                
                # Test auto-fill endpoint
                request_data = {
                    "case_id": case_id,
                    "form_code": "H-1B"
                }
                
                auto_fill_response = self.session.post(
                    f"{API_BASE}/intelligent-forms/auto-fill",
                    json=request_data
                )
                
                if auto_fill_response.status_code == 200:
                    auto_fill_result = auto_fill_response.json()
                    
                    # Check auto-filled data
                    auto_filled_data = auto_fill_result.get('auto_filled_data', {})
                    high_confidence_fields = auto_fill_result.get('high_confidence_fields', [])
                    confidence_stats = auto_fill_result.get('confidence_stats', {})
                    
                    has_auto_filled = len(auto_filled_data) > 0
                    has_high_confidence = len(high_confidence_fields) > 0
                    high_confidence_count = confidence_stats.get('high_confidence', 0)
                    
                    self.log_test(
                        "Auto-Fill - Campos Preenchidos Automaticamente",
                        has_auto_filled,
                        f"Preenchidos {len(auto_filled_data)} campos automaticamente",
                        {
                            "auto_filled_count": len(auto_filled_data),
                            "auto_filled_fields": list(auto_filled_data.keys()),
                            "sample_values": {k: v for k, v in list(auto_filled_data.items())[:3]}
                        }
                    )
                    
                    self.log_test(
                        "Auto-Fill - Campos de Alta Confiança (85%+)",
                        has_high_confidence,
                        f"Identificados {len(high_confidence_fields)} campos com alta confiança",
                        {
                            "high_confidence_count": len(high_confidence_fields),
                            "high_confidence_fields": high_confidence_fields,
                            "confidence_stats": confidence_stats
                        }
                    )
                    
                    # Check if confidence stats show high confidence > 0
                    self.log_test(
                        "Auto-Fill - Estatísticas de Confiança > 0",
                        high_confidence_count > 0,
                        f"Campos de alta confiança: {high_confidence_count}",
                        confidence_stats
                    )
                    
                    return auto_fill_result
                else:
                    self.log_test(
                        "Auto-Fill - Status 200 OK",
                        False,
                        f"HTTP {auto_fill_response.status_code}: {auto_fill_response.text[:200]}"
                    )
                    return None
            else:
                self.log_test(
                    "Auto-Fill - Criação de Caso",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Auto-Fill - Exception",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def test_dra_ana_validation(self):
        """Teste específico da validação com Dra. Ana"""
        print("👩‍⚕️ TESTE: Validação com Dra. Ana")
        
        try:
            # Test with form data that should trigger validation
            form_data = {
                "full_name": "Carlos Eduardo Silva",
                "date_of_birth": "05/15/1990",
                "place_of_birth": "São Paulo, SP, Brasil",
                "passport_number": "YC792396",
                "passport_country": "Brazil",
                "current_address": "Rua das Flores, 123, São Paulo, SP",
                "phone": "+55 11 99999-9999",
                "email": "carlos.silva@test.com",
                "employer_name": "TechCorp Inc.",
                "job_title": "Software Engineer",
                "specialty_occupation": "Computer Systems Analyst"
            }
            
            request_data = {
                "form_data": form_data,
                "visa_type": "H-1B",
                "step_id": "form_review"
            }
            
            response = self.session.post(
                f"{API_BASE}/intelligent-forms/validate",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                validation_result = result.get('validation_result', {})
                
                # Check validation structure
                has_validation_fields = all(field in validation_result for field in 
                                          ['is_valid', 'errors', 'warnings', 'completeness_score'])
                
                completeness_score = validation_result.get('completeness_score', 0)
                is_valid = validation_result.get('is_valid', False)
                errors = validation_result.get('errors', [])
                warnings = validation_result.get('warnings', [])
                
                self.log_test(
                    "Dra. Ana - Estrutura de Validação Completa",
                    has_validation_fields,
                    f"Campos de validação presentes: {list(validation_result.keys())}",
                    {
                        "validation_fields": list(validation_result.keys()),
                        "completeness_score": completeness_score,
                        "is_valid": is_valid,
                        "errors_count": len(errors),
                        "warnings_count": len(warnings)
                    }
                )
                
                # Check if Dra. Ana is working (should have some score or feedback)
                dra_ana_working = completeness_score > 0 or len(errors) > 0 or len(warnings) > 0
                
                self.log_test(
                    "Dra. Ana - Funcionando (Score > 0 ou Feedback)",
                    dra_ana_working,
                    f"Score: {completeness_score}, Erros: {len(errors)}, Avisos: {len(warnings)}",
                    {
                        "completeness_score": completeness_score,
                        "has_feedback": dra_ana_working,
                        "agent": result.get('agent', '')
                    }
                )
                
                return result
            else:
                self.log_test(
                    "Dra. Ana - Status 200 OK",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.log_test(
                "Dra. Ana - Exception",
                False,
                f"Exception: {str(e)}"
            )
            return None

    def run_focused_tests(self):
        """Executa os testes focados conforme solicitação do usuário"""
        print("🎯 INICIANDO TESTES FOCADOS DO SISTEMA INTELIGENTE DE FORMULÁRIOS")
        print("=" * 80)
        print("FOCO: Testar correções implementadas")
        print("1. ✅ Corrigido acesso aos documentos - agora busca na coleção `documents` por `case_id`")
        print("2. ✅ Melhorada extração de dados com múltiplas variações de campos")
        print("3. ✅ Adicionados dados de demonstração quando não há documentos")
        print("4. ✅ Logs detalhados para debug")
        print("=" * 80)
        
        # Execute focused tests
        self.test_case_a_no_validated_documents()
        self.test_case_b_with_validated_documents()
        self.test_auto_fill_endpoint()
        self.test_dra_ana_validation()
        
        # Generate summary
        self.generate_focused_summary()
    
    def generate_focused_summary(self):
        """Gera resumo dos testes focados"""
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS TESTES FOCADOS - CORREÇÕES IMPLEMENTADAS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 ESTATÍSTICAS:")
        print(f"   Total de testes: {total_tests}")
        print(f"   ✅ Aprovados: {passed_tests}")
        print(f"   ❌ Falharam: {failed_tests}")
        print(f"   📊 Taxa de sucesso: {success_rate:.1f}%")
        
        print(f"\n🎯 VALIDAÇÕES CRÍTICAS:")
        critical_validations = [
            "Caso A - Sugestões com Dados Demo",
            "Caso B - Sugestões com Dados Reais", 
            "Auto-Fill - Campos Preenchidos Automaticamente",
            "Auto-Fill - Campos de Alta Confiança (85%+)",
            "Dra. Ana - Funcionando (Score > 0 ou Feedback)"
        ]
        
        for validation in critical_validations:
            test_result = next((r for r in self.test_results if validation in r['test']), None)
            if test_result:
                status = "✅" if test_result['success'] else "❌"
                print(f"   {status} {validation}")
        
        if failed_tests > 0:
            print(f"\n❌ TESTES QUE FALHARAM:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "=" * 80)
        
        # Final assessment
        if success_rate >= 80:
            print("🎉 CORREÇÕES FUNCIONANDO CORRETAMENTE!")
        elif success_rate >= 60:
            print("⚠️ CORREÇÕES PARCIALMENTE FUNCIONANDO - NECESSÁRIO AJUSTES")
        else:
            print("❌ CORREÇÕES NÃO ESTÃO FUNCIONANDO - NECESSÁRIO INVESTIGAÇÃO")

if __name__ == "__main__":
    tester = FocusedIntelligentFormsTester()
    tester.run_focused_tests()