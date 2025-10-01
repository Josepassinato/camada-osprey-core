#!/usr/bin/env python3
"""
TESTE DIRETO DO DR. MIGUEL - Enhanced Forensic Analysis
Direct test of Dr. Miguel's forensic analysis capabilities
"""

import requests
import json
import os
import base64
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visaai.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def create_test_passport_content():
    """Create a realistic passport content for testing"""
    return f"""
    PASSPORT
    REPUBLIC OF BRAZIL
    PASSAPORTE
    
    Type/Tipo: P
    Country Code/Código do País: BRA
    Passport No./No. do Passaporte: BR123456789
    
    Surname/Sobrenome: SILVA
    Given Names/Nomes: JOÃO CARLOS
    Nationality/Nacionalidade: BRAZILIAN/BRASILEIRA
    Date of Birth/Data de Nascimento: 15 JAN 1985
    Sex/Sexo: M
    Place of Birth/Local de Nascimento: SAO PAULO, BRAZIL
    Date of Issue/Data de Emissão: 10 MAR 2020
    Date of Expiry/Data de Validade: 09 MAR 2030
    Authority/Autoridade: DPF
    
    Machine Readable Zone (MRZ):
    P<BRASILVA<<JOAO<CARLOS<<<<<<<<<<<<<<<<<<<<<<
    BR123456789<BRA8501159M3003096<<<<<<<<<<<<<<<6
    
    SECURITY FEATURES:
    - Watermark: Brazilian Coat of Arms
    - Security Thread: Embedded
    - Holographic Elements: Present
    - RFID Chip: Embedded (ePassport)
    - Digital Signature: Valid
    
    This is a valid Brazilian passport issued by the Federal Police (DPF)
    in accordance with ICAO Document 9303 standards.
    
    ADDITIONAL PASSPORT PAGES:
    
    PAGE 2: PERSONAL DATA
    Full Name: João Carlos Silva
    Nationality: Brazilian
    Date of Birth: 15 January 1985
    Place of Birth: São Paulo, SP, Brazil
    Sex: Male
    Height: 175 cm
    
    PAGE 3: EMERGENCY CONTACT
    Contact Person: Maria Silva (Mother)
    Address: Rua das Flores, 123, São Paulo, SP
    Phone: +55 11 1234-5678
    
    PAGE 4: VISA PAGES
    [Space for visa stamps and endorsements]
    
    PAGE 5-32: ADDITIONAL VISA PAGES
    [Multiple blank pages for future visa stamps]
    
    SECURITY VERIFICATION:
    This document contains multiple security features including:
    - Intaglio printing with raised text
    - Rainbow printing with color gradients
    - Microprinting visible under magnification
    - UV-reactive inks and fibers
    - Tactile features for visually impaired
    - Digital watermarks and security threads
    - RFID chip with encrypted biometric data
    - Optical security features and holograms
    
    TECHNICAL SPECIFICATIONS:
    Document Size: 125mm x 88mm (ID-3 format)
    Paper Type: Cotton-based security paper
    Printing Method: Offset lithography with security features
    Binding: Sewn binding with security thread
    Pages: 32 pages total
    Valid for: International travel to all countries
    
    ISSUING AUTHORITY INFORMATION:
    Issued by: Departamento de Polícia Federal (DPF)
    Issuing Office: São Paulo/SP
    Authorization Code: DPF-SP-2020-123456
    Officer ID: 987654
    Digital Signature: [Encrypted signature data]
    
    BIOMETRIC DATA:
    Facial Recognition: Encoded in RFID chip
    Fingerprint Data: Stored in secure chip
    Iris Scan: Available upon request
    
    TRAVEL HISTORY:
    [This section would contain entry/exit stamps]
    
    ADDITIONAL INFORMATION:
    This passport is valid for travel to all countries that recognize Brazilian travel documents.
    The holder is entitled to consular protection from Brazilian diplomatic missions worldwide.
    
    EMERGENCY PROCEDURES:
    In case of loss or theft, contact the nearest Brazilian consulate immediately.
    Report to local police and obtain a police report.
    Apply for emergency travel document if needed.
    
    RENEWAL INFORMATION:
    This passport may be renewed up to 6 months before expiration.
    Renewal applications must be submitted to DPF offices or Brazilian consulates.
    Required documents: Previous passport, birth certificate, photos, and fees.
    
    LEGAL NOTICES:
    This document is the property of the Federative Republic of Brazil.
    Alteration, forgery, or misuse is punishable by law.
    Maximum penalty: 2-6 years imprisonment plus fines.
    
    INTERNATIONAL AGREEMENTS:
    This passport is issued in accordance with ICAO Document 9303.
    Complies with international standards for machine-readable travel documents.
    Recognized by all ICAO member countries.
    
    TECHNICAL SUPPORT:
    For technical issues with the RFID chip, contact DPF technical support.
    Phone: 0800-123-4567
    Email: suporte.passaporte@dpf.gov.br
    Website: www.pf.gov.br
    """ * 20  # Make it much larger to exceed 50KB

