from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import openai
import json
import jwt
import bcrypt
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI configuration
openai.api_key = os.environ['OPENAI_API_KEY']

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'osprey-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="OSPREY Immigration API - B2C", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ApplicationStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress" 
    document_review = "document_review"
    ready_to_submit = "ready_to_submit"
    submitted = "submitted"
    approved = "approved"
    denied = "denied"

class VisaType(str, Enum):
    h1b = "h1b"
    l1 = "l1"
    o1 = "o1"
    eb5 = "eb5"
    f1 = "f1"
    b1b2 = "b1b2"
    green_card = "green_card"
    family = "family"

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    country_of_birth: Optional[str] = None
    current_country: Optional[str] = None
    date_of_birth: Optional[str] = None
    passport_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    country_of_birth: Optional[str] = None
    current_country: Optional[str] = None
    date_of_birth: Optional[str] = None
    passport_number: Optional[str] = None

class UserApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    visa_type: VisaType
    status: ApplicationStatus = ApplicationStatus.not_started
    progress_percentage: int = 0
    current_step: str = "getting_started"
    documents_uploaded: List[str] = []
    ai_recommendations: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationCreate(BaseModel):
    visa_type: VisaType

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    progress_percentage: Optional[int] = None
    current_step: Optional[str] = None

# Existing models (keeping them)
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
    analysis_type: str = "general"

class VisaRecommendationRequest(BaseModel):
    personal_info: Dict[str, Any]
    current_status: Optional[str] = None
    goals: List[str] = []

class TranslationRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str = "en"

