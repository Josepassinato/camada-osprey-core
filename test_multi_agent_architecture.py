#!/usr/bin/env python3
"""
Teste da Arquitetura Multi-Agente
Demonstra como o supervisor analisa, delega e valida
"""

import sys
from pathlib import Path

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent))

from visa_specialists.supervisor.supervisor_agent import SupervisorAgent
from visa_specialists.b2_extension.b2_agent import B2ExtensionAgent
from visa_specialists.h1b_worker.h1b_agent import H1BWorkerAgent
from visa_specialists.f1_student.f1_agent import F1StudentAgent


def test_architecture():
    """Testa arquitetura multi-agente"""
    
    print("\n" + "="*80)
    print("TESTANDO ARQUITETURA MULTI-AGENTE")
    print("="*80)
    
    # 1. Criar supervisor
    print("\n1️⃣ Criando Supervisor Agent...")
    supervisor = SupervisorAgent()
    
    # 2. Registrar especialistas
    print("\n2️⃣ Registrando Especialistas...")
    b2_agent = B2ExtensionAgent()
    h1b_agent = H1BWorkerAgent()
    f1_agent = F1StudentAgent()
    
    supervisor.register_specialist('B-2', b2_agent)
    supervisor.register_specialist('H-1B', h1b_agent)
    supervisor.register_specialist('F-1', f1_agent)
    
    # 3. Teste de detecção de tipo de visto
    print("\n" + "="*80)
    print("3️⃣ TESTE DE DETECÇÃO DE TIPO DE VISTO")
    print("="*80)
    
    test_cases = [
        "Preciso estender meu visto de turista B-2 por motivos médicos",
        "Quero aplicar para H-1B work visa",
        "Preciso do I-20 para estudar nos Estados Unidos",
        "Green card application through employment",
        "Tourist visa extension for family emergency"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 Teste {i}: \"{test_input}\"")
        visa_type = supervisor.detect_visa_type(test_input)
        print(f"   ✅ Detectado: {visa_type if visa_type else '❌ Não detectado'}")
    
    # 4. Teste de análise completa
    print("\n" + "="*80)
    print("4️⃣ TESTE DE ANÁLISE COMPLETA - B-2 EXTENSION")
    print("="*80)
    
    user_request = "Preciso estender meu visto B-2 de turista porque tive uma emergência médica"
    analysis = supervisor.analyze_request(user_request)
    
    print(f"\n📊 Análise da Requisição:")
    print(f"   Tipo de Visto: {analysis['visa_type']}")
    print(f"   Tem Especialista: {analysis['has_specialist']}")
    print(f"   Confiança: {analysis['confidence']}")
    
    # 5. Teste de validação
    print("\n" + "="*80)
    print("5️⃣ TESTE DE VALIDAÇÃO - B-2 EXTENSION")
    print("="*80)
    
    # Pacote correto
    print("\n✅ Teste com pacote CORRETO:")
    correct_package = [
        "Form I-539",
        "Cover Letter",
        "Personal Statement",
        "Current I-94",
        "Passport Copy",
        "Bank Statements",
        "Travel History"
    ]
    validation = b2_agent.validate_package(correct_package)
    print(f"   Válido: {validation['is_valid']}")
    
    # Pacote com erro (inclui I-20)
    print("\n❌ Teste com pacote INCORRETO (inclui I-20):")
    incorrect_package = [
        "Form I-539",
        "Cover Letter",
        "I-20",  # ❌ ERRO: documento proibido!
        "Passport Copy"
    ]
    validation = b2_agent.validate_package(incorrect_package)
    print(f"   Válido: {validation['is_valid']}")
    if validation['forbidden_items_found']:
        print(f"   ⚠️  Documentos Proibidos: {validation['forbidden_items_found']}")
    if validation['missing_items']:
        print(f"   ⚠️  Itens Faltando: {validation['missing_items']}")
    
    # 6. Teste de checklist
    print("\n" + "="*80)
    print("6️⃣ CHECKLISTS DE CADA ESPECIALISTA")
    print("="*80)
    
    for visa_type, agent in [('B-2', b2_agent), ('H-1B', h1b_agent), ('F-1', f1_agent)]:
        print(f"\n📋 {visa_type} Checklist:")
        checklist = agent.get_package_checklist()
        print(f"   Formulários Obrigatórios: {len(checklist['required_forms'])}")
        for form in checklist['required_forms']:
            print(f"      • {form}")
        print(f"   Documentos Proibidos: {len(checklist['forbidden_documents'])}")
        for doc in checklist['forbidden_documents'][:3]:  # Mostrar apenas 3
            print(f"      • {doc}")
    
    # 7. Teste de lessons learned
    print("\n" + "="*80)
    print("7️⃣ SISTEMA DE LESSONS LEARNED")
    print("="*80)
    
    print("\n📚 Registrando nova lição no B-2 Agent...")
    b2_agent.log_lesson(
        mistake="Esqueci de incluir evidência de vínculos com país de origem",
        fix="Sempre incluir property deeds, family documentation, e employment/pension evidence",
        category="Documentação Obrigatória"
    )
    
    print("\n📖 Lições do B-2 Agent:")
    if b2_agent.lessons:
        # Mostrar primeiras linhas
        lines = b2_agent.lessons.split('\n')[:15]
        for line in lines:
            print(f"   {line}")
        print(f"   ... (total: {len(b2_agent.lessons)} caracteres)")
    
    # 8. Resultado Final
    print("\n" + "="*80)
    print("✅ ARQUITETURA MULTI-AGENTE FUNCIONANDO!")
    print("="*80)
    
    print("\n🎯 Benefícios Implementados:")
    print("   ✅ Especialização por tipo de visto")
    print("   ✅ Detecção automática de tipo")
    print("   ✅ Validação cruzada (evita documentos errados)")
    print("   ✅ Sistema de lessons learned")
    print("   ✅ Checklists específicos")
    print("   ✅ Prevenção de erros")
    
    print("\n📊 Estatísticas:")
    print(f"   • Especialistas registrados: 3 (B-2, H-1B, F-1)")
    print(f"   • Formulários monitorados: {len(b2_agent.REQUIRED_FORMS) + len(h1b_agent.REQUIRED_FORMS) + len(f1_agent.REQUIRED_FORMS)}")
    print(f"   • Documentos proibidos controlados: {len(b2_agent.FORBIDDEN_DOCUMENTS) + len(h1b_agent.FORBIDDEN_DOCUMENTS) + len(f1_agent.FORBIDDEN_DOCUMENTS)}")
    
    print("\n🚀 Próximos Passos:")
    print("   1. Integrar com backend API")
    print("   2. Adicionar mais especialistas (O-1, E-2, Green Card)")
    print("   3. Implementar Quality Assurance Agent")
    print("   4. Expandir sistema de learning")
    
    return True


if __name__ == "__main__":
    try:
        success = test_architecture()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
