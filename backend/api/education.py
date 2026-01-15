import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from backend.core.auth import get_current_user
from backend.core.database import db
from backend.models.education import (
    InterviewAnswer,
    InterviewSession,
    InterviewStart,
    KnowledgeBaseQuery,
    VisaGuide,
)
from backend.models.enums import DifficultyLevel, VisaType
from backend.models.user import UserProgress
from backend.services.education import (
    evaluate_interview_answer,
    generate_interview_questions,
    generate_personalized_tips,
    search_knowledge_base,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/education/guides")
async def get_visa_guides(
    visa_type: Optional[VisaType] = None, current_user=Depends(get_current_user)
):
    """Get available visa guides."""
    try:
        guides_data = {
            VisaType.h1b: {
                "title": "Guia Completo H1-B",
                "description": "Tudo sobre o visto de trabalho H1-B",
                "difficulty_level": "intermediate",
                "estimated_time_minutes": 45,
                "sections": [
                    {"title": "Requisitos Básicos", "content": "Lista de requisitos essenciais"},
                    {"title": "Processo de Aplicação", "content": "Passo a passo detalhado"},
                    {"title": "Documentos Necessários", "content": "Checklist completo"},
                    {"title": "Timeline", "content": "Cronograma típico"},
                    {"title": "Dicas de Sucesso", "content": "Conselhos práticos"},
                ],
                "requirements": [
                    "Oferta de emprego",
                    "Graduação superior",
                    "Especialização na área",
                ],
                "common_mistakes": ["Documentação incompleta", "Não demonstrar especialização"],
                "success_tips": ["Prepare documentação detalhada", "Demonstre expertise única"],
            },
            VisaType.f1: {
                "title": "Guia Completo F1",
                "description": "Visto de estudante para universidades americanas",
                "difficulty_level": "beginner",
                "estimated_time_minutes": 30,
                "sections": [
                    {"title": "Elegibilidade", "content": "Critérios de elegibilidade"},
                    {"title": "Escolha da Escola", "content": "Como escolher instituição"},
                    {"title": "Processo I-20", "content": "Obtenção do formulário I-20"},
                    {"title": "Entrevista Consular", "content": "Preparação para entrevista"},
                    {"title": "Vida nos EUA", "content": "Dicas para estudantes"},
                ],
                "requirements": [
                    "Aceitação em escola aprovada",
                    "Recursos financeiros",
                    "Intenção de retorno",
                ],
                "common_mistakes": [
                    "Demonstrar intenção imigratória",
                    "Recursos financeiros insuficientes",
                ],
                "success_tips": [
                    "Demonstre laços com país de origem",
                    "Tenha recursos financeiros claros",
                ],
            },
            VisaType.family: {
                "title": "Reunificação Familiar",
                "description": "Processos de imigração baseados em família",
                "difficulty_level": "intermediate",
                "estimated_time_minutes": 50,
                "sections": [
                    {"title": "Tipos de Petição", "content": "Diferentes categorias familiares"},
                    {"title": "Processo I-130", "content": "Petição para parente"},
                    {"title": "Documentos Familiares", "content": "Comprovação de relacionamento"},
                    {"title": "Prioridades", "content": "Sistema de prioridades"},
                    {"title": "Adjustment vs Consular", "content": "Diferentes caminhos"},
                ],
                "requirements": [
                    "Relacionamento qualificado",
                    "Documentos comprobatórios",
                    "Sponsor qualificado",
                ],
                "common_mistakes": [
                    "Documentos familiares inadequados",
                    "Não comprovar relacionamento genuíno",
                ],
                "success_tips": ["Documente bem o relacionamento", "Mantenha registros detalhados"],
            },
        }

        if visa_type:
            guide_data = guides_data.get(visa_type)
            if guide_data:
                guide = VisaGuide(visa_type=visa_type, **guide_data)
                return {"guide": guide.dict()}
            raise HTTPException(status_code=404, detail="Guide not found")

        all_guides = []
        for v_type, guide_data in guides_data.items():
            guide = VisaGuide(visa_type=v_type, **guide_data)
            all_guides.append(guide.dict())
        return {"guides": all_guides}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visa guides: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting guides: {str(e)}")


@router.post("/education/guides/{visa_type}/complete")
async def complete_guide(visa_type: VisaType, current_user=Depends(get_current_user)):
    """Mark a guide as completed."""
    try:
        await db.user_progress.update_one(
            {"user_id": current_user["id"]},
            {
                "$addToSet": {"guides_completed": visa_type.value},
                "$inc": {"total_study_time_minutes": 30},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
            upsert=True,
        )

        return {"message": f"Guide {visa_type.value} marked as completed"}

    except Exception as e:
        logger.error(f"Error completing guide: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error completing guide: {str(e)}")


@router.post("/education/interview/start")
async def start_interview_simulation(
    request: InterviewStart, current_user=Depends(get_current_user)
):
    """Start a new interview simulation."""
    try:
        questions = await generate_interview_questions(
            request.interview_type,
            request.visa_type,
            request.difficulty_level or DifficultyLevel.beginner,
        )

        session = InterviewSession(
            user_id=current_user["id"],
            interview_type=request.interview_type,
            visa_type=request.visa_type,
            questions=questions,
        )

        await db.interview_sessions.insert_one(session.dict())

        return {
            "session": {
                "session_id": session.id,
                "interview_type": session.interview_type,
                "visa_type": session.visa_type,
                "difficulty": request.difficulty_level or DifficultyLevel.beginner,
                "questions": questions,
                "current_question": 0,
                "created_at": session.created_at.isoformat(),
            },
            "total_questions": len(questions),
            "estimated_duration": len(questions) * 2,
        }

    except Exception as e:
        logger.error(f"Error starting interview simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")


@router.post("/education/interview/{session_id}/answer")
async def submit_interview_answer(
    session_id: str, answer_data: InterviewAnswer, current_user=Depends(get_current_user)
):
    """Submit an answer to interview question."""
    try:
        session = await db.interview_sessions.find_one(
            {"id": session_id, "user_id": current_user["id"]}
        )
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")

        question = next(
            (q for q in session["questions"] if q["id"] == answer_data.question_id), None
        )
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        feedback = await evaluate_interview_answer(
            question, answer_data.answer, VisaType(session["visa_type"])
        )

        answer_record = {
            "question_id": answer_data.question_id,
            "answer": answer_data.answer,
            "feedback": feedback,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await db.interview_sessions.update_one(
            {"id": session_id},
            {
                "$push": {"answers": answer_record},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )

        return {"feedback": feedback, "next_question_index": len(session.get("answers", [])) + 1}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting interview answer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")


@router.post("/education/interview/{session_id}/complete")
async def complete_interview_session(session_id: str, current_user=Depends(get_current_user)):
    """Complete interview session and get final feedback."""
    try:
        session = await db.interview_sessions.find_one(
            {"id": session_id, "user_id": current_user["id"]}
        )
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")

        answers = session.get("answers", [])
        if not answers:
            raise HTTPException(status_code=400, detail="No answers submitted")

        scores = [answer.get("feedback", {}).get("score", 0) for answer in answers]
        overall_score = sum(scores) // len(scores) if scores else 0

        overall_feedback = {
            "overall_score": overall_score,
            "questions_answered": len(answers),
            "average_confidence": "médio",
            "strengths": ["Respostas completas", "Boa preparação"],
            "areas_for_improvement": ["Desenvolver mais detalhes", "Praticar mais"],
            "recommendations": [
                "Continue praticando com diferentes cenários",
                "Revise os guias interativos relacionados",
                "Considere praticar com diferentes níveis de dificuldade",
            ],
        }

        await db.interview_sessions.update_one(
            {"id": session_id},
            {
                "$set": {
                    "completed": True,
                    "score": overall_score,
                    "ai_feedback": overall_feedback,
                    "duration_minutes": 15,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        await db.user_progress.update_one(
            {"user_id": current_user["id"]},
            {
                "$addToSet": {"interviews_completed": session_id},
                "$inc": {"total_study_time_minutes": 15},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
            upsert=True,
        )

        return {"overall_feedback": overall_feedback, "session_completed": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing interview session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error completing interview: {str(e)}")


@router.get("/education/tips")
async def get_personalized_tips(current_user=Depends(get_current_user)):
    """Get personalized tips for user."""
    try:
        existing_tips = (
            await db.personalized_tips.find({"user_id": current_user["id"]}, {"_id": 0})
            .sort("created_at", -1)
            .limit(10)
            .to_list(10)
        )

        if not existing_tips:
            applications = await db.applications.find(
                {"user_id": current_user["id"]}, {"_id": 0}
            ).to_list(100)
            documents = await db.documents.find(
                {"user_id": current_user["id"]}, {"_id": 0, "content_base64": 0}
            ).to_list(100)

            tips = await generate_personalized_tips(
                current_user["id"], current_user, applications, documents
            )

            for tip in tips:
                await db.personalized_tips.insert_one(tip.dict())

            existing_tips = [tip.dict() for tip in tips]

        return {"tips": existing_tips}

    except Exception as e:
        logger.error(f"Error getting personalized tips: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting tips: {str(e)}")


@router.post("/education/tips/{tip_id}/read")
async def mark_tip_as_read(tip_id: str, current_user=Depends(get_current_user)):
    """Mark a tip as read."""
    try:
        await db.personalized_tips.update_one(
            {"id": tip_id, "user_id": current_user["id"]}, {"$set": {"is_read": True}}
        )
        return {"message": "Tip marked as read"}

    except Exception as e:
        logger.error(f"Error marking tip as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking tip as read: {str(e)}")


@router.post("/education/knowledge-base/search")
async def search_knowledge(query_data: KnowledgeBaseQuery, current_user=Depends(get_current_user)):
    """Search the knowledge base."""
    try:
        result = await search_knowledge_base(query_data.query, query_data.visa_type)

        await db.user_progress.update_one(
            {"user_id": current_user["id"]},
            {"$inc": {"knowledge_queries": 1}, "$set": {"updated_at": datetime.now(timezone.utc)}},
            upsert=True,
        )

        search_log = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "query": query_data.query,
            "visa_type": query_data.visa_type.value if query_data.visa_type else None,
            "category": query_data.category,
            "timestamp": datetime.now(timezone.utc),
        }
        await db.knowledge_searches.insert_one(search_log)

        return result

    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching knowledge base: {str(e)}")


@router.get("/education/progress")
async def get_user_progress(current_user=Depends(get_current_user)):
    """Get user's education progress."""
    try:
        progress = await db.user_progress.find_one({"user_id": current_user["id"]}, {"_id": 0})

        if not progress:
            progress = UserProgress(user_id=current_user["id"])
            await db.user_progress.insert_one(progress.dict())
            progress = progress.dict()

        total_interviews = await db.interview_sessions.count_documents(
            {"user_id": current_user["id"], "completed": True}
        )
        recent_tips = await db.personalized_tips.count_documents(
            {"user_id": current_user["id"], "is_read": False}
        )

        progress["total_completed_interviews"] = total_interviews
        progress["unread_tips_count"] = recent_tips

        return {"progress": progress}

    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting progress: {str(e)}")
