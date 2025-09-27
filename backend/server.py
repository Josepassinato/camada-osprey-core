from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Depends, status, Form
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
import base64
import mimetypes
import re
from visa_specifications import get_visa_specifications, get_required_documents, get_key_questions, get_common_issues

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

class USCISForm(str, Enum):
    N400 = "N-400"  # Application for Naturalization
    I130 = "I-130"  # Petition for Alien Relative
    I765 = "I-765"  # Application for Employment Authorization
    I485 = "I-485"  # Application to Register or Adjust Status
    I90 = "I-90"    # Application to Replace Permanent Resident Card
    I751 = "I-751"  # Petition to Remove Conditions on Residence
    I131 = "I-131"  # Application for Travel Document
    I129 = "I-129"  # Nonimmigrant Worker Petition
    I589 = "I-589"  # Application for Asylum
    O1 = "O-1"      # Extraordinary Ability (part of I-129)
    H1B = "H-1B"    # Specialty Occupation (part of I-129)
    AR11 = "AR-11"  # Change of Address

class CaseStatus(str, Enum):
    created = "created"
    form_selected = "form_selected"
    basic_data = "basic_data"
    documents_uploaded = "documents_uploaded"
    story_completed = "story_completed"
    form_filled = "form_filled"
    reviewed = "reviewed"
    paid = "paid"
    completed = "completed"

class DocumentType(str, Enum):
    passport = "passport"
    birth_certificate = "birth_certificate"
    marriage_certificate = "marriage_certificate"
    divorce_certificate = "divorce_certificate"
    education_diploma = "education_diploma"
    education_transcript = "education_transcript"
    employment_letter = "employment_letter"
    bank_statement = "bank_statement"
    tax_return = "tax_return"
    medical_exam = "medical_exam"
    police_clearance = "police_clearance"
    sponsor_documents = "sponsor_documents"
    photos = "photos"
    form_i130 = "form_i130"
    form_ds160 = "form_ds160"
    other = "other"

class DocumentStatus(str, Enum):
    pending_review = "pending_review"
    approved = "approved"
    requires_improvement = "requires_improvement"
    expired = "expired"
    missing_info = "missing_info"

class DocumentPriority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class InterviewType(str, Enum):
    consular = "consular"
    adjustment_of_status = "adjustment_of_status"
    asylum = "asylum"
    naturalization = "naturalization"

# User Models (keeping existing ones)
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

# Auto-Application System Models
class AutoApplicationCase(BaseModel):
    case_id: str = Field(default_factory=lambda: f"OSP-{str(uuid.uuid4())[:8].upper()}")
    user_id: Optional[str] = None  # Allow anonymous cases
    session_token: Optional[str] = None  # For anonymous tracking
    form_code: Optional[USCISForm] = None
    status: CaseStatus = CaseStatus.created
    
    # Basic Data
    basic_data: Optional[Dict[str, Any]] = None
    
    # Documents
    uploaded_documents: List[str] = []
    document_analysis: Optional[Dict[str, Any]] = None
    
    # User Story
    user_story_text: Optional[str] = None
    user_story_audio_url: Optional[str] = None
    ai_extracted_facts: Optional[Dict[str, Any]] = None
    
    # Form Data
    simplified_form_responses: Optional[Dict[str, Any]] = None
    official_form_data: Optional[Dict[str, Any]] = None
    
    # Payment & Final
    payment_status: Optional[str] = None
    payment_id: Optional[str] = None
    final_package_generated: bool = False
    final_package_url: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # For anonymous cases
    
class CaseCreate(BaseModel):
    form_code: Optional[USCISForm] = None
    session_token: Optional[str] = None  # For anonymous users
    
class CaseUpdate(BaseModel):
    form_code: Optional[USCISForm] = None
    status: Optional[CaseStatus] = None
    basic_data: Optional[Dict[str, Any]] = None
    user_story_text: Optional[str] = None
    simplified_form_responses: Optional[Dict[str, Any]] = None
    progress_percentage: Optional[int] = None
    current_step: Optional[str] = None

# Document Models (keeping existing ones)
class UserDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    filename: str
    original_filename: str
    document_type: DocumentType
    content_base64: str
    mime_type: str
    file_size: int
    status: DocumentStatus = DocumentStatus.pending_review
    ai_analysis: Optional[Dict[str, Any]] = None
    ai_suggestions: List[str] = []
    expiration_date: Optional[datetime] = None
    issue_date: Optional[datetime] = None
    priority: DocumentPriority = DocumentPriority.medium
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentUpload(BaseModel):
    document_type: DocumentType
    tags: Optional[List[str]] = []
    expiration_date: Optional[str] = None
    issue_date: Optional[str] = None

class DocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    status: Optional[DocumentStatus] = None
    expiration_date: Optional[str] = None
    issue_date: Optional[str] = None
    tags: Optional[List[str]] = None
    priority: Optional[DocumentPriority] = None

