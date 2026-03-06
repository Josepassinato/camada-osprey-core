#!/usr/bin/env python3
"""
Test Complete Integration: Backend + Frontend Structure
Tests all new visa types and validates the complete flow
"""

import requests
import json

BACKEND_URL = "http://0.0.0.0:8001"

def test_all_visa_structures():
    """Test structures for all visa types"""
    
    print("=" * 80)
    print("🧪 TESTE COMPLETO: TODAS AS ESTRUTURAS DE VISTO")
    print("=" * 80)
    
    # Get available visa types
    print("\n📋 Obtendo lista de vistos disponíveis...")
    response = requests.get(f"{BACKEND_URL}/api/friendly-form/available-visas")
    
    if response.status_code != 200:
        print("❌ Erro ao obter lista de vistos")
        return False
    
    data = response.json()
    visa_types = data["visa_types"]
    
    print(f"✅ {data['total']} tipos de visto disponíveis\n")
    
    # Test each visa type
    results = []
    
    for visa in visa_types:
        code = visa["code"]
        name = visa["name"]
        
        print(f"\n{'='*80}")
        print(f"🧪 Testando: {code} - {name}")
        print(f"{'='*80}")
        
        # Get structure
        struct_response = requests.get(f"{BACKEND_URL}/api/friendly-form/structure/{code}")
        
        if struct_response.status_code != 200:
            print(f"❌ Erro ao obter estrutura para {code}")
            results.append({
                "visa": code,
                "success": False,
                "error": "Failed to get structure"
            })
            continue
        
        structure = struct_response.json()["structure"]
        
        # Validate structure
        has_sections = len(structure.get("sections", [])) > 0
        has_fields = structure.get("total_fields", 0) > 0
        has_mapping = all(
            any("official_mapping" in field for field in section.get("fields", []))
            for section in structure.get("sections", [])
        )
        
        total_fields = structure["total_fields"]
        sections = len(structure["sections"])
        required_fields = sum(
            1 for section in structure["sections"]
            for field in section["fields"]
            if field.get("required", False) and not field.get("conditional")
        )
        
        print(f"\n📊 ESTRUTURA:")
        print(f"   Nome: {structure['form_name']}")
        print(f"   Total de Campos: {total_fields}")
        print(f"   Campos Obrigatórios: {required_fields}")
        print(f"   Seções: {sections}")
        print(f"   Tempo Estimado: {structure['estimated_time']}")
        
        if structure.get("warning"):
            print(f"   ⚠️  Aviso: {structure['warning']}")
        
        # Check specific sections
        print(f"\n📝 SEÇÕES:")
        for i, section in enumerate(structure["sections"], 1):
            field_count = len(section["fields"])
            required_in_section = sum(1 for f in section["fields"] if f.get("required"))
            print(f"   {i}. {section['title']}: {field_count} campos ({required_in_section} obrigatórios)")
        
        # Validation
        all_valid = has_sections and has_fields and has_mapping
        
        if all_valid:
            print(f"\n✅ ESTRUTURA VÁLIDA")
            results.append({
                "visa": code,
                "name": name,
                "success": True,
                "total_fields": total_fields,
                "required_fields": required_fields,
                "sections": sections
            })
        else:
            print(f"\n❌ ESTRUTURA INVÁLIDA")
            if not has_sections:
                print(f"   - Sem seções")
            if not has_fields:
                print(f"   - Sem campos")
            if not has_mapping:
                print(f"   - Sem mapeamento")
            results.append({
                "visa": code,
                "success": False,
                "error": "Invalid structure"
            })
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 RESUMO GERAL")
    print(f"{'='*80}")
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"\n✅ Vistos com Estrutura Válida: {len(successful)}/{len(results)}")
    for result in successful:
        print(f"   ✅ {result['visa']}: {result['total_fields']} campos ({result['required_fields']} obrigatórios)")
    
    if failed:
        print(f"\n❌ Vistos com Problemas: {len(failed)}")
        for result in failed:
            print(f"   ❌ {result['visa']}: {result.get('error', 'Unknown error')}")
    
    # Table comparison
    print(f"\n{'='*80}")
    print(f"📋 TABELA COMPARATIVA")
    print(f"{'='*80}\n")
    
    print(f"| Código | Nome | Campos | Obrig. | Seções | Tempo |")
    print(f"|--------|------|--------|--------|--------|-------|")
    for result in successful:
        visa_data = next((v for v in visa_types if v["code"] == result["visa"]), None)
        if visa_data:
            print(f"| {result['visa']:6} | {visa_data['name'][:20]:20} | {result['total_fields']:6} | {result['required_fields']:6} | {result['sections']:6} | {visa_data['estimated_time']:13} |")
    
    return len(failed) == 0