# Authentication helpers
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Authentication routes
@api_router.post("/auth/signup")
async def signup(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(user_data.password)
        
        user_doc = {
            "id": user_id,
            "email": user_data.email,
            "password": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "phone": user_data.phone,
            "country_of_birth": None,
            "current_country": None,
            "date_of_birth": None,
            "passport_number": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user_doc)
        
        # Create JWT token
        token = create_jwt_token(user_id, user_data.email)
        
        return {
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": user_id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name
            }
        }
    
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@api_router.post("/auth/login")
async def login(login_data: UserLogin):
    """Login user"""
    try:
        user = await db.users.find_one({"email": login_data.email})
        if not user or not verify_password(login_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        token = create_jwt_token(user["id"], user["email"])
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error logging in: {str(e)}")

# User profile routes
@api_router.get("/profile", response_model=UserProfile)
async def get_profile(current_user = Depends(get_current_user)):
    """Get user profile"""
    return UserProfile(**current_user)

@api_router.put("/profile")
async def update_profile(profile_data: UserProfileUpdate, current_user = Depends(get_current_user)):
    """Update user profile"""
    try:
        update_data = profile_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
        
        updated_user = await db.users.find_one({"id": current_user["id"]})
        return {"message": "Profile updated successfully", "user": UserProfile(**updated_user)}
    
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

# Application routes
@api_router.post("/applications")
async def create_application(app_data: ApplicationCreate, current_user = Depends(get_current_user)):
    """Create a new visa application"""
    try:
        # Check if user already has an application for this visa type
        existing_app = await db.applications.find_one({
            "user_id": current_user["id"],
            "visa_type": app_data.visa_type.value
        })
        
        if existing_app:
            raise HTTPException(status_code=400, detail="Application already exists for this visa type")
        
        application = UserApplication(
            user_id=current_user["id"],
            visa_type=app_data.visa_type
        )
        
        await db.applications.insert_one(application.dict())
        
        return {"message": "Application created successfully", "application": application}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating application: {str(e)}")

@api_router.get("/applications")
async def get_user_applications(current_user = Depends(get_current_user)):
    """Get all user applications"""
    try:
        applications = await db.applications.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
        return {"applications": applications}
    
    except Exception as e:
        logger.error(f"Error getting applications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting applications: {str(e)}")

@api_router.put("/applications/{application_id}")
async def update_application(application_id: str, update_data: ApplicationUpdate, current_user = Depends(get_current_user)):
    """Update application status/progress"""
    try:
        # Verify application belongs to user
        application = await db.applications.find_one({
            "id": application_id,
            "user_id": current_user["id"]
        })
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        await db.applications.update_one(
            {"id": application_id},
            {"$set": update_dict}
        )
        
        updated_app = await db.applications.find_one({"id": application_id})
        return {"message": "Application updated successfully", "application": updated_app}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating application: {str(e)}")

# Dashboard route
@api_router.get("/dashboard")
async def get_dashboard(current_user = Depends(get_current_user)):
    """Get user dashboard data"""
    try:
        # Get applications
        applications = await db.applications.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
        
        # Get recent chat sessions
        recent_chats = await db.chat_sessions.find(
            {"user_id": current_user["id"]}, {"_id": 0}
        ).sort("last_updated", -1).limit(5).to_list(5)
        
        # Get recent translations
        recent_translations = await db.translations.find(
            {"user_id": current_user["id"]}, {"_id": 0}
        ).sort("timestamp", -1).limit(3).to_list(3)
        
        # Calculate stats
        total_applications = len(applications)
        in_progress_apps = len([app for app in applications if app["status"] in ["in_progress", "document_review"]])
        completed_apps = len([app for app in applications if app["status"] in ["submitted", "approved"]])
        
        return {
            "user": {
                "name": f"{current_user['first_name']} {current_user['last_name']}",
                "email": current_user["email"]
            },
            "stats": {
                "total_applications": total_applications,
                "in_progress": in_progress_apps,
                "completed": completed_apps,
                "success_rate": 100 if completed_apps == 0 else int((len([app for app in applications if app["status"] == "approved"]) / completed_apps) * 100)
            },
            "applications": applications,
            "recent_activity": {
                "chats": recent_chats,
                "translations": recent_translations
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")

# Chat history route
@api_router.get("/chat/history")
async def get_chat_history(current_user = Depends(get_current_user)):
    """Get user's chat history with AI"""
    try:
        sessions = await db.chat_sessions.find(
            {"user_id": current_user["id"]}, {"_id": 0}
        ).sort("last_updated", -1).to_list(50)
        
        return {"chat_sessions": sessions}
    
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")

# Basic routes (keeping existing ones)
@api_router.get("/")
async def root():
    return {"message": "OSPREY Immigration API B2C - Ready to help with your immigration journey!"}

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

# AI-powered routes (updated to include user tracking)
@api_router.post("/chat", response_model=ChatResponse)
async def immigration_chat(request: ChatRequest, current_user = Depends(get_current_user)):
    """Chat assistente especializado em imigração usando OpenAI"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history from MongoDB
        conversation = await db.chat_sessions.find_one({"session_id": session_id})
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": f"""Você é um assistente especializado em imigração da OSPREY, uma plataforma B2C para auto-aplicação.

Usuário: {current_user['first_name']} {current_user['last_name']}

Suas responsabilidades:
- Fornecer informações precisas sobre processos imigratórios
- Orientar sobre documentação necessária para self-application
- Sugerir próximos passos no processo
- Manter tom amigável mas profissional
- SEMPRE mencionar que não oferece conselhos jurídicos
- Para casos complexos, recomendar consulta com advogado

IMPORTANTE: Esta é uma ferramenta de auto-aplicação. Você orienta o usuário a fazer sua própria aplicação, não fornece serviços jurídicos.

Responda sempre em português, seja claro e objetivo."""
            }
        ]
        
        # Add conversation history
        if conversation and "messages" in conversation:
            messages.extend(conversation["messages"][-10:])
        
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
        current_time = datetime.utcnow()
        new_messages = [
            {"role": "user", "content": request.message, "timestamp": current_time.isoformat()},
            {"role": "assistant", "content": ai_response, "timestamp": current_time.isoformat()}
        ]
        
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": {"$each": new_messages}},
                "$set": {
                    "user_id": current_user["id"],
                    "last_updated": current_time
                }
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
async def analyze_document(request: DocumentAnalysisRequest, current_user = Depends(get_current_user)):
    """Analisa documentos para processos de imigração usando OpenAI"""
    try:
        analysis_prompts = {
            "general": "Analise este documento e forneça um resumo dos pontos principais, identificando qualquer informação relevante para processos de imigração.",
            "immigration": "Analise este documento de imigração. Identifique: 1) Tipo de documento, 2) Informações pessoais, 3) Status atual, 4) Próximos passos necessários, 5) Documentos adicionais que podem ser necessários.",
            "legal": "Faça uma análise deste documento, identificando informações importantes e possíveis implicações para processos imigratórios. LEMBRE-SE: Esta é uma ferramenta de orientação, não de consultoria jurídica."
        }
        
        prompt = analysis_prompts.get(request.analysis_type, analysis_prompts["general"])
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente de análise de documentos para auto-aplicação em imigração. Forneça análises úteis em português. IMPORTANTE: Sempre mencione que esta é uma ferramenta de orientação e não substitui consultoria jurídica."
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
            "user_id": current_user["id"],
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
async def translate_text(request: TranslationRequest, current_user = Depends(get_current_user)):
    """Traduz textos usando OpenAI"""
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
                    "content": f"Você é um tradutor profissional especializado em documentos de imigração. Traduza o texto a seguir para {target_lang_name} mantendo o contexto e significado original."
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
            "user_id": current_user["id"],
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
async def get_visa_recommendation(request: VisaRecommendationRequest, current_user = Depends(get_current_user)):
    """Recomenda tipos de visto baseado no perfil do usuário"""
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
        5. Próximos passos para auto-aplicação

        IMPORTANTE: Esta é uma ferramenta de orientação. Para casos complexos, recomende consulta com advogado de imigração.

        Responda em português em formato estruturado.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente para auto-aplicação em imigração. Forneça recomendações precisas mas sempre mencione que não oferece consultoria jurídica."
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
            "user_id": current_user["id"],
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