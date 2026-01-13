import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from models.enums import USCISForm


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


class AutoApplicationCase(BaseModel):
    case_id: str = Field(default_factory=lambda: f"OSP-{str(uuid.uuid4())[:8].upper()}")
    user_id: Optional[str] = None
    session_token: Optional[str] = None
    form_code: Optional[USCISForm] = None
    status: CaseStatus = CaseStatus.created

    process_type: Optional[str] = None

    progress_percentage: int = 0
    current_step: Optional[str] = None

    basic_data: Optional[Dict[str, Any]] = None

    uploaded_documents: list[str] = []
    document_analysis: Optional[Dict[str, Any]] = None

    user_story_text: Optional[str] = None
    user_story_audio_url: Optional[str] = None
    ai_extracted_facts: Optional[Dict[str, Any]] = None

    simplified_form_responses: Optional[Dict[str, Any]] = None
    official_form_data: Optional[Dict[str, Any]] = None
    uscis_form_generated: bool = False

    ead_data: Optional[Dict[str, Any]] = None

    ai_processing: Optional[Dict[str, Any]] = None

    payment_status: Optional[str] = None
    payment_id: Optional[str] = None
    final_package_generated: bool = False
    final_package_url: Optional[str] = None
    completed_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


class CaseCreate(BaseModel):
    form_code: Optional[USCISForm] = None
    process_type: Optional[str] = None
    session_token: Optional[str] = None


class CaseUpdate(BaseModel):
    form_code: Optional[USCISForm] = None
    process_type: Optional[str] = None
    status: Optional[CaseStatus] = None
    basic_data: Optional[Dict[str, Any]] = None
    user_story_text: Optional[str] = None
    simplified_form_responses: Optional[Dict[str, Any]] = None
    progress_percentage: Optional[int] = None
    current_step: Optional[str] = None
    ead_data: Optional[Dict[str, Any]] = None
    letters: Optional[Dict[str, Any]] = None
    forms: Optional[Dict[str, Any]] = None
