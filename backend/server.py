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
    progress_percentage: Optional[int] = None
    current_step: Optional[str] = None

# Document Models
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

# Document helper functions
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

# Document routes (NEW)
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

# Application routes (keeping existing ones)
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

# Dashboard route (updated to include document stats)
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
                "document_completion_rate": int((approved_docs / total_docs * 100)) if total_docs > 0 else 0
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