import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "user"  # "user" | "admin" | "superadmin"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "user"  # "user" | "admin" | "superadmin"
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
