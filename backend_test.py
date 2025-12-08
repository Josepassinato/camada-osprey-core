#!/usr/bin/env python3
"""
🔍 TESTE END-TO-END COMPLETO APÓS CORREÇÃO DO BUG P0 - PDF GENERATION
Testing complete flow from friendly form to PDF download after pypdf migration fix
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime
import pypdf
import io

# Get backend URL from frontend .env
BACKEND_URL = "https://smart-visa-helper-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def create_test_case():
    """Create a test case for validation testing"""
    try:
        print("📝 Creating test case for validation...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"form_code": "I-539"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ Test case created: {case_id}")
                return case_id
            else:
                print(f"❌ No case_id in response: {case_data}")
                return None
        else:
            print(f"❌ Failed to create case: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception creating test case: {str(e)}")
        return None

def test_validation_endpoint(case_id: str, test_data: dict, test_name: str):
    """Test the friendly form validation endpoint"""
    try:
        print(f"\n🔍 {test_name}")
        print("-" * 50)
        
        print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/friendly-form")
        print(f"📤 Test Data: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            validation_result = response.json()
            print(f"📄 Validation Response: {json.dumps(validation_result, indent=2, ensure_ascii=False)}")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "processing_time": processing_time,
                "validation_result": validation_result
            }
        else:
            print(f"❌ Validation failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception during validation: {str(e)}")
        return {
            "success": False,
            "exception": str(e)
        }

def verify_mongodb_persistence(case_id: str):
    """Verify that validation data was saved to MongoDB"""
    try:
        print(f"\n💾 Verifying MongoDB persistence for case {case_id}")
        print("-" * 50)
        
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            case_data = response.json()
            case_info = case_data.get("case", {})
            
            # Check for validation-related fields
            simplified_form_responses = case_info.get("simplified_form_responses")
            friendly_form_validation = case_info.get("friendly_form_validation")
            
            print(f"📄 Simplified Form Responses: {json.dumps(simplified_form_responses, indent=2, ensure_ascii=False) if simplified_form_responses else 'None'}")
            print(f"📄 Friendly Form Validation: {json.dumps(friendly_form_validation, indent=2, ensure_ascii=False) if friendly_form_validation else 'None'}")
            
            persistence_checks = {
                "simplified_form_responses_saved": simplified_form_responses is not None,
                "friendly_form_validation_saved": friendly_form_validation is not None,
                "validation_status_present": friendly_form_validation.get("status") is not None if friendly_form_validation else False,
                "completion_percentage_present": friendly_form_validation.get("completion_percentage") is not None if friendly_form_validation else False,
                "validation_date_present": friendly_form_validation.get("validation_date") is not None if friendly_form_validation else False,
                "issues_array_present": isinstance(friendly_form_validation.get("issues"), list) if friendly_form_validation else False
            }
            
            print(f"\n🎯 PERSISTENCE CHECKS:")
            for check, passed in persistence_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            return {
                "success": True,
                "persistence_checks": persistence_checks,
                "case_data": case_info
            }
        else:
            print(f"❌ Failed to retrieve case: {response.status_code}")
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except Exception as e:
        print(f"❌ Exception during persistence check: {str(e)}")
        return {
            "success": False,
            "exception": str(e)
        }

def test_i539_pdf_generation_e2e():
    """
    🔍 TESTE END-TO-END COMPLETO APÓS CORREÇÃO DO BUG P0 - PDF GENERATION
    
    Testing complete flow after pypdf migration fix:
    1. Create I-539 case
    2. Fill friendly form with Portuguese data
    3. Verify data persistence (including _eua fields)
    4. Generate PDF with corrected pypdf library
    5. Download PDF and verify size
    6. CRITICAL: Extract field values from PDF to verify P0 bug fix
    
    SUCCESS CRITERIA:
    - Case created successfully
    - Friendly form data saved (including endereco_eua, cidade_eua, estado_eua, cep_eua)
    - PDF generated (status 200, >300KB)
    - PDF downloadable (status 200, application/pdf)
    - CRITICAL: At least 6/8 fields filled in PDF (P0 bug fix verification)
    """
    
    print("🔍 TESTE END-TO-END COMPLETO APÓS CORREÇÃO DO BUG P0 - PDF GENERATION")
    print("📋 Testing complete flow from friendly form to PDF download")
    print("🎯 Focus: Verify pypdf migration fixed empty PDF generation bug")
    print("=" * 80)
    
    results = {
        "step1_case_creation": {},
        "step2_friendly_form": {},
        "step3_data_verification": {},
        "step4_pdf_generation": {},
        "step5_pdf_download": {},
        "step6_pdf_field_verification": {},
        "summary": {}
    }
    
    # STEP 1: Create I-539 Case
    print("\n📋 STEP 1: Criar Caso I-539")
    print("-" * 60)
    
    try:
        print("📝 Creating I-539 case...")
        response = requests.post(
            f"{API_BASE}/auto-application/start",
            json={"form_code": "I-539"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            case_data = response.json()
            case_info = case_data.get("case", {})
            case_id = case_info.get("case_id")
            
            if case_id:
                print(f"✅ I-539 case created: {case_id}")
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
            results["step1_case_creation"] = {"success": False, "status_code": response.status_code}
            return results
            
    except Exception as e:
        print(f"❌ Exception creating case: {str(e)}")
        results["step1_case_creation"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 2: Fill Friendly Form with Portuguese Data (EXACT data from review request)
    print("\n📋 STEP 2: Preencher Formulário Amigável em Português")
    print("-" * 60)
    
    friendly_form_data = {
        "friendly_form_data": {
            "nome_completo": "Ana Paula Santos Silva",
            "data_nascimento": "1992-07-18",
            "endereco_eua": "789 Broadway Avenue",
            "cidade_eua": "Miami",
            "estado_eua": "FL",
            "cep_eua": "33101",
            "email": "ana.santos@test.com",
            "telefone": "+1-305-555-8888",
            "numero_passaporte": "BR555666777",
            "pais_nascimento": "Brazil",
            "status_atual": "B-2",
            "status_solicitado": "B-2 Extension",
            "data_entrada_eua": "2024-01-15",
            "numero_i94": "99887766554"
        },
        "basic_data": {}
    }
    
    try:
        print(f"📤 Sending friendly form data to case {case_id}...")
        print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/friendly-form")
        
        response = requests.post(
            f"{API_BASE}/case/{case_id}/friendly-form",
            json=friendly_form_data,
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
    
    # STEP 3: Verify Data Persistence (including _eua fields)
    print("\n📋 STEP 3: Verificar Salvamento dos Dados")
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
            
            print(f"📄 Simplified Form Responses: {json.dumps(simplified_responses, indent=2, ensure_ascii=False)}")
            
            # Verify critical fields including _eua fields
            verification_checks = {
                "simplified_form_responses_exists": simplified_responses is not None and len(simplified_responses) > 0,
                "nome_completo_saved": simplified_responses.get("nome_completo") == "Ana Paula Santos Silva",
                "endereco_eua_saved": simplified_responses.get("endereco_eua") == "789 Broadway Avenue",
                "cidade_eua_saved": simplified_responses.get("cidade_eua") == "Miami",
                "estado_eua_saved": simplified_responses.get("estado_eua") == "FL",
                "cep_eua_saved": simplified_responses.get("cep_eua") == "33101",
                "email_saved": simplified_responses.get("email") == "ana.santos@test.com",
                "telefone_saved": simplified_responses.get("telefone") == "+1-305-555-8888",
                "numero_passaporte_saved": simplified_responses.get("numero_passaporte") == "BR555666777"
            }
            
            print(f"\n🎯 DATA PERSISTENCE VERIFICATION:")
            for check, passed in verification_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["step3_data_verification"] = {
                "success": True,
                "verification_checks": verification_checks,
                "simplified_responses": simplified_responses,
                "passed": all(verification_checks.values())
            }
        else:
            print(f"❌ Failed to retrieve case: {response.status_code}")
            results["step3_data_verification"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception retrieving case: {str(e)}")
        results["step3_data_verification"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 4: Generate PDF Official I-539 (CRITICAL - Bug P0 verification)
    print("\n📋 STEP 4: Gerar PDF Oficial I-539 (⭐ CRÍTICO - Bug P0)")
    print("-" * 60)
    
    try:
        print(f"📝 Generating I-539 PDF for case {case_id}...")
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
            pdf_checks = {
                "success_true": pdf_result.get("success", False),
                "filename_present": pdf_result.get("filename") is not None,
                "file_size_adequate": pdf_result.get("file_size", 0) > 300000,  # >300KB
                "download_url_present": pdf_result.get("download_url") is not None
            }
            
            print(f"\n🎯 PDF GENERATION VERIFICATION:")
            for check, passed in pdf_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            results["step4_pdf_generation"] = {
                "success": True,
                "status_code": response.status_code,
                "pdf_result": pdf_result,
                "pdf_checks": pdf_checks,
                "passed": all(pdf_checks.values())
            }
        else:
            print(f"❌ PDF generation failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            results["step4_pdf_generation"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception generating PDF: {str(e)}")
        results["step4_pdf_generation"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 5: Download PDF and Verify
    print("\n📋 STEP 5: Download do PDF")
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
            download_checks = {
                "status_200": response.status_code == 200,
                "content_type_pdf": response.headers.get('Content-Type') == 'application/pdf',
                "file_size_adequate": len(response.content) > 300000,  # >300KB (~335KB expected)
                "content_not_empty": len(response.content) > 0
            }
            
            print(f"\n🎯 PDF DOWNLOAD VERIFICATION:")
            for check, passed in download_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Save PDF for field verification
            pdf_path = "/tmp/test_e2e_i539.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"💾 PDF saved to: {pdf_path}")
            
            results["step5_pdf_download"] = {
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
            results["step5_pdf_download"] = {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            return results
            
    except Exception as e:
        print(f"❌ Exception downloading PDF: {str(e)}")
        results["step5_pdf_download"] = {"success": False, "exception": str(e)}
        return results
    
    # STEP 6: CRITICAL PDF Field Verification (P0 Bug Fix Verification)
    print("\n📋 STEP 6: 🔍 VERIFICAÇÃO CRÍTICA DO BUG P0")
    print("-" * 60)
    
    try:
        pdf_path = results["step5_pdf_download"]["pdf_path"]
        print(f"🔍 Analyzing PDF fields in: {pdf_path}")
        
        # Read PDF and extract form fields using pypdf
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            print(f"📄 PDF Pages: {len(pdf_reader.pages)}")
            
            # Extract form fields - try multiple methods
            form_fields = {}
            
            # Method 1: get_form_text_fields()
            try:
                text_fields = pdf_reader.get_form_text_fields()
                if text_fields and isinstance(text_fields, dict):
                    form_fields.update(text_fields)
                    print(f"📊 Text fields detected: {len(text_fields)}")
            except Exception as e:
                print(f"⚠️  get_form_text_fields() failed: {str(e)}")
            
            # Method 2: get_fields()
            try:
                if hasattr(pdf_reader, 'get_fields'):
                    fields = pdf_reader.get_fields()
                    if fields and isinstance(fields, dict):
                        for k, v in fields.items():
                            if v and hasattr(v, 'get'):
                                field_value = v.get('/V', '')
                                if field_value:
                                    form_fields[k] = str(field_value)
                        print(f"📊 Fields via get_fields(): {len(fields)}")
            except Exception as e:
                print(f"⚠️  get_fields() failed: {str(e)}")
            
            # Method 3: Manual extraction from pages
            try:
                for page_num, page in enumerate(pdf_reader.pages):
                    if '/Annots' in page:
                        annotations = page['/Annots']
                        if annotations:
                            for annot_ref in annotations:
                                try:
                                    annot = annot_ref.get_object()
                                    if annot and '/T' in annot and '/V' in annot:
                                        field_name = str(annot['/T'])
                                        field_value = str(annot['/V']) if annot['/V'] else ''
                                        if field_value:
                                            form_fields[field_name] = field_value
                                except Exception:
                                    continue
                print(f"📊 Manual extraction found: {len(form_fields)} total fields")
            except Exception as e:
                print(f"⚠️  Manual extraction failed: {str(e)}")
            
            print(f"📊 Total form fields detected: {len(form_fields)}")
            
            # Critical fields to verify (from review request)
            critical_fields_check = {
                "Pt1Line1a_FamilyName": {
                    "expected": "Silva",
                    "actual": form_fields.get("Pt1Line1a_FamilyName", ""),
                    "filled": False
                },
                "Pt1Line1b_GivenName": {
                    "expected": "Ana",
                    "actual": form_fields.get("Pt1Line1b_GivenName", ""),
                    "filled": False
                },
                "Pt1Line7a_StreetNumberName": {
                    "expected": "789 Broadway Avenue",
                    "actual": form_fields.get("Pt1Line7a_StreetNumberName", ""),
                    "filled": False
                },
                "Pt1Line7c_CityOrTown": {
                    "expected": "Miami",
                    "actual": form_fields.get("Pt1Line7c_CityOrTown", ""),
                    "filled": False
                },
                "Pt1Line7d_State": {
                    "expected": "FL",
                    "actual": form_fields.get("Pt1Line7d_State", ""),
                    "filled": False
                },
                "Pt1Line7e_ZipCode": {
                    "expected": "33101",
                    "actual": form_fields.get("Pt1Line7e_ZipCode", ""),
                    "filled": False
                },
                "Pt1Line8_Email": {
                    "expected": "ana.santos@test.com",
                    "actual": form_fields.get("Pt1Line8_Email", ""),
                    "filled": False
                },
                "Pt1Line9_DaytimeTelephone": {
                    "expected": "+1-305-555-8888",
                    "actual": form_fields.get("Pt1Line9_DaytimeTelephone", ""),
                    "filled": False
                }
            }
            
            # Check which fields are filled
            fields_filled = 0
            print(f"\n🎯 CRITICAL FIELDS VERIFICATION:")
            print("=" * 60)
            
            for field_name, field_info in critical_fields_check.items():
                actual_value = field_info["actual"]
                expected_value = field_info["expected"]
                
                # Check if field contains expected value (partial match acceptable)
                if actual_value and (expected_value.lower() in actual_value.lower() or actual_value.lower() in expected_value.lower()):
                    field_info["filled"] = True
                    fields_filled += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"  {status} {field_name}:")
                print(f"      Expected: '{expected_value}'")
                print(f"      Actual: '{actual_value}'")
                print(f"      Filled: {field_info['filled']}")
            
            # P0 Bug Fix Assessment
            total_critical_fields = len(critical_fields_check)
            success_threshold = 6  # At least 6/8 fields must be filled
            
            print(f"\n🎯 P0 BUG FIX ASSESSMENT:")
            print("=" * 60)
            print(f"📊 Fields filled: {fields_filled}/{total_critical_fields}")
            print(f"🎯 Success threshold: {success_threshold}/{total_critical_fields}")
            
            p0_bug_fixed = fields_filled >= success_threshold
            
            if p0_bug_fixed:
                print(f"✅ BUG P0 CORRIGIDO! ({fields_filled}/{total_critical_fields} campos preenchidos)")
            else:
                print(f"❌ BUG P0 AINDA EXISTE ({fields_filled}/{total_critical_fields} campos preenchidos)")
            
            # Show all detected fields for debugging
            print(f"\n📄 ALL DETECTED FORM FIELDS ({len(form_fields)}):")
            for field_name, field_value in list(form_fields.items())[:20]:  # Show first 20
                print(f"  {field_name}: '{field_value}'")
            if len(form_fields) > 20:
                print(f"  ... and {len(form_fields) - 20} more fields")
            
            results["step6_pdf_field_verification"] = {
                "success": True,
                "total_form_fields": len(form_fields),
                "critical_fields_check": critical_fields_check,
                "fields_filled": fields_filled,
                "total_critical_fields": total_critical_fields,
                "success_threshold": success_threshold,
                "p0_bug_fixed": p0_bug_fixed,
                "all_form_fields": dict(list(form_fields.items())[:50]),  # Store first 50 for analysis
                "passed": p0_bug_fixed
            }
            
    except Exception as e:
        print(f"❌ Exception during PDF field verification: {str(e)}")
        results["step6_pdf_field_verification"] = {
            "success": False,
            "exception": str(e),
            "passed": False
        }
    
    # Generate Final Summary and Assessment
    print("\n📋 RESUMO FINAL - TESTE END-TO-END PDF GENERATION")
    print("=" * 80)
    
    # Count successful steps
    step_results = [
        results.get("step1_case_creation", {}).get("success", False),
        results.get("step2_friendly_form", {}).get("success", False),
        results.get("step3_data_verification", {}).get("passed", False),
        results.get("step4_pdf_generation", {}).get("passed", False),
        results.get("step5_pdf_download", {}).get("passed", False),
        results.get("step6_pdf_field_verification", {}).get("passed", False)
    ]
    
    successful_steps = sum(step_results)
    total_steps = len(step_results)
    success_rate = (successful_steps / total_steps) * 100
    
    # Individual step results
    step_names = [
        "STEP 1: Criar Caso I-539",
        "STEP 2: Preencher Formulário Amigável",
        "STEP 3: Verificar Salvamento dos Dados",
        "STEP 4: Gerar PDF Oficial I-539",
        "STEP 5: Download do PDF",
        "STEP 6: Verificação Crítica do Bug P0"
    ]
    
    print(f"📊 RESULTADOS POR ETAPA:")
    for i, (step_name, passed) in enumerate(zip(step_names, step_results)):
        status = "✅" if passed else "❌"
        print(f"  {status} {step_name}: {'SUCESSO' if passed else 'FALHOU'}")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
    
    # Critical P0 Bug Assessment
    p0_bug_fixed = results.get("step6_pdf_field_verification", {}).get("p0_bug_fixed", False)
    fields_filled = results.get("step6_pdf_field_verification", {}).get("fields_filled", 0)
    total_critical_fields = results.get("step6_pdf_field_verification", {}).get("total_critical_fields", 8)
    
    print(f"\n🎯 AVALIAÇÃO CRÍTICA DO BUG P0:")
    print("=" * 60)
    
    if p0_bug_fixed:
        print(f"✅ BUG P0 CORRIGIDO COM SUCESSO!")
        print(f"✅ Campos preenchidos no PDF: {fields_filled}/{total_critical_fields}")
        print(f"✅ Migração para pypdf funcionou corretamente")
        print(f"✅ PDFs I-539 não estão mais vazios")
    else:
        print(f"❌ BUG P0 AINDA EXISTE")
        print(f"❌ Campos preenchidos no PDF: {fields_filled}/{total_critical_fields}")
        print(f"❌ Menos de 6 campos preenchidos")
        print(f"❌ Migração pypdf pode ter problemas")
    
    # Detailed Analysis
    print(f"\n📋 ANÁLISE DETALHADA:")
    print("=" * 60)
    
    # Step-by-step analysis
    if results.get("step1_case_creation", {}).get("success"):
        case_id = results["step1_case_creation"]["case_id"]
        print(f"✅ STEP 1 - Caso I-539 criado: {case_id}")
    
    if results.get("step2_friendly_form", {}).get("success"):
        print(f"✅ STEP 2 - Formulário amigável preenchido com dados em português")
    
    if results.get("step3_data_verification", {}).get("passed"):
        print(f"✅ STEP 3 - Dados salvos corretamente (incluindo campos _eua)")
    
    if results.get("step4_pdf_generation", {}).get("passed"):
        pdf_size = results["step4_pdf_generation"]["pdf_result"].get("file_size", 0)
        print(f"✅ STEP 4 - PDF I-539 gerado ({pdf_size} bytes)")
    
    if results.get("step5_pdf_download", {}).get("passed"):
        download_size = results["step5_pdf_download"]["file_size"]
        print(f"✅ STEP 5 - PDF baixado com sucesso ({download_size} bytes)")
    
    if results.get("step6_pdf_field_verification", {}).get("success"):
        total_fields = results["step6_pdf_field_verification"]["total_form_fields"]
        print(f"✅ STEP 6 - PDF analisado ({total_fields} campos detectados)")
        
        # Show which critical fields were filled
        critical_fields = results["step6_pdf_field_verification"]["critical_fields_check"]
        filled_fields = [name for name, info in critical_fields.items() if info["filled"]]
        
        if filled_fields:
            print(f"✅ Campos preenchidos: {', '.join(filled_fields)}")
        
        empty_fields = [name for name, info in critical_fields.items() if not info["filled"]]
        if empty_fields:
            print(f"❌ Campos vazios: {', '.join(empty_fields)}")
    
    # Success Criteria Assessment
    print(f"\n🎯 CRITÉRIOS DE SUCESSO:")
    print("=" * 60)
    
    success_criteria = {
        "caso_i539_criado": results.get("step1_case_creation", {}).get("success", False),
        "dados_formulario_salvos": results.get("step3_data_verification", {}).get("passed", False),
        "campos_eua_salvos": results.get("step3_data_verification", {}).get("verification_checks", {}).get("endereco_eua_saved", False),
        "pdf_gerado_sucesso": results.get("step4_pdf_generation", {}).get("passed", False),
        "pdf_baixado_sucesso": results.get("step5_pdf_download", {}).get("passed", False),
        "pdf_tamanho_adequado": results.get("step5_pdf_download", {}).get("file_size", 0) > 300000,
        "campos_preenchidos_pdf": p0_bug_fixed,
        "sem_erros_500": all(
            results.get(step, {}).get("status_code", 500) != 500 
            for step in ["step1_case_creation", "step2_friendly_form", "step4_pdf_generation", "step5_pdf_download"]
        )
    }
    
    criteria_passed = sum(success_criteria.values())
    total_criteria = len(success_criteria)
    
    print(f"📊 CRITÉRIOS ATENDIDOS:")
    for criterion, passed in success_criteria.items():
        status = "✅" if passed else "❌"
        criterion_name = criterion.replace("_", " ").title()
        print(f"  {status} {criterion_name}: {'ATENDIDO' if passed else 'NÃO ATENDIDO'}")
    
    print(f"\n🎯 CRITÉRIOS ATENDIDOS: {criteria_passed}/{total_criteria} ({criteria_passed/total_criteria*100:.1f}%)")
    
    # Final Assessment
    system_ready = success_rate >= 80 and p0_bug_fixed
    
    if system_ready:
        print("\n✅ SISTEMA DE GERAÇÃO DE PDF: TOTALMENTE FUNCIONAL")
        print("✅ BUG P0 CRÍTICO: CORRIGIDO COM SUCESSO")
        print("✅ MIGRAÇÃO PYPDF: IMPLEMENTADA CORRETAMENTE")
        print("✅ FLUXO END-TO-END: OPERACIONAL")
        print("✅ FORMULÁRIOS I-539: PREENCHIDOS CORRETAMENTE")
    else:
        print("\n⚠️  SISTEMA DE GERAÇÃO DE PDF: NECESSITA CORREÇÕES")
        
        # Identify problem areas
        problem_areas = []
        if not success_criteria["caso_i539_criado"]:
            problem_areas.append("Criação de caso I-539")
        if not success_criteria["dados_formulario_salvos"]:
            problem_areas.append("Salvamento de dados do formulário")
        if not success_criteria["pdf_gerado_sucesso"]:
            problem_areas.append("Geração de PDF")
        if not success_criteria["campos_preenchidos_pdf"]:
            problem_areas.append("Preenchimento de campos no PDF (BUG P0)")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Store summary
    results["summary"] = {
        "successful_steps": successful_steps,
        "total_steps": total_steps,
        "success_rate": success_rate,
        "p0_bug_fixed": p0_bug_fixed,
        "fields_filled": fields_filled,
        "total_critical_fields": total_critical_fields,
        "success_criteria": success_criteria,
        "criteria_passed": criteria_passed,
        "total_criteria": total_criteria,
        "system_ready": system_ready,
        "case_id": results.get("step1_case_creation", {}).get("case_id")
    }
    
    return results
    
    # Generate Summary and Assessment
    print("\n📋 RESUMO FINAL - SISTEMA DE VALIDAÇÃO IA MELHORADA")
    print("=" * 80)
    
    # Count successful tests
    test_results = [
        results.get("test1_complete_data", {}).get("passed", False),
        results.get("test2_partial_data", {}).get("passed", False),
        results.get("test3_format_errors", {}).get("passed", False),
        results.get("test4_issues_verification", {}).get("passed", False),
        results.get("test5_mongodb_persistence", {}).get("passed", False)
    ]
    
    successful_tests = sum(test_results)
    total_tests = len(test_results)
    success_rate = (successful_tests / total_tests) * 100
    
    # Individual test results
    test_names = [
        "TEST 1: Dados Completos (I-539)",
        "TEST 2: Dados Parciais (50%)",
        "TEST 3: Erros de Formato",
        "TEST 4: Lista Detalhada de Issues",
        "TEST 5: Persistência MongoDB"
    ]
    
    print(f"📊 RESULTADOS DOS TESTES:")
    for i, (test_name, passed) in enumerate(zip(test_names, test_results)):
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}: {'PASSOU' if passed else 'FALHOU'}")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Detailed analysis
    print(f"\n📋 ANÁLISE DETALHADA:")
    print("=" * 60)
    
    # Test 1 Analysis
    if results.get("test1_complete_data", {}).get("success"):
        test1_result = results["test1_complete_data"]["validation_result"]
        print(f"✅ TEST 1 - Dados Completos:")
        print(f"  Status: {test1_result.get('validation_status', 'N/A')}")
        print(f"  Completude: {test1_result.get('completion_percentage', 0)}%")
        print(f"  Issues: {len(test1_result.get('validation_issues', []))}")
    
    # Test 2 Analysis
    if results.get("test2_partial_data", {}).get("success"):
        test2_result = results["test2_partial_data"]["validation_result"]
        print(f"⚠️  TEST 2 - Dados Parciais:")
        print(f"  Status: {test2_result.get('validation_status', 'N/A')}")
        print(f"  Completude: {test2_result.get('completion_percentage', 0)}%")
        print(f"  Issues: {len(test2_result.get('validation_issues', []))}")
    
    # Test 3 Analysis
    if results.get("test3_format_errors", {}).get("success"):
        test3_result = results["test3_format_errors"]["validation_result"]
        print(f"🔧 TEST 3 - Erros de Formato:")
        print(f"  Status: {test3_result.get('validation_status', 'N/A')}")
        print(f"  Completude: {test3_result.get('completion_percentage', 0)}%")
        print(f"  Issues: {len(test3_result.get('validation_issues', []))}")
    
    # Performance Analysis
    processing_times = []
    for test_key in ["test1_complete_data", "test2_partial_data", "test3_format_errors"]:
        if results.get(test_key, {}).get("processing_time"):
            processing_times.append(results[test_key]["processing_time"])
    
    if processing_times:
        avg_processing_time = sum(processing_times) / len(processing_times)
        print(f"\n⏱️  PERFORMANCE:")
        print(f"  Tempo médio de validação: {avg_processing_time:.2f}s")
        print(f"  Performance adequada: {'✅ SIM' if avg_processing_time < 2.0 else '❌ NÃO'} (< 2s)")
    
    # System Assessment
    print(f"\n🎯 AVALIAÇÃO DO SISTEMA:")
    print("=" * 60)
    
    criteria_met = {
        "validacao_diferencia_completo_incompleto": successful_tests >= 2,
        "completion_percentage_preciso": successful_tests >= 2,
        "issues_listados_com_detalhes": results.get("test4_issues_verification", {}).get("passed", False),
        "status_determinado_corretamente": successful_tests >= 2,
        "dados_persistem_mongodb": results.get("test5_mongodb_persistence", {}).get("passed", False),
        "performance_adequada": avg_processing_time < 2.0 if processing_times else False
    }
    
    criteria_passed = sum(criteria_met.values())
    total_criteria = len(criteria_met)
    
    print(f"📊 CRITÉRIOS DE SUCESSO:")
    for criterion, passed in criteria_met.items():
        status = "✅" if passed else "❌"
        criterion_name = criterion.replace("_", " ").title()
        print(f"  {status} {criterion_name}: {'ATENDIDO' if passed else 'NÃO ATENDIDO'}")
    
    print(f"\n🎯 CRITÉRIOS ATENDIDOS: {criteria_passed}/{total_criteria} ({criteria_passed/total_criteria*100:.1f}%)")
    
    # Final Assessment
    system_ready = success_rate >= 80 and criteria_passed >= 5
    
    if system_ready:
        print("\n✅ SISTEMA DE VALIDAÇÃO IA: TOTALMENTE FUNCIONAL")
        print("✅ VALIDAÇÃO EM DOIS ESTÁGIOS: OPERACIONAL")
        print("✅ CAMPOS OBRIGATÓRIOS POR TIPO DE VISTO: IMPLEMENTADO")
        print("✅ VALIDAÇÕES DE FORMATO: FUNCIONANDO")
        print("✅ CÁLCULO INTELIGENTE DE COMPLETUDE: ATIVO")
        print("✅ PERSISTÊNCIA MONGODB: CONFIRMADA")
    else:
        print("\n⚠️  SISTEMA DE VALIDAÇÃO IA: NECESSITA MELHORIAS")
        
        # Identify problem areas
        problem_areas = []
        if not criteria_met["validacao_diferencia_completo_incompleto"]:
            problem_areas.append("Diferenciação completo/incompleto")
        if not criteria_met["completion_percentage_preciso"]:
            problem_areas.append("Cálculo de completude")
        if not criteria_met["issues_listados_com_detalhes"]:
            problem_areas.append("Lista detalhada de issues")
        if not criteria_met["dados_persistem_mongodb"]:
            problem_areas.append("Persistência MongoDB")
        if not criteria_met["performance_adequada"]:
            problem_areas.append("Performance de validação")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Store summary
    results["summary"] = {
        "successful_tests": successful_tests,
        "total_tests": total_tests,
        "success_rate": success_rate,
        "criteria_met": criteria_met,
        "criteria_passed": criteria_passed,
        "total_criteria": total_criteria,
        "system_ready": system_ready,
        "avg_processing_time": avg_processing_time if processing_times else None
    }
    
    return results

# Helper function for additional testing if needed
def additional_validation_tests():
    """Placeholder for additional validation tests"""
    pass

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE END-TO-END COMPLETO APÓS CORREÇÃO DO BUG P0")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("🎯 Focus: Verificar se migração pypdf corrigiu bug de PDF vazio")
    
    # Execute main test
    test_results = test_i539_pdf_generation_e2e()
    
    # Save results to file
    with open("/app/i539_pdf_e2e_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "I-539 PDF Generation E2E Testing After P0 Bug Fix",
            "test_steps": [
                {"step": "Create I-539 Case", "expected": "Case created successfully"},
                {"step": "Fill Friendly Form", "expected": "Portuguese data saved"},
                {"step": "Verify Data Persistence", "expected": "_eua fields saved correctly"},
                {"step": "Generate PDF", "expected": "PDF generated >300KB"},
                {"step": "Download PDF", "expected": "PDF downloadable"},
                {"step": "Verify PDF Fields", "expected": "At least 6/8 fields filled"}
            ],
            "p0_bug_assessment": {
                "bug_fixed": test_results.get("summary", {}).get("p0_bug_fixed", False),
                "fields_filled": test_results.get("summary", {}).get("fields_filled", 0),
                "total_fields": test_results.get("summary", {}).get("total_critical_fields", 8)
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultados salvos em: /app/i539_pdf_e2e_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    p0_fixed = summary.get("p0_bug_fixed", False)
    success_rate = summary.get("success_rate", 0)
    
    if p0_fixed and success_rate >= 80:
        print("\n✅ RECOMENDAÇÃO: BUG P0 CORRIGIDO COM SUCESSO!")
        print("   ✅ Migração pypdf funcionou corretamente")
        print("   ✅ PDFs I-539 não estão mais vazios")
        print("   ✅ Campos do formulário sendo preenchidos")
        print("   ✅ Fluxo end-to-end operacional")
        print("   ✅ Sistema pronto para produção")
    elif p0_fixed:
        print("\n⚠️  RECOMENDAÇÃO: BUG P0 corrigido, mas outros problemas identificados")
        print("   ✅ PDF não está mais vazio")
        print("   ⚠️  Alguns passos do fluxo falharam")
        print("   🔧 Revisar áreas problemáticas")
    else:
        print("\n❌ RECOMENDAÇÃO: BUG P0 AINDA EXISTE!")
        print("   ❌ PDFs continuam vazios ou com poucos campos")
        print("   ❌ Migração pypdf pode ter problemas")
        print("   🚨 Correção urgente necessária")
        
        fields_filled = summary.get("fields_filled", 0)
        total_fields = summary.get("total_critical_fields", 8)
        print(f"   📊 Apenas {fields_filled}/{total_fields} campos preenchidos")
        print(f"   🎯 Necessário pelo menos 6/{total_fields} para aprovação")
    
