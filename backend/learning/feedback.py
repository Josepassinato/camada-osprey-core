"""
Feedback System
Sistema completo de coleta e análise de feedback dos usuários
Suporta thumbs up/down, ratings 1-5, e comentários
"""

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Tipos de feedback"""
    AI_RESPONSE = "ai_response"  # Feedback em resposta da IA
    FORM_USABILITY = "form_usability"  # Usabilidade do formulário
    DOCUMENT_UPLOAD = "document_upload"  # Processo de upload
    PDF_GENERATION = "pdf_generation"  # Geração de PDF
    GENERAL_EXPERIENCE = "general_experience"  # Experiência geral


class FeedbackRating(str, Enum):
    """Ratings possíveis"""
    VERY_POOR = "very_poor"  # 1 estrela
    POOR = "poor"  # 2 estrelas
    AVERAGE = "average"  # 3 estrelas
    GOOD = "good"  # 4 estrelas
    EXCELLENT = "excellent"  # 5 estrelas


class FeedbackSystem:
    """Sistema de gerenciamento de feedback"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.feedback
        
    async def submit_feedback(
        self,
        user_id: str,
        feedback_type: FeedbackType,
        rating: Optional[int] = None,  # 1-5
        thumbs: Optional[str] = None,  # "up" or "down"
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submeter feedback do usuário
        
        Args:
            user_id: ID do usuário
            feedback_type: Tipo de feedback
            rating: Rating 1-5 estrelas (opcional)
            thumbs: "up" ou "down" (opcional)
            comment: Comentário texto livre (opcional)
            metadata: Dados adicionais (ex: response_id, case_id)
        
        Returns:
            {
                "success": bool,
                "feedback_id": str,
                "message": str
            }
        """
        try:
            # Validar rating
            if rating is not None and (rating < 1 or rating > 5):
                return {
                    "success": False,
                    "error": "Rating must be between 1 and 5"
                }
            
            # Validar thumbs
            if thumbs is not None and thumbs not in ["up", "down"]:
                return {
                    "success": False,
                    "error": "Thumbs must be 'up' or 'down'"
                }
            
            # Criar documento de feedback
            feedback_doc = {
                "user_id": user_id,
                "type": feedback_type.value if isinstance(feedback_type, FeedbackType) else feedback_type,
                "rating": rating,
                "thumbs": thumbs,
                "comment": comment,
                "metadata": metadata or {},
                "timestamp": datetime.now(timezone.utc),
                "processed": False
            }
            
            # Inserir no banco
            result = await self.collection.insert_one(feedback_doc)
            feedback_id = str(result.inserted_id)
            
            logger.info(f"✅ Feedback submitted: type={feedback_type}, rating={rating}, thumbs={thumbs}")
            
            return {
                "success": True,
                "feedback_id": feedback_id,
                "message": "Feedback submitted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_feedback_stats(
        self,
        feedback_type: Optional[FeedbackType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obter estatísticas de feedback
        
        Returns:
            {
                "total_feedback": int,
                "thumbs_up": int,
                "thumbs_down": int,
                "thumbs_up_rate": float,
                "average_rating": float,
                "rating_distribution": {1: count, 2: count, ...},
                "feedback_by_type": {...}
            }
        """
        try:
            # Construir query
            query = {}
            if feedback_type:
                query["type"] = feedback_type.value
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            
            # Buscar todos os feedbacks
            feedbacks = await self.collection.find(query).to_list(length=None)
            
            if not feedbacks:
                return {
                    "total_feedback": 0,
                    "message": "No feedback data available"
                }
            
            # Calcular estatísticas
            total = len(feedbacks)
            thumbs_up = sum(1 for f in feedbacks if f.get("thumbs") == "up")
            thumbs_down = sum(1 for f in feedbacks if f.get("thumbs") == "down")
            
            # Ratings
            ratings = [f.get("rating") for f in feedbacks if f.get("rating")]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Distribuição de ratings
            rating_dist = {i: 0 for i in range(1, 6)}
            for r in ratings:
                if r in rating_dist:
                    rating_dist[r] += 1
            
            # Feedback por tipo
            by_type = {}
            for f in feedbacks:
                t = f.get("type", "unknown")
                by_type[t] = by_type.get(t, 0) + 1
            
            # Sentimento geral (baseado em thumbs + ratings)
            positive = thumbs_up + sum(1 for r in ratings if r >= 4)
            negative = thumbs_down + sum(1 for r in ratings if r <= 2)
            sentiment = "positive" if positive > negative else "negative" if negative > positive else "neutral"
            
            return {
                "total_feedback": total,
                "thumbs_up": thumbs_up,
                "thumbs_down": thumbs_down,
                "thumbs_up_rate": (thumbs_up / (thumbs_up + thumbs_down)) if (thumbs_up + thumbs_down) > 0 else 0,
                "average_rating": round(avg_rating, 2),
                "rating_distribution": rating_dist,
                "feedback_by_type": by_type,
                "sentiment": sentiment,
                "positive_count": positive,
                "negative_count": negative
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback stats: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_low_rated_items(
        self,
        feedback_type: Optional[FeedbackType] = None,
        threshold: int = 2,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Obter itens com baixa avaliação para análise
        
        Args:
            feedback_type: Filtrar por tipo
            threshold: Rating máximo para considerar "baixo" (default: 2)
            limit: Máximo de resultados
        
        Returns:
            Lista de feedbacks com baixa avaliação
        """
        try:
            query = {
                "$or": [
                    {"rating": {"$lte": threshold}},
                    {"thumbs": "down"}
                ]
            }
            
            if feedback_type:
                query["type"] = feedback_type.value
            
            feedbacks = await self.collection.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            # Formatar resultados
            results = []
            for f in feedbacks:
                results.append({
                    "feedback_id": str(f["_id"]),
                    "type": f.get("type"),
                    "rating": f.get("rating"),
                    "thumbs": f.get("thumbs"),
                    "comment": f.get("comment"),
                    "metadata": f.get("metadata", {}),
                    "timestamp": f.get("timestamp").isoformat() if f.get("timestamp") else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting low rated items: {str(e)}")
            return []
    
    async def get_user_feedback_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obter histórico de feedback de um usuário"""
        try:
            feedbacks = await self.collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit).to_list(length=limit)
            
            return [
                {
                    "feedback_id": str(f["_id"]),
                    "type": f.get("type"),
                    "rating": f.get("rating"),
                    "thumbs": f.get("thumbs"),
                    "comment": f.get("comment"),
                    "timestamp": f.get("timestamp").isoformat() if f.get("timestamp") else None
                }
                for f in feedbacks
            ]
            
        except Exception as e:
            logger.error(f"Error getting user feedback history: {str(e)}")
            return []
    
    async def mark_feedback_processed(self, feedback_id: str) -> bool:
        """Marcar feedback como processado"""
        try:
            from bson import ObjectId
            result = await self.collection.update_one(
                {"_id": ObjectId(feedback_id)},
                {"$set": {"processed": True, "processed_at": datetime.now(timezone.utc)}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error marking feedback as processed: {str(e)}")
            return False
    
    async def get_trending_issues(
        self,
        days: int = 7,
        min_occurrences: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identificar problemas recorrentes baseado em feedback negativo
        
        Args:
            days: Número de dias para analisar
            min_occurrences: Mínimo de ocorrências para considerar "trending"
        
        Returns:
            Lista de issues identificados
        """
        try:
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Buscar feedback negativo recente
            query = {
                "timestamp": {"$gte": start_date},
                "$or": [
                    {"rating": {"$lte": 2}},
                    {"thumbs": "down"}
                ],
                "comment": {"$exists": True, "$ne": ""}
            }
            
            feedbacks = await self.collection.find(query).to_list(length=None)
            
            if not feedbacks:
                return []
            
            # Agrupar por tipo e contar
            issues = {}
            for f in feedbacks:
                f_type = f.get("type", "unknown")
                if f_type not in issues:
                    issues[f_type] = {
                        "type": f_type,
                        "count": 0,
                        "comments": []
                    }
                issues[f_type]["count"] += 1
                if f.get("comment"):
                    issues[f_type]["comments"].append(f["comment"])
            
            # Filtrar por min_occurrences e ordenar
            trending = [
                {
                    "type": issue["type"],
                    "count": issue["count"],
                    "severity": "high" if issue["count"] >= min_occurrences * 2 else "medium",
                    "sample_comments": issue["comments"][:5]
                }
                for issue in issues.values()
                if issue["count"] >= min_occurrences
            ]
            
            trending.sort(key=lambda x: x["count"], reverse=True)
            
            return trending
            
        except Exception as e:
            logger.error(f"Error getting trending issues: {str(e)}")
            return []


# Helper functions for quick access
async def submit_ai_response_feedback(
    db,
    user_id: str,
    response_id: str,
    thumbs: str,
    rating: Optional[int] = None,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """Helper para feedback de resposta da IA"""
    system = FeedbackSystem(db)
    return await system.submit_feedback(
        user_id=user_id,
        feedback_type=FeedbackType.AI_RESPONSE,
        rating=rating,
        thumbs=thumbs,
        comment=comment,
        metadata={"response_id": response_id}
    )


async def submit_form_feedback(
    db,
    user_id: str,
    case_id: str,
    rating: int,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """Helper para feedback de formulário"""
    system = FeedbackSystem(db)
    return await system.submit_feedback(
        user_id=user_id,
        feedback_type=FeedbackType.FORM_USABILITY,
        rating=rating,
        comment=comment,
        metadata={"case_id": case_id}
    )


async def get_nps_score(db, days: int = 30) -> Dict[str, Any]:
    """
    Calcular Net Promoter Score (NPS)
    NPS = % Promoters (9-10) - % Detractors (0-6)
    Convertido para escala 1-5: Promoters (5), Passives (3-4), Detractors (1-2)
    """
    try:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        system = FeedbackSystem(db)
        
        feedbacks = await system.collection.find({
            "type": FeedbackType.GENERAL_EXPERIENCE.value,
            "rating": {"$exists": True},
            "timestamp": {"$gte": start_date}
        }).to_list(length=None)
        
        if not feedbacks:
            return {"nps": 0, "message": "No data available"}
        
        total = len(feedbacks)
        promoters = sum(1 for f in feedbacks if f.get("rating") == 5)
        detractors = sum(1 for f in feedbacks if f.get("rating") in [1, 2])
        passives = total - promoters - detractors
        
        nps = ((promoters - detractors) / total) * 100
        
        return {
            "nps": round(nps, 1),
            "promoters": promoters,
            "passives": passives,
            "detractors": detractors,
            "total_responses": total,
            "promoter_rate": round((promoters / total) * 100, 1),
            "detractor_rate": round((detractors / total) * 100, 1)
        }
        
    except Exception as e:
        logger.error(f"Error calculating NPS: {str(e)}")
        return {"nps": 0, "error": str(e)}
