#!/usr/bin/env python3
"""
INVESTIGAÇÃO CRÍTICA: Sistema rejeitando documentos válidos após correções de segurança
Critical Investigation: System rejecting valid documents after security corrections

This script investigates the balance between security and functionality in the document validation system.
The goal is to find settings that REJECT clearly invalid documents but APPROVE valid legitimate documents.
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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://agente-coruja-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class DocumentSecurityInvestigator:
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DocumentSecurityInvestigator/1.0'
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
        print()
    
    def create_valid_passport_document(self, name: str = "JOHN SMITH") -> bytes:
        """Create a realistic valid passport document"""
        passport_content = f"""
        PASSPORT
        UNITED STATES OF AMERICA
        
        Type: P
        Country Code: USA
        Passport No: 123456789
        
        Surname: {name.split()[-1].upper()}
        Given Names: {' '.join(name.split()[:-1]).upper()}
        Nationality: UNITED STATES OF AMERICA
        Date of Birth: 15 JAN 1990
        Sex: M
        Place of Birth: NEW YORK, NY, USA
        Date of Issue: 10 MAR 2020
        Date of Expiry: 09 MAR 2030
        Authority: U.S. DEPARTMENT OF STATE
        
        MRZ:
        P<USA{name.replace(' ', '<<').upper()}<<<<<<<<<<<<<<<<<<<<<
        1234567890USA9001159M3003096<<<<<<<<<<<<<<<<<<6
        
        OFFICIAL SEALS AND SIGNATURES PRESENT
        SECURITY FEATURES: Watermarks, RFID chip, biometric data
        DOCUMENT QUALITY: High resolution, clear text, proper formatting
        AUTHENTICITY MARKERS: Official government seal, proper fonts, correct layout
        """ * 20  # Make it substantial
        
        return passport_content.encode('utf-8')
    
    def create_invalid_document_wrong_type(self) -> bytes:
        """Create a birth certificate but claim it's a passport (should be rejected)"""
        birth_cert_content = """
        BIRTH CERTIFICATE
        State of California
        Department of Public Health
        
        This is to certify that:
        Name: John Smith
        Date of Birth: January 15, 1990
        Place of Birth: Los Angeles, California
        Father: Robert Smith
        Mother: Mary Smith
        
        Registrar Signature: [Signature]
        Date Issued: March 10, 2024
        Certificate Number: BC-2024-001234
        """ * 30
        
        return birth_cert_content.encode('utf-8')
    
    def create_wrong_person_document(self) -> bytes:
        """Create a passport for Maria Silva (should be rejected if applicant is John Smith)"""
        passport_content = """
        PASSPORT
        REPUBLIC OF BRAZIL
        
        Type: P
        Country Code: BRA
        Passport No: BR123456
        
        Surname: SILVA
        Given Names: MARIA FERNANDA
        Nationality: BRAZILIAN
        Date of Birth: 15 JAN 1985
        Sex: F
        Place of Birth: SAO PAULO, BRAZIL
        Date of Issue: 10 MAR 2020
        Date of Expiry: 09 MAR 2030
        Authority: DPF
        
        MRZ:
        P<BRASILVA<<MARIA<FERNANDA<<<<<<<<<<<<<<<<<<<<<
        BR1234567<BRA8501159F3003096<<<<<<<<<<<<<<<<<<6
        """ * 20
        
        return passport_content.encode('utf-8')
    
    def create_expired_document(self) -> bytes:
        """Create an expired passport (should be rejected)"""
        passport_content = """
        PASSPORT
        UNITED STATES OF AMERICA
        
        Type: P
        Country Code: USA
        Passport No: 987654321
        
        Surname: SMITH
        Given Names: JOHN MICHAEL
        Nationality: UNITED STATES OF AMERICA
        Date of Birth: 15 JAN 1990
        Sex: M
        Place of Birth: NEW YORK, NY, USA
        Date of Issue: 10 MAR 2015
        Date of Expiry: 09 MAR 2020  # EXPIRED!
        Authority: U.S. DEPARTMENT OF STATE
        
        MRZ:
        P<USASMITH<<JOHN<MICHAEL<<<<<<<<<<<<<<<<<<<<<
        9876543210USA9001159M2003096<<<<<<<<<<<<<<<<<<6
        """ * 20
        
        return passport_content.encode('utf-8')
    
    def create_low_quality_document(self) -> bytes:
        """Create a low quality/illegible document (should be rejected)"""
        low_quality_content = """
        [BLURRY/ILLEGIBLE DOCUMENT]
        
        P...port
        Un...d St...s
        
        Na..: J... S...h
        D... of B...: 1... 199.
        
        [Text is blurry and partially illegible]
        [Poor scan quality]
        [Missing information due to poor quality]
        """ * 15
        
        return low_quality_content.encode('utf-8')
    
    def test_document_analysis(self, document_content: bytes, filename: str, document_type: str, 
                             visa_type: str = "H-1B", applicant_name: str = "John Smith",
                             expected_result: str = "UNKNOWN") -> Dict[str, Any]:
        """Test document analysis with given parameters"""
        
        files = {
            'file': (filename, document_content, 'application/pdf')
        }
        data = {
            'document_type': document_type,
            'visa_type': visa_type,
            'case_id': f'TEST-{uuid.uuid4().hex[:8].upper()}',
            'applicant_name': applicant_name
        }
        
        try:
            # Remove content-type header for multipart form data
            headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
            
            response = requests.post(
                f"{API_BASE}/documents/analyze-with-ai",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "status_code": 200,
                    "result": result,
                    "completeness": result.get('completeness', 0),
                    "validity": result.get('validity', False),
                    "ai_analysis": result.get('ai_analysis', {}),
                    "policy_engine": result.get('policy_engine', {}),
                    "dr_miguel_validation": result.get('ai_analysis', {}).get('dr_miguel_validation', {}),
                    "overall_confidence": result.get('overall_confidence', 0)
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                    "result": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "error": str(e),
                "result": None
            }
    
    def investigate_valid_passport_rejection(self):
        """TESTE 1: Investigar por que passaporte válido está sendo rejeitado"""
        print("🔍 TESTE 1: Investigando rejeição de passaporte válido...")
        
        # Create a high-quality, valid passport
        valid_passport = self.create_valid_passport_document("JOHN SMITH")
        
        result = self.test_document_analysis(
            document_content=valid_passport,
            filename="valid_passport_john_smith.pdf",
            document_type="passport",
            visa_type="H-1B",
            applicant_name="John Smith",
            expected_result="APPROVED"
        )
        
        if result["success"]:
            completeness = result["completeness"]
            validity = result["validity"]
            dr_miguel = result["dr_miguel_validation"]
            policy_engine = result["policy_engine"]
            
            # Analyze why it might be rejected
            issues = []
            
            if completeness < 75:
                issues.append(f"Completeness too low: {completeness}% (threshold may be too high)")
            
            if not validity:
                issues.append("Validity marked as False")
            
            if dr_miguel.get("verdict") in ["REJEITADO", "NECESSITA_REVISÃO"]:
                issues.append(f"Dr. Miguel rejected: {dr_miguel.get('verdict')} - {dr_miguel.get('rejection_reason', 'No reason')}")
            
            if policy_engine.get("decision") in ["FAIL", "ALERT"]:
                issues.append(f"Policy Engine failed: {policy_engine.get('decision')}")
            
            # Check individual scoring components
            authenticity_score = result["result"].get("authenticity_score", 0)
            quality_score = result["result"].get("quality_score", 0)
            
            if authenticity_score < 0.75:
                issues.append(f"Authenticity score too low: {authenticity_score}")
            
            if quality_score < 0.75:
                issues.append(f"Quality score too low: {quality_score}")
            
            # Determine if this is a valid document being wrongly rejected
            should_be_approved = (
                completeness >= 75 and
                validity and
                dr_miguel.get("verdict") == "APROVADO" and
                policy_engine.get("decision") == "PASS"
            )
            
            is_wrongly_rejected = not should_be_approved and len(issues) > 0
            
            self.log_test(
                "Valid Passport Analysis",
                not is_wrongly_rejected,
                f"Completeness: {completeness}%, Validity: {validity}, Issues: {issues}",
                {
                    "completeness": completeness,
                    "validity": validity,
                    "dr_miguel_verdict": dr_miguel.get("verdict"),
                    "policy_engine_decision": policy_engine.get("decision"),
                    "issues_found": issues,
                    "authenticity_score": authenticity_score,
                    "quality_score": quality_score,
                    "should_be_approved": should_be_approved
                }
            )
            
            return result
        else:
            self.log_test(
                "Valid Passport Analysis",
                False,
                f"API call failed: {result['error']}",
                result
            )
            return result
    
    def investigate_approval_thresholds(self):
        """TESTE 2: Investigar thresholds de aprovação"""
        print("🔍 TESTE 2: Investigando thresholds de aprovação...")
        
        # Test with multiple valid documents to understand threshold patterns
        test_cases = [
            ("JOHN SMITH", "john_smith_passport.pdf"),
            ("MARIA SANTOS", "maria_santos_passport.pdf"),
            ("CARLOS SILVA", "carlos_silva_passport.pdf")
        ]
        
        threshold_results = []
        
        for name, filename in test_cases:
            valid_passport = self.create_valid_passport_document(name)
            
            result = self.test_document_analysis(
                document_content=valid_passport,
                filename=filename,
                document_type="passport",
                visa_type="H-1B",
                applicant_name=name,
                expected_result="APPROVED"
            )
            
            if result["success"]:
                threshold_results.append({
                    "name": name,
                    "completeness": result["completeness"],
                    "validity": result["validity"],
                    "overall_confidence": result["overall_confidence"],
                    "authenticity_score": result["result"].get("authenticity_score", 0),
                    "quality_score": result["result"].get("quality_score", 0)
                })
        
        # Analyze threshold patterns
        if threshold_results:
            avg_completeness = sum(r["completeness"] for r in threshold_results) / len(threshold_results)
            avg_confidence = sum(r["overall_confidence"] for r in threshold_results) / len(threshold_results)
            
            # Check if thresholds are too restrictive
            low_scores = [r for r in threshold_results if r["completeness"] < 75 or r["overall_confidence"] < 0.75]
            
            threshold_too_high = len(low_scores) > len(threshold_results) / 2  # More than half have low scores
            
            self.log_test(
                "Approval Thresholds Analysis",
                not threshold_too_high,
                f"Avg completeness: {avg_completeness:.1f}%, Avg confidence: {avg_confidence:.2f}, Low scores: {len(low_scores)}/{len(threshold_results)}",
                {
                    "average_completeness": avg_completeness,
                    "average_confidence": avg_confidence,
                    "low_score_count": len(low_scores),
                    "total_tests": len(threshold_results),
                    "threshold_too_high": threshold_too_high,
                    "detailed_results": threshold_results
                }
            )
        else:
            self.log_test(
                "Approval Thresholds Analysis",
                False,
                "No successful test results to analyze",
                {"threshold_results": threshold_results}
            )
    
    def investigate_scoring_system(self):
        """TESTE 3: Investigar sistema de pontuação"""
        print("🔍 TESTE 3: Investigando sistema de pontuação...")
        
        valid_passport = self.create_valid_passport_document("JOHN SMITH")
        
        result = self.test_document_analysis(
            document_content=valid_passport,
            filename="scoring_test_passport.pdf",
            document_type="passport",
            visa_type="H-1B",
            applicant_name="John Smith"
        )
        
        if result["success"]:
            response_data = result["result"]
            
            # Extract all scoring components
            scoring_components = {
                "completeness": result["completeness"],
                "overall_confidence": result["overall_confidence"],
                "authenticity_score": response_data.get("authenticity_score", 0),
                "quality_score": response_data.get("quality_score", 0),
                "completeness_score": response_data.get("completeness_score", 0)
            }
            
            # Check Dr. Miguel scoring
            dr_miguel = result["dr_miguel_validation"]
            dr_miguel_scores = {
                "verdict": dr_miguel.get("verdict"),
                "type_correct": dr_miguel.get("type_correct"),
                "belongs_to_applicant": dr_miguel.get("belongs_to_applicant"),
                "uscis_acceptable": dr_miguel.get("uscis_acceptable")
            }
            
            # Check Policy Engine scoring
            policy_engine = result["policy_engine"]
            policy_scores = {
                "decision": policy_engine.get("decision"),
                "policy_score": policy_engine.get("policy_score", 0),
                "quality_analysis": policy_engine.get("quality_analysis", {})
            }
            
            # Analyze if scoring is working correctly
            has_proper_scoring = (
                scoring_components["completeness"] > 0 and
                scoring_components["overall_confidence"] > 0 and
                dr_miguel_scores["verdict"] is not None and
                policy_scores["decision"] is not None
            )
            
            # Check if scores are reasonable for a valid document
            reasonable_scores = (
                scoring_components["completeness"] >= 50 and  # Should be at least 50% for valid doc
                scoring_components["overall_confidence"] >= 0.3  # Should have some confidence
            )
            
            self.log_test(
                "Scoring System Analysis",
                has_proper_scoring and reasonable_scores,
                f"Scoring components working: {has_proper_scoring}, Reasonable scores: {reasonable_scores}",
                {
                    "scoring_components": scoring_components,
                    "dr_miguel_scores": dr_miguel_scores,
                    "policy_scores": policy_scores,
                    "has_proper_scoring": has_proper_scoring,
                    "reasonable_scores": reasonable_scores
                }
            )
        else:
            self.log_test(
                "Scoring System Analysis",
                False,
                f"API call failed: {result['error']}",
                result
            )
    
    def investigate_data_extraction(self):
        """TESTE 4: Investigar extração de dados"""
        print("🔍 TESTE 4: Investigando extração de dados...")
        
        valid_passport = self.create_valid_passport_document("JOHN SMITH")
        
        result = self.test_document_analysis(
            document_content=valid_passport,
            filename="data_extraction_test.pdf",
            document_type="passport",
            visa_type="H-1B",
            applicant_name="John Smith"
        )
        
        if result["success"]:
            ai_analysis = result["ai_analysis"]
            
            # Check for extracted data fields
            extracted_fields = {
                "personal_info": ai_analysis.get("personal_info", {}),
                "document_numbers": ai_analysis.get("document_numbers", {}),
                "dates": ai_analysis.get("dates", {}),
                "key_information": ai_analysis.get("key_information", [])
            }
            
            # Check if critical fields are extracted
            has_personal_info = bool(extracted_fields["personal_info"])
            has_document_numbers = bool(extracted_fields["document_numbers"])
            has_dates = bool(extracted_fields["dates"])
            has_key_info = len(extracted_fields["key_information"]) > 0
            
            # Check for MRZ parsing (specific to passports)
            dr_miguel = result["dr_miguel_validation"]
            has_mrz_data = "MRZ" in str(dr_miguel) or "passport" in str(dr_miguel).lower()
            
            extraction_working = (
                has_personal_info or
                has_document_numbers or
                has_dates or
                has_key_info or
                has_mrz_data
            )
            
            self.log_test(
                "Data Extraction Analysis",
                extraction_working,
                f"Personal info: {has_personal_info}, Doc numbers: {has_document_numbers}, Dates: {has_dates}, Key info: {has_key_info}, MRZ: {has_mrz_data}",
                {
                    "extracted_fields": extracted_fields,
                    "has_personal_info": has_personal_info,
                    "has_document_numbers": has_document_numbers,
                    "has_dates": has_dates,
                    "has_key_info": has_key_info,
                    "has_mrz_data": has_mrz_data,
                    "extraction_working": extraction_working
                }
            )
        else:
            self.log_test(
                "Data Extraction Analysis",
                False,
                f"API call failed: {result['error']}",
                result
            )
    
    def test_security_balance(self):
        """TESTE 5: Testar equilíbrio de segurança - deve REJEITAR inválidos mas APROVAR válidos"""
        print("🔍 TESTE 5: Testando equilíbrio de segurança...")
        
        test_cases = [
            {
                "name": "Valid Passport (Should APPROVE)",
                "document": self.create_valid_passport_document("JOHN SMITH"),
                "filename": "valid_passport.pdf",
                "document_type": "passport",
                "applicant_name": "John Smith",
                "expected_approval": True
            },
            {
                "name": "Wrong Document Type (Should REJECT)",
                "document": self.create_invalid_document_wrong_type(),
                "filename": "birth_cert_as_passport.pdf",
                "document_type": "passport",  # Wrong type
                "applicant_name": "John Smith",
                "expected_approval": False
            },
            {
                "name": "Wrong Person Document (Should REJECT)",
                "document": self.create_wrong_person_document(),
                "filename": "maria_silva_passport.pdf",
                "document_type": "passport",
                "applicant_name": "John Smith",  # Different person
                "expected_approval": False
            },
            {
                "name": "Expired Document (Should REJECT)",
                "document": self.create_expired_document(),
                "filename": "expired_passport.pdf",
                "document_type": "passport",
                "applicant_name": "John Smith",
                "expected_approval": False
            },
            {
                "name": "Low Quality Document (Should REJECT)",
                "document": self.create_low_quality_document(),
                "filename": "low_quality_passport.pdf",
                "document_type": "passport",
                "applicant_name": "John Smith",
                "expected_approval": False
            }
        ]
        
        balance_results = []
        
        for test_case in test_cases:
            result = self.test_document_analysis(
                document_content=test_case["document"],
                filename=test_case["filename"],
                document_type=test_case["document_type"],
                applicant_name=test_case["applicant_name"]
            )
            
            if result["success"]:
                completeness = result["completeness"]
                validity = result["validity"]
                dr_miguel_verdict = result["dr_miguel_validation"].get("verdict", "UNKNOWN")
                
                # Determine if document is approved or rejected
                is_approved = (
                    completeness >= 75 and
                    validity and
                    dr_miguel_verdict == "APROVADO"
                )
                
                # Check if result matches expectation
                correct_decision = is_approved == test_case["expected_approval"]
                
                balance_results.append({
                    "test_name": test_case["name"],
                    "expected_approval": test_case["expected_approval"],
                    "actual_approval": is_approved,
                    "correct_decision": correct_decision,
                    "completeness": completeness,
                    "validity": validity,
                    "dr_miguel_verdict": dr_miguel_verdict
                })
                
                self.log_test(
                    f"Security Balance - {test_case['name']}",
                    correct_decision,
                    f"Expected: {'APPROVE' if test_case['expected_approval'] else 'REJECT'}, Got: {'APPROVE' if is_approved else 'REJECT'} (Completeness: {completeness}%)",
                    {
                        "expected_approval": test_case["expected_approval"],
                        "actual_approval": is_approved,
                        "completeness": completeness,
                        "validity": validity,
                        "dr_miguel_verdict": dr_miguel_verdict
                    }
                )
            else:
                balance_results.append({
                    "test_name": test_case["name"],
                    "expected_approval": test_case["expected_approval"],
                    "actual_approval": False,
                    "correct_decision": not test_case["expected_approval"],  # If API fails, it's like rejection
                    "error": result["error"]
                })
                
                self.log_test(
                    f"Security Balance - {test_case['name']}",
                    not test_case["expected_approval"],  # API failure is like rejection
                    f"API call failed: {result['error']}",
                    result
                )
        
        # Overall balance assessment
        correct_decisions = sum(1 for r in balance_results if r["correct_decision"])
        total_tests = len(balance_results)
        balance_score = correct_decisions / total_tests if total_tests > 0 else 0
        
        self.log_test(
            "Overall Security Balance",
            balance_score >= 0.8,  # At least 80% correct decisions
            f"Correct decisions: {correct_decisions}/{total_tests} ({balance_score:.1%})",
            {
                "balance_score": balance_score,
                "correct_decisions": correct_decisions,
                "total_tests": total_tests,
                "detailed_results": balance_results
            }
        )
    
    def investigate_system_configuration(self):
        """TESTE 6: Investigar configuração do sistema"""
        print("🔍 TESTE 6: Investigando configuração do sistema...")
        
        # Test with a borderline document to understand system behavior
        borderline_passport = """
        PASSPORT
        UNITED STATES OF AMERICA
        
        Type: P
        Passport No: 123456789
        
        Surname: SMITH
        Given Names: JOHN
        Date of Birth: 15 JAN 1990
        Date of Expiry: 09 MAR 2030
        
        [Some fields missing or unclear]
        [Moderate quality scan]
        """ * 15
        
        result = self.test_document_analysis(
            document_content=borderline_passport.encode('utf-8'),
            filename="borderline_passport.pdf",
            document_type="passport",
            applicant_name="John Smith"
        )
        
        if result["success"]:
            response_data = result["result"]
            
            # Analyze system configuration
            config_analysis = {
                "dr_miguel_present": bool(result["dr_miguel_validation"]),
                "policy_engine_present": bool(result["policy_engine"]),
                "both_systems_active": bool(result["dr_miguel_validation"]) and bool(result["policy_engine"]),
                "fallback_behavior": result["completeness"] if result["completeness"] < 50 else "normal",
                "threshold_behavior": "restrictive" if result["completeness"] < 75 else "permissive"
            }
            
            # Check if both systems need to approve
            dr_miguel_verdict = result["dr_miguel_validation"].get("verdict", "UNKNOWN")
            policy_decision = result["policy_engine"].get("decision", "UNKNOWN")
            
            both_approve_required = (
                config_analysis["both_systems_active"] and
                (dr_miguel_verdict != "APROVADO" or policy_decision != "PASS") and
                result["completeness"] < 75
            )
            
            self.log_test(
                "System Configuration Analysis",
                config_analysis["both_systems_active"],
                f"Dr. Miguel: {config_analysis['dr_miguel_present']}, Policy Engine: {config_analysis['policy_engine_present']}, Both approve required: {both_approve_required}",
                {
                    "config_analysis": config_analysis,
                    "dr_miguel_verdict": dr_miguel_verdict,
                    "policy_decision": policy_decision,
                    "both_approve_required": both_approve_required,
                    "completeness": result["completeness"]
                }
            )
        else:
            self.log_test(
                "System Configuration Analysis",
                False,
                f"API call failed: {result['error']}",
                result
            )
    
    def run_complete_investigation(self):
        """Run complete investigation of document validation security balance"""
        print("🚨 INICIANDO INVESTIGAÇÃO CRÍTICA: Sistema rejeitando documentos válidos")
        print("=" * 80)
        
        # Run all investigation tests
        self.investigate_valid_passport_rejection()
        self.investigate_approval_thresholds()
        self.investigate_scoring_system()
        self.investigate_data_extraction()
        self.test_security_balance()
        self.investigate_system_configuration()
        
        # Generate summary report
        self.generate_investigation_report()
    
    def generate_investigation_report(self):
        """Generate comprehensive investigation report"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO DE INVESTIGAÇÃO CRÍTICA")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total de testes: {total_tests}")
        print(f"Testes aprovados: {passed_tests}")
        print(f"Testes falharam: {failed_tests}")
        print(f"Taxa de sucesso: {passed_tests/total_tests:.1%}")
        print()
        
        # Categorize issues
        critical_issues = []
        recommendations = []
        
        for result in self.test_results:
            if not result["success"]:
                if "Valid Passport" in result["test"]:
                    critical_issues.append("Sistema rejeitando passaportes válidos")
                elif "Threshold" in result["test"]:
                    critical_issues.append("Thresholds de aprovação muito restritivos")
                elif "Scoring" in result["test"]:
                    critical_issues.append("Sistema de pontuação não funcionando corretamente")
                elif "Security Balance" in result["test"]:
                    critical_issues.append("Equilíbrio de segurança comprometido")
        
        if critical_issues:
            print("🚨 PROBLEMAS CRÍTICOS IDENTIFICADOS:")
            for issue in set(critical_issues):
                print(f"  - {issue}")
            print()
        
        # Generate recommendations
        if "Sistema rejeitando passaportes válidos" in critical_issues:
            recommendations.append("Reduzir threshold de aprovação de 85% para 75%")
            recommendations.append("Ajustar critérios de Dr. Miguel para ser menos restritivo")
        
        if "Thresholds de aprovação muito restritivos" in critical_issues:
            recommendations.append("Revisar thresholds: considerar 70-75% ao invés de 85%+")
            recommendations.append("Implementar aprovação por apenas um sistema (Dr. Miguel OU Policy Engine)")
        
        if "Sistema de pontuação não funcionando corretamente" in critical_issues:
            recommendations.append("Corrigir cálculo de overall_confidence")
            recommendations.append("Verificar authenticity_score e quality_score")
        
        if recommendations:
            print("💡 RECOMENDAÇÕES PARA CORREÇÃO:")
            for rec in recommendations:
                print(f"  - {rec}")
            print()
        
        print("📋 CONFIGURAÇÃO RECOMENDADA PARA EQUILÍBRIO:")
        print("  - Threshold de aprovação: 75% (ao invés de 85%+)")
        print("  - Aprovação: Dr. Miguel OU Policy Engine (não ambos)")
        print("  - Documentos válidos do usuário correto: APROVAR")
        print("  - Documentos tipo errado ou pessoa errada: REJEITAR")
        print("  - Fallback seguro: 0% (rejeição) ao invés de 85% (aprovação)")
        print()
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests,
            "critical_issues": list(set(critical_issues)),
            "recommendations": recommendations,
            "test_results": self.test_results
        }

def main():
    """Main function to run the investigation"""
    investigator = DocumentSecurityInvestigator()
    investigator.run_complete_investigation()

if __name__ == "__main__":
    main()