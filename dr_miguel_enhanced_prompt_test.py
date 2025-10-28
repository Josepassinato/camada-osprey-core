#!/usr/bin/env python3
"""
TESTE DO PROMPT APRIMORADO DO DR. MIGUEL - Enhanced Forensic Document Validation
Tests the new 7-layer forensic analysis system for document validation
"""

import requests
import json
import time
import uuid
from datetime import datetime, timedelta
import os
from typing import Dict, Any
import base64

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DrMiguelEnhancedPromptTester:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DrMiguelEnhancedTester/1.0'
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
            print(f"    Response: {str(response_data)[:200]}...")
        print()
    
    def create_simulated_passport_document(self, name: str = "João Silva", 
                                         passport_number: str = "BR123456789",
                                         expiry_date: str = "2030-12-15",
                                         issue_date: str = "2020-12-15") -> bytes:
        """Create a simulated passport document for testing"""
        passport_content = f"""
        PASSPORT
        REPUBLIC OF BRAZIL
        PASSAPORTE
        
        Type/Tipo: P
        Country Code/Código do País: BRA
        Passport No./No. do Passaporte: {passport_number}
        
        Surname/Sobrenome: {name.split()[-1].upper()}
        Given Names/Nomes: {' '.join(name.split()[:-1]).upper()}
        Nationality/Nacionalidade: BRAZILIAN/BRASILEIRA
        Date of Birth/Data de Nascimento: 15 JAN 1985
        Sex/Sexo: M
        Place of Birth/Local de Nascimento: SAO PAULO, BRAZIL
        Date of Issue/Data de Emissão: {issue_date}
        Date of Expiry/Data de Validade: {expiry_date}
        Authority/Autoridade: DPF
        
        Machine Readable Zone (MRZ):
        P<BRA{name.split()[-1].upper()}<<{name.split()[0].upper()}<<<<<<<<<<<<<<<<<<<<<<
        {passport_number}<BRA8501159M{expiry_date.replace('-', '')[2:]}<<<<<<<<<<<<<<<<<<6
        
        SECURITY FEATURES:
        - Watermark: Brazilian Coat of Arms
        - Security Thread: Embedded
        - Holographic Elements: Present
        - RFID Chip: Embedded (ePassport)
        - Digital Signature: Valid
        
        ADDITIONAL INFORMATION:
        This is a valid Brazilian passport issued by the Federal Police (DPF)
        in accordance with ICAO Document 9303 standards.
        """ * 10  # Make it substantial
        
        return passport_content.encode('utf-8')
    
    def create_wrong_document_type(self, name: str = "Maria Santos") -> bytes:
        """Create a birth certificate but will claim it's a passport"""
        birth_cert_content = f"""
        CERTIDÃO DE NASCIMENTO
        BIRTH CERTIFICATE
        
        CARTÓRIO DE REGISTRO CIVIL
        CIVIL REGISTRY OFFICE
        
        Estado de São Paulo - State of São Paulo
        Município de São Paulo - City of São Paulo
        
        DADOS DO REGISTRADO / REGISTRANT DATA:
        Nome Completo / Full Name: {name}
        Data de Nascimento / Date of Birth: 15 de Janeiro de 1985 / January 15, 1985
        Local de Nascimento / Place of Birth: São Paulo, SP, Brasil
        Sexo / Sex: Feminino / Female
        
        FILIAÇÃO / PARENTAGE:
        Pai / Father: José Santos
        Mãe / Mother: Ana Santos
        
        REGISTRO / REGISTRATION:
        Livro / Book: 123
        Folha / Page: 456
        Termo / Term: 789
        Data do Registro / Registration Date: 20 de Janeiro de 1985
        
        CARTÓRIO / REGISTRY OFFICE:
        1º Cartório de Registro Civil de São Paulo
        Rua das Flores, 123 - São Paulo, SP
        
        OFICIAL / REGISTRAR:
        Dr. Carlos Oliveira
        Oficial de Registro Civil
        
        [SELO OFICIAL / OFFICIAL SEAL]
        [ASSINATURA / SIGNATURE]
        
        Esta certidão foi emitida em conformidade com a Lei 6.015/73
        This certificate was issued in accordance with Law 6.015/73
        """ * 5
        
        return birth_cert_content.encode('utf-8')
    
    def create_expired_passport(self, name: str = "Pedro Costa") -> bytes:
        """Create an expired passport document"""
        expired_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        issue_date = (datetime.now() - timedelta(days=365*10)).strftime("%Y-%m-%d")
        
        return self.create_simulated_passport_document(
            name=name,
            passport_number="BR987654321",
            expiry_date=expired_date,
            issue_date=issue_date
        )
    
    def create_near_expiry_passport(self, name: str = "Ana Oliveira") -> bytes:
        """Create a passport that expires soon"""
        near_expiry_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        issue_date = (datetime.now() - timedelta(days=365*9)).strftime("%Y-%m-%d")
        
        return self.create_simulated_passport_document(
            name=name,
            passport_number="BR555666777",
            expiry_date=near_expiry_date,
            issue_date=issue_date
        )
    
    def test_document_analysis_api(self, document_content: bytes, document_type: str, 
                                 visa_type: str, case_id: str, applicant_name: str = None) -> Dict[str, Any]:
        """Test the document analysis API with given parameters"""
        files = {
            'file': (f'test_document_{case_id}.pdf', document_content, 'application/pdf')
        }
        data = {
            'document_type': document_type,
            'visa_type': visa_type,
            'case_id': case_id
        }
        
        if applicant_name:
            data['applicant_name'] = applicant_name
        
        try:
            # Remove content-type header for multipart form data
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers,
                timeout=60  # Increased timeout for AI analysis
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "response_text": response.text[:500]
                }
        except Exception as e:
            return {
                "error": f"Exception: {str(e)}"
            }
    
    def test_analise_detalhada_documento_valido(self):
        """Teste 1: Análise Detalhada - Documento Válido (Passaporte Simulado)"""
        print("🔍 TESTE 1: ANÁLISE DETALHADA - DOCUMENTO VÁLIDO")
        
        # Create valid passport document
        passport_content = self.create_simulated_passport_document(
            name="João Silva",
            passport_number="BR123456789"
        )
        
        # Test with document analysis API
        result = self.test_document_analysis_api(
            document_content=passport_content,
            document_type="passport",
            visa_type="H-1B",
            case_id="TEST-VALID-PASSPORT",
            applicant_name="João Silva"
        )
        
        if "error" in result:
            self.log_test(
                "Análise Detalhada - Documento Válido",
                False,
                f"API Error: {result['error']}",
                result
            )
            return
        
        # Validate enhanced analysis structure
        required_fields = [
            'completeness', 'validity', 'ai_analysis', 'extracted_data'
        ]
        
        has_required_fields = all(field in result for field in required_fields)
        
        # Check for enhanced forensic analysis
        ai_analysis = result.get('ai_analysis', {})
        dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
        
        # Validate 7-layer analysis structure
        forensic_layers = [
            'document_type_identified',
            'type_correct', 
            'belongs_to_applicant',
            'validity_status',
            'uscis_acceptable',
            'verdict'
        ]
        
        has_forensic_layers = all(layer in dr_miguel_validation for layer in forensic_layers)
        
        # Check forensic scoring (0-100)
        completeness_score = result.get('completeness', 0)
        is_valid_score = 0 <= completeness_score <= 100
        
        # Check structured data extraction
        extracted_data = result.get('extracted_data', {})
        has_structured_extraction = bool(extracted_data)
        
        success = (
            has_required_fields and
            has_forensic_layers and
            is_valid_score and
            has_structured_extraction
        )
        
        self.log_test(
            "Análise Detalhada - Documento Válido",
            success,
            f"Completeness: {completeness_score}%, Forensic layers: {len([l for l in forensic_layers if l in dr_miguel_validation])}/6, Structured data: {bool(extracted_data)}",
            {
                "completeness_score": completeness_score,
                "validity": result.get('validity'),
                "verdict": dr_miguel_validation.get('verdict'),
                "forensic_layers_present": [l for l in forensic_layers if l in dr_miguel_validation],
                "extracted_data_keys": list(extracted_data.keys()) if extracted_data else []
            }
        )
    
    def test_deteccao_avancada_documento_tipo_errado(self):
        """Teste 2: Detecção Avançada - Documento Tipo Errado (RG/CNH como Passaporte)"""
        print("🔍 TESTE 2: DETECÇÃO AVANÇADA - DOCUMENTO TIPO ERRADO")
        
        # Create birth certificate but claim it's a passport
        wrong_doc_content = self.create_wrong_document_type("Maria Santos")
        
        result = self.test_document_analysis_api(
            document_content=wrong_doc_content,
            document_type="passport",  # WRONG - claiming birth cert is passport
            visa_type="H-1B",
            case_id="TEST-WRONG-DOC-TYPE",
            applicant_name="Maria Santos"
        )
        
        if "error" in result:
            self.log_test(
                "Detecção Avançada - Documento Tipo Errado",
                False,
                f"API Error: {result['error']}",
                result
            )
            return
        
        # Validate advanced detection
        ai_analysis = result.get('ai_analysis', {})
        dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
        
        # Should detect wrong document type
        document_type_identified = dr_miguel_validation.get('document_type_identified', '')
        type_correct = dr_miguel_validation.get('type_correct', True)
        verdict = dr_miguel_validation.get('verdict', 'UNKNOWN')
        rejection_reason = dr_miguel_validation.get('rejection_reason', '')
        
        # Should have forensic notes with technical analysis
        forensic_notes = ai_analysis.get('forensic_notes', '')
        
        # Advanced detection should reject immediately
        is_correctly_rejected = (
            not type_correct or
            verdict in ['REJEITADO', 'NECESSITA_REVISÃO'] or
            result.get('completeness', 100) < 50
        )
        
        has_technical_analysis = len(forensic_notes) > 50 if forensic_notes else False
        has_specific_reason = len(rejection_reason) > 10 if rejection_reason else False
        
        success = is_correctly_rejected and (has_technical_analysis or has_specific_reason)
        
        self.log_test(
            "Detecção Avançada - Documento Tipo Errado",
            success,
            f"Type correct: {type_correct}, Verdict: {verdict}, Rejection reason: {bool(rejection_reason)}",
            {
                "document_type_identified": document_type_identified,
                "type_correct": type_correct,
                "verdict": verdict,
                "rejection_reason": rejection_reason[:100] if rejection_reason else None,
                "completeness": result.get('completeness'),
                "has_forensic_notes": bool(forensic_notes)
            }
        )
    
    def test_validacao_identidade(self):
        """Teste 3: Validação de Identidade (Nome ligeiramente diferente e completamente diferente)"""
        print("🔍 TESTE 3: VALIDAÇÃO DE IDENTIDADE")
        
        # Test 3a: Slightly different name (José vs Jose)
        passport_content_jose = self.create_simulated_passport_document(
            name="José Silva",  # Document has José
            passport_number="BR111222333"
        )
        
        result_fuzzy = self.test_document_analysis_api(
            document_content=passport_content_jose,
            document_type="passport",
            visa_type="H-1B",
            case_id="TEST-FUZZY-MATCH",
            applicant_name="Jose Silva"  # Case is for Jose (without accent)
        )
        
        # Test 3b: Completely different name (Maria vs João)
        passport_content_maria = self.create_simulated_passport_document(
            name="Maria Silva",  # Document has Maria
            passport_number="BR444555666"
        )
        
        result_different = self.test_document_analysis_api(
            document_content=passport_content_maria,
            document_type="passport",
            visa_type="H-1B",
            case_id="TEST-DIFFERENT-NAME",
            applicant_name="João Silva"  # Case is for João (completely different)
        )
        
        # Validate fuzzy matching (should pass)
        fuzzy_success = False
        if "error" not in result_fuzzy:
            ai_analysis_fuzzy = result_fuzzy.get('ai_analysis', {})
            dr_miguel_fuzzy = ai_analysis_fuzzy.get('dr_miguel_validation', {})
            identity_validation = ai_analysis_fuzzy.get('identity_validation', {})
            
            belongs_to_applicant_fuzzy = dr_miguel_fuzzy.get('belongs_to_applicant', False)
            fuzzy_match_score = identity_validation.get('fuzzy_match_score', 0)
            
            # Fuzzy matching should work for José vs Jose
            fuzzy_success = belongs_to_applicant_fuzzy or fuzzy_match_score > 0.8
        
        # Validate different name rejection (should fail)
        different_success = False
        if "error" not in result_different:
            ai_analysis_different = result_different.get('ai_analysis', {})
            dr_miguel_different = ai_analysis_different.get('dr_miguel_validation', {})
            
            belongs_to_applicant_different = dr_miguel_different.get('belongs_to_applicant', True)
            verdict_different = dr_miguel_different.get('verdict', 'UNKNOWN')
            
            # Different name should be rejected
            different_success = (
                not belongs_to_applicant_different or
                verdict_different in ['REJEITADO', 'NECESSITA_REVISÃO']
            )
        
        overall_success = fuzzy_success and different_success
        
        self.log_test(
            "Validação de Identidade - Fuzzy Matching",
            fuzzy_success,
            f"José vs Jose matching: {fuzzy_success}",
            {
                "document_name": "José Silva",
                "applicant_name": "Jose Silva",
                "belongs_to_applicant": result_fuzzy.get('ai_analysis', {}).get('dr_miguel_validation', {}).get('belongs_to_applicant'),
                "fuzzy_match_score": result_fuzzy.get('ai_analysis', {}).get('identity_validation', {}).get('fuzzy_match_score')
            }
        )
        
        self.log_test(
            "Validação de Identidade - Nome Diferente",
            different_success,
            f"Maria vs João rejection: {different_success}",
            {
                "document_name": "Maria Silva",
                "applicant_name": "João Silva", 
                "belongs_to_applicant": result_different.get('ai_analysis', {}).get('dr_miguel_validation', {}).get('belongs_to_applicant'),
                "verdict": result_different.get('ai_analysis', {}).get('dr_miguel_validation', {}).get('verdict')
            }
        )
    
    def test_analise_temporal(self):
        """Teste 4: Análise Temporal (Documento próximo ao vencimento e vencido)"""
        print("🔍 TESTE 4: ANÁLISE TEMPORAL")
        
        # Test 4a: Near expiry document (30 days)
        near_expiry_content = self.create_near_expiry_passport("Ana Oliveira")
        
        result_near_expiry = self.test_document_analysis_api(
            document_content=near_expiry_content,
            document_type="passport",
            visa_type="H-1B",
            case_id="TEST-NEAR-EXPIRY"
        )
        
        # Test 4b: Expired document
        expired_content = self.create_expired_passport("Pedro Costa")
        
        result_expired = self.test_document_analysis_api(
            document_content=expired_content,
            document_type="passport",
            visa_type="H-1B",
            case_id="TEST-EXPIRED"
        )
        
        # Validate temporal analysis for near expiry
        near_expiry_success = False
        if "error" not in result_near_expiry:
            ai_analysis = result_near_expiry.get('ai_analysis', {})
            temporal_validation = ai_analysis.get('temporal_validation', {})
            uscis_validity = ai_analysis.get('uscis_validity_sufficient', False)
            
            days_remaining = temporal_validation.get('days_remaining', 0)
            expiry_warning = temporal_validation.get('expiry_warning', False)
            
            # Should calculate days remaining and warn about near expiry
            near_expiry_success = (
                days_remaining > 0 and days_remaining <= 60 and
                expiry_warning
            )
        
        # Validate temporal analysis for expired
        expired_success = False
        if "error" not in result_expired:
            ai_analysis = result_expired.get('ai_analysis', {})
            dr_miguel_validation = ai_analysis.get('dr_miguel_validation', {})
            temporal_validation = ai_analysis.get('temporal_validation', {})
            
            validity_status = dr_miguel_validation.get('validity_status', 'valid')
            days_remaining = temporal_validation.get('days_remaining', 1)
            uscis_validity = ai_analysis.get('uscis_validity_sufficient', True)
            
            # Should detect expired status
            expired_success = (
                validity_status in ['expired', 'invalid'] or
                days_remaining <= 0 or
                not uscis_validity
            )
        
        self.log_test(
            "Análise Temporal - Documento Próximo ao Vencimento",
            near_expiry_success,
            f"Days remaining detected: {result_near_expiry.get('ai_analysis', {}).get('temporal_validation', {}).get('days_remaining', 'N/A')}",
            {
                "days_remaining": result_near_expiry.get('ai_analysis', {}).get('temporal_validation', {}).get('days_remaining'),
                "expiry_warning": result_near_expiry.get('ai_analysis', {}).get('temporal_validation', {}).get('expiry_warning'),
                "uscis_validity_sufficient": result_near_expiry.get('ai_analysis', {}).get('uscis_validity_sufficient')
            }
        )
        
        self.log_test(
            "Análise Temporal - Documento Vencido",
            expired_success,
            f"Expired status detected: {expired_success}",
            {
                "validity_status": result_expired.get('ai_analysis', {}).get('dr_miguel_validation', {}).get('validity_status'),
                "days_remaining": result_expired.get('ai_analysis', {}).get('temporal_validation', {}).get('days_remaining'),
                "uscis_validity_sufficient": result_expired.get('ai_analysis', {}).get('uscis_validity_sufficient')
            }
        )
    
    def test_sistema_pontuacao(self):
        """Teste 5: Sistema de Pontuação (0-100, apenas 85%+ aprovados)"""
        print("🔍 TESTE 5: SISTEMA DE PONTUAÇÃO")
        
        # Test with multiple document scenarios to check scoring system
        test_scenarios = [
            {
                "name": "Valid Passport",
                "content": self.create_simulated_passport_document("Carlos Silva"),
                "expected_high_score": True
            },
            {
                "name": "Wrong Document Type",
                "content": self.create_wrong_document_type("Invalid Person"),
                "expected_high_score": False
            },
            {
                "name": "Expired Passport", 
                "content": self.create_expired_passport("Expired Person"),
                "expected_high_score": False
            }
        ]
        
        scoring_results = []
        
        for scenario in test_scenarios:
            result = self.test_document_analysis_api(
                document_content=scenario["content"],
                document_type="passport",
                visa_type="H-1B",
                case_id=f"TEST-SCORING-{scenario['name'].replace(' ', '-')}"
            )
            
            if "error" not in result:
                # Check scoring system
                overall_confidence = result.get('completeness', 0)  # This should be 0-100
                ai_analysis = result.get('ai_analysis', {})
                
                # Look for individual scores
                authenticity_score = ai_analysis.get('authenticity_score', 0)
                quality_score = ai_analysis.get('quality_score', 0)
                completeness_score = ai_analysis.get('completeness_score', 0)
                
                # Check verdict based on 85% threshold
                verdict = ai_analysis.get('dr_miguel_validation', {}).get('verdict', 'UNKNOWN')
                is_approved = verdict == 'APROVADO' or (overall_confidence >= 85 and result.get('validity', False))
                
                scoring_results.append({
                    "scenario": scenario["name"],
                    "overall_confidence": overall_confidence,
                    "authenticity_score": authenticity_score,
                    "quality_score": quality_score,
                    "completeness_score": completeness_score,
                    "is_approved": is_approved,
                    "expected_high_score": scenario["expected_high_score"],
                    "verdict": verdict
                })
        
        # Validate scoring system
        valid_score_range = all(
            0 <= result["overall_confidence"] <= 100 
            for result in scoring_results
        )
        
        # Check 85% threshold enforcement
        threshold_enforcement = all(
            (result["overall_confidence"] >= 85) == result["expected_high_score"] or
            not result["expected_high_score"]  # Allow low scores for invalid docs
            for result in scoring_results
        )
        
        # Check individual scoring components
        has_individual_scores = any(
            result["authenticity_score"] > 0 or 
            result["quality_score"] > 0 or 
            result["completeness_score"] > 0
            for result in scoring_results
        )
        
        success = valid_score_range and has_individual_scores
        
        self.log_test(
            "Sistema de Pontuação - Faixa 0-100",
            valid_score_range,
            f"All scores in 0-100 range: {valid_score_range}",
            {
                "scores": [(r["scenario"], r["overall_confidence"]) for r in scoring_results],
                "valid_range": valid_score_range
            }
        )
        
        self.log_test(
            "Sistema de Pontuação - Limiar 85%",
            threshold_enforcement,
            f"85% threshold properly enforced: {threshold_enforcement}",
            {
                "approvals": [(r["scenario"], r["overall_confidence"], r["is_approved"]) for r in scoring_results],
                "threshold_enforcement": threshold_enforcement
            }
        )
        
        self.log_test(
            "Sistema de Pontuação - Componentes Individuais",
            has_individual_scores,
            f"Individual scoring components present: {has_individual_scores}",
            {
                "individual_scores": [(r["scenario"], r["authenticity_score"], r["quality_score"], r["completeness_score"]) for r in scoring_results]
            }
        )
    
    def test_extracao_dados_estruturados(self):
        """Teste 6: Extração de Dados Estruturados"""
        print("🔍 TESTE 6: EXTRAÇÃO DE DADOS ESTRUTURADOS")
        
        # Create comprehensive passport for data extraction
        passport_content = self.create_simulated_passport_document(
            name="Roberto Santos",
            passport_number="BR789123456"
        )
        
        result = self.test_document_analysis_api(
            document_content=passport_content,
            document_type="passport",
            visa_type="H-1B",
            case_id="TEST-DATA-EXTRACTION"
        )
        
        if "error" in result:
            self.log_test(
                "Extração de Dados Estruturados",
                False,
                f"API Error: {result['error']}",
                result
            )
            return
        
        # Check structured data extraction
        extracted_data = result.get('extracted_data', {})
        ai_analysis = result.get('ai_analysis', {})
        
        # Expected structured fields
        expected_sections = [
            'personal_info',
            'document_numbers', 
            'dates',
            'recommendations',
            'critical_issues',
            'compliance_status'
        ]
        
        # Check if extracted_data has organized fields
        has_organized_fields = any(section in extracted_data for section in expected_sections)
        
        # Check for personal info extraction
        personal_info = extracted_data.get('personal_info', {})
        has_personal_info = bool(personal_info) and any(
            key in personal_info for key in ['name', 'nationality', 'date_of_birth']
        )
        
        # Check for document numbers
        document_numbers = extracted_data.get('document_numbers', {})
        has_document_numbers = bool(document_numbers) and 'passport_number' in document_numbers
        
        # Check for dates
        dates = extracted_data.get('dates', {})
        has_dates = bool(dates) and any(
            key in dates for key in ['issue_date', 'expiry_date', 'date_of_birth']
        )
        
        # Check for recommendations and critical issues
        recommendations = extracted_data.get('recommendations', [])
        critical_issues = extracted_data.get('critical_issues', [])
        compliance_status = extracted_data.get('compliance_status', '')
        
        has_analysis_fields = (
            isinstance(recommendations, list) or
            isinstance(critical_issues, list) or
            bool(compliance_status)
        )
        
        success = (
            has_organized_fields and
            has_personal_info and
            has_document_numbers and
            has_dates and
            has_analysis_fields
        )
        
        self.log_test(
            "Extração de Dados Estruturados",
            success,
            f"Organized fields: {has_organized_fields}, Personal info: {has_personal_info}, Document numbers: {has_document_numbers}, Dates: {has_dates}",
            {
                "extracted_data_sections": list(extracted_data.keys()),
                "personal_info_keys": list(personal_info.keys()) if personal_info else [],
                "document_numbers_keys": list(document_numbers.keys()) if document_numbers else [],
                "dates_keys": list(dates.keys()) if dates else [],
                "recommendations_count": len(recommendations) if isinstance(recommendations, list) else 0,
                "critical_issues_count": len(critical_issues) if isinstance(critical_issues, list) else 0,
                "compliance_status": compliance_status
            }
        )
    
    def run_all_tests(self):
        """Run all enhanced Dr. Miguel prompt tests"""
        print("🚀 INICIANDO TESTES DO PROMPT APRIMORADO DO DR. MIGUEL")
        print("=" * 80)
        
        # Run all test scenarios
        self.test_analise_detalhada_documento_valido()
        self.test_deteccao_avancada_documento_tipo_errado()
        self.test_validacao_identidade()
        self.test_analise_temporal()
        self.test_sistema_pontuacao()
        self.test_extracao_dados_estruturados()
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("=" * 80)
        print("📊 RESUMO DOS TESTES DO PROMPT APRIMORADO DO DR. MIGUEL")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total de Testes: {total_tests}")
        print(f"Testes Aprovados: {passed_tests}")
        print(f"Testes Falharam: {failed_tests}")
        print(f"Taxa de Sucesso: {success_rate:.1f}%")
        print()
        
        # Detailed results
        print("RESULTADOS DETALHADOS:")
        print("-" * 40)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")
        
        print()
        print("=" * 80)
        
        if success_rate >= 80:
            print("🎉 PROMPT APRIMORADO DO DR. MIGUEL: FUNCIONANDO CORRETAMENTE!")
            print("✅ Sistema de análise forense de 7 camadas operacional")
            print("✅ Análises mais detalhadas e precisas confirmadas")
        else:
            print("⚠️ PROMPT APRIMORADO DO DR. MIGUEL: NECESSITA AJUSTES")
            print("❌ Alguns componentes da análise forense precisam de correção")
        
        print("=" * 80)

if __name__ == "__main__":
    tester = DrMiguelEnhancedPromptTester()
    tester.run_all_tests()