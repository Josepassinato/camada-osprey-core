#!/usr/bin/env python3
"""
I-539 SPECIFIC BACKEND TESTING
Testing the I-539 implementation as requested by the user
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://iaimmigration.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎯 I-539 TESTING TARGET: {BACKEND_URL}")
print("="*80)

class I539Tester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'I539Tester/1.0'
        })
        self.auth_token = None
        self.test_email = f"i539.test.{uuid.uuid4().hex[:6]}@gmail.com"
        self.test_password = "I539Test2024!"
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: any = None):
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
            print(f"    🔍 Response: {str(response_data)[:300]}...")
        print()
    
    def setup_auth(self):
        """Setup authentication for testing"""
        print("🔐 Setting up authentication...")
        
        # Try to signup
        signup_data = {
            "email": self.test_email,
            "password": self.test_password,
            "first_name": "I539",
            "last_name": "Tester",
            "phone": "+5511999999999"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/signup", json=signup_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
            elif response.status_code == 400 and "already registered" in response.text:
                # Try login
                login_data = {
                    "email": self.test_email,
                    "password": self.test_password
                }
                login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    data = login_response.json()
                    self.auth_token = data.get('token')
            
            if self.auth_token:
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                print(f"    ✅ Authentication successful")
            else:
                print(f"    ❌ Authentication failed")
                
        except Exception as e:
            print(f"    ❌ Authentication error: {str(e)}")
    
    def test_i539_uscis_form_definition(self):
        """Test 1: Verificar se USCISForm.I539 está definido corretamente"""
        print("📋 TESTE 1: Endpoint de formulários - USCISForm.I539")
        
        try:
            # Test creating a case with I-539 form
            case_data = {}
            
            response = self.session.post(f"{API_BASE}/auto-application/start", json=case_data)
            
            if response.status_code == 200:
                data = response.json()
                case_info = data.get('case', {})
                case_id = case_info.get('case_id')
                
                if case_id:
                    # Test updating case with I-539
                    update_data = {
                        "form_code": "I-539",
                        "status": "form_selected"
                    }
                    
                    update_response = self.session.put(
                        f"{API_BASE}/auto-application/case/{case_id}",
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        update_result = update_response.json()
                        i539_accepted = update_result.get('form_code') == 'I-539'
                        
                        self.log_test(
                            "I-539 USCIS Form Definition",
                            i539_accepted,
                            f"I-539 aceito na criação de casos: {'✓' if i539_accepted else '✗'}",
                            {"form_code": update_result.get('form_code'), "case_id": case_id}
                        )
                        return case_id
                    else:
                        self.log_test(
                            "I-539 USCIS Form Definition",
                            False,
                            f"Falha ao atualizar caso com I-539: HTTP {update_response.status_code}",
                            update_response.text[:200]
                        )
                else:
                    self.log_test(
                        "I-539 USCIS Form Definition",
                        False,
                        "Nenhum case_id retornado"
                    )
            else:
                self.log_test(
                    "I-539 USCIS Form Definition",
                    False,
                    f"Falha ao criar caso: HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("I-539 USCIS Form Definition", False, f"Exception: {str(e)}")
        
        return None
    
    def test_i539_owl_agent_fields(self):
        """Test 2: Campos do Owl Agent - verificar campos específicos do I-539"""
        print("🦉 TESTE 2: Campos do Owl Agent I-539")
        
        try:
            # Start an I-539 session
            session_data = {
                "case_id": f"I539-FIELDS-{uuid.uuid4().hex[:8].upper()}",
                "visa_type": "I-539",
                "language": "pt"
            }
            
            response = self.session.post(f"{API_BASE}/owl-agent/start-session", json=session_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if I-539 is accepted as visa_type
                visa_type_accepted = data.get('visa_type') == 'I-539'
                has_session_id = 'session_id' in data and data['session_id']
                
                session_id = data.get('session_id')
                
                # Expected I-539 specific fields
                expected_fields = [
                    'current_status', 'i94_number', 'entry_date',
                    'authorized_stay_until', 'extension_until', 'extension_reason',
                    'passport_number', 'passport_expiry', 'financial_support', 'us_address'
                ]
                
                fields_found = []
                
                # Test field guidance for I-539 specific fields
                if session_id:
                    for field in expected_fields[:5]:  # Test first 5 fields
                        try:
                            field_response = self.session.get(
                                f"{API_BASE}/owl-agent/field-guidance/{session_id}/{field}"
                            )
                            if field_response.status_code == 200:
                                field_data = field_response.json()
                                if field_data and 'question_pt' in field_data:
                                    fields_found.append(field)
                        except:
                            pass
                
                fields_available = len(fields_found) >= 3  # At least 3 fields should work
                
                success = visa_type_accepted and has_session_id and fields_available
                
                self.log_test(
                    "I-539 Owl Agent Fields",
                    success,
                    f"Visa type I-539: {'✓' if visa_type_accepted else '✗'}, Session: {'✓' if has_session_id else '✗'}, Campos encontrados: {len(fields_found)}/5",
                    {
                        "visa_type": data.get('visa_type'),
                        "session_id": session_id,
                        "fields_found": fields_found,
                        "expected_fields": expected_fields
                    }
                )
                return session_id
            else:
                self.log_test(
                    "I-539 Owl Agent Fields",
                    False,
                    f"Falha ao iniciar sessão I-539: HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("I-539 Owl Agent Fields", False, f"Exception: {str(e)}")
        
        return None
    
    def test_i539_session_creation(self):
        """Test 3: Teste de criação de sessão com visa_type='I-539'"""
        print("🦉 TESTE 3: Criação de sessão I-539")
        
        try:
            session_data = {
                "case_id": f"I539-SESSION-{uuid.uuid4().hex[:8].upper()}",
                "visa_type": "I-539",
                "language": "pt"
            }
            
            response = self.session.post(f"{API_BASE}/owl-agent/start-session", json=session_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify I-539 specific response
                correct_visa_type = data.get('visa_type') == 'I-539'
                has_session_id = 'session_id' in data and data['session_id']
                correct_language = data.get('language') == 'pt'
                
                # Check for I-539 specific welcome message
                welcome_msg = data.get('welcome_message', '').lower()
                has_i539_welcome = 'i-539' in welcome_msg and ('extensão' in welcome_msg or 'extension' in welcome_msg)
                
                # Check for I-539 specific fields in response
                fields_data = data.get('fields', [])
                current_field = data.get('current_field', {})
                
                has_i539_fields = any(
                    field_id in str(fields_data) + str(current_field) 
                    for field_id in ['current_status', 'i94_number', 'extension_reason']
                )
                
                success = correct_visa_type and has_session_id and correct_language
                
                self.log_test(
                    "I-539 Session Creation",
                    success,
                    f"Visa I-539: {'✓' if correct_visa_type else '✗'}, Session ID: {'✓' if has_session_id else '✗'}, Português: {'✓' if correct_language else '✗'}, Mensagem específica: {'✓' if has_i539_welcome else '✗'}",
                    {
                        "visa_type": data.get('visa_type'),
                        "session_id": data.get('session_id'),
                        "language": data.get('language'),
                        "has_welcome": has_i539_welcome,
                        "has_fields": has_i539_fields
                    }
                )
                return data.get('session_id')
            else:
                self.log_test(
                    "I-539 Session Creation",
                    False,
                    f"HTTP {response.status_code}",
                    response.text[:200]
                )
        except Exception as e:
            self.log_test("I-539 Session Creation", False, f"Exception: {str(e)}")
        
        return None
    
    def test_i539_field_validation(self, session_id):
        """Test 4: Teste de validação de campos I-539"""
        print("🔍 TESTE 4: Validação de campos I-539")
        
        if not session_id:
            self.log_test("I-539 Field Validation", False, "Nenhum session_id disponível")
            return
        
        try:
            # Test validation for I-539 specific fields
            validation_tests = [
                {
                    "field_id": "current_status",
                    "valid_value": "B-2",
                    "invalid_value": "INVALID_STATUS_123"
                },
                {
                    "field_id": "i94_number", 
                    "valid_value": "12345678901",
                    "invalid_value": "123"  # Too short
                },
                {
                    "field_id": "extension_reason",
                    "valid_value": "Preciso estender minha permanência para continuar o tratamento médico no Hospital ABC, que está previsto para durar mais 3 meses conforme atestado médico anexado.",
                    "invalid_value": "Quero ficar"  # Too short
                }
            ]
            
            validation_results = []
            
            for test in validation_tests:
                try:
                    # Test valid value
                    valid_data = {
                        "session_id": session_id,
                        "field_id": test["field_id"],
                        "value": test["valid_value"]
                    }
                    
                    valid_response = self.session.post(f"{API_BASE}/owl-agent/validate-field", json=valid_data)
                    
                    # Test invalid value
                    invalid_data = {
                        "session_id": session_id,
                        "field_id": test["field_id"],
                        "value": test["invalid_value"]
                    }
                    
                    invalid_response = self.session.post(f"{API_BASE}/owl-agent/validate-field", json=invalid_data)
                    
                    # Check validation results
                    valid_accepted = valid_response.status_code == 200
                    if valid_accepted and valid_response.json():
                        valid_result = valid_response.json()
                        valid_accepted = valid_result.get('valid', False) or valid_result.get('score', 0) > 50
                    
                    invalid_rejected = True
                    if invalid_response.status_code == 200 and invalid_response.json():
                        invalid_result = invalid_response.json()
                        invalid_rejected = not invalid_result.get('valid', True) or invalid_result.get('score', 100) < 50
                    
                    field_validation_ok = valid_accepted and invalid_rejected
                    validation_results.append({
                        "field": test["field_id"],
                        "valid_accepted": valid_accepted,
                        "invalid_rejected": invalid_rejected,
                        "overall": field_validation_ok
                    })
                    
                except Exception as field_error:
                    validation_results.append({
                        "field": test["field_id"],
                        "valid_accepted": False,
                        "invalid_rejected": False,
                        "overall": False,
                        "error": str(field_error)
                    })
            
            # Overall validation success
            successful_validations = sum(1 for r in validation_results if r["overall"])
            validation_success = successful_validations >= len(validation_results) // 2
            
            self.log_test(
                "I-539 Field Validation",
                validation_success,
                f"Validações bem-sucedidas: {successful_validations}/{len(validation_results)}",
                {
                    "session_id": session_id,
                    "validation_results": validation_results,
                    "success_rate": f"{successful_validations}/{len(validation_results)}"
                }
            )
            
        except Exception as e:
            self.log_test("I-539 Field Validation", False, f"Exception: {str(e)}")
    
    def test_i539_pricing_structure(self):
        """Test 5: Teste de taxas I-539 ($370 + $85 biometria)"""
        print("💰 TESTE 5: Estrutura de taxas I-539")
        
        try:
            # Create a case for pricing test
            case_response = self.session.post(f"{API_BASE}/auto-application/start", json={})
            
            if case_response.status_code == 200:
                case_info = case_response.json().get('case', {})
                case_id = case_info.get('case_id')
                
                if case_id:
                    # Update case to I-539
                    update_data = {
                        "form_code": "I-539",
                        "status": "form_selected"
                    }
                    
                    update_response = self.session.put(
                        f"{API_BASE}/auto-application/case/{case_id}",
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        # Try to get case finalizer information
                        finalizer_response = self.session.post(
                            f"{API_BASE}/case-finalizer/complete",
                            json={"case_id": case_id}
                        )
                        
                        pricing_found = False
                        correct_amounts = False
                        
                        if finalizer_response.status_code == 200:
                            finalizer_data = finalizer_response.json()
                            
                            # Look for I-539 pricing in the response
                            response_text = str(finalizer_data).lower()
                            pricing_found = 'i-539' in response_text and ('370' in response_text or '85' in response_text)
                            
                            # Check for correct amounts ($370 base + $85 biometrics)
                            fees_data = finalizer_data.get('fees', {})
                            if isinstance(fees_data, dict):
                                # Look for I-539 specific fees
                                i539_fees = fees_data.get('I-539_extension', []) or fees_data.get('I-539_change', [])
                                if i539_fees:
                                    amounts = [fee.get('amount', 0) for fee in i539_fees if isinstance(fee, dict)]
                                    correct_amounts = 370 in amounts and 85 in amounts
                            
                            # Alternative check in fee structure
                            if not correct_amounts:
                                all_text = str(finalizer_data)
                                correct_amounts = '370' in all_text and '85' in all_text and 'i-539' in all_text.lower()
                        
                        success = pricing_found and correct_amounts
                        
                        self.log_test(
                            "I-539 Pricing Structure",
                            success,
                            f"Taxas I-539 encontradas: {'✓' if pricing_found else '✗'}, Valores corretos ($370 + $85): {'✓' if correct_amounts else '✗'}",
                            {
                                "case_id": case_id,
                                "pricing_found": pricing_found,
                                "correct_amounts": correct_amounts,
                                "finalizer_status": finalizer_response.status_code
                            }
                        )
                    else:
                        self.log_test(
                            "I-539 Pricing Structure",
                            False,
                            f"Falha ao atualizar caso para I-539: HTTP {update_response.status_code}",
                            update_response.text[:200]
                        )
                else:
                    self.log_test("I-539 Pricing Structure", False, "Nenhum case_id retornado")
            else:
                self.log_test(
                    "I-539 Pricing Structure",
                    False,
                    f"Falha ao criar caso: HTTP {case_response.status_code}",
                    case_response.text[:200]
                )
                
        except Exception as e:
            self.log_test("I-539 Pricing Structure", False, f"Exception: {str(e)}")
    
    def run_i539_tests(self):
        """Execute all I-539 specific tests"""
        print("🚀 INICIANDO TESTES ESPECÍFICOS I-539 BACKEND")
        print("="*80)
        
        # Setup authentication
        self.setup_auth()
        
        # Run tests
        print("\n📋 EXECUTANDO TESTES I-539...")
        
        # Test 1: USCIS Form Definition
        case_id = self.test_i539_uscis_form_definition()
        
        # Test 2: Owl Agent Fields
        session_id = self.test_i539_owl_agent_fields()
        
        # Test 3: Session Creation
        if not session_id:
            session_id = self.test_i539_session_creation()
        
        # Test 4: Field Validation
        self.test_i539_field_validation(session_id)
        
        # Test 5: Pricing Structure
        self.test_i539_pricing_structure()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 RESUMO DOS TESTES I-539 BACKEND")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 ESTATÍSTICAS:")
        print(f"   Total de Testes: {total_tests}")
        print(f"   ✅ Aprovados: {passed_tests}")
        print(f"   ❌ Falharam: {failed_tests}")
        print(f"   📈 Taxa de Sucesso: {success_rate:.1f}%")
        print()
        
        print("📋 RESULTADOS DETALHADOS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}")
            if result['details']:
                print(f"      📋 {result['details']}")
        print()
        
        # Assessment
        if success_rate >= 80:
            print("🎉 I-539 IMPLEMENTAÇÃO APROVADA!")
            print("   ✅ Taxa de sucesso ≥80%")
            print("   ✅ Funcionalidades I-539 operacionais")
        elif success_rate >= 60:
            print("⚠️ I-539 IMPLEMENTAÇÃO PARCIALMENTE FUNCIONAL")
            print("   ⚠️ Algumas correções necessárias")
            print("   ⚠️ Revisar falhas identificadas")
        else:
            print("❌ I-539 IMPLEMENTAÇÃO NECESSITA CORREÇÕES")
            print("   ❌ Taxa de sucesso <60%")
            print("   ❌ Correções críticas necessárias")
        
        print("="*80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "i539_ready": success_rate >= 80
        }

if __name__ == "__main__":
    tester = I539Tester()
    tester.run_i539_tests()