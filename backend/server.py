from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import openai
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI configuration
openai.api_key = os.environ['OPENAI_API_KEY']

# Create the main app without a prefix
app = FastAPI(title="OSPREY Immigration API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    context: Optional[Dict[str, Any]] = None

class DocumentAnalysisRequest(BaseModel):
    document_text: str
    document_type: Optional[str] = None
    analysis_type: str = "general"  # general, immigration, legal

class VisaRecommendationRequest(BaseModel):
    personal_info: Dict[str, Any]
    current_status: Optional[str] = None
    goals: List[str] = []

class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str = "en"

# Basic routes
@api_router.get("/")
async def root():
    return {"message": "OSPREY Immigration API - Ready to help with your immigration journey!"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# AI-powered routes
@api_router.post("/chat", response_model=ChatResponse)
async def immigration_chat(request: ChatRequest):
    """
    Chat assistente especializado em imigração usando OpenAI
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history from MongoDB
        conversation = await db.chat_sessions.find_one({"session_id": session_id})
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": """Você é um assistente especializado em imigração da OSPREY, uma plataforma líder em auto aplicação imigratória.

Suas responsabilidades:
- Fornecer informações precisas sobre processos imigratórios
- Explicar tipos de visto (H1-B, L1, O1, EB-5, F1, etc.)
- Orientar sobre documentação necessária  
- Sugerir próximos passos no processo
- Manter tom profissional mas acessível
- Sempre recomendar consulta com advogado para casos complexos

Características da OSPREY:
- Plataforma 100% digital
- Taxa de sucesso de 98%
- Suporte 24/7
- Aprovação garantida ou reembolso total
- Mais de 5.000 processos aprovados

Responda sempre em português, seja claro e objetivo."""
            }
        ]
        
        # Add conversation history
        if conversation and "messages" in conversation:
            messages.extend(conversation["messages"][-10:])  # Last 10 messages for context
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Call OpenAI
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Save conversation to MongoDB
        new_messages = [
            {"role": "user", "content": request.message, "timestamp": datetime.utcnow()},
            {"role": "assistant", "content": ai_response, "timestamp": datetime.utcnow()}
        ]
        
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": {"$each": new_messages}},
                "$set": {"last_updated": datetime.utcnow()}
            },
            upsert=True
        )
        
        return ChatResponse(
            message=ai_response,
            session_id=session_id,
            context=request.context
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@api_router.post("/analyze-document")
async def analyze_document(request: DocumentAnalysisRequest):
    """
    Analisa documentos para processos de imigração usando OpenAI
    """
    try:
        analysis_prompts = {
            "general": "Analise este documento e forneça um resumo dos pontos principais, identificando qualquer informação relevante para processos de imigração.",
            "immigration": "Analise este documento de imigração. Identifique: 1) Tipo de documento, 2) Informações pessoais, 3) Status atual, 4) Próximos passos necessários, 5) Documentos adicionais que podem ser necessários.",
            "legal": "Faça uma análise jurídica deste documento, identificando cláusulas importantes, obrigações, direitos e possíveis implicações legais."
        }
        
        prompt = analysis_prompts.get(request.analysis_type, analysis_prompts["general"])
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em análise de documentos de imigração. Forneça análises detalhadas, precisas e úteis em português."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nDocumento:\n{request.document_text}"
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        analysis = response.choices[0].message.content
        
        # Save analysis to MongoDB
        analysis_record = {
            "id": str(uuid.uuid4()),
            "document_type": request.document_type,
            "analysis_type": request.analysis_type,
            "analysis": analysis,
            "timestamp": datetime.utcnow()
        }
        
        await db.document_analyses.insert_one(analysis_record)
        
        return {
            "analysis": analysis,
            "analysis_id": analysis_record["id"],
            "timestamp": analysis_record["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error in document analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")

@api_router.post("/translate")
async def translate_text(request: TranslationRequest):
    """
    Traduz textos usando OpenAI
    """
    try:
        if request.source_language == "auto":
            detect_prompt = f"Detecte o idioma deste texto e responda apenas com o código do idioma (pt, en, es, etc.): {request.text[:200]}"
            detect_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": detect_prompt}],
                max_tokens=10,
                temperature=0
            )
            source_lang = detect_response.choices[0].message.content.strip()
        else:
            source_lang = request.source_language
        
        # Translation
        language_names = {
            "pt": "português", "en": "inglês", "es": "espanhol",
            "fr": "francês", "de": "alemão", "it": "italiano"
        }
        
        target_lang_name = language_names.get(request.target_language, request.target_language)
        
        translation_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Você é um tradutor profissional. Traduza o texto a seguir para {target_lang_name} mantendo o contexto e significado original."
                },
                {
                    "role": "user",
                    "content": request.text
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        translated_text = translation_response.choices[0].message.content
        
        # Save translation to MongoDB
        translation_record = {
            "id": str(uuid.uuid4()),
            "original_text": request.text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": request.target_language,
            "provider": "openai",
            "timestamp": datetime.utcnow()
        }
        
        await db.translations.insert_one(translation_record)
        
        return {
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": request.target_language,
            "translation_id": translation_record["id"]
        }
        
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error translating text: {str(e)}")

@api_router.post("/visa-recommendation")
async def get_visa_recommendation(request: VisaRecommendationRequest):
    """
    Recomenda tipos de visto baseado no perfil do usuário
    """
    try:
        prompt = f"""
        Baseado nas informações fornecidas, recomende os tipos de visto mais adequados para esta pessoa.

        Informações pessoais: {json.dumps(request.personal_info, ensure_ascii=False)}
        Status atual: {request.current_status}
        Objetivos: {', '.join(request.goals)}

        Forneça:
        1. Top 3 recomendações de visto com explicação
        2. Requisitos para cada visto
        3. Tempo estimado de processo
        4. Documentação necessária
        5. Próximos passos

        Responda em formato JSON estruturado.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um consultor especializado em imigração americana. Forneça recomendações precisas e atualizadas sobre tipos de visto."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        recommendation = response.choices[0].message.content
        
        # Save recommendation
        recommendation_record = {
            "id": str(uuid.uuid4()),
            "personal_info": request.personal_info,
            "current_status": request.current_status,
            "goals": request.goals,
            "recommendation": recommendation,
            "timestamp": datetime.utcnow()
        }
        
        await db.visa_recommendations.insert_one(recommendation_record)
        
        return {
            "recommendation": recommendation,
            "recommendation_id": recommendation_record["id"],
            "timestamp": recommendation_record["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error in visa recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting visa recommendation: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()