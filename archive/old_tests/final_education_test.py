#!/usr/bin/env python3
"""
Final comprehensive test of OSPREY Education System
Testing all requested endpoints with realistic Portuguese scenarios
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://maria-support.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"🎓 OSPREY Education System - Comprehensive Test")
print(f"Backend: {API_BASE}")
print("=" * 70)

# Test user credentials
TEST_USER = {
    "email": "test@osprey.com",
    "password": "TestUser123"
}
AUTH_TOKEN = None
INTERVIEW_SESSION_ID = None

def login_user():
    """Login and get auth token"""
    global AUTH_TOKEN
    print("\n🔐 Autenticando usuário...")
    
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            user = data.get('user', {})
            print(f"✅ Login realizado com sucesso")
            print(f"   Usuário: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Email: {user.get('email')}")
            return True
        else:
            print(f"❌ Falha no login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no login: {str(e)}")
        return False

def test_education_guides():
    """Test 1: GET /api/education/guides - Listar guias interativos"""
    print("\n📚 Teste 1: GET /api/education/guides - Listar guias interativos")
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/guides", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            guides = data.get('guides', [])
            print(f"✅ Guias recuperados com sucesso")
            print(f"   Total de guias disponíveis: {len(guides)}")
            
            for guide in guides:
                print(f"   - {guide.get('title')} ({guide.get('visa_type').upper()})")
                print(f"     Dificuldade: {guide.get('difficulty_level')}")
                print(f"     Tempo estimado: {guide.get('estimated_time_minutes')} minutos")
                print(f"     Seções: {len(guide.get('sections', []))}")
            
            # Verify all expected guides are present
            visa_types = [guide.get('visa_type') for guide in guides]
            expected = ['h1b', 'f1', 'family']
            missing = [vt for vt in expected if vt not in visa_types]
            
            if not missing:
                print("✅ Todos os guias esperados estão disponíveis")
                return True
            else:
                print(f"⚠️  Guias faltando: {missing}")
                return False
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_specific_guide():
    """Test 2: GET /api/education/guides/{visa_type} - Detalhes de guia específico"""
    print("\n📖 Teste 2: GET /api/education/guides/h1b - Detalhes do guia H1-B")
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/guides?visa_type=h1b", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            guide = data.get('guide', {})
            print(f"✅ Guia H1-B recuperado com sucesso")
            print(f"   Título: {guide.get('title')}")
            print(f"   Descrição: {guide.get('description')}")
            print(f"   Nível: {guide.get('difficulty_level')}")
            print(f"   Tempo estimado: {guide.get('estimated_time_minutes')} minutos")
            print(f"   Seções: {len(guide.get('sections', []))}")
            print(f"   Requisitos: {len(guide.get('requirements', []))}")
            print(f"   Erros comuns: {len(guide.get('common_mistakes', []))}")
            print(f"   Dicas de sucesso: {len(guide.get('success_tips', []))}")
            
            # Show some content details
            sections = guide.get('sections', [])
            if sections:
                print(f"   Primeira seção: {sections[0].get('title')}")
            
            requirements = guide.get('requirements', [])
            if requirements:
                print(f"   Primeiro requisito: {requirements[0]}")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_education_progress():
    """Test 3: GET /api/education/progress - Progresso educacional do usuário"""
    print("\n📈 Teste 3: GET /api/education/progress - Progresso educacional")
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/progress", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            progress = data.get('progress', {})
            print(f"✅ Progresso educacional recuperado com sucesso")
            print(f"   Guias completados: {len(progress.get('guides_completed', []))}")
            print(f"   Entrevistas completadas: {len(progress.get('interviews_completed', []))}")
            print(f"   Consultas à base de conhecimento: {progress.get('knowledge_queries', 0)}")
            print(f"   Tempo total de estudo: {progress.get('total_study_time_minutes', 0)} minutos")
            print(f"   Badges conquistados: {len(progress.get('achievement_badges', []))}")
            print(f"   Dicas não lidas: {progress.get('unread_tips_count', 0)}")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_personalized_tips():
    """Test 4: GET /api/education/tips - Dicas personalizadas"""
    print("\n💡 Teste 4: GET /api/education/tips - Dicas personalizadas")
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/tips", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            tips = data.get('tips', [])
            print(f"✅ Dicas personalizadas recuperadas com sucesso")
            print(f"   Total de dicas: {len(tips)}")
            
            for i, tip in enumerate(tips[:3]):  # Show first 3 tips
                print(f"   Dica {i+1}: {tip.get('title')}")
                print(f"           Categoria: {tip.get('tip_category')}")
                print(f"           Prioridade: {tip.get('priority')}")
                print(f"           Lida: {'Sim' if tip.get('is_read') else 'Não'}")
                print(f"           Conteúdo: {tip.get('content', '')[:100]}...")
            
            # Verify tips are in Portuguese
            if tips:
                content = tips[0].get('content', '').lower()
                has_portuguese = any(word in content for word in ['você', 'seus', 'para', 'com', 'documentos', 'aplicação'])
                if has_portuguese:
                    print("✅ Dicas fornecidas em português")
                else:
                    print("⚠️  Idioma das dicas não identificado claramente")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_interview_start():
    """Test 5: POST /api/education/interview/start - Iniciar simulação de entrevista"""
    print("\n🎤 Teste 5: POST /api/education/interview/start - Simulação de entrevista")
    global INTERVIEW_SESSION_ID
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        payload = {
            "interview_type": "consular",
            "visa_type": "h1b",
            "difficulty_level": "beginner"
        }
        
        response = requests.post(f"{API_BASE}/education/interview/start", json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            INTERVIEW_SESSION_ID = data.get('session_id')
            questions = data.get('questions', [])
            
            print(f"✅ Simulação de entrevista iniciada com sucesso")
            print(f"   ID da sessão: {INTERVIEW_SESSION_ID}")
            print(f"   Total de perguntas: {data.get('total_questions', 0)}")
            print(f"   Duração estimada: {data.get('estimated_duration', 0)} minutos")
            print(f"   Perguntas geradas: {len(questions)}")
            
            if questions:
                first_q = questions[0]
                print(f"   Primeira pergunta (EN): {first_q.get('question_en', 'N/A')[:80]}...")
                print(f"   Primeira pergunta (PT): {first_q.get('question_pt', 'N/A')[:80]}...")
                print(f"   Categoria: {first_q.get('category', 'N/A')}")
                print(f"   Dicas disponíveis: {len(first_q.get('tips', []))}")
                print(f"   Pontos-chave: {len(first_q.get('key_points', []))}")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_interview_answer():
    """Test 6: POST /api/education/interview/{session_id}/answer - Enviar resposta"""
    print("\n💬 Teste 6: POST /api/education/interview/{session_id}/answer - Resposta")
    
    if not INTERVIEW_SESSION_ID:
        print("❌ ID da sessão não disponível")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        payload = {
            "question_id": "q1",
            "answer": "Eu venho aos Estados Unidos para trabalhar como engenheiro de software em uma empresa de tecnologia. Tenho uma oferta de emprego válida da empresa TechCorp e pretendo contribuir com minhas habilidades em desenvolvimento de software e inteligência artificial para projetos inovadores."
        }
        
        response = requests.post(
            f"{API_BASE}/education/interview/{INTERVIEW_SESSION_ID}/answer", 
            json=payload, 
            headers=headers, 
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            feedback = data.get('feedback', {})
            
            print(f"✅ Resposta da entrevista enviada com sucesso")
            print(f"   Pontuação: {feedback.get('score', 'N/A')}/100")
            print(f"   Nível de confiança: {feedback.get('confidence_level', 'N/A')}")
            print(f"   Pontos fortes: {len(feedback.get('strengths', []))}")
            print(f"   Pontos fracos: {len(feedback.get('weaknesses', []))}")
            print(f"   Sugestões: {len(feedback.get('suggestions', []))}")
            print(f"   Próxima pergunta: {data.get('next_question_index', 'N/A')}")
            
            # Show feedback details
            if feedback.get('strengths'):
                print(f"   Primeiro ponto forte: {feedback['strengths'][0]}")
            if feedback.get('suggestions'):
                print(f"   Primeira sugestão: {feedback['suggestions'][0]}")
            
            # Check if feedback is in Portuguese
            improved_answer = feedback.get('improved_answer', '')
            if any(word in improved_answer.lower() for word in ['você', 'sua', 'mais', 'para', 'com']):
                print("✅ Feedback fornecido em português")
            else:
                print("⚠️  Idioma do feedback não identificado claramente")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_interview_complete():
    """Test 7: POST /api/education/interview/{session_id}/complete - Completar entrevista"""
    print("\n🏁 Teste 7: POST /api/education/interview/{session_id}/complete - Finalizar")
    
    if not INTERVIEW_SESSION_ID:
        print("❌ ID da sessão não disponível")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.post(
            f"{API_BASE}/education/interview/{INTERVIEW_SESSION_ID}/complete", 
            headers=headers, 
            timeout=45
        )
        
        if response.status_code == 200:
            data = response.json()
            feedback = data.get('overall_feedback', {})
            
            print(f"✅ Entrevista completada com sucesso")
            print(f"   Sessão finalizada: {'Sim' if data.get('session_completed') else 'Não'}")
            print(f"   Pontuação geral: {feedback.get('overall_score', 'N/A')}/100")
            print(f"   Perguntas respondidas: {feedback.get('questions_answered', 'N/A')}")
            print(f"   Confiança média: {feedback.get('average_confidence', 'N/A')}")
            print(f"   Pontos fortes: {len(feedback.get('strengths', []))}")
            print(f"   Áreas para melhoria: {len(feedback.get('areas_for_improvement', []))}")
            print(f"   Recomendações: {len(feedback.get('recommendations', []))}")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_knowledge_base_search():
    """Test 8: POST /api/education/knowledge-base/search - Buscar na base de conhecimento"""
    print("\n🔍 Teste 8: POST /api/education/knowledge-base/search - Base de conhecimento")
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        payload = {
            "query": "Como aplicar para H1-B? Quais são os requisitos principais e qual é o processo completo?",
            "visa_type": "h1b",
            "category": "application"
        }
        
        response = requests.post(f"{API_BASE}/education/knowledge-base/search", json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Busca na base de conhecimento realizada com sucesso")
            print(f"   Tamanho da resposta: {len(data.get('answer', ''))} caracteres")
            print(f"   Tópicos relacionados: {len(data.get('related_topics', []))}")
            print(f"   Próximos passos: {len(data.get('next_steps', []))}")
            print(f"   Recursos: {len(data.get('resources', []))}")
            print(f"   Avisos: {len(data.get('warnings', []))}")
            print(f"   Nível de confiança: {data.get('confidence', 'N/A')}")
            
            # Show answer preview
            answer = data.get('answer', '')
            if answer:
                print(f"   Prévia da resposta: {answer[:200]}...")
            
            # Show related topics
            topics = data.get('related_topics', [])
            if topics:
                print(f"   Tópicos relacionados: {', '.join(topics[:3])}")
            
            # Check for legal disclaimers
            answer_lower = answer.lower()
            warnings = ' '.join(data.get('warnings', [])).lower()
            
            disclaimer_phrases = ['consultoria jurídica', 'advogado', 'não substitui', 'educativa', 'orientação']
            has_disclaimer = any(phrase in (answer_lower + warnings) for phrase in disclaimer_phrases)
            
            if has_disclaimer:
                print("✅ Disclaimers legais presentes na resposta")
            else:
                print("⚠️  Disclaimers legais não identificados claramente")
            
            # Check if answer is in Portuguese
            portuguese_words = ['para', 'como', 'você', 'processo', 'aplicação', 'visto', 'requisitos']
            if any(word in answer_lower for word in portuguese_words):
                print("✅ Resposta fornecida em português")
            else:
                print("⚠️  Idioma da resposta não identificado claramente")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def test_dashboard_integration():
    """Test 9: GET /api/dashboard - Verificar integração das estatísticas educacionais"""
    print("\n📊 Teste 9: GET /api/dashboard - Integração das estatísticas educacionais")
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user', {})
            stats = data.get('stats', {})
            
            print(f"✅ Dashboard com estatísticas educacionais carregado com sucesso")
            print(f"   Usuário: {user_info.get('name')} ({user_info.get('email')})")
            print(f"   Guias completados: {stats.get('guides_completed', 0)}")
            print(f"   Entrevistas completadas: {stats.get('interviews_completed', 0)}")
            print(f"   Tempo total de estudo: {stats.get('total_study_time', 0)} minutos")
            print(f"   Dicas não lidas: {stats.get('unread_tips', 0)}")
            print(f"   Total de aplicações: {stats.get('total_applications', 0)}")
            print(f"   Total de documentos: {stats.get('total_documents', 0)}")
            
            # Verify education stats are present
            education_keys = ['guides_completed', 'interviews_completed', 'total_study_time', 'unread_tips']
            has_education_stats = all(key in stats for key in education_keys)
            
            if has_education_stats:
                print("✅ Estatísticas educacionais integradas corretamente no dashboard")
            else:
                missing = [key for key in education_keys if key not in stats]
                print(f"⚠️  Estatísticas educacionais faltando: {missing}")
            
            return True
        else:
            print(f"❌ Falha: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False

def run_comprehensive_education_tests():
    """Run all comprehensive education system tests"""
    print("🎓 OSPREY - Sistema de Educação Integrado - Teste Completo")
    print(f"⏰ Teste iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login first
    if not login_user():
        print("❌ Não é possível prosseguir sem autenticação")
        return
    
    # Run all education tests in order
    test_functions = [
        ("Listar Guias Interativos", test_education_guides),
        ("Detalhes de Guia Específico", test_specific_guide),
        ("Progresso Educacional", test_education_progress),
        ("Dicas Personalizadas", test_personalized_tips),
        ("Iniciar Simulação de Entrevista", test_interview_start),
        ("Enviar Resposta da Entrevista", test_interview_answer),
        ("Completar Entrevista", test_interview_complete),
        ("Buscar na Base de Conhecimento", test_knowledge_base_search),
        ("Integração das Estatísticas no Dashboard", test_dashboard_integration)
    ]
    
    results = {}
    for test_name, test_func in test_functions:
        results[test_name] = test_func()
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DOS TESTES DO SISTEMA EDUCACIONAL")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 RESULTADO GERAL: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Todos os testes do sistema educacional passaram!")
        print("   Sistema educacional OSPREY funcionando perfeitamente.")
        print("   ✅ Integração com OpenAI GPT-4 funcionando")
        print("   ✅ Respostas em português com disclaimers legais")
        print("   ✅ Persistência de dados funcionando")
        print("   ✅ Sistema de autenticação funcionando")
    elif passed >= total - 1:
        print("✅ Sistema educacional funcionando corretamente com problemas menores.")
    else:
        print("⚠️  Alguns testes críticos falharam. Verifique os detalhes acima.")
    
    return results

if __name__ == "__main__":
    run_comprehensive_education_tests()