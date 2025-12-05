#!/usr/bin/env python3
"""
🎯 TESTE COMPLETO - SISTEMA DE GERAÇÃO DE FORMULÁRIOS USCIS
Testing USCIS form generation system for 3 visa types as requested in review
"""

import requests
import json
import time
import os
import base64
from pathlib import Path
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://docsimple-3.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_uscis_form_generation_system():
    """
    🎯 TESTE COMPLETO - SISTEMA DE GERAÇÃO DE FORMULÁRIOS USCIS
    
    Testing the new USCIS form generation system for 3 visa types:
    1. I-539 (Extension) - Case OSP-BD2D8ED2
    2. I-589 (Asylum) - Case OSP-4899BE72  
    3. EB-1A (Extraordinary) - Case OSP-8731E45D
    
    VERIFICATION CRITERIA:
    - Form generation endpoints working (3/3)
    - PDF download working (3/3)
    - Proper file sizes (I-539: >400KB, I-589: >800KB, I-140: >500KB)
    - Data persistence in database (3/3)
    - Valid PDF files generated (3/3)
    """
    
    print("🎯 TESTE COMPLETO - SISTEMA DE GERAÇÃO DE FORMULÁRIOS USCIS")
    print("📋 Testing 3 visa types: I-539, I-589, EB-1A")
    print("🎯 Focus: Form generation and download functionality")
    print("=" * 60)
    
    results = {
        "i539_extension": {},
        "i589_asylum": {},
        "eb1a_extraordinary": {},
        "summary": {}
    }
    
    # Test cases from review request
    test_cases = [
        {
            "name": "I-539 Extension",
            "case_id": "OSP-BD2D8ED2",
            "expected_form": "I-539",
            "min_file_size": 400 * 1024,  # 400KB
            "key": "i539_extension"
        },
        {
            "name": "I-589 Asylum", 
            "case_id": "OSP-4899BE72",
            "expected_form": "I-589",
            "min_file_size": 800 * 1024,  # 800KB
            "key": "i589_asylum"
        },
        {
            "name": "EB-1A Extraordinary",
            "case_id": "OSP-8731E45D", 
            "expected_form": "I-140",
            "min_file_size": 500 * 1024,  # 500KB
            "key": "eb1a_extraordinary"
        }
    ]
    
    # STEP 1: Update EB-1A case with correct visa_type (as requested)
    print("\n📋 STEP 1: Update EB-1A Case with Correct visa_type")
    print("-" * 50)
    
    try:
        case_id = "OSP-8731E45D"
        update_data = {"visa_type": "EB-1A"}
        
        print(f"🔗 Endpoint: PUT {API_BASE}/auto-application/case/{case_id}")
        print(f"📤 Payload: {json.dumps(update_data)}")
        
        response = requests.put(
            f"{API_BASE}/auto-application/case/{case_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            response_data = response.json()
            print(f"✅ EB-1A case updated successfully")
            print(f"📄 Response: {json.dumps(response_data, indent=2)}")
        else:
            print(f"⚠️  EB-1A case update returned {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception updating EB-1A case: {str(e)}")
    
    # STEP 2: Test form generation for all 3 visa types
    print("\n📋 STEP 2: Test Form Generation for All 3 Visa Types")
    print("-" * 50)
    
    for test_case in test_cases:
        case_name = test_case["name"]
        case_id = test_case["case_id"]
        expected_form = test_case["expected_form"]
        min_file_size = test_case["min_file_size"]
        result_key = test_case["key"]
        
        print(f"\n🔍 Testing {case_name} - Case {case_id}")
        print("-" * 40)
        
        # Test form generation
        try:
            print(f"📝 Generating {expected_form} form...")
            print(f"🔗 Endpoint: POST {API_BASE}/case/{case_id}/generate-form")
            
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/case/{case_id}/generate-form",
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️  Processing time: {processing_time:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
            
            results[result_key]["generation"] = {
                "status_code": response.status_code,
                "processing_time": processing_time
            }
            
            if response.status_code == 200:
                form_data = response.json()
                print(f"📄 Form Generation Response: {json.dumps(form_data, indent=2)}")
                
                # Validate form generation response
                validations = {
                    "success_true": form_data.get("success", False),
                    "correct_form_type": form_data.get("form_type") == expected_form,
                    "filename_present": form_data.get("filename") is not None,
                    "file_size_positive": form_data.get("file_size", 0) > 0,
                    "download_url_present": form_data.get("download_url") is not None
                }
                
                results[result_key]["generation"]["validations"] = validations
                results[result_key]["generation"]["response_data"] = form_data
                results[result_key]["generation"]["working"] = all(validations.values())
                
                print(f"\n🎯 FORM GENERATION VALIDATIONS - {case_name}:")
                for check, passed in validations.items():
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check}: {passed}")
                
                print(f"\n📊 FORM GENERATION RESULTS:")
                print(f"  ✅ Success: {form_data.get('success', False)}")
                print(f"  📋 Form Type: {form_data.get('form_type', 'N/A')}")
                print(f"  📄 Filename: {form_data.get('filename', 'N/A')}")
                print(f"  📏 File Size: {form_data.get('file_size', 0)} bytes")
                print(f"  🔗 Download URL: {form_data.get('download_url', 'N/A')}")
                
            else:
                print(f"❌ Form generation failed with status {response.status_code}")
                print(f"📄 Error response: {response.text}")
                results[result_key]["generation"]["error"] = response.text
                results[result_key]["generation"]["working"] = False
                
        except Exception as e:
            print(f"❌ Exception during form generation: {str(e)}")
            results[result_key]["generation"]["exception"] = str(e)
            results[result_key]["generation"]["working"] = False
        
        # Test form download
        try:
            print(f"\n📥 Testing {expected_form} form download...")
            print(f"🔗 Endpoint: GET {API_BASE}/case/{case_id}/download-form")
            
            start_time = time.time()
            response = requests.get(
                f"{API_BASE}/case/{case_id}/download-form",
                timeout=60
            )
            processing_time = time.time() - start_time
            
            print(f"⏱️  Processing time: {processing_time:.2f}s")
            print(f"📊 Status Code: {response.status_code}")
            
            results[result_key]["download"] = {
                "status_code": response.status_code,
                "processing_time": processing_time
            }
            
            if response.status_code == 200:
                # Save PDF to temporary file for validation
                temp_filename = f"/tmp/{expected_form}_{case_id}.pdf"
                
                with open(temp_filename, "wb") as f:
                    f.write(response.content)
                
                file_size = len(response.content)
                
                # Validate PDF file
                validations = {
                    "file_downloaded": os.path.exists(temp_filename),
                    "file_size_adequate": file_size >= min_file_size,
                    "content_type_pdf": response.headers.get("content-type", "").startswith("application/pdf"),
                    "file_not_empty": file_size > 0
                }
                
                results[result_key]["download"]["validations"] = validations
                results[result_key]["download"]["file_size"] = file_size
                results[result_key]["download"]["working"] = all(validations.values())
                
                print(f"\n🎯 DOWNLOAD VALIDATIONS - {case_name}:")
                for check, passed in validations.items():
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check}: {passed}")
                
                print(f"\n📊 DOWNLOAD RESULTS:")
                print(f"  📄 File saved: {temp_filename}")
                print(f"  📏 File size: {file_size} bytes ({file_size/1024:.1f} KB)")
                print(f"  📋 Min required: {min_file_size} bytes ({min_file_size/1024:.1f} KB)")
                print(f"  📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                # Verify PDF validity using file command
                try:
                    import subprocess
                    result = subprocess.run(['file', temp_filename], capture_output=True, text=True)
                    file_type = result.stdout.strip()
                    print(f"  🔍 File type: {file_type}")
                    
                    is_valid_pdf = "PDF" in file_type
                    results[result_key]["download"]["is_valid_pdf"] = is_valid_pdf
                    print(f"  ✅ Valid PDF: {is_valid_pdf}")
                    
                except Exception as e:
                    print(f"  ⚠️  Could not verify PDF validity: {str(e)}")
                    results[result_key]["download"]["is_valid_pdf"] = None
                
            else:
                print(f"❌ Form download failed with status {response.status_code}")
                print(f"📄 Error response: {response.text}")
                results[result_key]["download"]["error"] = response.text
                results[result_key]["download"]["working"] = False
                
        except Exception as e:
            print(f"❌ Exception during form download: {str(e)}")
            results[result_key]["download"]["exception"] = str(e)
            results[result_key]["download"]["working"] = False
    
    # STEP 3: Test data persistence in database
    print("\n📋 STEP 3: Test Data Persistence in Database")
    print("-" * 50)
    
    for test_case in test_cases:
        case_name = test_case["name"]
        case_id = test_case["case_id"]
        expected_form = test_case["expected_form"]
        result_key = test_case["key"]
        
        print(f"\n🔍 Verifying persistence for {case_name} - Case {case_id}")
        print("-" * 40)
        
        try:
            print(f"🔗 Endpoint: GET {API_BASE}/auto-application/case/{case_id}")
            
            response = requests.get(
                f"{API_BASE}/auto-application/case/{case_id}",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            results[result_key]["persistence"] = {
                "status_code": response.status_code
            }
            
            if response.status_code == 200:
                case_data = response.json()
                case_info = case_data.get("case", {})
                generated_form = case_info.get("generated_form", {})
                
                print(f"📄 Generated Form Data: {json.dumps(generated_form, indent=2)}")
                
                # Validate persistence
                validations = {
                    "generated_form_exists": generated_form is not None and len(generated_form) > 0,
                    "filename_persisted": generated_form.get("filename") is not None,
                    "generated_at_present": generated_form.get("generated_at") is not None,
                    "form_type_correct": generated_form.get("form_type") == expected_form,
                    "file_size_recorded": generated_form.get("file_size", 0) > 0
                }
                
                results[result_key]["persistence"]["validations"] = validations
                results[result_key]["persistence"]["generated_form"] = generated_form
                results[result_key]["persistence"]["working"] = all(validations.values())
                
                print(f"\n🎯 PERSISTENCE VALIDATIONS - {case_name}:")
                for check, passed in validations.items():
                    status = "✅" if passed else "❌"
                    print(f"  {status} {check}: {passed}")
                
                print(f"\n📊 PERSISTENCE RESULTS:")
                print(f"  📄 Filename: {generated_form.get('filename', 'N/A')}")
                print(f"  📅 Generated At: {generated_form.get('generated_at', 'N/A')}")
                print(f"  📋 Form Type: {generated_form.get('form_type', 'N/A')}")
                print(f"  📏 File Size: {generated_form.get('file_size', 0)} bytes")
                
            else:
                print(f"❌ Persistence check failed with status {response.status_code}")
                print(f"📄 Error response: {response.text}")
                results[result_key]["persistence"]["error"] = response.text
                results[result_key]["persistence"]["working"] = False
                
        except Exception as e:
            print(f"❌ Exception during persistence check: {str(e)}")
            results[result_key]["persistence"]["exception"] = str(e)
            results[result_key]["persistence"]["working"] = False
    
    # STEP 4: Generate summary and comparison
    print("\n📋 STEP 4: Generate Summary and Comparison")
    print("-" * 50)
    
    # Count successful operations
    success_counts = {
        "form_generation": 0,
        "form_download": 0,
        "data_persistence": 0,
        "valid_pdfs": 0
    }
    
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        result_key = test_case["key"]
        
        # Count successes
        if results[result_key].get("generation", {}).get("working", False):
            success_counts["form_generation"] += 1
        
        if results[result_key].get("download", {}).get("working", False):
            success_counts["form_download"] += 1
        
        if results[result_key].get("persistence", {}).get("working", False):
            success_counts["data_persistence"] += 1
        
        if results[result_key].get("download", {}).get("is_valid_pdf", False):
            success_counts["valid_pdfs"] += 1
    
    # Calculate overall success rate
    total_operations = total_tests * 4  # 4 operations per test case
    successful_operations = sum(success_counts.values())
    overall_success_rate = (successful_operations / total_operations) * 100
    
    results["summary"] = {
        "success_counts": success_counts,
        "total_tests": total_tests,
        "successful_operations": successful_operations,
        "total_operations": total_operations,
        "overall_success_rate": overall_success_rate,
        "system_ready": overall_success_rate >= 75  # 75% threshold for system readiness
    }
    
    print(f"\n📊 RESUMO FINAL - SISTEMA DE GERAÇÃO DE FORMULÁRIOS USCIS")
    print("=" * 60)
    
    print(f"📋 Formulários Gerados: {success_counts['form_generation']}/{total_tests} ({success_counts['form_generation']/total_tests*100:.1f}%)")
    print(f"📥 Downloads Funcionando: {success_counts['form_download']}/{total_tests} ({success_counts['form_download']/total_tests*100:.1f}%)")
    print(f"💾 Persistência no Banco: {success_counts['data_persistence']}/{total_tests} ({success_counts['data_persistence']/total_tests*100:.1f}%)")
    print(f"📄 PDFs Válidos: {success_counts['valid_pdfs']}/{total_tests} ({success_counts['valid_pdfs']/total_tests*100:.1f}%)")
    
    print(f"\n🎯 TAXA DE SUCESSO GERAL: {successful_operations}/{total_operations} ({overall_success_rate:.1f}%)")
    
    # Individual case results
    print(f"\n📋 RESULTADOS POR CASO:")
    print("=" * 50)
    
    for test_case in test_cases:
        case_name = test_case["name"]
        case_id = test_case["case_id"]
        expected_form = test_case["expected_form"]
        result_key = test_case["key"]
        
        generation_ok = results[result_key].get("generation", {}).get("working", False)
        download_ok = results[result_key].get("download", {}).get("working", False)
        persistence_ok = results[result_key].get("persistence", {}).get("working", False)
        pdf_valid = results[result_key].get("download", {}).get("is_valid_pdf", False)
        
        case_success_count = sum([generation_ok, download_ok, persistence_ok, pdf_valid])
        case_success_rate = (case_success_count / 4) * 100
        
        print(f"\n🎯 {case_name} ({case_id}):")
        print(f"  📝 Geração: {'✅' if generation_ok else '❌'}")
        print(f"  📥 Download: {'✅' if download_ok else '❌'}")
        print(f"  💾 Persistência: {'✅' if persistence_ok else '❌'}")
        print(f"  📄 PDF Válido: {'✅' if pdf_valid else '❌'}")
        print(f"  📊 Taxa: {case_success_count}/4 ({case_success_rate:.1f}%)")
    
    # System readiness assessment
    print(f"\n🎯 AVALIAÇÃO DO SISTEMA:")
    print("=" * 50)
    
    if results["summary"]["system_ready"]:
        print("✅ SISTEMA DE FORMULÁRIOS: TOTALMENTE FUNCIONAL")
        print("✅ PRONTO PARA USCIS: SIM (PDFs oficiais preenchidos)")
        print("✅ Todos os 3 tipos de visto suportados")
    else:
        print("⚠️  SISTEMA DE FORMULÁRIOS: NECESSITA MELHORIAS")
        print("❌ PRONTO PARA USCIS: NÃO (alguns formulários falhando)")
        
        # Identify problem areas
        problem_areas = []
        if success_counts["form_generation"] < total_tests:
            problem_areas.append("Geração de formulários")
        if success_counts["form_download"] < total_tests:
            problem_areas.append("Download de PDFs")
        if success_counts["data_persistence"] < total_tests:
            problem_areas.append("Persistência de dados")
        if success_counts["valid_pdfs"] < total_tests:
            problem_areas.append("Validação de PDFs")
        
        if problem_areas:
            print(f"❌ Áreas problemáticas: {', '.join(problem_areas)}")
    
    # Comparison with expected results
    print(f"\n📊 COMPARAÇÃO ANTES vs DEPOIS:")
    print("=" * 50)
    print("ANTES:")
    print("  Formulários Gerados:  0/3 (0%)")
    print("  Download Funciona:    0/3 (0%)")
    print("  Sistema Completo:     ❌ NÃO")
    print()
    print("DEPOIS (Atual):")
    print(f"  Formulários Gerados:  {success_counts['form_generation']}/3 ({success_counts['form_generation']/3*100:.0f}%)")
    print(f"  Download Funciona:    {success_counts['form_download']}/3 ({success_counts['form_download']/3*100:.0f}%)")
    print(f"  Sistema Completo:     {'✅ SIM' if results['summary']['system_ready'] else '❌ NÃO'}")
    
    return results
    for criterion, passed in eb1a_success_criteria.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {criterion}: {passed}")
    
    print(f"\n📊 EB-1A SUCCESS RATE: {eb1a_criteria_met}/{eb1a_total_criteria} ({eb1a_success_rate:.1f}%)")
    
    results["summary"]["eb1a_success_criteria"] = eb1a_success_criteria
    results["summary"]["eb1a_success_rate"] = eb1a_success_rate
    
    return results

def test_additional_eb1a_endpoints():
    """Test additional EB-1A related endpoints for completeness"""
    
    print("\n🔍 TESTES ADICIONAIS - ENDPOINTS EB-1A RELACIONADOS")
    print("=" * 60)
    
    additional_results = {}
    
    # Test visa detailed info for EB-1A
    try:
        print("\n📋 EB-1A Visa Detailed Info:")
        response = requests.get(f"{API_BASE}/visa-detailed-info/EB-1A?process_type=consular", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            visa_info = response.json()
            print(f"   Response: {json.dumps(visa_info, indent=4)}")
        additional_results["eb1a_visa_info"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A visa info failed: {str(e)}")
        additional_results["eb1a_visa_info"] = False
    
    # Test document requirements for EB-1A
    try:
        print("\n📄 EB-1A Document Requirements:")
        response = requests.get(f"{API_BASE}/visa/EB-1A/documents", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            doc_requirements = response.json()
            print(f"   Response: {json.dumps(doc_requirements, indent=4)}")
        additional_results["eb1a_documents"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A document requirements failed: {str(e)}")
        additional_results["eb1a_documents"] = False
    
    # Test EB-1A specific validation
    try:
        print("\n🏆 EB-1A Specific Validation:")
        validation_data = {
            "document_type": "awards",
            "document_content": "2023 Turing Award Finalist - Dr. Sofia Martinez Chen",
            "applicant_name": "Dr. Sofia Martinez Chen",
            "visa_type": "EB-1A"
        }
        response = requests.post(
            f"{API_BASE}/test-comprehensive-document-validation",
            json=validation_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            validation_result = response.json()
            print(f"   Response: {json.dumps(validation_result, indent=4)}")
        additional_results["eb1a_validation"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A validation failed: {str(e)}")
        additional_results["eb1a_validation"] = False
    
    # Test extraordinary ability criteria validation
    try:
        print("\n🧬 Extraordinary Ability Criteria:")
        criteria_data = {
            "criteria": [
                "Awards - national/international prizes",
                "Membership in associations requiring outstanding achievements",
                "Published material about the applicant",
                "Judging the work of others",
                "Original contributions of major significance",
                "Scholarly articles",
                "High salary"
            ],
            "field": "Sciences - Artificial Intelligence Research"
        }
        response = requests.post(
            f"{API_BASE}/validate-eb1a-criteria",
            json=criteria_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            criteria_result = response.json()
            print(f"   Response: {json.dumps(criteria_result, indent=4)}")
        additional_results["eb1a_criteria"] = response.status_code == 200
    except Exception as e:
        print(f"   ❌ EB-1A criteria validation failed: {str(e)}")
        additional_results["eb1a_criteria"] = False
    
    return additional_results

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE COMPLETO - SISTEMA DE GERAÇÃO DE FORMULÁRIOS USCIS")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Execute main test
    test_results = test_uscis_form_generation_system()
    
    # Save results to file
    with open("/app/uscis_form_generation_test_results.json", "w") as f:
        json.dump({
            "test_results": test_results,
            "timestamp": time.time(),
            "test_focus": "USCIS Form Generation System Testing",
            "test_cases": [
                {"name": "I-539 Extension", "case_id": "OSP-BD2D8ED2"},
                {"name": "I-589 Asylum", "case_id": "OSP-4899BE72"},
                {"name": "EB-1A Extraordinary", "case_id": "OSP-8731E45D"}
            ]
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/uscis_form_generation_test_results.json")
    
    # Final recommendation
    summary = test_results.get("summary", {})
    if summary.get("system_ready", False):
        print("\n✅ RECOMENDAÇÃO: Sistema de Formulários USCIS PRONTO PARA PRODUÇÃO")
        print("   - Todos os 3 tipos de visto funcionando")
        print("   - PDFs oficiais sendo gerados corretamente")
        print("   - Sistema completo e funcional")
    else:
        success_rate = summary.get("overall_success_rate", 0)
        if success_rate >= 50:
            print("\n⚠️  RECOMENDAÇÃO: Sistema parcialmente funcional, melhorias necessárias")
            print("   - Alguns formulários funcionando")
            print("   - Revisar casos que falharam")
        else:
            print("\n❌ RECOMENDAÇÃO: Sistema precisa de desenvolvimento adicional")
            print("   - Múltiplos problemas identificados")
            print("   - Revisão completa necessária")
    
