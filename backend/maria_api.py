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
        
        if chat_msg.user_id and db is not None:
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
        if db is not None:
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


@router.post("/voice/text-to-speech")
async def text_to_speech(request: dict):
    """
    Converte texto em áudio (voz da Maria)
    Usa Gemini/Google Cloud TTS para vozes naturais
    """
    try:
        text = request.get("text")
        language = request.get("language", "pt-BR")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        result = await maria_voice.text_to_speech(
            text=text,
            language=language,
            voice_gender="female",
            speaking_rate=1.0,
            pitch=0.0
        )
        
        return result
        
    except Exception as e:
        print(f"❌ Erro no TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/speech-to-text")
async def speech_to_text(request: dict):
    """
    Converte áudio em texto
    Usa Gemini/Google Cloud Speech-to-Text
    """
    try:
        import base64
        
        audio_base64 = request.get("audio")
        language = request.get("language", "pt-BR")
        
        if not audio_base64:
            raise HTTPException(status_code=400, detail="Audio is required")
        
        # Decodificar base64
        audio_data = base64.b64decode(audio_base64)
        
        result = await maria_voice.speech_to_text(
            audio_data=audio_data,
            language=language
        )
        
        return result
        
    except Exception as e:
        print(f"❌ Erro no STT: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp/send")
async def send_whatsapp(request: dict):
    """
    Envia mensagem do WhatsApp via Baileys
    Apenas para admins/sistema interno
    """
    try:
        phone = request.get("phone")
        message = request.get("message")
        
        if not phone or not message:
            raise HTTPException(status_code=400, detail="Phone and message are required")
        
        result = await maria_whatsapp.send_message(phone, message)
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao enviar WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp/welcome/{user_id}")
async def send_welcome_whatsapp(user_id: str):
    """
    Envia mensagem de boas-vindas da Maria via WhatsApp
    Chamado automaticamente após signup/pagamento
    """
    try:
        if not db:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Buscar usuário
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Buscar caso ativo
        case = await db.auto_cases.find_one({
            "user_id": user_id,
            "status": {"$in": ["in_progress", "not_started"]}
        })
        
        phone = user.get("phone")
        if not phone:
            return {
                "success": False,
                "error": "User has no phone number"
            }
        
        user_name = user.get("first_name", "Usuário")
        visa_type = case.get("form_code", "seu visto") if case else "seu visto"
        
        result = await maria_whatsapp.send_welcome_message(
            phone_number=phone,
            user_name=user_name,
            visa_type=visa_type
        )
        
        # Salvar no log
        if result.get("success") and db:
            await db.maria_whatsapp_log.insert_one({
                "user_id": user_id,
                "phone": phone,
                "message_type": "welcome",
                "success": True,
                "message_id": result.get("message_id"),
                "timestamp": datetime.utcnow()
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Erro ao enviar boas-vindas WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whatsapp/status")
async def whatsapp_status():
    """
    Verifica status da conexão WhatsApp (Baileys)
    """
    try:
        status = await maria_whatsapp.check_connection_status()
        return status
        
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


@router.get("/health")
async def maria_health_check():
    """Health check do serviço da Maria"""
    whatsapp_status = await maria_whatsapp.check_connection_status()
    
    return {
        "service": "Maria - Assistente Virtual Osprey",
        "status": "active",
        "personality": maria.personality["name"],
        "version": "1.0",
        "capabilities": {
            "chat": True,
            "emotional_support": True,
            "uscis_information": True,
            "sales": True,
            "voice": maria_voice.available,
            "whatsapp": whatsapp_status.get("connected", False)
        },
        "integrations": {
            "gemini": maria_voice.available,
            "baileys": whatsapp_status.get("connected", False)
        }
    }
