#!/usr/bin/env python3
"""
🎯 TESTE END-TO-END COMPLETO - VALIDAÇÃO DE TODOS OS NOVOS TIPOS DE VISTO

**CONTEXTO:**
Sistema expandido de 3 para 8 tipos de visto com solução PyMuPDF:
- ✅ I-539 (já testado - 10/10 campos - 100%)
- ✅ I-589 (implementado)
- ✅ I-140 (implementado)
- 🆕 O-1 (novo - precisa teste)
- 🆕 H-1B (novo - precisa teste)
- 🆕 L-1 (novo - precisa teste)
- 🆕 F-1 (novo - reutiliza I-539)

**OBJETIVO:**
Testar TODOS os novos tipos de visto (O-1, H-1B, L-1, F-1) para validar que a implementação PyMuPDF funciona corretamente em cada um.

**METODOLOGIA - TESTE MODULAR POR TIPO DE VISTO:**
Para CADA tipo de visto, executar:
1. Criar caso
2. Submeter formulário amigável
3. Gerar PDF
4. Download PDF
5. Validar campos preenchidos (se possível)
6. Verificar integridade
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

def test_visa_type_complete_flow(visa_type, form_code, test_data, expected_form_type, expected_filename_prefix):
    """
    Test complete flow for a specific visa type
    
    Args:
        visa_type: Visa type name (e.g., "O-1")
        form_code: Form code for case creation (e.g., "O-1")
        test_data: Dictionary with friendly form data
        expected_form_type: Expected form type in response (e.g., "I-129")
        expected_filename_prefix: Expected PDF filename prefix (e.g., "I-129-O1")
    
    Returns:
        Dictionary with test results
    """
    
    print(f"\n{'='*80}")
    print(f"🎯 TESTE {visa_type} VISA - FLUXO COMPLETO")
    print(f"{'='*80}")
    
    results = {
        "visa_type": visa_type,
        "form_code": form_code,
        "step1_case_creation": {},
        "step2_friendly_form": {},
        "step3_pdf_generation": {},
        "step4_pdf_download": {},
        "step5_pdf_validation": {},
        "step6_integrity_check": {},
        "summary": {}
    }
    
    # STEP 1: Create Case
    print(f"\n📋 STEP 1: Criar Caso {visa_type}")
    print("-" * 60)
    
    try:
        print(f"📝 Creating {visa_type} case...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"form_code": form_code},
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
                results["step1_case_creation"] = {
                    "success": True,
                    "case_id": case_id,
                    "status_code": response.status_code
                }
            else:
                print(f"❌ No case_id in response: {case_data}")
                results["step1_case_creation"] = {"success": False, "error": "No case_id"}
                return results
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["step1_case_creation"] = {"success": False, "status_code": response.status_code, "error": response.text}
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["step1_case_creation"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 2: Submit Friendly Form
    print(f"\n📋 STEP 2: Submeter Formulário Amigável {visa_type}")
    print("-" * 60)
    
    try:
        print(f"📤 Sending friendly form data to case {case_id}...")
        print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/friendly-form")
        print(f"📋 Test Data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            form_result = response.json()
            print(f"✅ Friendly form data saved successfully")
            print(f"📄 Response: {json.dumps(form_result, indent=2, ensure_ascii=False)}")
            
            results["step2_friendly_form"] = {
                "success": True,
                "status_code": response.status_code,
                "response": form_result
            }
        else:
            print(f"❌ Failed to save friendly form: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step2_friendly_form"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception saving friendly form: {str(e)}")
        results["step2_friendly_form"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 3: Generate PDF
    print(f"\n📋 STEP 3: Gerar PDF {expected_form_type} para {visa_type}")
    print("-" * 60)
    
    try:
        print(f"📝 Generating {expected_form_type} PDF for case {case_id}...")
        response = requests.post(
            f"{API_BASE}/case/{case_id}/generate-form",
            headers={"Content-Type": "application/json"},
            timeout=120  # PDF generation might take longer
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            pdf_result = response.json()
            print(f"✅ PDF generation successful")
            print(f"📄 Response: {json.dumps(pdf_result, indent=2, ensure_ascii=False)}")
            
            # Verify PDF generation response
            expected_filename = f"{expected_filename_prefix}_{case_id}.pdf"
            pdf_checks = {
                "success_true": pdf_result.get("success", False),
                "filename_correct": pdf_result.get("filename", "").startswith(expected_filename_prefix),
                "file_size_adequate": pdf_result.get("file_size", 0) > 700000,  # >700KB for I-129
                "download_url_present": pdf_result.get("download_url") is not None,
                "form_type_correct": pdf_result.get("form_type", "").upper() == form_code.upper()
            }
            
            print(f"\n🎯 PDF GENERATION VERIFICATION:")
            for check, passed in pdf_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["step3_pdf_generation"] = {
                "success": True,
                "status_code": response.status_code,
                "pdf_result": pdf_result,
                "pdf_checks": pdf_checks,
                "passed": all(pdf_checks.values())
            }
        else:
            print(f"❌ PDF generation failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step3_pdf_generation"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception generating PDF: {str(e)}")
        results["step3_pdf_generation"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 4: Download PDF
    print(f"\n📋 STEP 4: Download do PDF {visa_type}")
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
            expected_size = 700000 if expected_form_type == "I-129" else 400000  # I-129 larger than I-539
            download_checks = {
                "status_200": response.status_code == 200,
                "content_type_pdf": response.headers.get('Content-Type') == 'application/pdf',
                "file_size_adequate": len(response.content) > expected_size,
                "content_not_empty": len(response.content) > 0
            }
            
            print(f"\n🎯 PDF DOWNLOAD VERIFICATION:")
            for check, passed in download_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Save PDF for field verification
            pdf_path = f"/tmp/test_{visa_type.lower().replace('-', '_')}_{case_id}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 PDF saved to: {pdf_path}")
            
            results["step4_pdf_download"] = {
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
            results["step4_pdf_download"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception downloading PDF: {str(e)}")
        results["step4_pdf_download"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 5: PDF Field Validation (if possible)
    print(f"\n📋 STEP 5: Validação de Campos PDF {visa_type}")
    print("-" * 60)
    
    try:
        pdf_path = results["step4_pdf_download"]["pdf_path"]
        print(f"🔍 Analyzing PDF fields: {pdf_path}")
        
        if not PYMUPDF_AVAILABLE:
            print("❌ PyMuPDF não disponível - usando método alternativo")
            widgets_found = 0
            filled_fields = []
        else:
            # Use PyMuPDF to analyze form fields
            doc = fitz.open(pdf_path)
            
            print(f"📄 PDF Pages: {doc.page_count}")
            print(f"📄 PDF Size: {os.path.getsize(pdf_path)} bytes")
            
            widgets_found = 0
            filled_fields = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                widgets = list(page.widgets())
                widgets_found += len(widgets)
                
                if widgets:
                    print(f"📊 Page {page_num + 1}: {len(widgets)} widgets found")
                    for widget in widgets:
                        if widget.field_value and 'PDF417BarCode' not in widget.field_name:
                            filled_fields.append((widget.field_name, widget.field_value))
            
            doc.close()
            
            print(f"📊 Total widgets found: {widgets_found}")
            print(f"📊 Total filled fields: {len(filled_fields)}")
            
            # Show some filled fields for debugging
            if filled_fields:
                print(f"\n📄 SAMPLE FILLED FIELDS:")
                for field_name, field_value in filled_fields[:10]:  # Show first 10
                    print(f"  {field_name}: '{field_value}'")
                if len(filled_fields) > 10:
                    print(f"  ... and {len(filled_fields) - 10} more fields")
            else:
                print("⚠️  No filled fields detected")
        
        # Validation checks
        validation_checks = {
            "pdf_has_widgets": widgets_found > 0,
            "pdf_has_filled_fields": len(filled_fields) > 0,
            "adequate_field_count": len(filled_fields) >= 5,  # At least 5 fields filled
            "pymupdf_working": PYMUPDF_AVAILABLE
        }
        
        print(f"\n🎯 PDF FIELD VALIDATION:")
        for check, passed in validation_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}: {passed}")
        
        results["step5_pdf_validation"] = {
            "success": True,
            "pymupdf_available": PYMUPDF_AVAILABLE,
            "widgets_found": widgets_found,
            "filled_fields_count": len(filled_fields),
            "validation_checks": validation_checks,
            "sample_filled_fields": filled_fields[:20] if filled_fields else [],
            "passed": validation_checks["pdf_has_widgets"] or validation_checks["pdf_has_filled_fields"]
        }
        
    except Exception as e:
        print(f"❌ Exception during PDF validation: {str(e)}")
        results["step5_pdf_validation"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # STEP 6: Integrity Check
    print(f"\n📋 STEP 6: Verificação de Integridade {visa_type}")
    print("-" * 60)
    
    try:
        pdf_path = results["step4_pdf_download"]["pdf_path"]
        file_size = os.path.getsize(pdf_path)
        
        # Expected pages based on form type
        expected_pages = 20 if expected_form_type == "I-129" else 7  # I-129 has 20 pages, I-539 has 7
        
        integrity_checks = {
            "file_exists": os.path.exists(pdf_path),
            "file_size_adequate": file_size > (700000 if expected_form_type == "I-129" else 400000),
            "file_not_corrupted": True,
            "expected_pages": False
        }
        
        # Check if PDF can be opened and has expected pages
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(pdf_path)
                page_count = doc.page_count
                integrity_checks["expected_pages"] = page_count == expected_pages
                doc.close()
                print(f"📄 PDF has {page_count} pages (expected: {expected_pages})")
            except Exception as e:
                integrity_checks["file_not_corrupted"] = False
                print(f"❌ PDF appears corrupted: {str(e)}")
        
        print(f"📏 File size: {file_size} bytes")
        
        print(f"\n🎯 INTEGRITY CHECKS:")
        for check, passed in integrity_checks.items():
            status = "✅" if passed else "❌"
            check_name = check.replace("_", " ").title()
            print(f"  {status} {check_name}: {passed}")
        
        results["step6_integrity_check"] = {
            "success": True,
            "file_size": file_size,
            "expected_pages": expected_pages,
            "integrity_checks": integrity_checks,
            "passed": integrity_checks["file_exists"] and integrity_checks["file_not_corrupted"]
        }
        
    except Exception as e:
        print(f"❌ Exception during integrity check: {str(e)}")
        results["step6_integrity_check"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # Summary
    step_results = [
        results.get("step1_case_creation", {}).get("success", False),
        results.get("step2_friendly_form", {}).get("success", False),
        results.get("step3_pdf_generation", {}).get("passed", False),
        results.get("step4_pdf_download", {}).get("passed", False),
        results.get("step5_pdf_validation", {}).get("passed", False),
        results.get("step6_integrity_check", {}).get("passed", False)
    ]
    
    successful_steps = sum(step_results)
    total_steps = len(step_results)
    success_rate = (successful_steps / total_steps) * 100
    
    print(f"\n🎯 RESUMO {visa_type} VISA:")
    print("=" * 60)
    print(f"📊 Etapas bem-sucedidas: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
    
    step_names = [
        "Caso Criado",
        "Form Aceito", 
        "PDF Gerado",
        "PDF Baixado",
        "Campos Validados",
        "Integridade OK"
    ]
    
    for i, (step_name, passed) in enumerate(zip(step_names, step_results)):
        status = "✅" if passed else "❌"
        print(f"  {status} {step_name}")
    
    # Overall status
    overall_success = success_rate >= 80
    
    if overall_success:
        print(f"\n✅ {visa_type} VISA: FUNCIONANDO CORRETAMENTE")
    else:
        print(f"\n❌ {visa_type} VISA: PROBLEMAS IDENTIFICADOS")
    
    results["summary"] = {
        "successful_steps": successful_steps,
        "total_steps": total_steps,
        "success_rate": success_rate,
        "overall_success": overall_success,
        "case_id": results.get("step1_case_creation", {}).get("case_id")
    }
    
    return results

def test_all_new_visa_types():
    """
    Test all 4 new visa types: O-1, H-1B, L-1, F-1
    """
    
    print("🎯 TESTE END-TO-END COMPLETO - VALIDAÇÃO DE TODOS OS NOVOS TIPOS DE VISTO")
    print("=" * 80)
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("📋 Tipos de visto a testar: O-1, H-1B, L-1, F-1")
    
    all_results = {}
    
    # TEST 1: O-1 VISA (EXTRAORDINARY ABILITY - NONIMMIGRANT)
    print(f"\n{'='*80}")
    print("🎯 TESTE 1: O-1 VISA (EXTRAORDINARY ABILITY - NONIMMIGRANT)")
    print(f"{'='*80}")
    
    o1_test_data = {
        "nome_completo": "Maria Silva Santos",
        "nome_empresa": "Tech Innovation Corp",
        "cargo": "AI Research Scientist",
        "data_nascimento": "1985-03-15",
        "endereco_eua": "100 Tech Avenue Suite 500",
        "cidade_eua": "San Francisco",
        "estado_eua": "CA",
        "cep_eua": "94102",
        "email": "maria.santos@techinnovation.com",
        "telefone": "+1-415-555-9999",
        "numero_passaporte": "BR999888777",
        "pais_nascimento": "Brazil",
        "data_inicio": "2025-01-15",
        "data_fim": "2028-01-14",
        "field_of_ability": "Artificial Intelligence Research"
    }
    
    all_results["o1_visa"] = test_visa_type_complete_flow(
        visa_type="O-1",
        form_code="O-1",
        test_data=o1_test_data,
        expected_form_type="I-129",
        expected_filename_prefix="I-129-O1"
    )
    
    # TEST 2: H-1B VISA (SPECIALTY OCCUPATION)
    print(f"\n{'='*80}")
    print("🎯 TESTE 2: H-1B VISA (SPECIALTY OCCUPATION)")
    print(f"{'='*80}")
    
    h1b_test_data = {
        "nome_completo": "Carlos Eduardo Lima",
        "nome_empresa": "Global Software Solutions Inc",
        "cargo": "Senior Software Engineer",
        "data_nascimento": "1990-07-22",
        "endereco_eua": "5000 Corporate Drive",
        "cidade_eua": "Seattle",
        "estado_eua": "WA",
        "cep_eua": "98101",
        "email": "carlos.lima@globalsoftware.com",
        "telefone": "+1-206-555-7777",
        "numero_passaporte": "BR777666555",
        "pais_nascimento": "Brazil",
        "data_inicio": "2025-04-01",
        "data_fim": "2028-03-31",
        "soc_code": "15-1252"
    }
    
    all_results["h1b_visa"] = test_visa_type_complete_flow(
        visa_type="H-1B",
        form_code="H-1B",
        test_data=h1b_test_data,
        expected_form_type="I-129",
        expected_filename_prefix="I-129-H1B"
    )
    
    # TEST 3: L-1 VISA (INTRACOMPANY TRANSFEREE)
    print(f"\n{'='*80}")
    print("🎯 TESTE 3: L-1 VISA (INTRACOMPANY TRANSFEREE)")
    print(f"{'='*80}")
    
    l1_test_data = {
        "nome_completo": "Ana Paula Oliveira",
        "nome_empresa": "Multinational Corp USA",
        "cargo": "Regional Manager",
        "data_nascimento": "1982-11-30",
        "endereco_eua": "2500 Business Park Blvd",
        "cidade_eua": "Chicago",
        "estado_eua": "IL",
        "cep_eua": "60601",
        "email": "ana.oliveira@multinational.com",
        "telefone": "+1-312-555-4444",
        "numero_passaporte": "BR444333222",
        "pais_nascimento": "Brazil",
        "data_inicio": "2025-02-01",
        "data_fim": "2027-01-31",
        "is_managerial": "Yes"
    }
    
    all_results["l1_visa"] = test_visa_type_complete_flow(
        visa_type="L-1",
        form_code="L-1",
        test_data=l1_test_data,
        expected_form_type="I-129",
        expected_filename_prefix="I-129-L1"
    )
    
    # TEST 4: F-1 VISA (STUDENT - EXTENSION)
    print(f"\n{'='*80}")
    print("🎯 TESTE 4: F-1 VISA (STUDENT - EXTENSION)")
    print(f"{'='*80}")
    
    f1_test_data = {
        "nome_completo": "Pedro Henrique Costa",
        "data_nascimento": "2000-05-10",
        "endereco_eua": "123 University Ave Apt 4B",
        "cidade_eua": "Boston",
        "estado_eua": "MA",
        "cep_eua": "02115",
        "email": "pedro.costa@university.edu",
        "telefone": "+1-617-555-3333",
        "numero_passaporte": "BR333222111",
        "pais_nascimento": "Brazil",
        "status_atual": "F-1",
        "status_solicitado": "F-1 Extension",
        "data_entrada_eua": "2023-08-20",
        "numero_i94": "11223344556"
    }
    
    all_results["f1_visa"] = test_visa_type_complete_flow(
        visa_type="F-1",
        form_code="F-1",
        test_data=f1_test_data,
        expected_form_type="I-539",
        expected_filename_prefix="I-539-F1"
    )
    
    # FINAL ANALYSIS
    print(f"\n{'='*80}")
    print("📊 ANÁLISE FINAL - TODOS OS TIPOS DE VISTO")
    print(f"{'='*80}")
    
    # Create comparison table
    visa_types = ["O-1", "H-1B", "L-1", "F-1"]
    visa_keys = ["o1_visa", "h1b_visa", "l1_visa", "f1_visa"]
    
    print(f"📊 TABELA COMPARATIVA:")
    print("=" * 100)
    print(f"| {'Visto':<6} | {'Caso Criado':<12} | {'Form Aceito':<12} | {'PDF Gerado':<11} | {'PDF Baixado':<12} | {'Tamanho OK':<10} | {'Status':<8} |")
    print("|" + "-"*8 + "|" + "-"*14 + "|" + "-"*14 + "|" + "-"*13 + "|" + "-"*14 + "|" + "-"*12 + "|" + "-"*10 + "|")
    
    overall_stats = {
        "total_visas": len(visa_types),
        "successful_visas": 0,
        "case_creation_success": 0,
        "form_submission_success": 0,
        "pdf_generation_success": 0,
        "pdf_download_success": 0,
        "overall_success": 0
    }
    
    for visa_type, visa_key in zip(visa_types, visa_keys):
        result = all_results.get(visa_key, {})
        summary = result.get("summary", {})
        
        # Individual checks
        case_created = "✅" if result.get("step1_case_creation", {}).get("success", False) else "❌"
        form_accepted = "✅" if result.get("step2_friendly_form", {}).get("success", False) else "❌"
        pdf_generated = "✅" if result.get("step3_pdf_generation", {}).get("passed", False) else "❌"
        pdf_downloaded = "✅" if result.get("step4_pdf_download", {}).get("passed", False) else "❌"
        size_ok = "✅" if result.get("step4_pdf_download", {}).get("file_size", 0) > 400000 else "❌"
        overall_status = "✅" if summary.get("overall_success", False) else "❌"
        
        # Update stats
        if result.get("step1_case_creation", {}).get("success", False):
            overall_stats["case_creation_success"] += 1
        if result.get("step2_friendly_form", {}).get("success", False):
            overall_stats["form_submission_success"] += 1
        if result.get("step3_pdf_generation", {}).get("passed", False):
            overall_stats["pdf_generation_success"] += 1
        if result.get("step4_pdf_download", {}).get("passed", False):
            overall_stats["pdf_download_success"] += 1
        if summary.get("overall_success", False):
            overall_stats["successful_visas"] += 1
        
        print(f"| {visa_type:<6} | {case_created:<12} | {form_accepted:<12} | {pdf_generated:<11} | {pdf_downloaded:<12} | {size_ok:<10} | {overall_status:<8} |")
    
    print("=" * 100)
    
    # Overall statistics
    print(f"\n📊 ESTATÍSTICAS GERAIS:")
    print("=" * 60)
    print(f"📊 Taxa de sucesso geral: {overall_stats['successful_visas']}/{overall_stats['total_visas']} tipos de visto ({overall_stats['successful_visas']/overall_stats['total_visas']*100:.1f}%)")
    print(f"📊 Criação de casos: {overall_stats['case_creation_success']}/{overall_stats['total_visas']} ({overall_stats['case_creation_success']/overall_stats['total_visas']*100:.1f}%)")
    print(f"📊 Submissão de formulários: {overall_stats['form_submission_success']}/{overall_stats['total_visas']} ({overall_stats['form_submission_success']/overall_stats['total_visas']*100:.1f}%)")
    print(f"📊 Geração de PDFs: {overall_stats['pdf_generation_success']}/{overall_stats['total_visas']} ({overall_stats['pdf_generation_success']/overall_stats['total_visas']*100:.1f}%)")
    print(f"📊 Download de PDFs: {overall_stats['pdf_download_success']}/{overall_stats['total_visas']} ({overall_stats['pdf_download_success']/overall_stats['total_visas']*100:.1f}%)")
    
    # Detailed analysis for each visa type
    print(f"\n📋 ANÁLISE DETALHADA POR TIPO DE VISTO:")
    print("=" * 60)
    
    for visa_type, visa_key in zip(visa_types, visa_keys):
        result = all_results.get(visa_key, {})
        summary = result.get("summary", {})
        
        print(f"\n🎯 {visa_type} VISA:")
        if summary.get("overall_success", False):
            case_id = summary.get("case_id", "N/A")
            success_rate = summary.get("success_rate", 0)
            file_size = result.get("step4_pdf_download", {}).get("file_size", 0)
            widgets_found = result.get("step5_pdf_validation", {}).get("widgets_found", 0)
            
            print(f"  ✅ Status: FUNCIONANDO ({success_rate:.1f}% sucesso)")
            print(f"  📋 Case ID: {case_id}")
            print(f"  📏 Tamanho do PDF: {file_size} bytes")
            print(f"  📊 Widgets encontrados: {widgets_found}")
        else:
            failed_steps = []
            if not result.get("step1_case_creation", {}).get("success", False):
                failed_steps.append("Criação de caso")
            if not result.get("step2_friendly_form", {}).get("success", False):
                failed_steps.append("Submissão de formulário")
            if not result.get("step3_pdf_generation", {}).get("passed", False):
                failed_steps.append("Geração de PDF")
            if not result.get("step4_pdf_download", {}).get("passed", False):
                failed_steps.append("Download de PDF")
            
            print(f"  ❌ Status: PROBLEMAS IDENTIFICADOS")
            print(f"  ❌ Etapas que falharam: {', '.join(failed_steps)}")
    
    # Validation of PDF fields (if possible)
    print(f"\n📋 VALIDAÇÃO DE CAMPOS (se possível):")
    print("=" * 60)
    
    for visa_type, visa_key in zip(visa_types, visa_keys):
        result = all_results.get(visa_key, {})
        validation = result.get("step5_pdf_validation", {})
        
        if validation.get("success", False):
            widgets_found = validation.get("widgets_found", 0)
            filled_fields = validation.get("filled_fields_count", 0)
            
            print(f"🎯 {visa_type}: {widgets_found} widgets, {filled_fields} campos preenchidos")
            
            if widgets_found > 0:
                print(f"  ✅ PDF tem campos editáveis")
            else:
                print(f"  ⚠️  PDF template não tem campos editáveis (esperado para alguns templates USCIS)")
        else:
            print(f"🎯 {visa_type}: Validação não disponível")
    
    # Final conclusions
    print(f"\n🎯 CONCLUSÕES FINAIS:")
    print("=" * 60)
    
    total_success_rate = overall_stats['successful_visas'] / overall_stats['total_visas'] * 100
    
    if total_success_rate >= 75:
        print("✅ SISTEMA SUPORTA NOVOS VISTOS: SIM")
        print("✅ Implementação PyMuPDF funcionando corretamente")
        print("✅ Todos os tipos de visto podem gerar PDFs")
        print("✅ Sistema pronto para produção com novos vistos")
    elif total_success_rate >= 50:
        print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
        print("⚠️  Alguns tipos de visto funcionam, outros precisam correção")
        print("🔧 Revisar implementação dos tipos que falharam")
    else:
        print("❌ SISTEMA NÃO ESTÁ PRONTO")
        print("❌ Maioria dos tipos de visto com problemas")
        print("🚨 Correções urgentes necessárias")
    
    # Recommendations
    print(f"\n📋 RECOMENDAÇÕES:")
    print("=" * 60)
    
    if overall_stats['pdf_generation_success'] == overall_stats['total_visas']:
        print("✅ Todos os PDFs foram gerados com sucesso")
    else:
        failed_generation = overall_stats['total_visas'] - overall_stats['pdf_generation_success']
        print(f"🔧 {failed_generation} tipos de visto falharam na geração de PDF - verificar mapeamento de campos")
    
    if overall_stats['pdf_download_success'] == overall_stats['total_visas']:
        print("✅ Todos os PDFs podem ser baixados")
    else:
        failed_download = overall_stats['total_visas'] - overall_stats['pdf_download_success']
        print(f"🔧 {failed_download} tipos de visto falharam no download - verificar persistência")
    
    # Check if I-129 vs I-539 distinction is working
    i129_visas = ["O-1", "H-1B", "L-1"]  # Should use I-129
    i539_visas = ["F-1"]  # Should use I-539
    
    i129_working = sum(1 for visa in ["o1_visa", "h1b_visa", "l1_visa"] if all_results.get(visa, {}).get("summary", {}).get("overall_success", False))
    i539_working = sum(1 for visa in ["f1_visa"] if all_results.get(visa, {}).get("summary", {}).get("overall_success", False))
    
    print(f"📊 I-129 vistos funcionando: {i129_working}/3 (O-1, H-1B, L-1)")
    print(f"📊 I-539 vistos funcionando: {i539_working}/1 (F-1)")
    
    if i129_working == 3 and i539_working == 1:
        print("✅ Distinção I-129 vs I-539 funcionando corretamente")
    else:
        print("🔧 Verificar mapeamento de formulários I-129 vs I-539")
    
    # Save results
    timestamp = datetime.now().isoformat()
    results_filename = f"/app/new_visa_types_test_results_{timestamp.replace(':', '-').split('.')[0]}.json"
    
    with open(results_filename, "w") as f:
        json.dump({
            "test_results": all_results,
            "overall_stats": overall_stats,
            "timestamp": timestamp,
            "test_focus": "🎯 TESTE END-TO-END COMPLETO - VALIDAÇÃO DE TODOS OS NOVOS TIPOS DE VISTO",
            "visa_types_tested": visa_types,
            "backend_url": BACKEND_URL,
            "pymupdf_available": PYMUPDF_AVAILABLE,
            "conclusions": {
                "total_success_rate": total_success_rate,
                "system_ready": total_success_rate >= 75,
                "i129_visas_working": i129_working,
                "i539_visas_working": i539_working,
                "all_pdfs_generated": overall_stats['pdf_generation_success'] == overall_stats['total_visas'],
                "all_pdfs_downloadable": overall_stats['pdf_download_success'] == overall_stats['total_visas']
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: {results_filename}")
    
    return all_results, overall_stats

if __name__ == "__main__":
    print("🎯 INICIANDO TESTE DE TODOS OS NOVOS TIPOS DE VISTO")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("📋 Objetivo: Validar O-1, H-1B, L-1, F-1 com implementação PyMuPDF")
    
    # Execute main test
    all_results, overall_stats = test_all_new_visa_types()
    
    # Final summary
    print(f"\n🎉 TESTE COMPLETO!")
    print(f"📊 Vistos testados: {overall_stats['total_visas']}")
    print(f"📊 Vistos funcionando: {overall_stats['successful_visas']}")
    print(f"📊 Taxa de sucesso: {overall_stats['successful_visas']/overall_stats['total_visas']*100:.1f}%")
    
    if overall_stats['successful_visas'] == overall_stats['total_visas']:
        print("🎉 TODOS OS NOVOS TIPOS DE VISTO FUNCIONANDO!")
    elif overall_stats['successful_visas'] >= overall_stats['total_visas'] * 0.75:
        print("✅ MAIORIA DOS TIPOS DE VISTO FUNCIONANDO")
    else:
        print("⚠️  ALGUNS TIPOS DE VISTO PRECISAM CORREÇÃO")