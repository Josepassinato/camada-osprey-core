import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models.enums import DifficultyLevel, InterviewType, VisaType


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    tip_category: str
    title: str
    content: str
    priority: str
    visa_type: Optional[VisaType] = None
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeBaseQuery(BaseModel):
    query: str
    visa_type: Optional[VisaType] = None
    category: Optional[str] = None
