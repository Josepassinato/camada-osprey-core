import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import openai

from models.education import PersonalizedTip
from models.enums import DifficultyLevel, VisaType, InterviewType

logger = logging.getLogger(__name__)


async def generate_interview_questions(
    interview_type: InterviewType,
    visa_type: VisaType,
    difficulty_level: DifficultyLevel,
) -> List[Dict[str, Any]]:
    """Generate interview questions using sistema."""
    try:
        difficulty_map = {
            DifficultyLevel.beginner: "perguntas básicas e introdutórias",
            DifficultyLevel.intermediate: "perguntas moderadas com alguns detalhes",
            DifficultyLevel.advanced: "perguntas complexas e cenários desafiadores",
        }

        prompt = f"""
        Gere 10 perguntas de entrevista para imigração americana:
        
        Tipo de entrevista: {interview_type.value}
        Tipo de visto: {visa_type.value}
        Nível: {difficulty_map[difficulty_level]}
        
        Para cada pergunta, forneça:
        - A pergunta em inglês (como seria feita pelo oficial)
        - Tradução em português
        - Dicas de como responder
        - Pontos importantes a mencionar
        
        Retorne APENAS um JSON array:
        [
            {{
                "id": "q1",
                "question_en": "pergunta em inglês",
                "question_pt": "pergunta em português", 
                "category": "categoria",
                "difficulty": "{difficulty_level.value}",
                "tips": ["dica1", "dica2"],
                "key_points": ["ponto1", "ponto2"]
            }}
        ]
        
        IMPORTANTE: Estas são perguntas educativas para preparação. Para casos reais, recomende consultoria jurídica.
        """

        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not configured")

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em entrevistas de imigração. Responda APENAS em JSON válido.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.3,
        )

        questions_text = response.choices[0].message.content.strip()
        questions_text = questions_text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(questions_text)
        except json.JSONDecodeError:
            return [
                {
                    "id": "q1",
                    "question_en": "What is the purpose of your visit to the United States?",
                    "question_pt": "Qual é o propósito da sua visita aos Estados Unidos?",
                    "category": "purpose",
                    "difficulty": difficulty_level.value,
                    "tips": ["Seja claro e direto", "Mencione detalhes específicos"],
                    "key_points": ["Propósito específico", "Duração planejada"],
                }
            ]

    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        return []


