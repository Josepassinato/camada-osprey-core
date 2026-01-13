from datetime import datetime
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