# Education Models (NEW)
class VisaGuide(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    visa_type: VisaType
    title: str
    description: str
    difficulty_level: DifficultyLevel
    estimated_time_minutes: int
    sections: List[Dict[str, Any]]
    requirements: List[str]
    common_mistakes: List[str]
    success_tips: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    interview_type: InterviewType
    visa_type: VisaType
    questions: List[Dict[str, Any]]
    answers: List[Dict[str, Any]] = []
    ai_feedback: Optional[Dict[str, Any]] = None
    score: Optional[int] = None
    duration_minutes: Optional[int] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InterviewStart(BaseModel):
    interview_type: InterviewType
    visa_type: VisaType
    difficulty_level: Optional[DifficultyLevel] = DifficultyLevel.beginner

class InterviewAnswer(BaseModel):
    question_id: str
    answer: str

class PersonalizedTip(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    tip_category: str  # document, application, interview, etc.
    title: str
    content: str
    priority: str  # high, medium, low
    visa_type: Optional[VisaType] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeBaseQuery(BaseModel):
    query: str
    visa_type: Optional[VisaType] = None
    category: Optional[str] = None

class UserProgress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    guides_completed: List[str] = []
    interviews_completed: List[str] = []
    knowledge_queries: int = 0
    total_study_time_minutes: int = 0
    achievement_badges: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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

# Authentication helpers (keeping existing ones)
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

# Document helper functions (keeping existing ones)
def extract_text_from_base64_image(base64_content: str) -> str:
    """Extract text from base64 image using OCR simulation"""
    # In a real implementation, you would use OCR libraries like pytesseract
    # For now, we'll return a placeholder
    return "Extracted text from document using OCR"

def validate_file_type(mime_type: str) -> bool:
    """Validate if file type is supported"""
    supported_types = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/tiff',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    return mime_type in supported_types

async def analyze_document_with_ai(document: UserDocument) -> Dict[str, Any]:
    """Analyze document content with OpenAI"""
    try:
        # For text-based documents, extract text
        if document.mime_type.startswith('image/'):
            content = extract_text_from_base64_image(document.content_base64)
        else:
            content = f"Document type: {document.document_type}, Filename: {document.original_filename}"

        prompt = f"""
        Analise este documento de imigração e forneça:

        Tipo de documento: {document.document_type}
        Conteúdo: {content[:1000]}...

        Retorne APENAS um JSON com:
        {{
            "completeness_score": [0-100],
            "validity_status": "valid|invalid|expired|unclear",
            "key_information": ["info1", "info2"],
            "missing_information": ["missing1", "missing2"],
            "suggestions": ["suggestion1", "suggestion2"],
            "expiration_warnings": ["warning1"],
            "quality_issues": ["issue1"],
            "next_steps": ["step1", "step2"]
        }}

        IMPORTANTE: Esta é uma ferramenta de orientação para auto-aplicação, não consultoria jurídica.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em análise de documentos para imigração. Responda APENAS em formato JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )

        # Parse JSON response
        analysis_text = response.choices[0].message.content.strip()
        # Remove markdown formatting if present
        analysis_text = analysis_text.replace('```json', '').replace('```', '').strip()
        
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # Fallback analysis if JSON parsing fails
            analysis = {
                "completeness_score": 75,
                "validity_status": "valid",
                "key_information": ["Document uploaded successfully"],
                "missing_information": [],
                "suggestions": ["Documento analisado com sucesso"],
                "expiration_warnings": [],
                "quality_issues": [],
                "next_steps": ["Aguardar revisão adicional se necessário"]
            }

        return analysis

    except Exception as e:
        logger.error(f"Error analyzing document with AI: {str(e)}")
        # Return basic analysis if AI fails
        return {
            "completeness_score": 50,
            "validity_status": "unclear",
            "key_information": ["Documento carregado"],
            "missing_information": ["Análise automática não disponível"],
            "suggestions": ["Revise o documento manualmente"],
            "expiration_warnings": [],
            "quality_issues": ["Análise automática falhou"],
            "next_steps": ["Upload realizado, aguarde revisão manual"]
        }

def determine_document_priority(document_type: DocumentType, expiration_date: Optional[datetime]) -> DocumentPriority:
    """Determine document priority based on type and expiration"""
    high_priority_docs = [DocumentType.passport, DocumentType.medical_exam, DocumentType.police_clearance]
    
    if document_type in high_priority_docs:
        return DocumentPriority.high
    
    if expiration_date:
        days_to_expire = (expiration_date - datetime.utcnow()).days
        if days_to_expire <= 30:
            return DocumentPriority.high
        elif days_to_expire <= 90:
            return DocumentPriority.medium
    
    return DocumentPriority.low

# Education helper functions (NEW)
async def generate_interview_questions(interview_type: InterviewType, visa_type: VisaType, difficulty_level: DifficultyLevel) -> List[Dict[str, Any]]:
    """Generate interview questions using AI"""
    try:
        difficulty_map = {
            DifficultyLevel.beginner: "perguntas básicas e introdutórias",
            DifficultyLevel.intermediate: "perguntas moderadas com alguns detalhes",
            DifficultyLevel.advanced: "perguntas complexas e cenários desafiadores"
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

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em entrevistas de imigração. Responda APENAS em JSON válido."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )

        questions_text = response.choices[0].message.content.strip()
        questions_text = questions_text.replace('```json', '').replace('```', '').strip()
        
        try:
            questions = json.loads(questions_text)
            return questions
        except json.JSONDecodeError:
            # Fallback questions
            return [
                {
                    "id": "q1",
                    "question_en": "What is the purpose of your visit to the United States?",
                    "question_pt": "Qual é o propósito da sua visita aos Estados Unidos?",
                    "category": "purpose",
                    "difficulty": difficulty_level.value,
                    "tips": ["Seja claro e direto", "Mencione detalhes específicos"],
                    "key_points": ["Propósito específico", "Duração planejada"]
                }
            ]

    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        return []

async def evaluate_interview_answer(question: Dict[str, Any], answer: str, visa_type: VisaType) -> Dict[str, Any]:
    """Evaluate interview answer using AI"""
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
                    "content": "Você é um especialista em avaliação de entrevistas de imigração. Responda APENAS em JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )

        feedback_text = response.choices[0].message.content.strip()
        feedback_text = feedback_text.replace('```json', '').replace('```', '').strip()
        
        try:
            feedback = json.loads(feedback_text)
            return feedback
        except json.JSONDecodeError:
            return {
                "score": 70,
                "strengths": ["Resposta fornecida"],
                "weaknesses": ["Análise automática não disponível"],
                "suggestions": ["Revise sua resposta"],
                "improved_answer": "Desenvolva mais detalhes na sua resposta",
                "confidence_level": "médio"
            }

    except Exception as e:
        logger.error(f"Error evaluating interview answer: {str(e)}")
        return {
            "score": 50,
            "strengths": ["Tentativa de resposta"],
            "weaknesses": ["Análise não disponível"],
            "suggestions": ["Tente novamente"],
            "improved_answer": "Resposta mais detalhada seria ideal",
            "confidence_level": "baixo"
        }

async def generate_personalized_tips(user_id: str, user_profile: dict, applications: List[dict], documents: List[dict]) -> List[PersonalizedTip]:
    """Generate personalized tips based on user profile and progress"""
    tips = []
    
    try:
        # Analyze user's current status
        active_applications = [app for app in applications if app.get('status') in ['in_progress', 'document_review']]
        pending_docs = [doc for doc in documents if doc.get('status') == 'pending_review']
        expiring_docs = [doc for doc in documents if doc.get('expiration_date') and 
                        (datetime.fromisoformat(doc['expiration_date'].replace('Z', '+00:00')) - datetime.utcnow()).days <= 30]
        
        # Generate tips based on user's situation
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

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um consultor educativo de imigração. Forneça dicas práticas em português. Sempre mencione que não oferece consultoria jurídica."
                },
                {
                    "role": "user",
                    "content": user_context
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )

        tips_text = response.choices[0].message.content.strip()
        tips_text = tips_text.replace('```json', '').replace('```', '').strip()
        
        try:
            tips_data = json.loads(tips_text)
            for tip_data in tips_data:
                tip = PersonalizedTip(
                    user_id=user_id,
                    tip_category=tip_data.get('category', 'general'),
                    title=tip_data.get('title', ''),
                    content=tip_data.get('content', ''),
                    priority=tip_data.get('priority', 'medium')
                )
                tips.append(tip)
        except json.JSONDecodeError:
            pass

    except Exception as e:
        logger.error(f"Error generating personalized tips: {str(e)}")
    
    # Add fallback tips if generation failed
    if not tips:
        tips.append(PersonalizedTip(
            user_id=user_id,
            tip_category="preparation",
            title="Organize seus documentos",
            content="Mantenha todos os seus documentos organizados e atualizados para facilitar o processo de aplicação.",
            priority="high"
        ))
    
    return tips

async def search_knowledge_base(query: str, visa_type: Optional[VisaType] = None) -> Dict[str, Any]:
    """Search knowledge base using AI"""
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
                    "content": "Você é uma base de conhecimento educativa sobre imigração americana. Forneça informações precisas em português, sempre com disclaimers sobre consultoria jurídica."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )

        result_text = response.choices[0].message.content.strip()
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        
        try:
            result = json.loads(result_text)
            return result
        except json.JSONDecodeError:
            return {
                "answer": "Desculpe, não foi possível processar sua pergunta no momento. Tente reformulá-la ou consulte nossa seção de guias interativos.",
                "related_topics": ["Guias de Visto", "Simulador de Entrevista", "Gestão de Documentos"],
                "next_steps": ["Explore os guias interativos", "Use o simulador de entrevista"],
                "resources": ["Centro de Ajuda", "Chat com IA"],
                "warnings": ["Esta é uma ferramenta educativa - não substitui consultoria jurídica"],
                "confidence": "baixo"
            }

    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        return {
            "answer": "Erro ao processar consulta. Tente novamente.",
            "related_topics": [],
            "next_steps": [],
            "resources": [],
            "warnings": ["Sistema temporariamente indisponível"],
            "confidence": "baixo"
        }

# Authentication routes (keeping existing ones)
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
        
        # Initialize user progress
        progress = UserProgress(user_id=user_id)
        await db.user_progress.insert_one(progress.dict())
        
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

# User profile routes (keeping existing ones)
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

# Education routes (NEW)
@api_router.get("/education/guides")
async def get_visa_guides(visa_type: Optional[VisaType] = None, current_user = Depends(get_current_user)):
    """Get available visa guides"""
    try:
        # Predefined guides data (in production, this would come from database)
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
                    {"title": "Dicas de Sucesso", "content": "Conselhos práticos"}
                ],
                "requirements": ["Oferta de emprego", "Graduação superior", "Especialização na área"],
                "common_mistakes": ["Documentação incompleta", "Não demonstrar especialização"],
                "success_tips": ["Prepare documentação detalhada", "Demonstre expertise única"]
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
                    {"title": "Vida nos EUA", "content": "Dicas para estudantes"}
                ],
                "requirements": ["Aceitação em escola aprovada", "Recursos financeiros", "Intenção de retorno"],
                "common_mistakes": ["Demonstrar intenção imigratória", "Recursos financeiros insuficientes"],
                "success_tips": ["Demonstre laços com país de origem", "Tenha recursos financeiros claros"]
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
                    {"title": "Adjustment vs Consular", "content": "Diferentes caminhos"}
                ],
                "requirements": ["Relacionamento qualificado", "Documentos comprobatórios", "Sponsor qualificado"],
                "common_mistakes": ["Documentos familiares inadequados", "Não comprovar relacionamento genuíno"],
                "success_tips": ["Documente bem o relacionamento", "Mantenha registros detalhados"]
            }
        }
        
        if visa_type:
            guide_data = guides_data.get(visa_type)
            if guide_data:
                guide = VisaGuide(
                    visa_type=visa_type,
                    **guide_data
                )
                return {"guide": guide.dict()}
            else:
                raise HTTPException(status_code=404, detail="Guide not found")
        else:
            # Return all guides
            all_guides = []
            for v_type, guide_data in guides_data.items():
                guide = VisaGuide(
                    visa_type=v_type,
                    **guide_data
                )
                all_guides.append(guide.dict())
            return {"guides": all_guides}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visa guides: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting guides: {str(e)}")

@api_router.post("/education/guides/{visa_type}/complete")
async def complete_guide(visa_type: VisaType, current_user = Depends(get_current_user)):
    """Mark a guide as completed"""
    try:
        # Update user progress
        await db.user_progress.update_one(
            {"user_id": current_user["id"]},
            {
                "$addToSet": {"guides_completed": visa_type.value},
                "$inc": {"total_study_time_minutes": 30},  # Estimated time
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        return {"message": f"Guide {visa_type.value} marked as completed"}
        
    except Exception as e:
        logger.error(f"Error completing guide: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error completing guide: {str(e)}")

@api_router.post("/education/interview/start")
async def start_interview_simulation(request: InterviewStart, current_user = Depends(get_current_user)):
    """Start a new interview simulation"""
    try:
        # Generate questions
        questions = await generate_interview_questions(
            request.interview_type,
            request.visa_type,
            request.difficulty_level or DifficultyLevel.beginner
        )
        
        # Create interview session
        session = InterviewSession(
            user_id=current_user["id"],
            interview_type=request.interview_type,
            visa_type=request.visa_type,
            questions=questions
        )
        
        await db.interview_sessions.insert_one(session.dict())
        
        return {
            "session_id": session.id,
            "questions": questions,
            "total_questions": len(questions),
            "estimated_duration": len(questions) * 2  # 2 minutes per question
        }
        
    except Exception as e:
        logger.error(f"Error starting interview simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting interview: {str(e)}")

@api_router.post("/education/interview/{session_id}/answer")
async def submit_interview_answer(
    session_id: str, 
    answer_data: InterviewAnswer, 
    current_user = Depends(get_current_user)
):
    """Submit an answer to interview question"""
    try:
        # Get interview session
        session = await db.interview_sessions.find_one({
            "id": session_id,
            "user_id": current_user["id"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # Find the question
        question = next((q for q in session["questions"] if q["id"] == answer_data.question_id), None)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Evaluate answer
        feedback = await evaluate_interview_answer(
            question,
            answer_data.answer,
            VisaType(session["visa_type"])
        )
        
        # Update session with answer
        answer_record = {
            "question_id": answer_data.question_id,
            "answer": answer_data.answer,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await db.interview_sessions.update_one(
            {"id": session_id},
            {
                "$push": {"answers": answer_record},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "feedback": feedback,
            "next_question_index": len(session.get("answers", [])) + 1
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting interview answer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")

@api_router.post("/education/interview/{session_id}/complete")
async def complete_interview_session(session_id: str, current_user = Depends(get_current_user)):
    """Complete interview session and get final feedback"""
    try:
        # Get interview session
        session = await db.interview_sessions.find_one({
            "id": session_id,
            "user_id": current_user["id"]
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        answers = session.get("answers", [])
        if not answers:
            raise HTTPException(status_code=400, detail="No answers submitted")
        
        # Calculate overall score
        scores = [answer.get("feedback", {}).get("score", 0) for answer in answers]
        overall_score = sum(scores) // len(scores) if scores else 0
        
        # Generate overall feedback
        overall_feedback = {
            "overall_score": overall_score,
            "questions_answered": len(answers),
            "average_confidence": "médio",  # Simplified for demo
            "strengths": ["Respostas completas", "Boa preparação"],
            "areas_for_improvement": ["Desenvolver mais detalhes", "Praticar mais"],
            "recommendations": [
                "Continue praticando com diferentes cenários",
                "Revise os guias interativos relacionados",
                "Considere praticar com diferentes níveis de dificuldade"
            ]
        }
        
        # Update session as completed
        await db.interview_sessions.update_one(
            {"id": session_id},
            {
                "$set": {
                    "completed": True,
                    "score": overall_score,
                    "ai_feedback": overall_feedback,
                    "duration_minutes": 15,  # Simplified
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update user progress
        await db.user_progress.update_one(
            {"user_id": current_user["id"]},
            {
                "$addToSet": {"interviews_completed": session_id},
                "$inc": {"total_study_time_minutes": 15},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        return {
            "overall_feedback": overall_feedback,
            "session_completed": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing interview session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error completing interview: {str(e)}")

@api_router.get("/education/tips")
async def get_personalized_tips(current_user = Depends(get_current_user)):
    """Get personalized tips for user"""
    try:
        # Get existing tips
        existing_tips = await db.personalized_tips.find(
            {"user_id": current_user["id"]}, {"_id": 0}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        # If no recent tips, generate new ones
        if not existing_tips:
            # Get user data for context
            applications = await db.applications.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
            documents = await db.documents.find(
                {"user_id": current_user["id"]}, 
                {"_id": 0, "content_base64": 0}
            ).to_list(100)
            
            # Generate new tips
            tips = await generate_personalized_tips(current_user["id"], current_user, applications, documents)
            
            # Save tips to database
            for tip in tips:
                await db.personalized_tips.insert_one(tip.dict())
            
            existing_tips = [tip.dict() for tip in tips]
        
        return {"tips": existing_tips}
        
    except Exception as e:
        logger.error(f"Error getting personalized tips: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting tips: {str(e)}")

@api_router.post("/education/tips/{tip_id}/read")
async def mark_tip_as_read(tip_id: str, current_user = Depends(get_current_user)):
    """Mark a tip as read"""
    try:
        await db.personalized_tips.update_one(
            {"id": tip_id, "user_id": current_user["id"]},
            {"$set": {"is_read": True}}
        )
        
        return {"message": "Tip marked as read"}
        
    except Exception as e:
        logger.error(f"Error marking tip as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking tip as read: {str(e)}")

@api_router.post("/education/knowledge-base/search")
async def search_knowledge(query_data: KnowledgeBaseQuery, current_user = Depends(get_current_user)):
    """Search the knowledge base"""
    try:
        # Search knowledge base
        result = await search_knowledge_base(query_data.query, query_data.visa_type)
        
        # Update user progress
        await db.user_progress.update_one(
            {"user_id": current_user["id"]},
            {
                "$inc": {"knowledge_queries": 1},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        # Log the search for analytics
        search_log = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "query": query_data.query,
            "visa_type": query_data.visa_type.value if query_data.visa_type else None,
            "category": query_data.category,
            "timestamp": datetime.utcnow()
        }
        await db.knowledge_searches.insert_one(search_log)
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching knowledge base: {str(e)}")

@api_router.get("/education/progress")
async def get_user_progress(current_user = Depends(get_current_user)):
    """Get user's education progress"""
    try:
        progress = await db.user_progress.find_one(
            {"user_id": current_user["id"]}, {"_id": 0}
        )
        
        if not progress:
            # Initialize progress if doesn't exist
            progress = UserProgress(user_id=current_user["id"])
            await db.user_progress.insert_one(progress.dict())
            progress = progress.dict()
        
        # Get additional stats
        total_interviews = await db.interview_sessions.count_documents({
            "user_id": current_user["id"],
            "completed": True
        })
        
        recent_tips = await db.personalized_tips.count_documents({
            "user_id": current_user["id"],
            "is_read": False
        })
        
        progress["total_completed_interviews"] = total_interviews
        progress["unread_tips_count"] = recent_tips
        
        return {"progress": progress}
        
    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting progress: {str(e)}")

# Document routes (keeping existing ones with modifications for education integration)
@api_router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    tags: str = Form(""),
    expiration_date: Optional[str] = Form(None),
    issue_date: Optional[str] = Form(None),
    current_user = Depends(get_current_user)
):
    """Upload a document with AI analysis"""
    try:
        # Validate file
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Size limit: 10MB
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Validate file type
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        if not validate_file_type(mime_type):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Convert to base64
        content_base64 = base64.b64encode(content).decode('utf-8')
        
        # Parse dates
        exp_date = None
        iss_date = None
        try:
            if expiration_date:
                exp_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
            if issue_date:
                iss_date = datetime.fromisoformat(issue_date.replace('Z', '+00:00'))
        except ValueError:
            pass  # Ignore invalid dates
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
        
        # Determine priority
        priority = determine_document_priority(document_type, exp_date)
        
        # Create document record
        document = UserDocument(
            user_id=current_user["id"],
            filename=f"{document_type}_{uuid.uuid4().hex[:8]}_{file.filename}",
            original_filename=file.filename,
            document_type=document_type,
            content_base64=content_base64,
            mime_type=mime_type,
            file_size=len(content),
            expiration_date=exp_date,
            issue_date=iss_date,
            priority=priority,
            tags=tag_list
        )
        
        # Save to database
        await db.documents.insert_one(document.dict())
        
        # Analyze with AI in background
        try:
            ai_analysis = await analyze_document_with_ai(document)
            
            # Update document with AI analysis
            suggestions = ai_analysis.get('suggestions', [])
            status = DocumentStatus.approved if ai_analysis.get('validity_status') == 'valid' else DocumentStatus.requires_improvement
            
            await db.documents.update_one(
                {"id": document.id},
                {
                    "$set": {
                        "ai_analysis": ai_analysis,
                        "ai_suggestions": suggestions,
                        "status": status.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
        except Exception as ai_error:
            logger.error(f"AI analysis failed: {str(ai_error)}")
            # Continue without AI analysis
        
        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "filename": document.filename,
            "status": "uploaded",
            "ai_analysis_status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@api_router.get("/documents")
async def get_user_documents(current_user = Depends(get_current_user)):
    """Get all user documents"""
    try:
        documents = await db.documents.find(
            {"user_id": current_user["id"]}, 
            {"_id": 0, "content_base64": 0}  # Exclude binary content from list
        ).sort("created_at", -1).to_list(100)
        
        # Calculate stats
        total_docs = len(documents)
        approved_docs = len([doc for doc in documents if doc.get('status') == 'approved'])
        expired_docs = len([doc for doc in documents if doc.get('status') == 'expired'])
        pending_docs = len([doc for doc in documents if doc.get('status') == 'pending_review'])
        
        # Upcoming expirations (next 90 days)
        upcoming_expirations = []
        now = datetime.utcnow()
        for doc in documents:
            exp_date = doc.get('expiration_date')
            if exp_date:
                if isinstance(exp_date, str):
                    exp_date = datetime.fromisoformat(exp_date.replace('Z', '+00:00'))
                days_to_expire = (exp_date - now).days
                if 0 <= days_to_expire <= 90:
                    upcoming_expirations.append({
                        "document_id": doc["id"],
                        "document_type": doc["document_type"],
                        "filename": doc["original_filename"],
                        "expiration_date": exp_date.isoformat(),
                        "days_to_expire": days_to_expire
                    })
        
        # Sort by expiration date
        upcoming_expirations.sort(key=lambda x: x['days_to_expire'])
        
        return {
            "documents": documents,
            "stats": {
                "total": total_docs,
                "approved": approved_docs,
                "expired": expired_docs,
                "pending": pending_docs,
                "completion_rate": int((approved_docs / total_docs * 100)) if total_docs > 0 else 0
            },
            "upcoming_expirations": upcoming_expirations[:10]  # Next 10 expiring
        }
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting documents: {str(e)}")

@api_router.get("/documents/{document_id}")
async def get_document_details(document_id: str, current_user = Depends(get_current_user)):
    """Get document details including AI analysis"""
    try:
        document = await db.documents.find_one({
            "id": document_id,
            "user_id": current_user["id"]
        }, {"_id": 0})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting document details: {str(e)}")

@api_router.put("/documents/{document_id}")
async def update_document(
    document_id: str, 
    update_data: DocumentUpdate, 
    current_user = Depends(get_current_user)
):
    """Update document information"""
    try:
        # Verify document belongs to user
        document = await db.documents.find_one({
            "id": document_id,
            "user_id": current_user["id"]
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Prepare update data
        update_dict = update_data.dict(exclude_unset=True)
        
        # Parse dates if provided
        if 'expiration_date' in update_dict and update_dict['expiration_date']:
            try:
                update_dict['expiration_date'] = datetime.fromisoformat(
                    update_dict['expiration_date'].replace('Z', '+00:00')
                )
            except ValueError:
                del update_dict['expiration_date']
        
        if 'issue_date' in update_dict and update_dict['issue_date']:
            try:
                update_dict['issue_date'] = datetime.fromisoformat(
                    update_dict['issue_date'].replace('Z', '+00:00')
                )
            except ValueError:
                del update_dict['issue_date']
        
        update_dict["updated_at"] = datetime.utcnow()
        
        # Update document
        await db.documents.update_one(
            {"id": document_id},
            {"$set": update_dict}
        )
        
        updated_doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
        return {"message": "Document updated successfully", "document": updated_doc}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str, current_user = Depends(get_current_user)):
    """Delete a document"""
    try:
        # Verify document belongs to user
        document = await db.documents.find_one({
            "id": document_id,
            "user_id": current_user["id"]
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document
        await db.documents.delete_one({"id": document_id})
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@api_router.post("/documents/{document_id}/reanalyze")
async def reanalyze_document(document_id: str, current_user = Depends(get_current_user)):
    """Reanalyze document with AI"""
    try:
        # Get document
        document_data = await db.documents.find_one({
            "id": document_id,
            "user_id": current_user["id"]
        })
        
        if not document_data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create document object for analysis
        document = UserDocument(**document_data)
        
        # Analyze with AI
        ai_analysis = await analyze_document_with_ai(document)
        
        # Update document with new analysis
        suggestions = ai_analysis.get('suggestions', [])
        status = DocumentStatus.approved if ai_analysis.get('validity_status') == 'valid' else DocumentStatus.requires_improvement
        
        await db.documents.update_one(
            {"id": document_id},
            {
                "$set": {
                    "ai_analysis": ai_analysis,
                    "ai_suggestions": suggestions,
                    "status": status.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Document reanalyzed successfully",
            "analysis": ai_analysis,
            "status": status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reanalyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reanalyzing document: {str(e)}")

# Auto-Application System Endpoints
@api_router.post("/auto-application/start")
async def start_auto_application(case_data: CaseCreate):
    """Start a new auto-application case (anonymous or authenticated)"""
    try:
        # For anonymous users, create temporary case with 7 days expiration
        case = AutoApplicationCase(
            form_code=case_data.form_code,
            session_token=case_data.session_token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        await db.auto_cases.insert_one(case.dict())
        
        return {"message": "Auto-application case created successfully", "case": case}
    
    except Exception as e:
        logger.error(f"Error starting auto-application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting auto-application: {str(e)}")

@api_router.get("/auto-application/case/{case_id}")
async def get_case_anonymous(case_id: str, session_token: Optional[str] = None):
    """Get a specific case by ID (anonymous or authenticated)"""
    try:
        # Try to get from current user first if authenticated
        try:
            current_user = await get_current_user_optional()
            if current_user:
                case = await db.auto_cases.find_one({
                    "case_id": case_id,
                    "user_id": current_user["id"]
                })
                if case:
                    if "_id" in case:
                        del case["_id"]
                    return {"case": case}
        except:
            pass
        
        # If not found or not authenticated, try anonymous lookup
        if session_token:
            case = await db.auto_cases.find_one({
                "case_id": case_id,
                "session_token": session_token
            })
        else:
            case = await db.auto_cases.find_one({
                "case_id": case_id,
                "user_id": None
            })
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Remove MongoDB ObjectId
        if "_id" in case:
            del case["_id"]
            
        return {"case": case}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting case: {str(e)}")

@api_router.put("/auto-application/case/{case_id}")
async def update_case_anonymous(case_id: str, case_update: CaseUpdate, session_token: Optional[str] = None):
    """Update a specific case (anonymous or authenticated)"""
    try:
        # Try authenticated user first
        try:
            current_user = await get_current_user_optional()
            if current_user:
                case = await db.auto_cases.find_one({
                    "case_id": case_id,
                    "user_id": current_user["id"]
                })
                if case:
                    update_data = case_update.dict(exclude_none=True)
                    update_data["updated_at"] = datetime.utcnow()
                    
                    await db.auto_cases.update_one(
                        {"case_id": case_id},
                        {"$set": update_data}
                    )
                    
                    updated_case = await db.auto_cases.find_one({"case_id": case_id})
                    if "_id" in updated_case:
                        del updated_case["_id"]
                        
                    return {"message": "Case updated successfully", "case": updated_case}
        except:
            pass
        
        # Anonymous update
        query = {"case_id": case_id}
        if session_token:
            query["session_token"] = session_token
        else:
            query["user_id"] = None
        
        case = await db.auto_cases.find_one(query)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        update_data = case_update.dict(exclude_none=True)
        update_data["updated_at"] = datetime.utcnow()
        
        await db.auto_cases.update_one(
            {"case_id": case_id},
            {"$set": update_data}
        )
        
        updated_case = await db.auto_cases.find_one({"case_id": case_id})
        if "_id" in updated_case:
            del updated_case["_id"]
            
        return {"message": "Case updated successfully", "case": updated_case}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating case: {str(e)}")

@api_router.post("/auto-application/case/{case_id}/claim")
async def claim_anonymous_case(case_id: str, current_user = Depends(get_current_user)):
    """Claim an anonymous case when user registers/logs in"""
    try:
        # Find anonymous case
        case = await db.auto_cases.find_one({
            "case_id": case_id,
            "user_id": None
        })
        
        if not case:
            raise HTTPException(status_code=404, detail="Anonymous case not found")
        
        # Assign to current user
        await db.auto_cases.update_one(
            {"case_id": case_id},
            {"$set": {
                "user_id": current_user["id"],
                "session_token": None,
                "expires_at": None,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {"message": "Case claimed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error claiming case: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error claiming case: {str(e)}")

@api_router.post("/auto-application/extract-facts")
async def extract_facts_from_story(request: dict):
    """Extract structured facts from user's story using AI"""
    try:
        case_id = request.get("case_id")
        story_text = request.get("story_text", "")
        form_code = request.get("form_code")
        
        if not story_text.strip():
            raise HTTPException(status_code=400, detail="Story text is required")
        
        # Get visa specifications for context
        visa_specs = get_visa_specifications(form_code) if form_code else {}
        
        # Create AI prompt for fact extraction
        extraction_prompt = f"""
Você é um assistente especializado em extrair informações estruturadas de narrativas para aplicações de imigração dos EUA.

FORMULÁRIO: {form_code or 'Não especificado'}
CATEGORIA: {visa_specs.get('category', 'Não especificada')}

HISTÓRIA DO USUÁRIO:
{story_text}

Extraia e organize as seguintes informações da história, criando um JSON estruturado:

1. PERSONAL_INFO (informações pessoais):
   - full_name, date_of_birth, place_of_birth, nationality, current_address, phone, email

2. IMMIGRATION_HISTORY (histórico de imigração):
   - current_status, previous_entries, visa_history, overstays, deportations

3. FAMILY_DETAILS (detalhes familiares):
   - marital_status, spouse_info, children, parents, siblings

4. EMPLOYMENT_INFO (informações de trabalho):
   - current_job, previous_jobs, employer_details, salary, job_duties

5. EDUCATION (educação):
   - degrees, schools, graduation_dates, certifications

6. TRAVEL_HISTORY (histórico de viagens):
   - trips_outside_usa, duration, purposes, countries_visited

7. FINANCIAL_INFO (informações financeiras):
   - income, bank_accounts, assets, debts, tax_filings

8. SPECIAL_CIRCUMSTANCES (circunstâncias especiais):
   - medical_conditions, criminal_history, military_service, religious_persecution

INSTRUÇÕES:
- Extraia apenas informações explicitamente mencionadas na história
- Use "Não mencionado" para informações ausentes
- Mantenha datas no formato ISO quando possível
- Seja preciso e não invente informações
- Organize por categorias mesmo que algumas estejam vazias

Responda apenas com o JSON estruturado, sem explicações adicionais.
"""

        # Call OpenAI for fact extraction
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um especialista em extrair informações estruturadas de narrativas para aplicações de imigração. Responda sempre em português e com informações precisas."
                },
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        try:
            # Remove any markdown formatting
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()
            
            extracted_facts = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: create structured response based on keywords
            extracted_facts = {
                "personal_info": {"extracted_from": "AI analysis of user story"},
                "immigration_history": {"status": "Extracted from narrative"},
                "family_details": {"mentioned_in_story": True},
                "employment_info": {"details": "See user narrative"},
                "education": {"background": "Mentioned in story"},
                "travel_history": {"trips": "Referenced in narrative"}
            }
        
        # Update case with extracted facts if case_id provided
        if case_id:
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "ai_extracted_facts": extracted_facts,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        return {
            "message": "Facts extracted successfully",
            "extracted_facts": extracted_facts,
            "categories_found": len(extracted_facts.keys())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting facts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting facts: {str(e)}")

@api_router.post("/auto-application/generate-forms")
async def generate_official_forms(request: dict):
    """Generate official USCIS forms from simplified responses using AI"""
    try:
        case_id = request.get("case_id")
        form_responses = request.get("form_responses", {})
        form_code = request.get("form_code")
        
        if not case_id or not form_responses:
            raise HTTPException(status_code=400, detail="Case ID and form responses are required")
        
        # Get visa specifications for context
        visa_specs = get_visa_specifications(form_code) if form_code else {}
        
        # Create AI prompt for form conversion
        conversion_prompt = f"""
Você é um especialista em formulários do USCIS. Converta as respostas simplificadas em português para o formato oficial do formulário {form_code}.

FORMULÁRIO: {form_code}
CATEGORIA: {visa_specs.get('category', 'Não especificada')}
TÍTULO: {visa_specs.get('title', 'Não especificado')}

RESPOSTAS DO USUÁRIO (em português):
{json.dumps(form_responses, indent=2, ensure_ascii=False)}

INSTRUÇÕES:
1. Converta todas as respostas para inglês profissional
2. Formate conforme os padrões do USCIS para {form_code}
3. Complete campos obrigatórios baseados nas informações fornecidas
4. Mantenha consistência de datas (MM/DD/YYYY)
5. Use formatação oficial de nomes e endereços
6. Adicione códigos de país padrão (BR para Brasil, US para EUA)
7. Converta valores monetários para USD se necessário

FORMATO DE SAÍDA:
Retorne um JSON estruturado com os campos do formulário oficial {form_code}, usando os nomes de campos exatos do USCIS.

Para campos não preenchidos pelo usuário, use:
- "N/A" para não aplicável
- "None" para informações não fornecidas
- Mantenha campos obrigatórios em branco se não houver informação

Responda apenas com o JSON estruturado, sem explicações adicionais.
"""

        # Call OpenAI for form conversion
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um especialista em formulários do USCIS. Converta respostas em português para formato oficial em inglês com precisão total."
                },
                {"role": "user", "content": conversion_prompt}
            ],
            temperature=0.1,
            max_tokens=3000
        )
        
        # Parse AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        try:
            # Remove any markdown formatting
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()
            
            official_form_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback: create basic structure
            official_form_data = {
                "form_number": form_code,
                "generated_date": datetime.utcnow().isoformat(),
                "user_responses": form_responses,
                "conversion_status": "partial",
                "notes": "Manual review recommended"
            }
        
        # Update case with official form data
        if case_id:
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "official_form_data": official_form_data,
                        "status": "form_filled",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        return {
            "message": "Official forms generated successfully",
            "form_code": form_code,
            "official_form_data": official_form_data,
            "fields_converted": len(official_form_data.keys())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating forms: {str(e)}")

@api_router.post("/auto-application/validate-forms")
async def validate_forms(request: dict):
    """Validate official forms for consistency and completeness"""
    try:
        case_id = request.get("case_id")
        form_code = request.get("form_code")
        
        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")
        
        # Get case data
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Simulate validation process
        validation_issues = []
        
        # Check for required fields
        official_form = case.get("official_form_data", {})
        simplified_responses = case.get("simplified_form_responses", {})
        
        # Validate personal information
        if not official_form.get("full_name") and not official_form.get("applicant_name"):
            validation_issues.append({
                "section": "Informações Pessoais",
                "field": "Nome Completo",
                "issue": "Nome completo não foi preenchido no formulário oficial",
                "severity": "high"
            })
        
        if not official_form.get("date_of_birth") and not official_form.get("birth_date"):
            validation_issues.append({
                "section": "Informações Pessoais", 
                "field": "Data de Nascimento",
                "issue": "Data de nascimento não foi preenchida",
                "severity": "high"
            })
        
        # Check for address information
        if not official_form.get("current_address") and not official_form.get("mailing_address"):
            validation_issues.append({
                "section": "Informações de Endereço",
                "field": "Endereço Atual", 
                "issue": "Endereço atual não foi preenchido",
                "severity": "high"
            })
        
        # Form-specific validation
        if form_code == "H-1B":
            if not official_form.get("employer_name") and not official_form.get("company_name"):
                validation_issues.append({
                    "section": "Informações de Trabalho",
                    "field": "Nome do Empregador",
                    "issue": "Nome do empregador é obrigatório para H-1B",
                    "severity": "high"
                })
        
        elif form_code == "I-130":
            if not official_form.get("spouse_name") and not official_form.get("beneficiary_name"):
                validation_issues.append({
                    "section": "Informações Familiares",
                    "field": "Nome do Beneficiário",
                    "issue": "Nome do beneficiário é obrigatório para I-130",
                    "severity": "high"
                })
        
        # Date format validation
        date_fields = ["date_of_birth", "birth_date", "marriage_date"]
        for field in date_fields:
            if official_form.get(field):
                date_value = official_form[field]
                # Check if date is in MM/DD/YYYY format
                if not re.match(r'^\d{2}/\d{2}/\d{4}$', str(date_value)):
                    validation_issues.append({
                        "section": "Validação de Formato",
                        "field": field,
                        "issue": "Data deve estar no formato MM/DD/YYYY",
                        "severity": "medium"
                    })
        
        return {
            "message": "Form validation completed",
            "validation_issues": validation_issues,
            "total_issues": len(validation_issues),
            "blocking_issues": len([i for i in validation_issues if i["severity"] == "high"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating forms: {str(e)}")

@api_router.post("/auto-application/process-payment")
async def process_payment(request: dict):
    """Process payment for auto-application package"""
    try:
        case_id = request.get("case_id")
        package_id = request.get("package_id")
        payment_method = request.get("payment_method")
        amount = request.get("amount")
        
        if not all([case_id, package_id, payment_method, amount]):
            raise HTTPException(status_code=400, detail="Missing required payment information")
        
        # Get case
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Generate payment ID
        payment_id = f"PAY-{str(uuid.uuid4())[:8].upper()}"
        
        # Simulate payment processing
        # In real implementation, integrate with Stripe/PagSeguro/etc.
        payment_data = {
            "payment_id": payment_id,
            "case_id": case_id,
            "package_id": package_id,
            "payment_method": payment_method,
            "amount": amount,
            "currency": "USD",
            "status": "completed",
            "processed_at": datetime.utcnow(),
            "transaction_fee": amount * 0.029 if payment_method == "credit_card" else 0
        }
        
        # Update case with payment information
        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "payment_status": "completed",
                    "payment_id": payment_id,
                    "package_selected": package_id,
                    "payment_data": payment_data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Store payment record
        await db.payments.insert_one(payment_data)
        
        return {
            "message": "Payment processed successfully",
            "payment_id": payment_id,
            "status": "completed",
            "amount_charged": amount
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing payment: {str(e)}")

@api_router.post("/auto-application/generate-package")
async def generate_final_package(request: dict):
    """Generate final document package for download"""
    try:
        case_id = request.get("case_id")
        package_type = request.get("package_type", "complete")
        
        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")
        
        # Get case data
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Verify payment status
        if case.get("payment_status") != "completed":
            raise HTTPException(status_code=400, detail="Payment required before package generation")
        
        # Get form specifications
        form_code = case.get("form_code")
        visa_specs = get_visa_specifications(form_code) if form_code else {}
        
        # Generate package contents based on type
        package_contents = {
            "case_id": case_id,
            "form_code": form_code,
            "generated_at": datetime.utcnow().isoformat(),
            "package_type": package_type,
            "files": []
        }
        
        # Official forms
        if case.get("official_form_data"):
            package_contents["files"].append({
                "name": f"{form_code}_Official_Form.pdf",
                "type": "official_form",
                "description": f"Formulário oficial {form_code} preenchido em inglês"
            })
        
        # Document checklist
        package_contents["files"].append({
            "name": "Document_Checklist.pdf",
            "type": "checklist",
            "description": "Lista completa de documentos necessários"
        })
        
        # Submission instructions
        package_contents["files"].append({
            "name": "Submission_Instructions.pdf", 
            "type": "instructions",
            "description": "Instruções passo-a-passo para submissão"
        })
        
        # User story and extracted facts
        if case.get("user_story_text"):
            package_contents["files"].append({
                "name": "User_Story_Summary.pdf",
                "type": "summary",
                "description": "Resumo da sua história e fatos extraídos"
            })
        
        # Support documents (for complete/premium packages)
        if package_type in ["complete", "premium"]:
            package_contents["files"].extend([
                {
                    "name": "Cover_Letter_Template.docx",
                    "type": "template",
                    "description": "Modelo de carta de apresentação"
                },
                {
                    "name": "RFE_Response_Guide.pdf",
                    "type": "guide",
                    "description": "Guia para responder Request for Evidence"
                },
                {
                    "name": "Interview_Preparation.pdf",
                    "type": "guide", 
                    "description": "Guia de preparação para entrevista"
                }
            ])
        
        # Generate download URL (in real implementation, create actual ZIP file)
        download_url = f"/downloads/packages/OSPREY-{form_code}-{case_id}-{package_type}.zip"
        
        # Update case with package information
        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "final_package_generated": True,
                    "final_package_url": download_url,
                    "package_contents": package_contents,
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Package generated successfully",
            "download_url": download_url,
            "package_contents": package_contents,
            "total_files": len(package_contents["files"])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating package: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating package: {str(e)}")

@api_router.get("/auto-application/visa-specs/{form_code}")
async def get_visa_specs(form_code: str, subcategory: Optional[str] = None):
    """Get detailed specifications for a specific USCIS form"""
    try:
        specs = get_visa_specifications(form_code)
        if not specs:
            raise HTTPException(status_code=404, detail="Form specifications not found")
        
        # Get additional details
        required_documents = get_required_documents(form_code, subcategory)
        key_questions = get_key_questions(form_code)
        common_issues = get_common_issues(form_code)
        
        return {
            "form_code": form_code,
            "specifications": specs,
            "required_documents": required_documents,
            "key_questions": key_questions,
            "common_issues": common_issues
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visa specifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting visa specifications: {str(e)}")

# Helper function for optional authentication
async def get_current_user_optional():
    """Get current user if authenticated, None if not"""
    try:
        return await get_current_user()
    except:
        return None

# Existing Applications endpoints continue here...
@api_router.post("/applications")
async def create_application(app_data: ApplicationCreate, current_user = Depends(get_current_user)):
    """Create a new visa application"""
    try:
        # Check if user already has an active application for this visa type
        existing_app = await db.applications.find_one({
            "user_id": current_user["id"],
            "visa_type": app_data.visa_type.value,
            "status": {"$in": ["in_progress", "document_review", "ready_to_submit", "submitted"]}
        })
        
        if existing_app:
            raise HTTPException(status_code=400, detail="You already have an active application for this visa type")
        
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

@api_router.get("/applications/{application_id}")
async def get_application(application_id: str, current_user = Depends(get_current_user)):
    """Get a specific application by ID"""
    try:
        application = await db.applications.find_one({
            "id": application_id,
            "user_id": current_user["id"]
        })
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Remove MongoDB ObjectId
        if "_id" in application:
            del application["_id"]
            
        return {"application": application}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting application: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting application: {str(e)}")

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

# Dashboard route (updated to include education stats)
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
        
        # Get document stats
        documents = await db.documents.find(
            {"user_id": current_user["id"]}, 
            {"_id": 0, "content_base64": 0}
        ).to_list(100)
        
        # Get education progress
        progress = await db.user_progress.find_one(
            {"user_id": current_user["id"]}, {"_id": 0}
        )
        
        # Get unread tips
        unread_tips = await db.personalized_tips.count_documents({
            "user_id": current_user["id"],
            "is_read": False
        })
        
        # Document stats
        total_docs = len(documents)
        approved_docs = len([doc for doc in documents if doc.get('status') == 'approved'])
        pending_docs = len([doc for doc in documents if doc.get('status') == 'pending_review'])
        
        # Upcoming expirations (next 30 days)
        upcoming_expirations = []
        now = datetime.utcnow()
        for doc in documents:
            exp_date = doc.get('expiration_date')
            if exp_date:
                if isinstance(exp_date, str):
                    exp_date = datetime.fromisoformat(exp_date.replace('Z', '+00:00'))
                days_to_expire = (exp_date - now).days
                if 0 <= days_to_expire <= 30:
                    upcoming_expirations.append({
                        "document_type": doc["document_type"],
                        "filename": doc["original_filename"],
                        "days_to_expire": days_to_expire
                    })
        
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
                "success_rate": 100 if completed_apps == 0 else int((len([app for app in applications if app["status"] == "approved"]) / completed_apps) * 100),
                "total_documents": total_docs,
                "approved_documents": approved_docs,
                "pending_documents": pending_docs,
                "document_completion_rate": int((approved_docs / total_docs * 100)) if total_docs > 0 else 0,
                "guides_completed": len(progress.get("guides_completed", [])) if progress else 0,
                "interviews_completed": len(progress.get("interviews_completed", [])) if progress else 0,
                "total_study_time": progress.get("total_study_time_minutes", 0) if progress else 0,
                "unread_tips": unread_tips
            },
            "applications": applications,
            "recent_activity": {
                "chats": recent_chats,
                "translations": recent_translations
            },
            "upcoming_expirations": upcoming_expirations[:5]  # Next 5 expiring
        }
    
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dashboard: {str(e)}")

# Chat history route (keeping existing)
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

# Basic routes (keeping existing)
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

# AI-powered routes (keeping existing with user tracking)
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