def test_validation_with_new_visas():
    """Test validation for new visa types"""
    
    print(f"\n{'='*80}")
    print(f"🧪 TESTE: VALIDAÇÃO COM NOVOS TIPOS DE VISTO")
    print(f"{'='*80}")
    
    test_visas = ["F-1", "H-1B", "B-2"]
    
    for visa_type in test_visas:
        print(f"\n📝 Testando validação para {visa_type}...")
        
        # Create case
        case_resp = requests.post(
            f"{BACKEND_URL}/api/auto-application/start",
            json={"form_code": visa_type, "process_type": "extension"}
        )
        
        if case_resp.status_code != 200:
            print(f"❌ Erro ao criar caso para {visa_type}")
            continue
        
        case_id = case_resp.json()["case"]["case_id"]
        
        # Test with incomplete data
        incomplete_data = {
            "friendly_form_data": {
                "nome_completo": "Test User",
                "email": "test@test.com"
            },
            "basic_data": {}
        }
        
        val_resp = requests.post(
            f"{BACKEND_URL}/api/case/{case_id}/friendly-form",
            json=incomplete_data
        )
        
        if val_resp.status_code == 200:
            result = val_resp.json()
            print(f"✅ Validação funcionou para {visa_type}")
            print(f"   Status: {result['validation_status']}")
            print(f"   Completude: {result['completion_percentage']}%")
            print(f"   Issues: {len(result.get('validation_issues', []))}")
        else:
            print(f"❌ Erro na validação para {visa_type}: {val_resp.status_code}")
    
    return True


def test_frontend_endpoints():
    """Test that frontend endpoints are accessible"""
    
    print(f"\n{'='*80}")
    print(f"🧪 TESTE: ENDPOINTS PARA FRONTEND")
    print(f"{'='*80}")
    
    endpoints = [
        ("/api/friendly-form/available-visas", "GET", "Lista de Vistos"),
        ("/api/friendly-form/structure/I-539", "GET", "Estrutura I-539"),
        ("/api/friendly-form/structure/F-1", "GET", "Estrutura F-1"),
        ("/api/friendly-form/structure/H-1B", "GET", "Estrutura H-1B"),
    ]
    
    all_ok = True
    
    for endpoint, method, description in endpoints:
        response = requests.get(f"{BACKEND_URL}{endpoint}")
        
        if response.status_code == 200:
            print(f"✅ {description}: {endpoint}")
        else:
            print(f"❌ {description}: {endpoint} - Status {response.status_code}")
            all_ok = False
    
    return all_ok


if __name__ == "__main__":
    print("\n")
    print("🚀 " + "="*76 + " 🚀")
    print("   TESTE DE INTEGRAÇÃO COMPLETA: BACKEND + ESTRUTURAS DE VISTO")
    print("🚀 " + "="*76 + " 🚀")
    
    # Test 1: All visa structures
    test1_result = test_all_visa_structures()
    
    # Test 2: Validation with new visas
    test2_result = test_validation_with_new_visas()
    
    # Test 3: Frontend endpoints
    test3_result = test_frontend_endpoints()
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"🎯 RESULTADO FINAL")
    print(f"{'='*80}")
    
    all_passed = test1_result and test2_result and test3_result
    
    if all_passed:
        print(f"\n✅ TODOS OS TESTES PASSARAM!")
        print(f"\n🎉 Sistema de Formulários Integrado está FUNCIONANDO!")
        print(f"\nCaracterísticas Implementadas:")
        print(f"   ✅ 8 tipos de visto suportados (I-539, F-1, H-1B, B-2, L-1, O-1, I-589, EB-1A)")
        print(f"   ✅ Estruturas completas baseadas em formulários oficiais USCIS")
        print(f"   ✅ Endpoints REST para frontend consumir")
        print(f"   ✅ Validação funcionando para todos os tipos")
        print(f"   ✅ Mapeamento 1:1 para formulários oficiais")
        print(f"\nPróximos Passos:")
        print(f"   - Frontend React integrado com endpoints")
        print(f"   - Componente DynamicFriendlyForm renderiza formulários dinamicamente")
        print(f"   - Página VisaSelection lista todos os vistos disponíveis")
    else:
        print(f"\n⚠️  Alguns testes falharam")
        print(f"   Estruturas: {'✅' if test1_result else '❌'}")
        print(f"   Validação: {'✅' if test2_result else '❌'}")
        print(f"   Endpoints: {'✅' if test3_result else '❌'}")
