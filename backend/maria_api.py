"""
Maria API Endpoints
Endpoints para chat com a assistente virtual Maria
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from maria_agent import maria
from maria_whatsapp import maria_whatsapp
from maria_voice import maria_voice

router = APIRouter(prefix="/api/maria", tags=["maria"])

# MongoDB será inicializado no startup do server.py
db = None

def init_db(database):
    """Inicializa referência ao banco de dados"""
    global db
    db = database


# ============================================================================
# MODELS
# ============================================================================

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    needs_disclaimer: bool = False
    disclaimer_text: Optional[str] = None
    emotion_detected: Optional[str] = None
    timestamp: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat_with_maria(chat_msg: ChatMessage):
    """
    Chat com a Maria - Assistente Virtual
    
    Aceita mensagem do usuário e retorna resposta da Maria.
    Salva conversa no MongoDB para histórico.
    """
    try:
        # Gerar ou usar conversation_id existente
        conversation_id = chat_msg.conversation_id or str(uuid.uuid4())
        
        # Buscar contexto do usuário se autenticado
        user_context = None
        conversation_history = []
        
        if chat_msg.user_id and db:
            # Buscar informações do usuário
            user = await db.users.find_one({"id": chat_msg.user_id})
            
            # Buscar caso ativo
            active_case = await db.auto_cases.find_one({
                "user_id": chat_msg.user_id,
                "status": {"$in": ["in_progress", "document_review", "ready_to_submit"]}
            })
            
            if user:
                user_context = {
                    "name": user.get("first_name", "Usuário"),
                    "visa_type": active_case.get("form_code") if active_case else "Não especificado",
                    "progress": active_case.get("progress_percentage", 0) if active_case else 0,
                    "case_status": active_case.get("status") if active_case else "Iniciando"
                }
            
            # Buscar histórico da conversa
            if db:
                history = await db.maria_conversations.find({
                    "conversation_id": conversation_id
                }).sort("timestamp", 1).to_list(length=10)
                
                conversation_history = []
                for msg in history:
                    conversation_history.append({"role": "user", "content": msg.get("user_message")})
                    conversation_history.append({"role": "assistant", "content": msg.get("maria_response")})
        
        # Processar mensagem com Maria
        result = await maria.chat(
            user_message=chat_msg.message,
            conversation_history=conversation_history,
            user_context=user_context
        )
        
        # Salvar conversa no MongoDB
        if db:
            await db.maria_conversations.insert_one({
                "conversation_id": conversation_id,
                "user_id": chat_msg.user_id,
                "user_message": chat_msg.message,
                "maria_response": result["response"],
                "emotion_detected": result.get("emotion_detected"),
                "needs_disclaimer": result.get("needs_disclaimer"),
                "timestamp": datetime.utcnow(),
                "user_context": user_context
            })
        
        return ChatResponse(
            response=result["response"],
            conversation_id=conversation_id,
            needs_disclaimer=result.get("needs_disclaimer", False),
            disclaimer_text=result.get("disclaimer_text"),
            emotion_detected=result.get("emotion_detected"),
            timestamp=result["timestamp"]
        )
        
    except Exception as e:
        print(f"❌ Erro no chat com Maria: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/welcome")
async def get_welcome_message(user_id: Optional[str] = None):
    """
    Retorna mensagem de boas-vindas da Maria
    Personalizada com nome e tipo de visto do usuário se autenticado
    """
    try:
        user_name = None
        visa_type = None
        
        if user_id and db:
            user = await db.users.find_one({"id": user_id})
            if user:
                user_name = user.get("first_name")
            
            active_case = await db.auto_cases.find_one({
                "user_id": user_id,
                "status": {"$in": ["in_progress", "document_review", "ready_to_submit"]}
            })
            if active_case:
                visa_type = active_case.get("form_code")
        
        welcome_msg = maria.get_welcome_message(user_name, visa_type)
        
        return {
            "success": True,
            "message": welcome_msg,
            "user_name": user_name,
            "visa_type": visa_type
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar welcome message: {e}")
        return {
            "success": True,
            "message": maria.get_welcome_message()
        }


@router.get("/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: str, limit: int = 50):
    """
    Retorna histórico de uma conversa específica
    """
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        messages = await db.maria_conversations.find({
            "conversation_id": conversation_id
        }).sort("timestamp", 1).limit(limit).to_list(length=limit)
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "type": "user",
                "content": msg.get("user_message"),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else None
            })
            formatted_messages.append({
                "type": "maria",
                "content": msg.get("maria_response"),
                "emotion_detected": msg.get("emotion_detected"),
                "timestamp": msg.get("timestamp").isoformat() if msg.get("timestamp") else None
            })
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "messages": formatted_messages,
            "total": len(formatted_messages)
        }
        
    except Exception as e:
        print(f"❌ Erro ao buscar histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/overview")
async def get_maria_analytics():
    """
    Analytics da Maria - para admin
    """
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Total de conversas
        total_conversations = await db.maria_conversations.distinct("conversation_id")
        
        # Total de mensagens
        total_messages = await db.maria_conversations.count_documents({})
        
        # Emoções detectadas
        emotions = await db.maria_conversations.aggregate([
            {"$match": {"emotion_detected": {"$ne": None}}},
            {"$group": {"_id": "$emotion_detected", "count": {"$sum": 1}}}
        ]).to_list(length=100)
        
        # Conversas por dia (últimos 7 dias)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        daily_conversations = await db.maria_conversations.aggregate([
            {"$match": {"timestamp": {"$gte": seven_days_ago}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]).to_list(length=7)
        
        return {
            "success": True,
            "analytics": {
                "total_conversations": len(total_conversations),
                "total_messages": total_messages,
                "emotions_detected": {item["_id"]: item["count"] for item in emotions},
                "daily_activity": daily_conversations,
                "avg_messages_per_conversation": total_messages / len(total_conversations) if len(total_conversations) > 0 else 0
            }
        }
        
    except Exception as e:
        print(f"❌ Erro ao buscar analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def maria_health_check():
    """Health check do serviço da Maria"""
    return {
        "service": "Maria - Assistente Virtual Osprey",
        "status": "active",
        "personality": maria.personality["name"],
        "version": "1.0",
        "capabilities": [
            "chat",
            "emotional_support",
            "uscis_information",
            "sales",
            "whatsapp_integration"
        ]
    }