def test_direct_api_call():
    """Test the document analysis API directly"""
    print("🔍 TESTE DIRETO DA API /api/documents/analyze-with-ai")
    print("=" * 60)
    
    # Create test document
    passport_content = create_test_passport_content().encode('utf-8')
    
    # Prepare the request
    files = {
        'file': ('passport_joao_silva.pdf', passport_content, 'application/pdf')
    }
    data = {
        'document_type': 'passport',
        'visa_type': 'H-1B',
        'case_id': 'TEST-DIRECT-API',
        'applicant_name': 'João Carlos Silva'
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/documents/analyze-with-ai",
            files=files,
            data=data,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n📊 RESULTADO DA ANÁLISE:")
            print("-" * 40)
            
            # Basic fields
            print(f"Valid: {result.get('valid', 'N/A')}")
            print(f"Legible: {result.get('legible', 'N/A')}")
            print(f"Completeness: {result.get('completeness', 'N/A')}%")
            
            # Enhanced analysis
            enhanced_analysis = result.get('enhanced_analysis', {})
            if enhanced_analysis:
                print(f"\n🔬 ANÁLISE APRIMORADA:")
                print(f"Verdict: {enhanced_analysis.get('verdict', 'N/A')}")
                print(f"Confidence Score: {enhanced_analysis.get('confidence_score', 'N/A')}")
                print(f"Document Type Identified: {enhanced_analysis.get('document_type_identified', 'N/A')}")
                print(f"Type Matches Expected: {enhanced_analysis.get('type_matches_expected', 'N/A')}")
                print(f"USCIS Acceptable: {enhanced_analysis.get('uscis_acceptable', 'N/A')}")
                
                # Detailed analysis
                detailed_analysis = enhanced_analysis.get('detailed_analysis', {})
                if detailed_analysis:
                    print(f"\n📋 ANÁLISE DETALHADA:")
                    quality_assessment = detailed_analysis.get('quality_assessment', {})
                    if quality_assessment:
                        print(f"Quality Status: {quality_assessment.get('status', 'N/A')}")
                        print(f"Quality Score: {quality_assessment.get('overall_quality_score', 'N/A')}")
                    
                    validation_results = detailed_analysis.get('validation_results', {})
                    if validation_results:
                        print(f"Validation Valid: {validation_results.get('is_valid', 'N/A')}")
                        print(f"Overall Confidence: {validation_results.get('overall_confidence', 'N/A')}")
                
                # Issues and recommendations
                issues = enhanced_analysis.get('issues', [])
                if issues:
                    print(f"\n⚠️ ISSUES ({len(issues)}):")
                    for issue in issues[:3]:  # Show first 3
                        print(f"  - {issue}")
                
                recommendations = enhanced_analysis.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
                    for rec in recommendations[:3]:  # Show first 3
                        print(f"  - {rec}")
            
            # Policy Engine results
            policy_engine = result.get('policy_engine', {})
            if policy_engine:
                print(f"\n🏛️ POLICY ENGINE:")
                print(f"Decision: {policy_engine.get('decision', 'N/A')}")
                print(f"Overall Score: {policy_engine.get('overall_score', 'N/A')}")
                
                messages = policy_engine.get('messages', [])
                if messages:
                    print(f"Messages ({len(messages)}):")
                    for msg in messages[:2]:  # Show first 2
                        print(f"  - {msg}")
            
            # Dr. Paula Assessment
            dra_paula_assessment = result.get('dra_paula_assessment', '')
            if dra_paula_assessment:
                print(f"\n👩‍⚕️ DRA. PAULA ASSESSMENT:")
                print(f"{dra_paula_assessment[:200]}...")
            
            # Check for forensic analysis structure
            print(f"\n🔍 ESTRUTURA DE ANÁLISE FORENSE:")
            print(f"Enhanced Analysis Present: {bool(enhanced_analysis)}")
            print(f"Policy Engine Present: {bool(policy_engine)}")
            print(f"Detailed Analysis Present: {bool(enhanced_analysis.get('detailed_analysis'))}")
            
            # Check if this looks like the 7-layer forensic analysis
            has_forensic_structure = (
                enhanced_analysis and
                'confidence_score' in enhanced_analysis and
                'verdict' in enhanced_analysis and
                'detailed_analysis' in enhanced_analysis
            )
            
            print(f"Forensic Structure Detected: {has_forensic_structure}")
            
            if not has_forensic_structure:
                print("\n❌ PROBLEMA: Estrutura de análise forense de 7 camadas não detectada!")
                print("A análise não está retornando o formato JSON estruturado esperado.")
            else:
                print("\n✅ Estrutura de análise aprimorada detectada!")
            
        else:
            print(f"❌ ERRO: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")

if __name__ == "__main__":
    test_direct_api_call()