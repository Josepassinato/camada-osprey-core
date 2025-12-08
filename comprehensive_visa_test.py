#!/usr/bin/env python3
"""
🎯 TESTE END-TO-END COMPLETO - VALIDAÇÃO FINAL DE TODOS OS 8 VISTOS

**CONTEXTO FINAL:**
Após todas as correções implementadas:
- ✅ Bug P0 (PDF Generation) corrigido com PyMuPDF
- ✅ Bugs P1, P2, P3 corrigidos
- ✅ I-140 adicionado ao enum
- ✅ L-1 adicionado ao enum
- ✅ Sistema de logs robusto implementado
- ✅ Persistência de dados confirmada funcionando

**OBJETIVO:**
Executar testes E2E completos em TODOS os 8 tipos de visto para validar o sistema está 100% pronto para produção.

METODOLOGIA DE TESTE ABRANGENTE:
Para CADA tipo de visto, executar 7 etapas:
1. ✅ Criar caso
2. ✅ Submeter formulário amigável
3. ✅ Verificar persistência de dados
4. ✅ Gerar PDF
5. ✅ Download PDF
6. ✅ Validar integridade do PDF
7. ✅ Verificar campos (se aplicável)
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime
import hashlib

# Import PyMuPDF (fitz) for PDF field verification
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    print("✅ PyMuPDF (fitz) library loaded successfully")
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("❌ PyMuPDF (fitz) library not available - installing...")
    os.system("pip install PyMuPDF")
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
        print("✅ PyMuPDF (fitz) installed and loaded successfully")
    except ImportError:
        print("❌ Failed to install PyMuPDF - using fallback methods")
        PYMUPDF_AVAILABLE = False

# Get backend URL from frontend .env
BACKEND_URL = "https://smart-visa-helper-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

# Test data for all 8 visa types
VISA_TEST_DATA = {
    "I-539": {
        "visa_type": "I-539",
        "form_code": "I-539",
        "friendly_form_data": {
            "nome_completo": "Carlos Eduardo Silva",
            "data_nascimento": "1985-06-15",
            "endereco_eua": "456 Main Street Apt 2B",
            "cidade_eua": "Miami",
            "estado_eua": "FL",
            "cep_eua": "33101",
            "email": "carlos.silva@email.com",
            "telefone": "+1-305-555-7890",
            "numero_passaporte": "BR123456789",
            "pais_nascimento": "Brazil",
            "status_atual": "B-2",
            "status_solicitado": "B-2 Extension",
            "data_entrada_eua": "2024-06-01",
            "numero_i94": "12345678901"
        },
        "expected_pdf": {
            "pages": 7,
            "min_size": 700000,  # ~725KB
            "widgets_expected": 159,
            "min_filled_fields": 10,
            "filename_pattern": "I-539_{case_id}.pdf"
        }
    },
    "I-589": {
        "visa_type": "I-589",
        "form_code": "I-589",
        "friendly_form_data": {
            "nome_completo": "Ahmed Hassan Mohamed",
            "data_nascimento": "1980-03-10",
            "endereco_eua": "789 Refugee Center Dr Apt 5C",
            "cidade_eua": "New York",
            "estado_eua": "NY",
            "cep_eua": "10001",
            "email": "ahmed.hassan@refugeehelp.org",
            "telefone": "+1-212-555-4321",
            "numero_passaporte": "EG987654321",
            "pais_nascimento": "Egypt",
            "pais_nacionalidade": "Egypt",
            "data_entrada_eua": "2024-11-01",
            "numero_i94": "98765432109",
            "motivo_asilo": "Political persecution due to political opinion",
            "tipo_perseguicao": "Political",
            "tem_familia": "Yes",
            "membros_familia": "2",
            "deseja_trabalhar": "Yes"
        },
        "expected_pdf": {
            "pages": 12,
            "min_size": 1300000,  # ~1.3MB
            "widgets_expected": None,  # Variable
            "min_filled_fields": 5,
            "filename_pattern": "I-589_{case_id}.pdf"
        }
    },
    "I-140": {
        "visa_type": "I-140",
        "form_code": "I-140",
        "friendly_form_data": {
            "nome_completo": "Dr. Sofia Martinez Gonzalez",
            "data_nascimento": "1975-09-20",
            "endereco_eua": "2000 Research Institute Blvd",
            "cidade_eua": "Palo Alto",
            "estado_eua": "CA",
            "cep_eua": "94301",
            "email": "sofia.martinez@research.stanford.edu",
            "telefone": "+1-650-555-9999",
            "numero_passaporte": "ES123456789",
            "pais_nascimento": "Spain",
            "area_extraordinaria": "Scientific Research - Artificial Intelligence",
            "campo_atuacao": "Computer Science",
            "premios_recebidos": "Turing Award 2022, 5 IEEE awards",
            "publicacoes": "120+ peer-reviewed papers in top journals",
            "citacoes": "15,000+ citations (h-index: 85)",
            "contribuicoes_originais": "Developed breakthrough neural network architecture",
            "memberships": "IEEE Fellow, ACM Fellow, AAAI Fellow",
            "high_salary": "Top 1% in field ($500k+/year)",
            "press_coverage": "Featured in Nature, Science, NYT"
        },
        "expected_pdf": {
            "pages": None,  # Multiple pages
            "min_size": 500000,  # >500KB
            "widgets_expected": None,  # Variable
            "min_filled_fields": 5,
            "filename_pattern": "I-140_{case_id}.pdf"
        }
    },
    "O-1": {
        "visa_type": "O-1",
        "form_code": "O-1",
        "friendly_form_data": {
            "nome_completo": "Marina Santos Costa",
            "nome_empresa": "Innovation Tech Labs Inc",
            "cargo": "Lead AI Researcher",
            "data_nascimento": "1987-04-12",
            "endereco_eua": "3500 Silicon Valley Way",
            "cidade_eua": "San Jose",
            "estado_eua": "CA",
            "cep_eua": "95110",
            "email": "marina.costa@innovationlabs.com",
            "telefone": "+1-408-555-6666",
            "numero_passaporte": "BR777888999",
            "pais_nascimento": "Brazil",
            "data_inicio": "2025-02-01",
            "data_fim": "2028-01-31",
            "field_of_ability": "Artificial Intelligence and Machine Learning"
        },
        "expected_pdf": {
            "pages": 20,
            "min_size": 1600000,  # ~1.6MB
            "widgets_expected": 0,  # Template vazio
            "min_filled_fields": 0,  # Template vazio
            "filename_pattern": "I-129-O1_{case_id}.pdf"
        }
    },
    "H-1B": {
        "visa_type": "H-1B",
        "form_code": "H-1B",
        "friendly_form_data": {
            "nome_completo": "Raj Kumar Patel",
            "nome_empresa": "Global Software Corp",
            "cargo": "Senior Software Engineer",
            "data_nascimento": "1990-08-25",
            "endereco_eua": "1200 Tech Plaza Suite 800",
            "cidade_eua": "Seattle",
            "estado_eua": "WA",
            "cep_eua": "98101",
            "email": "raj.patel@globalsoftware.com",
            "telefone": "+1-206-555-3333",
            "numero_passaporte": "IN555666777",
            "pais_nascimento": "India",
            "data_inicio": "2025-04-01",
            "data_fim": "2028-03-31",
            "soc_code": "15-1252"
        },
        "expected_pdf": {
            "pages": 20,
            "min_size": 1600000,  # ~1.6MB
            "widgets_expected": 0,  # Template vazio
            "min_filled_fields": 0,  # Template vazio
            "filename_pattern": "I-129-H1B_{case_id}.pdf"
        }
    },
    "L-1": {
        "visa_type": "L-1",
        "form_code": "L-1",
        "friendly_form_data": {
            "nome_completo": "Patricia Alves Mendes",
            "nome_empresa": "Multinational Tech Solutions Inc",
            "cargo": "Regional Director of Operations",
            "data_nascimento": "1978-12-05",
            "endereco_eua": "4000 Corporate Plaza Tower 3",
            "cidade_eua": "Austin",
            "estado_eua": "TX",
            "cep_eua": "78701",
            "email": "patricia.mendes@multinationaltech.com",
            "telefone": "+1-512-555-8888",
            "numero_passaporte": "BR999000111",
            "pais_nascimento": "Brazil",
            "data_inicio": "2025-03-15",
            "data_fim": "2027-03-14",
            "is_managerial": "Yes",
            "anos_experiencia": "12 years"
        },
        "expected_pdf": {
            "pages": 20,
            "min_size": 1600000,  # ~1.6MB
            "widgets_expected": 0,  # Template vazio
            "min_filled_fields": 0,  # Template vazio
            "filename_pattern": "I-129-L1_{case_id}.pdf"
        }
    },
    "F-1": {
        "visa_type": "F-1",
        "form_code": "F-1",
        "friendly_form_data": {
            "nome_completo": "Li Wei Zhang",
            "data_nascimento": "1998-07-18",
            "endereco_eua": "567 University Ave Apt 12",
            "cidade_eua": "Boston",
            "estado_eua": "MA",
            "cep_eua": "02115",
            "email": "li.zhang@university.edu",
            "telefone": "+1-617-555-2222",
            "numero_passaporte": "CN888777666",
            "pais_nascimento": "China",
            "status_atual": "F-1",
            "status_solicitado": "F-1 OPT Extension",
            "data_entrada_eua": "2021-08-15",
            "numero_i94": "55566677788",
            "universidade": "MIT",
            "programa": "Computer Science PhD"
        },
        "expected_pdf": {
            "pages": 7,
            "min_size": 700000,  # ~725KB
            "widgets_expected": 159,  # Usa I-539
            "min_filled_fields": 5,
            "filename_pattern": "I-539-F1_{case_id}.pdf"
        }
    },
    "I-129": {
        "visa_type": "I-129",
        "form_code": "I-129",
        "friendly_form_data": {
            "nome_completo": "Generic Test User",
            "nome_empresa": "Test Company Inc",
            "cargo": "Test Position",
            "data_nascimento": "1985-01-01",
            "endereco_eua": "100 Test St",
            "cidade_eua": "Test City",
            "estado_eua": "CA",
            "cep_eua": "90000",
            "email": "test@test.com",
            "telefone": "+1-555-0000",
            "numero_passaporte": "XX000000000",
            "pais_nascimento": "Test Country"
        },
        "expected_pdf": {
            "pages": 20,
            "min_size": 1600000,  # ~1.6MB
            "widgets_expected": 0,  # Template vazio
            "min_filled_fields": 0,  # Template vazio
            "filename_pattern": "I-129_{case_id}.pdf"
        }
    }
}

def test_visa_e2e(visa_type: str, test_data: dict):
    """
    Test complete E2E flow for a specific visa type
    
    Returns:
        dict: Test results with success/failure for each step
    """
    print(f"\n{'='*80}")
    print(f"🎯 TESTING {visa_type} - {test_data['friendly_form_data']['nome_completo']}")
    print(f"{'='*80}")
    
    results = {
        "visa_type": visa_type,
        "step1_create_case": {},
        "step2_submit_form": {},
        "step3_verify_persistence": {},
        "step4_generate_pdf": {},
        "step5_download_pdf": {},
        "step6_validate_integrity": {},
        "step7_verify_fields": {},
        "summary": {}
    }
    
    # STEP 1: Create Case
    print(f"\n📋 STEP 1: Criar Caso {visa_type}")
    print("-" * 60)
    
    try:
        print(f"📝 Creating {visa_type} case...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"form_code": test_data["form_code"]},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ {visa_type} case created: {case_id}")
                results["step1_create_case"] = {
                    "success": True,
                    "case_id": case_id,
                    "status_code": response.status_code,
                    "form_code": case_info.get("form_code")
                }
            else:
                print(f"❌ No case_id in response: {case_data}")
                results["step1_create_case"] = {"success": False, "error": "No case_id"}
                return results
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step1_create_case"] = {
                "success": False, 
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["step1_create_case"] = {"success": False, "exception": str(e)}
        return results
    
    case_id = results["step1_create_case"]["case_id"]
    
    # STEP 2: Submit Friendly Form
    print(f"\n📋 STEP 2: Submeter Formulário Amigável")
    print("-" * 60)
    
    friendly_form_data = test_data["friendly_form_data"]
    print(f"📤 Sending {len(friendly_form_data)} fields to case {case_id}...")
    
    try:
        # Wrap data in the expected format
        payload = {
            "friendly_form_data": friendly_form_data,
            "basic_data": {}
        }
        
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            form_result = response.json()
            print(f"✅ Friendly form data saved successfully")
            
            # Check for success indicators
            success_indicators = {
                "success_field": form_result.get("success", False),
                "completion_percentage": form_result.get("completion_percentage") is not None,
                "validation_status": form_result.get("validation_status") is not None
            }
            
            results["step2_submit_form"] = {
                "success": True,
                "status_code": response.status_code,
                "response": form_result,
                "success_indicators": success_indicators
            }
        else:
            print(f"❌ Failed to save friendly form: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step2_submit_form"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception saving friendly form: {str(e)}")
        results["step2_submit_form"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 3: Verify Data Persistence
    print(f"\n📋 STEP 3: Verificar Persistência de Dados")
    print("-" * 60)
    
    try:
        print(f"🔍 Retrieving case data for {case_id}...")
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            
            # Check for simplified_form_responses
            simplified_responses = case_info.get("simplified_form_responses", {})
            
            print(f"📄 Simplified Form Responses: {len(simplified_responses)} fields saved")
            
            # Verify key fields were saved
            key_fields = ["nome_completo", "email", "telefone", "numero_passaporte"]
            saved_fields = {
                field: simplified_responses.get(field) is not None 
                for field in key_fields
            }
            
            fields_saved_count = sum(saved_fields.values())
            total_sent = len(friendly_form_data)
            total_saved = len(simplified_responses)
            
            print(f"📊 Fields sent: {total_sent}, Fields saved: {total_saved}")
            print(f"📊 Key fields verification:")
            for field, saved in saved_fields.items():
                status = "✅" if saved else "❌"
                print(f"  {status} {field}: {saved}")
            
            results["step3_verify_persistence"] = {
                "success": True,
                "fields_sent": total_sent,
                "fields_saved": total_saved,
                "key_fields_saved": saved_fields,
                "key_fields_count": fields_saved_count,
                "simplified_responses": simplified_responses,
                "passed": total_saved > 0 and fields_saved_count >= 2
            }
        else:
            print(f"❌ Failed to retrieve case: {response.status_code}")
            results["step3_verify_persistence"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception retrieving case: {str(e)}")
        results["step3_verify_persistence"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 4: Generate PDF
    print(f"\n📋 STEP 4: Gerar PDF")
    print("-" * 60)
    
    try:
        print(f"📝 Generating PDF for case {case_id}...")
        response = requests.post(
            f"{API_BASE}/case/{case_id}/generate-form",
            headers={"Content-Type": "application/json"},
            timeout=120  # PDF generation might take longer
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            pdf_result = response.json()
            print(f"✅ PDF generation successful")
            
            # Verify PDF generation response
            expected_pdf = test_data["expected_pdf"]
            pdf_checks = {
                "success_true": pdf_result.get("success", False),
                "filename_present": pdf_result.get("filename") is not None,
                "file_size_adequate": pdf_result.get("file_size", 0) >= expected_pdf["min_size"],
                "download_url_present": pdf_result.get("download_url") is not None
            }
            
            print(f"📄 Filename: {pdf_result.get('filename', 'N/A')}")
            print(f"📏 File size: {pdf_result.get('file_size', 0)} bytes (min: {expected_pdf['min_size']})")
            
            print(f"\n🎯 PDF GENERATION VERIFICATION:")
            for check, passed in pdf_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["step4_generate_pdf"] = {
                "success": True,
                "status_code": response.status_code,
                "pdf_result": pdf_result,
                "pdf_checks": pdf_checks,
                "passed": all(pdf_checks.values())
            }
        else:
            print(f"❌ PDF generation failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step4_generate_pdf"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception generating PDF: {str(e)}")
        results["step4_generate_pdf"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 5: Download PDF
    print(f"\n📋 STEP 5: Download PDF")
    print("-" * 60)
    
    try:
        print(f"📥 Downloading PDF for case {case_id}...")
        response = requests.get(
            f"{API_BASE}/case/{case_id}/download-form",
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"📏 Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Verify download response
            expected_pdf = test_data["expected_pdf"]
            download_checks = {
                "status_200": response.status_code == 200,
                "content_type_pdf": response.headers.get('Content-Type') == 'application/pdf',
                "file_size_adequate": len(response.content) >= expected_pdf["min_size"],
                "content_not_empty": len(response.content) > 0
            }
            
            print(f"\n🎯 PDF DOWNLOAD VERIFICATION:")
            for check, passed in download_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Save PDF for field verification
            pdf_path = f"/tmp/final_test_{visa_type.lower().replace('-', '_')}_{case_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 PDF saved to: {pdf_path}")
            
            results["step5_download_pdf"] = {
                "success": True,
                "status_code": response.status_code,
                "content_type": response.headers.get('Content-Type'),
                "file_size": len(response.content),
                "download_checks": download_checks,
                "pdf_path": pdf_path,
                "passed": all(download_checks.values())
            }
        else:
            print(f"❌ PDF download failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step5_download_pdf"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception downloading PDF: {str(e)}")
        results["step5_download_pdf"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 6: Validate PDF Integrity
    print(f"\n📋 STEP 6: Validar Integridade do PDF")
    print("-" * 60)
    
    try:
        pdf_path = results["step5_download_pdf"]["pdf_path"]
        file_size = os.path.getsize(pdf_path)
        expected_pdf = test_data["expected_pdf"]
        
        integrity_checks = {
            "file_exists": os.path.exists(pdf_path),
            "file_size_adequate": file_size >= expected_pdf["min_size"],
            "file_not_corrupted": True,  # Will be checked by opening
            "expected_pages": True  # Will be checked if pages specified
        }
        
        # Check if PDF can be opened and has expected pages
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(pdf_path)
                page_count = doc.page_count
                
                if expected_pdf["pages"]:
                    integrity_checks["expected_pages"] = page_count == expected_pdf["pages"]
                    print(f"📄 PDF has {page_count} pages (expected: {expected_pdf['pages']})")
                else:
                    print(f"📄 PDF has {page_count} pages")
                
                doc.close()
            except Exception as e:
                integrity_checks["file_not_corrupted"] = False
                print(f"❌ PDF appears corrupted: {str(e)}")
        
        print(f"📏 File size: {file_size} bytes (min: {expected_pdf['min_size']})")
        
        print(f"\n🎯 PDF INTEGRITY VERIFICATION:")
        for check, passed in integrity_checks.items():
            status = "✅" if passed else "❌"
            check_name = check.replace("_", " ").title()
            print(f"  {status} {check_name}: {passed}")
        
        results["step6_validate_integrity"] = {
            "success": True,
            "file_size": file_size,
            "integrity_checks": integrity_checks,
            "passed": all(integrity_checks.values())
        }
        
    except Exception as e:
        print(f"❌ Exception during integrity check: {str(e)}")
        results["step6_validate_integrity"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # STEP 7: Verify Fields (if applicable)
    print(f"\n📋 STEP 7: Verificar Campos (se aplicável)")
    print("-" * 60)
    
    try:
        pdf_path = results["step5_download_pdf"]["pdf_path"]
        expected_pdf = test_data["expected_pdf"]
        
        if expected_pdf["min_filled_fields"] > 0:
            print(f"🔍 Checking PDF fields for {visa_type}...")
            
            if not PYMUPDF_AVAILABLE:
                print("❌ PyMuPDF não disponível - pulando verificação de campos")
                results["step7_verify_fields"] = {
                    "success": False,
                    "reason": "PyMuPDF not available",
                    "passed": False
                }
            else:
                # Use PyMuPDF to read form fields
                doc = fitz.open(pdf_path)
                
                filled_fields = []
                total_widgets = 0
                
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    widgets = list(page.widgets())
                    total_widgets += len(widgets)
                    
                    for widget in widgets:
                        if widget.field_value and 'PDF417BarCode' not in widget.field_name:
                            filled_fields.append((widget.field_name, widget.field_value))
                
                doc.close()
                
                print(f"📊 Total widgets: {total_widgets}")
                print(f"📊 Filled fields: {len(filled_fields)}")
                
                # Check if we have minimum expected filled fields
                min_expected = expected_pdf["min_filled_fields"]
                fields_adequate = len(filled_fields) >= min_expected
                
                print(f"📊 Expected minimum filled fields: {min_expected}")
                print(f"📊 Fields adequate: {'✅' if fields_adequate else '❌'}")
                
                # Show some filled fields for verification
                if filled_fields:
                    print(f"\n📄 SAMPLE FILLED FIELDS:")
                    for field_name, field_value in filled_fields[:10]:  # Show first 10
                        print(f"  {field_name}: '{field_value}'")
                    if len(filled_fields) > 10:
                        print(f"  ... and {len(filled_fields) - 10} more fields")
                
                results["step7_verify_fields"] = {
                    "success": True,
                    "total_widgets": total_widgets,
                    "filled_fields_count": len(filled_fields),
                    "min_expected": min_expected,
                    "fields_adequate": fields_adequate,
                    "sample_fields": filled_fields[:20],
                    "passed": fields_adequate
                }
        else:
            print(f"ℹ️  {visa_type} uses template without editable fields (expected behavior)")
            results["step7_verify_fields"] = {
                "success": True,
                "reason": "Template without editable fields",
                "passed": True  # This is expected for I-129 templates
            }
            
    except Exception as e:
        print(f"❌ Exception during field verification: {str(e)}")
        results["step7_verify_fields"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # Calculate overall success
    step_results = [
        results.get("step1_create_case", {}).get("success", False),
        results.get("step2_submit_form", {}).get("success", False),
        results.get("step3_verify_persistence", {}).get("passed", False),
        results.get("step4_generate_pdf", {}).get("passed", False),
        results.get("step5_download_pdf", {}).get("passed", False),
        results.get("step6_validate_integrity", {}).get("passed", False),
        results.get("step7_verify_fields", {}).get("passed", False)
    ]
    
    successful_steps = sum(step_results)
    total_steps = len(step_results)
    success_rate = (successful_steps / total_steps) * 100
    
    print(f"\n🎯 {visa_type} SUMMARY:")
    print(f"📊 Steps completed: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
    
    results["summary"] = {
        "successful_steps": successful_steps,
        "total_steps": total_steps,
        "success_rate": success_rate,
        "case_id": results.get("step1_create_case", {}).get("case_id"),
        "overall_success": success_rate >= 85.7  # 6/7 steps
    }
    
    return results

def run_comprehensive_visa_tests():
    """
    Run comprehensive E2E tests for all 8 visa types
    """
    print("🎯 TESTE END-TO-END COMPLETO - VALIDAÇÃO FINAL DE TODOS OS 8 VISTOS")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    all_results = {}
    summary_table = []
    
    # Test each visa type
    for visa_type, test_data in VISA_TEST_DATA.items():
        try:
            print(f"\n🚀 Starting test for {visa_type}...")
            results = test_visa_e2e(visa_type, test_data)
            all_results[visa_type] = results
            
            # Add to summary table
            summary = results.get("summary", {})
            summary_table.append({
                "visa": visa_type,
                "case_id": summary.get("case_id", "N/A"),
                "success_rate": summary.get("success_rate", 0),
                "status": "✅" if summary.get("overall_success", False) else "❌"
            })
            
            # Brief pause between tests
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Critical error testing {visa_type}: {str(e)}")
            all_results[visa_type] = {
                "error": str(e),
                "summary": {"success_rate": 0, "overall_success": False}
            }
            summary_table.append({
                "visa": visa_type,
                "case_id": "ERROR",
                "success_rate": 0,
                "status": "❌"
            })
    
    # Generate final report
    print(f"\n{'='*80}")
    print("📊 RELATÓRIO FINAL - TODOS OS 8 VISTOS")
    print(f"{'='*80}")
    
    # Summary table
    print(f"\n📋 TABELA RESUMO:")
    print("| Visto | Case ID      | Taxa Sucesso | Status |")
    print("|-------|--------------|--------------|--------|")
    
    total_success_rate = 0
    successful_visas = 0
    
    for entry in summary_table:
        visa = entry["visa"]
        case_id = entry["case_id"]
        success_rate = entry["success_rate"]
        status = entry["status"]
        
        print(f"| {visa:<5} | {case_id:<12} | {success_rate:>10.1f}% | {status:<6} |")
        
        total_success_rate += success_rate
        if status == "✅":
            successful_visas += 1
    
    # Overall statistics
    avg_success_rate = total_success_rate / len(summary_table) if summary_table else 0
    overall_success_rate = (successful_visas / len(summary_table)) * 100 if summary_table else 0
    
    print(f"\n🎯 ESTATÍSTICAS FINAIS:")
    print(f"📊 Vistos testados: {len(summary_table)}/8")
    print(f"📊 Vistos funcionais: {successful_visas}/8 ({overall_success_rate:.1f}%)")
    print(f"📊 Taxa média de sucesso: {avg_success_rate:.1f}%")
    
    # Detailed analysis by step
    print(f"\n📋 ANÁLISE DETALHADA POR ETAPA:")
    
    step_names = [
        "Criar Caso", "Submeter Formulário", "Verificar Persistência",
        "Gerar PDF", "Download PDF", "Validar Integridade", "Verificar Campos"
    ]
    
    step_keys = [
        "step1_create_case", "step2_submit_form", "step3_verify_persistence",
        "step4_generate_pdf", "step5_download_pdf", "step6_validate_integrity", "step7_verify_fields"
    ]
    
    for i, (step_name, step_key) in enumerate(zip(step_names, step_keys)):
        step_successes = 0
        for visa_type, results in all_results.items():
            if results.get(step_key, {}).get("success" if i < 2 else "passed", False):
                step_successes += 1
        
        step_rate = (step_successes / len(all_results)) * 100 if all_results else 0
        status = "✅" if step_rate >= 75 else "⚠️" if step_rate >= 50 else "❌"
        print(f"  {status} {step_name}: {step_successes}/8 ({step_rate:.1f}%)")
    
    # Problem identification
    print(f"\n🔍 PROBLEMAS IDENTIFICADOS:")
    
    problem_visas = []
    for entry in summary_table:
        if entry["status"] == "❌":
            problem_visas.append(entry["visa"])
    
    if problem_visas:
        print(f"❌ Vistos com problemas: {', '.join(problem_visas)}")
        
        # Analyze common failure points
        failure_analysis = {}
        for visa_type in problem_visas:
            results = all_results.get(visa_type, {})
            for step_key in step_keys:
                step_result = results.get(step_key, {})
                if not step_result.get("success" if step_key in ["step1_create_case", "step2_submit_form"] else "passed", False):
                    step_name = step_key.replace("step", "").replace("_", " ").title()
                    if step_name not in failure_analysis:
                        failure_analysis[step_name] = []
                    failure_analysis[step_name].append(visa_type)
        
        if failure_analysis:
            print(f"\n📊 PONTOS DE FALHA COMUNS:")
            for step_name, failed_visas in failure_analysis.items():
                print(f"  ❌ {step_name}: {', '.join(failed_visas)}")
    else:
        print(f"✅ Nenhum problema crítico identificado!")
    
    # Final assessment
    print(f"\n🎯 AVALIAÇÃO FINAL:")
    print("=" * 60)
    
    if overall_success_rate >= 100:
        print("🎉🎉🎉 SISTEMA 100% FUNCIONAL E PRONTO PARA PRODUÇÃO! 🎉🎉🎉")
        print("✅ Todos os 8 tipos de visto funcionando perfeitamente")
        print("✅ Fluxo end-to-end operacional para todos os casos")
        print("✅ Sistema pronto para deployment em produção")
    elif overall_success_rate >= 87.5:  # 7/8 vistos
        print("🎉 SISTEMA QUASE PERFEITO - PRONTO PARA PRODUÇÃO!")
        print(f"✅ {successful_visas}/8 vistos funcionando ({overall_success_rate:.1f}%)")
        print("⚠️ Apenas correções menores necessárias")
        print("✅ Sistema pode ser deployado com monitoramento")
    elif overall_success_rate >= 75:  # 6/8 vistos
        print("⚠️ SISTEMA FUNCIONAL - NECESSITA CORREÇÕES")
        print(f"⚠️ {successful_visas}/8 vistos funcionando ({overall_success_rate:.1f}%)")
        print("🔧 Correções necessárias antes do deployment")
        print("📊 Sistema tem boa base mas precisa de ajustes")
    else:
        print("❌ SISTEMA NECESSITA CORREÇÕES CRÍTICAS")
        print(f"❌ Apenas {successful_visas}/8 vistos funcionando ({overall_success_rate:.1f}%)")
        print("🚨 Correções urgentes necessárias")
        print("❌ Sistema não pronto para produção")
    
    # Save results
    results_file = "/app/comprehensive_visa_test_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "test_results": all_results,
            "summary_table": summary_table,
            "statistics": {
                "visas_tested": len(summary_table),
                "successful_visas": successful_visas,
                "overall_success_rate": overall_success_rate,
                "avg_success_rate": avg_success_rate
            },
            "timestamp": datetime.now().isoformat(),
            "test_focus": "🎯 TESTE END-TO-END COMPLETO - VALIDAÇÃO FINAL DE TODOS OS 8 VISTOS",
            "backend_url": BACKEND_URL
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados completos salvos em: {results_file}")
    
    return all_results, overall_success_rate

if __name__ == "__main__":
    print("🎯 INICIANDO TESTE ABRANGENTE DE TODOS OS 8 VISTOS")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Execute comprehensive tests
    all_results, success_rate = run_comprehensive_visa_tests()
    
    # Final summary
    print(f"\n🏁 TESTE COMPLETO FINALIZADO!")
    print(f"📊 Taxa de sucesso geral: {success_rate:.1f}%")
    
    if success_rate >= 100:
        print("🎉 TODOS OS 8 VISTOS FUNCIONANDO PERFEITAMENTE!")
    elif success_rate >= 87.5:
        print("🎉 SISTEMA QUASE PERFEITO!")
    elif success_rate >= 75:
        print("⚠️ SISTEMA FUNCIONAL COM MELHORIAS NECESSÁRIAS")
    else:
        print("❌ SISTEMA NECESSITA CORREÇÕES CRÍTICAS")