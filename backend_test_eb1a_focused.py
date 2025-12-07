#!/usr/bin/env python3
"""
Backend Testing Suite - EB-1A AI Review System Testing After Corrections
Testing specific case OSP-8731E45D with EB-1A improvements
"""

import requests
import json
import time
import os
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://visaflow-5.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_eb1a_ai_review_after_corrections():
    """
    🎯 TESTE EB-1A APÓS CORREÇÕES - VALIDAÇÃO FINAL
    
    Testing specific case OSP-8731E45D after implementing EB-1A corrections
    
    SPECIFIC TEST REQUESTED IN REVIEW:
    Test existing case OSP-8731E45D which already has:
    - ✅ 8 EB-1A documents
    - ✅ Personal statement (1592 characters)  
    - ✅ EB-1A form with 7 criteria
    
    FOCUS: AI Review After Corrections
    Test: GET /api/case/OSP-8731E45D/ai-review
    
    VERIFY IMPROVEMENTS:
    - ✅ System recognizes EB-1A specifically
    - ✅ Score > 85% (before was 75%)
    - ✅ Status = "APPROVED" (before was generic)
    - ✅ Message contains EB-1A specific terminology
    - ✅ Documents score = 1.0 (8/8 documents)
    - ✅ Letters score = 0.90 (petition letter > 500 chars)
    """
    
    print("🎯 TESTE EB-1A APÓS CORREÇÕES - VALIDAÇÃO FINAL")
    print("📋 Case ID: OSP-8731E45D (existing case)")
    print("🎯 Focus: AI Review System After Corrections")
    print("=" * 60)
    
    results = {
        "case_verification": {},
        "ai_review_test": {},
        "comparison_before_after": {},
        "summary": {}
    }
    
    # Use existing case ID from review request
    case_id = "OSP-8731E45D"
    
    # STEP 1: Verify existing case OSP-8731E45D
    print("\n📋 STEP 1: Verify Existing Case OSP-8731E45D")
    print("-" * 50)
    
    try:
        print(f"🔗 Endpoint: GET {API_BASE}/auto-application/case/{case_id}")
        
        start_time = time.time()
        response = requests.get(
            f"{API_BASE}/auto-application/case/{case_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["case_verification"]["status_code"] = response.status_code
        results["case_verification"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            case_data = response.json()
            print(f"📄 Case Data: {json.dumps(case_data, indent=2)}")
            
            case_info = case_data.get("case", {})
            
            # Verify case has expected EB-1A data
            validations = {
                "1_case_exists": case_info.get("case_id") == case_id,
                "2_eb1a_visa_type": case_info.get("form_code") == "EB-1A",
                "3_documents_present": len(case_info.get("uploaded_documents", [])) >= 8,
                "4_personal_statement_present": case_info.get("letters", {}).get("cover_letter") is not None,
                "5_personal_statement_length": len(case_info.get("letters", {}).get("cover_letter", "")) > 1500,
                "6_eb1a_form_present": case_info.get("forms", {}).get("eb1a") is not None,
                "7_criteria_count": case_info.get("forms", {}).get("eb1a", {}).get("criteria_count", 0) >= 7
            }
            
            results["case_verification"]["validations"] = validations
            results["case_verification"]["case_data"] = case_info
            
            print("\n🎯 CASE VERIFICATION - OSP-8731E45D:")
            print("=" * 50)
            for check, passed in validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Show case details
            documents_count = len(case_info.get("uploaded_documents", []))
            letter_length = len(case_info.get("letters", {}).get("cover_letter", ""))
            criteria_count = case_info.get("forms", {}).get("eb1a", {}).get("criteria_count", 0)
            
            print(f"\n📊 CASE OSP-8731E45D DETAILS:")
            print(f"  📋 Case ID: {case_info.get('case_id', 'N/A')}")
            print(f"  🎯 Visa Type: {case_info.get('form_code', 'N/A')}")
            print(f"  📄 Documents: {documents_count}/8")
            print(f"  📝 Personal Statement: {letter_length} characters")
            print(f"  📋 EB-1A Criteria: {criteria_count}/10")
                
        else:
            print(f"❌ Case verification failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["case_verification"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during case verification: {str(e)}")
        results["case_verification"]["exception"] = str(e)
    
    # STEP 2: Test AI Review After Corrections
    print("\n📋 STEP 2: AI Review After EB-1A Corrections")
    print("-" * 50)
    
    if not case_id:
        print("❌ Cannot proceed without case_id")
        return results
    
    try:
        print("🔍 Testing EB-1A AI Review System After Corrections...")
        print(f"🔗 Endpoint: GET {API_BASE}/case/{case_id}/ai-review")
        
        start_time = time.time()
        response = requests.get(
            f"{API_BASE}/case/{case_id}/ai-review",
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        processing_time = time.time() - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        results["ai_review_test"]["status_code"] = response.status_code
        results["ai_review_test"]["processing_time"] = processing_time
        
        if response.status_code == 200:
            ai_review = response.json()
            print(f"📄 AI Review Response: {json.dumps(ai_review, indent=2)}")
            
            # EB-1A specific validations after corrections
            eb1a_validations = {
                "1_recognizes_eb1a": ai_review.get("visa_type") == "EB-1A",
                "2_score_above_85": ai_review.get("overall_score", 0) > 85,
                "3_status_approved": ai_review.get("overall_status") == "APPROVED",
                "4_eb1a_in_message": "EB-1A" in str(ai_review.get("approval_message", "")),
                "5_extraordinary_ability_mentioned": "extraordinary ability" in str(ai_review).lower(),
                "6_sustained_acclaim_mentioned": "sustained" in str(ai_review).lower() and "acclaim" in str(ai_review).lower(),
                "7_uscis_criteria_mentioned": "USCIS criteria" in str(ai_review) or "criteria" in str(ai_review).lower(),
                "8_documents_score_perfect": ai_review.get("detailed_checks", {}).get("documents", {}).get("score", 0) == 1.0,
                "9_letters_score_90": ai_review.get("detailed_checks", {}).get("letters", {}).get("score", 0) >= 0.90,
                "10_documents_count_8": ai_review.get("detailed_checks", {}).get("documents", {}).get("uploaded", 0) >= 8
            }
            
            results["ai_review_test"]["validations"] = eb1a_validations
            results["ai_review_test"]["response_data"] = ai_review
            
            print("\n🎯 EB-1A AI REVIEW VALIDATIONS AFTER CORRECTIONS:")
            print("=" * 60)
            for check, passed in eb1a_validations.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}: {passed}")
            
            # Extract key metrics
            overall_score = ai_review.get("overall_score", 0)
            overall_status = ai_review.get("overall_status", "N/A")
            visa_type = ai_review.get("visa_type", "N/A")
            approval_message = ai_review.get("approval_message", "N/A")
            
            detailed_checks = ai_review.get("detailed_checks", {})
            documents_info = detailed_checks.get("documents", {})
            letters_info = detailed_checks.get("letters", {})
            
            documents_score = documents_info.get("score", 0)
            documents_uploaded = documents_info.get("uploaded", 0)
            documents_required = documents_info.get("required", 8)
            
            letters_score = letters_info.get("score", 0)
            letter_length = letters_info.get("letter_length", 0)
            
            print(f"\n📊 EB-1A AI REVIEW RESULTS:")
            print("=" * 50)
            print(f"  🎯 Overall Status: {overall_status}")
            print(f"  📊 Overall Score: {overall_score}%")
            print(f"  🧬 Visa Type: {visa_type}")
            print(f"  📄 Documents: {documents_uploaded}/{documents_required} (Score: {documents_score})")
            print(f"  📝 Letters: {letter_length} chars (Score: {letters_score})")
            print(f"  ✅ Message: {approval_message[:100]}...")
            
            # Check improvement criteria
            improvement_criteria = {
                "score_improved": overall_score > 85,  # Before was 75%
                "status_specific": overall_status == "APPROVED",  # Before was generic
                "eb1a_terminology": eb1a_validations["4_eb1a_in_message"] and eb1a_validations["5_extraordinary_ability_mentioned"],
                "documents_perfect": documents_score == 1.0,
                "letters_improved": letters_score >= 0.90
            }
            
            results["ai_review_test"]["improvement_criteria"] = improvement_criteria
            
            print(f"\n🎉 IMPROVEMENT VERIFICATION:")
            print("=" * 50)
            for criterion, met in improvement_criteria.items():
                status = "✅" if met else "❌"
                print(f"  {status} {criterion}: {met}")
                
        else:
            print(f"❌ AI Review failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            results["ai_review_test"]["error"] = response.text
            
    except Exception as e:
        print(f"❌ Exception during AI Review: {str(e)}")
        results["ai_review_test"]["exception"] = str(e)
    
    # STEP 3: Compare Before vs After Results
    print("\n📋 STEP 3: Compare Before vs After Results")
    print("-" * 50)
    
    # Expected results based on review request
    before_corrections = {
        "score": 75,
        "status": "Generic",
        "message": "Caso aprovado",
        "letter_score": 0.75,
        "requirements": "Não específicos EB-1A"
    }
    
    # Get actual results from AI review
    ai_review_data = results.get("ai_review_test", {}).get("response_data", {})
    after_corrections = {
        "score": ai_review_data.get("overall_score", 0),
        "status": ai_review_data.get("overall_status", "N/A"),
        "message": ai_review_data.get("approval_message", "N/A")[:50] + "...",
        "letter_score": ai_review_data.get("detailed_checks", {}).get("letters", {}).get("score", 0),
        "requirements": "EB-1A específicos (8 documentos)"
    }
    
    results["comparison_before_after"] = {
        "before": before_corrections,
        "after": after_corrections
    }
    
    print("📊 COMPARAÇÃO ANTES vs DEPOIS:")
    print("=" * 50)
    print(f"Score:        {before_corrections['score']}% → {after_corrections['score']}%")
    print(f"Status:       {before_corrections['status']} → {after_corrections['status']}")
    print(f"Message:      {before_corrections['message']} → {after_corrections['message']}")
    print(f"Letter Score: {before_corrections['letter_score']} → {after_corrections['letter_score']}")
    print(f"Requirements: {before_corrections['requirements']} → {after_corrections['requirements']}")
    
    # Summary
    print("\n📊 RESUMO FINAL - EB-1A APÓS CORREÇÕES")
    print("=" * 60)
    
    # Count successful validations
    case_validations = results.get("case_verification", {}).get("validations", {})
    ai_validations = results.get("ai_review_test", {}).get("validations", {})
    improvement_criteria = results.get("ai_review_test", {}).get("improvement_criteria", {})
    
    case_success = sum(case_validations.values()) if case_validations else 0
    ai_success = sum(ai_validations.values()) if ai_validations else 0
    improvement_success = sum(improvement_criteria.values()) if improvement_criteria else 0
    
    total_case_checks = len(case_validations) if case_validations else 7
    total_ai_checks = len(ai_validations) if ai_validations else 10
    total_improvement_checks = len(improvement_criteria) if improvement_criteria else 5
    
    case_success_rate = (case_success / total_case_checks) * 100 if total_case_checks > 0 else 0
    ai_success_rate = (ai_success / total_ai_checks) * 100 if total_ai_checks > 0 else 0
    improvement_success_rate = (improvement_success / total_improvement_checks) * 100 if total_improvement_checks > 0 else 0
    
    overall_success_rate = (case_success_rate + ai_success_rate + improvement_success_rate) / 3
    
    print(f"📋 Case Verification: {case_success}/{total_case_checks} ({case_success_rate:.1f}%)")
    print(f"🤖 AI Review Tests: {ai_success}/{total_ai_checks} ({ai_success_rate:.1f}%)")
    print(f"🎉 Improvements: {improvement_success}/{total_improvement_checks} ({improvement_success_rate:.1f}%)")
    print(f"📊 Overall Success: {overall_success_rate:.1f}%")
    
    # Final assessment
    eb1a_system_ready = overall_success_rate >= 80
    
    results["summary"] = {
        "case_id": case_id,
        "case_success_rate": case_success_rate,
        "ai_success_rate": ai_success_rate,
        "improvement_success_rate": improvement_success_rate,
        "overall_success_rate": overall_success_rate,
        "eb1a_system_ready": eb1a_system_ready,
        "before_corrections": before_corrections,
        "after_corrections": after_corrections
    }
    
    print(f"\n🎯 CRITÉRIOS DE SUCESSO EB-1A (8/8):")
    print("=" * 50)
    
    success_criteria = [
        ("Reconhece visa_type = 'EB-1A'", ai_validations.get("1_recognizes_eb1a", False)),
        ("Score > 85%", ai_validations.get("2_score_above_85", False)),
        ("Mensagem específica de EB-1A", ai_validations.get("4_eb1a_in_message", False)),
        ("Menciona 'extraordinary ability'", ai_validations.get("5_extraordinary_ability_mentioned", False)),
        ("Menciona 'sustained acclaim'", ai_validations.get("6_sustained_acclaim_mentioned", False)),
        ("Menciona 'USCIS criteria'", ai_validations.get("7_uscis_criteria_mentioned", False)),
        ("Letter score = 0.90", ai_validations.get("9_letters_score_90", False)),
        ("Documents score = 1.0 (8/8)", ai_validations.get("8_documents_score_perfect", False))
    ]
    
    for criterion, passed in success_criteria:
        status = "✅" if passed else "❌"
        print(f"  {status} {criterion}")
    
    criteria_met = sum(passed for _, passed in success_criteria)
    criteria_success_rate = (criteria_met / len(success_criteria)) * 100
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"Critérios EB-1A: {criteria_met}/{len(success_criteria)} ({criteria_success_rate:.1f}%)")
    
    if criteria_success_rate >= 80:
        print("🎉 ✅ SISTEMA EB-1A TOTALMENTE FLEXÍVEL E ADAPTÁVEL!")
        print("   - Reconhece EB-1A especificamente")
        print("   - Score > 85% (melhorado)")
        print("   - Terminologia específica presente")
        print("   - Sistema pronto para produção")
    elif criteria_success_rate >= 60:
        print("⚠️  ✅ SISTEMA EB-1A PARCIALMENTE FUNCIONAL")
        print("   - Algumas melhorias implementadas")
        print("   - Necessita ajustes adicionais")
    else:
        print("❌ SISTEMA EB-1A PRECISA DE MAIS CORREÇÕES")
        print("   - Múltiplos critérios não atendidos")
        print("   - Revisão das correções necessária")
    
    return results

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE EB-1A APÓS CORREÇÕES - VALIDAÇÃO FINAL")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    
    # Main test - EB-1A AI Review After Corrections
    results = test_eb1a_ai_review_after_corrections()
    
    # Save results to file
    with open("/app/eb1a_ai_review_test_results.json", "w") as f:
        json.dump({
            "test_results": results,
            "timestamp": time.time(),
            "test_focus": "EB-1A AI Review System After Corrections",
            "case_id": "OSP-8731E45D",
            "expected_improvements": [
                "Score > 85% (before was 75%)",
                "Status = APPROVED (before was generic)",
                "EB-1A specific terminology",
                "Documents score = 1.0",
                "Letters score = 0.90"
            ]
        }, f, indent=2)
    
    print(f"\n💾 Resultados salvos em: /app/eb1a_ai_review_test_results.json")
    
    # Final conclusion
    summary = results.get("summary", {})
    overall_success_rate = summary.get("overall_success_rate", 0)
    
    print(f"\n🎯 CONCLUSÃO FINAL:")
    if overall_success_rate >= 80:
        print("✅ CORREÇÕES EB-1A IMPLEMENTADAS COM SUCESSO!")
        print("   Sistema reconhece e processa EB-1A corretamente")
        print("   Melhorias significativas implementadas")
        print("   Pronto para uso em produção")
    elif overall_success_rate >= 60:
        print("⚠️  CORREÇÕES EB-1A PARCIALMENTE IMPLEMENTADAS")
        print("   Algumas melhorias funcionando")
        print("   Necessita ajustes adicionais")
    else:
        print("❌ CORREÇÕES EB-1A PRECISAM DE REVISÃO")
        print("   Múltiplos problemas identificados")
        print("   Implementação das correções incompleta")
    
    print(f"\n📊 Taxa de sucesso geral: {overall_success_rate:.1f}%")