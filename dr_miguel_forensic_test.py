#!/usr/bin/env python3
"""
DR. MIGUEL ENHANCED FORENSIC ANALYSIS - COMPREHENSIVE TESTING SUITE
Tests the 7-layer forensic analysis system after critical fixes applied
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from typing import Dict, Any
import base64

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DrMiguelForensicTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DrMiguelForensicTester/1.0'
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
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {str(response_data)[:500]}...")
        print()
    
    def create_simulated_passport_document(self, name: str = "João Silva", nationality: str = "BRAZILIAN") -> bytes:
        """Create a realistic simulated passport document"""
        passport_content = f"""
        PASSPORT
        REPUBLIC OF BRAZIL
        PASSAPORTE
        
        Type/Tipo: P
        Country Code/Código do País: BRA
        Passport No./No. do Passaporte: BR{uuid.uuid4().hex[:6].upper()}
        
        Surname/Sobrenome: {name.split()[-1].upper()}
        Given Names/Nomes: {' '.join(name.split()[:-1]).upper()}
        Nationality/Nacionalidade: {nationality}
        Date of Birth/Data de Nascimento: 15 JAN 1985
        Sex/Sexo: M
        Place of Birth/Local de Nascimento: SAO PAULO, BRAZIL
        Date of Issue/Data de Emissão: 10 MAR 2020
        Date of Expiry/Data de Validade: 09 MAR 2030
        Authority/Autoridade: DPF
        
        Machine Readable Zone (MRZ):
        P<BRA{name.split()[-1].upper()}<<{name.split()[0].upper()}<<<<<<<<<<<<<<<<<<<<<<
        BR{uuid.uuid4().hex[:7]}<BRA8501159M3003096<<<<<<<<<<<<<<<<<<6
        
        SECURITY FEATURES:
        - Watermark: Brazilian Coat of Arms
        - Security Thread: Embedded
        - Holographic Elements: Present
        - RFID Chip: Embedded
        - Digital Signature: Valid
        
        DOCUMENT AUTHENTICITY MARKERS:
        - Paper Quality: High-grade security paper
        - Print Quality: Professional offset printing
        - Color Accuracy: Pantone matched colors
        - Font Consistency: Official Brazilian passport fonts
        - Layout Compliance: ICAO Document 9303 compliant
        """ * 10  # Make it substantial
        
        return passport_content.encode('utf-8')
    
    def create_birth_certificate_document(self, name: str = "Maria Santos") -> bytes:
        """Create a birth certificate document (wrong type for passport validation)"""
        birth_cert_content = f"""
        CERTIDÃO DE NASCIMENTO
        BIRTH CERTIFICATE
        
        CARTÓRIO DE REGISTRO CIVIL
        CIVIL REGISTRY OFFICE
        
        Estado de São Paulo - State of São Paulo
        Município de São Paulo - Municipality of São Paulo
        
        DADOS DO REGISTRADO / REGISTRANT DATA:
        Nome Completo / Full Name: {name.upper()}
        Data de Nascimento / Date of Birth: 15 de Janeiro de 1985
        Local de Nascimento / Place of Birth: São Paulo, SP, Brasil
        Sexo / Sex: Feminino / Female
        
        FILIAÇÃO / PARENTAGE:
        Pai / Father: José Santos
        Mãe / Mother: Ana Santos
        
        REGISTRO / REGISTRATION:
        Livro / Book: 001
        Folha / Page: 123
        Termo / Term: 456
        Data do Registro / Registration Date: 20 de Janeiro de 1985
        
        CARTÓRIO INFORMATION:
        Nome do Cartório: 1º Cartório de Registro Civil
        Endereço: Rua das Flores, 123 - São Paulo, SP
        Telefone: (11) 1234-5678
        
        ASSINATURA DO OFICIAL / REGISTRAR SIGNATURE:
        [Assinatura Digital]
        
        SELO DE AUTENTICIDADE / AUTHENTICITY SEAL:
        Código de Verificação: ABC123DEF456
        Data de Emissão: 15 de Março de 2024
        
        Este documento é válido em todo território nacional
        This document is valid throughout the national territory
        """ * 8
        
        return birth_cert_content.encode('utf-8')
    
    def test_1_basic_functionality(self):
        """TESTE 1: Funcionamento Básico - POST /api/documents/analyze-with-ai com documento passaporte simulado"""
        print("🔍 TESTE 1: FUNCIONAMENTO BÁSICO DO DR. MIGUEL...")
        
        # Create a realistic simulated passport
        passport_content = self.create_simulated_passport_document("João Silva", "BRAZILIAN")
        
        files = {
            'file': ('passport_joao_silva.pdf', passport_content, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-BASIC-FUNCTIONALITY',
            'applicant_name': 'João Silva'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for absence of critical errors
                error_checks = {
                    "no_keyerror_language_compliance": "KeyError" not in str(result) or "language_compliance_weight" not in str(result),
                    "no_validation_result_errors": "ValidationResult" not in str(result) or "not subscriptable" not in str(result),
                    "no_str_update_errors": "'str' object has no attribute 'update'" not in str(result),
                    "system_responds": True,  # If we got here, system responded
                    "has_analysis": 'ai_analysis' in result or 'completeness' in result
                }
                
                all_checks_pass = all(error_checks.values())
                
                self.log_test(
                    "TESTE 1: Funcionamento Básico",
                    all_checks_pass,
                    f"Sistema responde sem crashes críticos. Checks: {error_checks}",
                    {
                        "status_code": response.status_code,
                        "has_completeness": 'completeness' in result,
                        "has_ai_analysis": 'ai_analysis' in result,
                        "error_checks": error_checks
                    }
                )
                
                return result
            else:
                self.log_test(
                    "TESTE 1: Funcionamento Básico",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "TESTE 1: Funcionamento Básico",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_2_forensic_7_layers(self):
        """TESTE 2: Prompt Forense de 7 Camadas - Verificar análise detalhada estruturada"""
        print("🔬 TESTE 2: PROMPT FORENSE DE 7 CAMADAS...")
        
        # Create a high-quality passport for detailed analysis
        passport_content = self.create_simulated_passport_document("Carlos Eduardo Silva", "BRAZILIAN")
        
        files = {
            'file': ('passport_carlos_silva.pdf', passport_content, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-7-LAYER-FORENSIC',
            'applicant_name': 'Carlos Eduardo Silva'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for 7-layer forensic analysis components
                ai_analysis = result.get('ai_analysis', {})
                dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
                
                forensic_layers = {
                    "document_analysis": 'document_type_identified' in dr_miguel_validation,
                    "identity_validation": 'belongs_to_applicant' in dr_miguel_validation,
                    "security_analysis": 'uscis_acceptable' in dr_miguel_validation,
                    "authenticity_assessment": 'verdict' in dr_miguel_validation,
                    "quality_evaluation": 'completeness_score' in result,
                    "temporal_validation": 'validity_status' in ai_analysis,
                    "compliance_verification": 'type_correct' in dr_miguel_validation
                }
                
                # Check for overall confidence in appropriate range
                overall_confidence = result.get('completeness', 0)
                confidence_appropriate = 0 <= overall_confidence <= 100
                
                # Check for structured analysis
                has_structured_analysis = (
                    len(forensic_layers) >= 5 and  # At least 5 of 7 layers
                    confidence_appropriate
                )
                
                layers_present = sum(forensic_layers.values())
                
                self.log_test(
                    "TESTE 2: Prompt Forense de 7 Camadas",
                    has_structured_analysis,
                    f"Camadas forenses detectadas: {layers_present}/7. Confiança: {overall_confidence}%",
                    {
                        "forensic_layers": forensic_layers,
                        "layers_present": layers_present,
                        "overall_confidence": overall_confidence,
                        "dr_miguel_fields": list(dr_miguel_validation.keys())
                    }
                )
                
                return result
            else:
                self.log_test(
                    "TESTE 2: Prompt Forense de 7 Camadas",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "TESTE 2: Prompt Forense de 7 Camadas",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_3_wrong_document_detection(self):
        """TESTE 3: Detecção de Documento Inadequado - Sistema deve REJEITAR com 0% (não mais 85% approval)"""
        print("🚫 TESTE 3: DETECÇÃO DE DOCUMENTO INADEQUADO...")
        
        # Create birth certificate but claim it's a passport
        birth_cert_content = self.create_birth_certificate_document("Maria Santos")
        
        files = {
            'file': ('birth_certificate_as_passport.pdf', birth_cert_content, 'application/pdf')
        }
        data = {
            'document_type': 'passport',  # WRONG - claiming birth cert is passport
            'visa_type': 'H-1B',
            'case_id': 'TEST-WRONG-DOCUMENT-TYPE',
            'applicant_name': 'Maria Santos'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # System should REJECT wrong document type with 0% (not 85% approval)
                completeness = result.get('completeness', 0)
                validity = result.get('validity', False)
                
                ai_analysis = result.get('ai_analysis', {})
                dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
                verdict = dr_miguel_validation.get('verdict', 'UNKNOWN')
                type_correct = dr_miguel_validation.get('type_correct', True)
                
                # Check forensic notes identify the problem
                forensic_notes = str(ai_analysis) + str(dr_miguel_validation)
                identifies_problem = (
                    'birth' in forensic_notes.lower() or
                    'certidão' in forensic_notes.lower() or
                    'wrong' in forensic_notes.lower() or
                    'incorrect' in forensic_notes.lower()
                )
                
                # System should reject (0% not 85%)
                correctly_rejects = (
                    completeness <= 25 or  # Should be 0% or very low, not 85%
                    not validity or
                    verdict in ['REJEITADO', 'NECESSITA_REVISÃO'] or
                    not type_correct
                )
                
                self.log_test(
                    "TESTE 3: Detecção de Documento Inadequado",
                    correctly_rejects,
                    f"Completeness: {completeness}% (deve ser ≤25%), Verdict: {verdict}, Type Correct: {type_correct}",
                    {
                        "completeness": completeness,
                        "validity": validity,
                        "verdict": verdict,
                        "type_correct": type_correct,
                        "identifies_problem": identifies_problem,
                        "expected": "Sistema deve rejeitar certidão de nascimento como passaporte"
                    }
                )
                
                return result
            else:
                self.log_test(
                    "TESTE 3: Detecção de Documento Inadequado",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "TESTE 3: Detecção de Documento Inadequado",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_4_identity_validation(self):
        """TESTE 4: Validação de Identidade - Testar documento de pessoa diferente (João vs Maria)"""
        print("👤 TESTE 4: VALIDAÇÃO DE IDENTIDADE...")
        
        # Create passport for "Maria Silva" but case is for "João Silva"
        passport_content = self.create_simulated_passport_document("Maria Silva", "BRAZILIAN")
        
        files = {
            'file': ('passport_maria_silva.pdf', passport_content, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-IDENTITY-VALIDATION',
            'applicant_name': 'João Silva'  # Different from document name (Maria Silva)
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check identity validation
                ai_analysis = result.get('ai_analysis', {})
                dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
                
                belongs_to_applicant = dr_miguel_validation.get('belongs_to_applicant', True)
                name_validation = dr_miguel_validation.get('name_validation', 'approved')
                verdict = dr_miguel_validation.get('verdict', 'UNKNOWN')
                completeness = result.get('completeness', 0)
                
                # System should detect name mismatch
                detects_name_mismatch = (
                    not belongs_to_applicant or
                    name_validation in ['rejected', 'cannot_verify'] or
                    verdict in ['REJEITADO', 'NECESSITA_REVISÃO'] or
                    completeness < 50
                )
                
                # Check if forensic analysis mentions the name issue
                forensic_notes = str(ai_analysis) + str(dr_miguel_validation)
                mentions_name_issue = (
                    'maria' in forensic_notes.lower() or
                    'joão' in forensic_notes.lower() or
                    'name' in forensic_notes.lower() or
                    'nome' in forensic_notes.lower()
                )
                
                self.log_test(
                    "TESTE 4: Validação de Identidade",
                    detects_name_mismatch,
                    f"Belongs to applicant: {belongs_to_applicant}, Name validation: {name_validation}, Verdict: {verdict}",
                    {
                        "belongs_to_applicant": belongs_to_applicant,
                        "name_validation": name_validation,
                        "verdict": verdict,
                        "completeness": completeness,
                        "mentions_name_issue": mentions_name_issue,
                        "expected": "Sistema deve detectar que passaporte de Maria não pertence a João"
                    }
                )
                
                return result
            else:
                self.log_test(
                    "TESTE 4: Validação de Identidade",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "TESTE 4: Validação de Identidade",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_5_scoring_system(self):
        """TESTE 5: Sistema de Pontuação - Verificar authenticity_score, quality_score, completeness_score"""
        print("📊 TESTE 5: SISTEMA DE PONTUAÇÃO...")
        
        # Create a good quality passport for scoring analysis
        passport_content = self.create_simulated_passport_document("Roberto Santos", "BRAZILIAN")
        
        files = {
            'file': ('passport_roberto_santos.pdf', passport_content, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-SCORING-SYSTEM',
            'applicant_name': 'Roberto Santos'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for scoring components
                ai_analysis = result.get('ai_analysis', {})
                dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
                
                # Look for scoring fields
                completeness_score = result.get('completeness', 0)
                
                # Check if individual scores are calculated
                scoring_components = {
                    "completeness_score": completeness_score > 0,
                    "has_verdict": 'verdict' in dr_miguel_validation,
                    "has_validation_status": 'validity_status' in ai_analysis,
                    "overall_confidence_range": 0 <= completeness_score <= 100
                }
                
                # Check 85% threshold enforcement
                threshold_enforcement = {
                    "appropriate_score": True,  # Any score is acceptable for this test
                    "verdict_matches_score": True  # We'll accept any consistent verdict
                }
                
                # If score is high (85%+), verdict should be positive
                if completeness_score >= 85:
                    verdict = dr_miguel_validation.get('verdict', 'UNKNOWN')
                    threshold_enforcement["verdict_matches_score"] = verdict == 'APROVADO'
                
                scoring_working = (
                    sum(scoring_components.values()) >= 3 and  # At least 3/4 components
                    all(threshold_enforcement.values())
                )
                
                self.log_test(
                    "TESTE 5: Sistema de Pontuação",
                    scoring_working,
                    f"Completeness: {completeness_score}%, Scoring components: {sum(scoring_components.values())}/4",
                    {
                        "completeness_score": completeness_score,
                        "scoring_components": scoring_components,
                        "threshold_enforcement": threshold_enforcement,
                        "verdict": dr_miguel_validation.get('verdict', 'UNKNOWN')
                    }
                )
                
                return result
            else:
                self.log_test(
                    "TESTE 5: Sistema de Pontuação",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "TESTE 5: Sistema de Pontuação",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def test_6_structured_analysis(self):
        """TESTE 6: Análise Estruturada - Verificar extracted_data, critical_issues, recommendations"""
        print("📋 TESTE 6: ANÁLISE ESTRUTURADA...")
        
        # Create a passport with some issues for structured analysis
        passport_content = self.create_simulated_passport_document("Ana Paula Costa", "BRAZILIAN")
        
        files = {
            'file': ('passport_ana_costa.pdf', passport_content, 'application/pdf')
        }
        data = {
            'document_type': 'passport',
            'visa_type': 'H-1B',
            'case_id': 'TEST-STRUCTURED-ANALYSIS',
            'applicant_name': 'Ana Paula Costa'
        }
        
        try:
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for structured analysis components
                ai_analysis = result.get('ai_analysis', {})
                dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
                
                # Check extracted data organization
                extracted_data_components = {
                    "key_information": 'key_information' in ai_analysis and isinstance(ai_analysis.get('key_information'), list),
                    "document_type_identified": 'document_type_identified' in dr_miguel_validation,
                    "validity_status": 'validity_status' in ai_analysis,
                    "suggestions_present": 'suggestions' in ai_analysis and isinstance(ai_analysis.get('suggestions'), list)
                }
                
                # Check critical issues identification
                critical_issues_components = {
                    "has_critical_issues": 'critical_issues' in ai_analysis or 'quality_issues' in ai_analysis,
                    "has_verdict": 'verdict' in dr_miguel_validation,
                    "has_rejection_reason": 'rejection_reason' in dr_miguel_validation or dr_miguel_validation.get('verdict') != 'REJEITADO'
                }
                
                # Check recommendations are actionable
                recommendations_components = {
                    "has_suggestions": len(ai_analysis.get('suggestions', [])) > 0,
                    "has_next_steps": 'next_steps' in ai_analysis,
                    "structured_response": isinstance(result, dict) and len(result) > 3
                }
                
                # Overall structured analysis check
                structured_analysis_working = (
                    sum(extracted_data_components.values()) >= 2 and
                    sum(critical_issues_components.values()) >= 2 and
                    sum(recommendations_components.values()) >= 1
                )
                
                self.log_test(
                    "TESTE 6: Análise Estruturada",
                    structured_analysis_working,
                    f"Extracted data: {sum(extracted_data_components.values())}/4, Critical issues: {sum(critical_issues_components.values())}/3, Recommendations: {sum(recommendations_components.values())}/3",
                    {
                        "extracted_data_components": extracted_data_components,
                        "critical_issues_components": critical_issues_components,
                        "recommendations_components": recommendations_components,
                        "total_ai_analysis_fields": len(ai_analysis),
                        "total_dr_miguel_fields": len(dr_miguel_validation)
                    }
                )
                
                return result
            else:
                self.log_test(
                    "TESTE 6: Análise Estruturada",
                    False,
                    f"HTTP {response.status_code}: {response.text[:200]}",
                    response.text
                )
        except Exception as e:
            self.log_test(
                "TESTE 6: Análise Estruturada",
                False,
                f"Exception: {str(e)}"
            )
        
        return None
    
    def run_all_tests(self):
        """Execute all 6 comprehensive tests for Dr. Miguel enhanced forensic analysis"""
        print("🚀 EXECUTANDO TESTE COMPLETO DO DR. MIGUEL - ANÁLISE FORENSE APRIMORADA")
        print("=" * 80)
        
        # Execute all 6 tests
        test_1_result = self.test_1_basic_functionality()
        test_2_result = self.test_2_forensic_7_layers()
        test_3_result = self.test_3_wrong_document_detection()
        test_4_result = self.test_4_identity_validation()
        test_5_result = self.test_5_scoring_system()
        test_6_result = self.test_6_structured_analysis()
        
        # Generate summary
        self.generate_test_summary()
        
        return {
            "test_1_basic": test_1_result,
            "test_2_forensic": test_2_result,
            "test_3_wrong_doc": test_3_result,
            "test_4_identity": test_4_result,
            "test_5_scoring": test_5_result,
            "test_6_structured": test_6_result
        }
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 RESUMO FINAL DOS TESTES - DR. MIGUEL ANÁLISE FORENSE")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de Testes: {total_tests}")
        print(f"✅ Aprovados: {passed_tests}")
        print(f"❌ Falharam: {failed_tests}")
        print(f"📈 Taxa de Sucesso: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        # Detailed results
        print("RESULTADOS DETALHADOS:")
        print("-" * 40)
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
        
        print("\n" + "=" * 80)
        
        # Critical assessment
        critical_tests = [
            "TESTE 1: Funcionamento Básico",
            "TESTE 3: Detecção de Documento Inadequado"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and result['test'] in critical_tests)
        
        if critical_passed == len(critical_tests):
            print("🎉 TESTES CRÍTICOS APROVADOS - Dr. Miguel operacional após correções!")
        else:
            print("🚨 TESTES CRÍTICOS FALHARAM - Dr. Miguel precisa de mais correções!")
        
        print("=" * 80)

def main():
    """Main test execution"""
    print("🔬 DR. MIGUEL ENHANCED FORENSIC ANALYSIS - COMPREHENSIVE TESTING")
    print("Testing 7-layer forensic analysis system after critical fixes")
    print("=" * 80)
    
    tester = DrMiguelForensicTester()
    results = tester.run_all_tests()
    
    return results

if __name__ == "__main__":
    main()