async def evaluate_interview_answer(
    question: Dict[str, Any],
    answer: str,
    visa_type: VisaType,
) -> Dict[str, Any]:
    """Evaluate interview answer using sistema."""
    try:
        prompt = f"""
        Avalie esta resposta de entrevista de imigração:

        Pergunta: {question.get('question_pt')}
        Resposta do usuário: {answer}
        Tipo de visto: {visa_type.value}
        
        Forneça feedback APENAS em JSON:
        {{
            "score": [0-100],
            "strengths": ["ponto forte 1", "ponto forte 2"],
            "weaknesses": ["ponto fraco 1", "ponto fraco 2"],
            "suggestions": ["sugestão 1", "sugestão 2"],
            "improved_answer": "exemplo de resposta melhorada",
            "confidence_level": "baixo|médio|alto"
        }}
        
        IMPORTANTE: Esta é uma ferramenta educativa. Para preparação real, recomende consultoria jurídica.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em avaliação de entrevistas de imigração. Responda APENAS em JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.3,
        )

        feedback_text = response.choices[0].message.content.strip()
        feedback_text = feedback_text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(feedback_text)
        except json.JSONDecodeError:
            return {
                "score": 70,
                "strengths": ["Resposta fornecida"],
                "weaknesses": ["Análise automática não disponível"],
                "suggestions": ["Revise sua resposta"],
                "improved_answer": "Desenvolva mais detalhes na sua resposta",
                "confidence_level": "médio",
            }

    except Exception as e:
        logger.error(f"Error evaluating interview answer: {str(e)}")
        return {
            "score": 50,
            "strengths": ["Tentativa de resposta"],
            "weaknesses": ["Análise não disponível"],
            "suggestions": ["Tente novamente"],
            "improved_answer": "Resposta mais detalhada seria ideal",
            "confidence_level": "baixo",
        }


async def generate_personalized_tips(
    user_id: str,
    user_profile: dict,
    applications: List[dict],
    documents: List[dict],
) -> List[PersonalizedTip]:
    """Generate personalized tips based on user profile and progress."""
    tips: List[PersonalizedTip] = []

    try:
        active_applications = [
            app for app in applications if app.get("status") in ["in_progress", "document_review"]
        ]
        pending_docs = [doc for doc in documents if doc.get("status") == "pending_review"]
        expiring_docs = [
            doc
            for doc in documents
            if doc.get("expiration_date")
            and (datetime.fromisoformat(doc["expiration_date"].replace("Z", "+00:00")) - datetime.now(timezone.utc)).days <= 30
        ]

        user_context = f"""
        Usuário: {user_profile.get('first_name', '')} {user_profile.get('last_name', '')}
        País de nascimento: {user_profile.get('country_of_birth', 'Não informado')}
        Aplicações ativas: {len(active_applications)}
        Documentos pendentes: {len(pending_docs)}
        Documentos expirando: {len(expiring_docs)}
        
        Gere 5 dicas personalizadas para este usuário em formato JSON:
        [
            {{
                "category": "document|application|interview|preparation",
                "title": "Título da dica",
                "content": "Conteúdo detalhado da dica",
                "priority": "high|medium|low"
            }}
        ]
        """

        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not configured")

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um consultor educativo de imigração. Forneça dicas práticas em português. Sempre mencione que não oferece consultoria jurídica.",
                },
                {"role": "user", "content": user_context},
            ],
            max_tokens=1500,
            temperature=0.7,
        )

        tips_text = response.choices[0].message.content.strip()
        tips_text = tips_text.replace("```json", "").replace("```", "").strip()

        try:
            tips_data = json.loads(tips_text)
            for tip_data in tips_data:
                tip = PersonalizedTip(
                    user_id=user_id,
                    tip_category=tip_data.get("category", "general"),
                    title=tip_data.get("title", ""),
                    content=tip_data.get("content", ""),
                    priority=tip_data.get("priority", "medium"),
                )
                tips.append(tip)
        except json.JSONDecodeError:
            pass

    except Exception as e:
        logger.warning(f"Error generating personalized tips (fallback to defaults): {str(e)}")

    if not tips:
        tips.append(
            PersonalizedTip(
                user_id=user_id,
                tip_category="preparation",
                title="Organize seus documentos",
                content="Mantenha todos os seus documentos organizados e atualizados para facilitar o processo de aplicação.",
                priority="high",
            )
        )

    return tips


async def search_knowledge_base(
    query: str,
    visa_type: Optional[VisaType] = None,
) -> Dict[str, Any]:
    """Search knowledge base using sistema."""
    try:
        context_filter = f"para visto {visa_type.value}" if visa_type else "para imigração americana"

        prompt = f"""
        Responda esta pergunta sobre imigração americana {context_filter}:
        
        Pergunta: {query}
        
        Forneça uma resposta educativa e informativa em JSON:
        {{
            "answer": "resposta detalhada e precisa",
            "related_topics": ["tópico1", "tópico2", "tópico3"],
            "next_steps": ["passo1", "passo2"],
            "resources": ["recurso1", "recurso2"],
            "warnings": ["aviso importante se aplicável"],
            "confidence": "alto|médio|baixo"
        }}
        
        IMPORTANTE: 
        - Esta é informação educativa para auto-aplicação
        - Sempre mencione que não substitui consultoria jurídica
        - Para casos complexos, recomende consultar um advogado
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é uma base de conhecimento educativa sobre imigração americana. Forneça informações precisas em português, sempre com disclaimers sobre consultoria jurídica.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.3,
        )

        result_text = response.choices[0].message.content.strip()
        result_text = result_text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {
                "answer": "Desculpe, não foi possível processar sua pergunta no momento. Tente reformulá-la ou consulte nossa seção de guias interativos.",
                "related_topics": ["Guias de Visto", "Simulador de Entrevista", "Gestão de Documentos"],
                "next_steps": ["Explore os guias interativos", "Use o simulador de entrevista"],
                "resources": ["Centro de Ajuda", "Chat com sistema"],
                "warnings": ["Esta é uma ferramenta educativa - não substitui consultoria jurídica"],
                "confidence": "baixo",
            }

    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        return {
            "answer": "Erro ao processar consulta. Tente novamente.",
            "related_topics": [],
            "next_steps": [],
            "resources": [],
            "warnings": ["Sistema temporariamente indisponível"],
            "confidence": "baixo",
        }
