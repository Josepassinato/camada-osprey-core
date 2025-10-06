"""
Advanced Analytics Data Models
Sistema completo de analytics para aplicação de imigração
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from enum import Enum
import uuid

# Analytics Event Types
class EventType(str, Enum):
    USER_SIGNUP = "user_signup"
    USER_LOGIN = "user_login"
    CASE_STARTED = "case_started"
    FORM_SELECTED = "form_selected"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_ANALYZED = "document_analyzed"
    DOCUMENT_VALIDATED = "document_validated"
    AI_CHAT_SESSION = "ai_chat_session"
    COVER_LETTER_GENERATED = "cover_letter_generated"
    CASE_COMPLETED = "case_completed"
    ERROR_OCCURRED = "error_occurred"
    API_CALL = "api_call"
    PROCESSING_TIME = "processing_time"

class AnalyticsEvent(BaseModel):
    """Base analytics event model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    case_id: Optional[str] = None
    
    # Event-specific data
    properties: Dict[str, Any] = {}
    
    # Performance metrics
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None

class DocumentProcessingMetrics(BaseModel):
    """Metrics for document processing analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    document_type: str
    validator_type: str  # social_security, tax_document, medical_record, utility_bill, etc.
    
    # Processing metrics
    ocr_start_time: datetime
    ocr_end_time: datetime
    ocr_duration_ms: float
    validation_duration_ms: float
    total_processing_time_ms: float
    
    # Quality metrics
    confidence_score: float
    validation_status: str  # VALID, INVALID, SUSPICIOUS
    issues_found: List[str] = []
    
    # File metrics
    file_size_bytes: int
    file_type: str
    image_resolution: Optional[str] = None
    
    # Results
    fields_extracted: int
    fields_validated: int
    extraction_accuracy: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserJourneyMetrics(BaseModel):
    """User journey and conversion metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: Optional[str] = None
    
    # Journey stages
    journey_start: datetime
    form_selection_time: Optional[datetime] = None
    basic_data_completion_time: Optional[datetime] = None
    document_upload_start_time: Optional[datetime] = None
    first_document_uploaded_time: Optional[datetime] = None
    all_documents_uploaded_time: Optional[datetime] = None
    case_completion_time: Optional[datetime] = None
    
    # Conversion metrics
    completed_form_selection: bool = False
    completed_basic_data: bool = False
    started_document_upload: bool = False
    completed_document_upload: bool = False
    completed_case: bool = False
    
    # Drop-off analysis
    dropped_off: bool = False
    drop_off_stage: Optional[str] = None
    drop_off_time: Optional[datetime] = None
    
    # Retry patterns
    retry_attempts: Dict[str, int] = {}  # stage -> attempt_count
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AIModelMetrics(BaseModel):
    """AI model performance metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str  # dr_paula, document_validator, ocr_engine, etc.
    request_id: str
    
    # Request details
    request_type: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    
    # Performance metrics
    request_start_time: datetime
    request_end_time: datetime
    response_time_ms: float
    
    # Quality metrics
    success: bool
    confidence_score: Optional[float] = None
    user_feedback: Optional[str] = None  # positive, negative, neutral
    
    # Error tracking
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    # Context
    visa_type: Optional[str] = None
    document_type: Optional[str] = None
    user_language: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessIntelligenceMetrics(BaseModel):
    """Business intelligence and usage metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: date
    
    # User metrics
    new_users: int = 0
    active_users: int = 0
    returning_users: int = 0
    
    # Application metrics
    cases_started: int = 0
    cases_completed: int = 0
    conversion_rate: float = 0.0
    
    # Document metrics
    documents_uploaded: int = 0
    documents_processed: int = 0
    average_processing_time_ms: float = 0.0
    
    # Visa type breakdown
    visa_type_distribution: Dict[str, int] = {}
    
    # Geographic data
    country_distribution: Dict[str, int] = {}
    
    # Revenue metrics (if applicable)
    revenue: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SystemHealthMetrics(BaseModel):
    """Real-time system health metrics"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # System resources
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    
    # API metrics
    active_requests: int
    requests_per_minute: float
    average_response_time_ms: float
    error_rate_percent: float
    
    # Database metrics
    database_connections: int
    query_average_time_ms: float
    
    # AI services
    ai_service_status: Dict[str, str] = {}  # service_name -> "healthy" | "degraded" | "down"
    ai_queue_size: int = 0
    
    # Document processing queue
    documents_in_queue: int = 0
    ocr_processing_active: int = 0
    
    # Alerts
    active_alerts: List[str] = []

class PerformanceBenchmark(BaseModel):
    """Performance benchmarks and thresholds"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_type: str
    benchmark_value: float
    current_value: float
    threshold_warning: float
    threshold_critical: float
    
    status: str = "normal"  # normal, warning, critical
    
    measured_at: datetime = Field(default_factory=datetime.utcnow)

# Analytics Query Models
class AnalyticsQuery(BaseModel):
    """Base analytics query model"""
    start_date: date
    end_date: date
    filters: Dict[str, Any] = {}
    group_by: Optional[str] = None
    metrics: List[str] = []

class DocumentAnalyticsQuery(AnalyticsQuery):
    """Document processing analytics query"""
    document_types: Optional[List[str]] = None
    validator_types: Optional[List[str]] = None
    confidence_threshold: Optional[float] = None

class UserJourneyQuery(AnalyticsQuery):
    """User journey analytics query"""
    visa_types: Optional[List[str]] = None
    completion_status: Optional[str] = None  # completed, dropped_off, all

class AIPerformanceQuery(AnalyticsQuery):
    """AI performance analytics query"""
    model_names: Optional[List[str]] = None
    success_only: bool = False

# Analytics Response Models
class AnalyticsResponse(BaseModel):
    """Base analytics response"""
    query: AnalyticsQuery
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentAnalyticsResponse(AnalyticsResponse):
    """Document processing analytics response"""
    total_documents_processed: int
    average_processing_time_ms: float
    average_confidence_score: float
    success_rate: float
    validation_status_distribution: Dict[str, int]
    validator_performance: Dict[str, Dict[str, Any]]

class UserJourneyResponse(AnalyticsResponse):
    """User journey analytics response"""
    total_sessions: int
    conversion_funnel: Dict[str, float]
    average_time_to_complete_ms: float
    drop_off_analysis: Dict[str, int]
    retry_patterns: Dict[str, float]

class AIPerformanceResponse(AnalyticsResponse):
    """AI performance analytics response"""
    total_requests: int
    average_response_time_ms: float
    success_rate: float
    model_performance: Dict[str, Dict[str, Any]]
    error_distribution: Dict[str, int]

class BusinessIntelligenceResponse(AnalyticsResponse):
    """Business intelligence response"""
    total_users: int
    total_cases: int
    revenue: float
    growth_metrics: Dict[str, float]
    geographic_insights: Dict[str, Any]
    visa_type_insights: Dict[str, Any]

class SystemHealthResponse(BaseModel):
    """Real-time system health response"""
    overall_status: str  # healthy, degraded, critical
    system_metrics: SystemHealthMetrics
    service_statuses: Dict[str, str]
    active_alerts: List[str]
    recommendations: List[str]
    last_updated: datetime = Field(default_factory=datetime.utcnow)