# Osprey Backend - Enterprise Immigration AI Platform

FastAPI-based backend API for the Osprey B2C immigration case processing system. This service orchestrates multi-agent AI systems, document processing, payment workflows, and USCIS form generation.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [Environment Configuration](#environment-configuration)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [API Modules](#api-modules)
- [Models](#models)
- [Services](#services)
- [AI Agent System](#ai-agent-system)
- [Database Schema](#database-schema)
- [Authentication & Security](#authentication--security)
- [External Integrations](#external-integrations)
- [Logging & Observability](#logging--observability)
- [Development Guide](#development-guide)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Design Patterns](#design-patterns)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Recent Fixes](#recent-fixes)
- [AI Agent Guidelines](#ai-agent-guidelines)

---

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB 6.0+ (local or remote)
- Required API keys (OpenAI, Stripe, etc. - see [Environment Configuration](#environment-configuration))

### Installation

```bash
cd backend
pip3 install -r requirements.txt
```

### Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env
```

### Run Development Server

```bash
python3 server.py
```

The API will be available at:
- **API Server**: `http://localhost:8001`
- **Interactive API Docs**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

---

## Architecture Overview

Osprey Backend follows a **modular, domain-driven architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend SPA                         │
│                   (Vite + React + TypeScript)              │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│                    FastAPI Application                      │
│                      (server.py)                            │
├─────────────────────────────────────────────────────────────┤
│  Middleware: CORS, Auth, Error Handling, Logging           │
└─────┬────────┬────────┬────────┬────────┬──────────────────┘
      │        │        │        │        │
┌─────▼────┐ ┌▼────┐ ┌─▼─────┐ ┌▼─────┐ ┌▼──────┐
│  API     │ │Core │ │Models │ │Servs │ │Agents │
│ Routers  │ │Utils│ │Pydantic││Logic │ │AI/LLM │
└─────┬────┘ └┬────┘ └───────┘ └┬─────┘ └┬──────┘
      │       │                  │        │
      └───────┴──────────────────┴────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼───┐  ┌────▼────┐  ┌───▼────┐
    │MongoDB │  │External │  │ Cache  │
    │        │  │APIs     │  │ Redis  │
    └────────┘  └─────────┘  └────────┘
```

### Key Architectural Principles

1. **API-First Design**: All functionality exposed via RESTful API with OpenAPI documentation
2. **Domain Separation**: Routers in `api/` handle HTTP, services in `services/` handle business logic
3. **Type Safety**: Pydantic models for request/response validation
4. **Async-First**: Motor (async MongoDB driver) for non-blocking I/O
5. **Multi-Agent AI**: Coordinated specialist agents for document validation, form filling, QA
6. **Observable**: Structured logging + Sentry integration for production monitoring

---

## Technology Stack

### Core Framework
- **FastAPI 0.110.1**: Modern, fast web framework for building APIs
- **Uvicorn 0.25.0**: ASGI server for running FastAPI
- **Pydantic 2.11.7**: Data validation and settings management
- **Python 3.11+**: Type hints, async/await, pattern matching

### Database & Storage
- **MongoDB 6.0+**: Primary database (via Motor 3.3.1 async driver)
- **PyMongo 4.5.0**: Synchronous MongoDB driver (for scripts)
- **Redis** (optional): Session cache and rate limiting

### AI & Machine Learning
- **OpenAI API 1.99.9**: GPT-4o, GPT-4-turbo for reasoning and generation
- **Google Gemini 1.39.1**: Multi-modal AI for document analysis
- **LiteLLM 1.77.4**: Unified LLM interface for multiple providers
- **Google Document AI 3.6.0+**: OCR and structured document extraction
- **Google Vision AI 3.10.2+**: Image analysis and document classification

### Payments & Email
- **Stripe 12.5.1**: Payment processing, subscriptions, webhooks
- **Resend 2.17.0**: Transactional email delivery

### Document Processing
- **PyMuPDF 1.25.3**: PDF parsing and manipulation
- **PyPDF2 3.0.1**: PDF merging and splitting
- **ReportLab 4.4.4**: PDF generation for official documents
- **FPDF2 2.8.4**: Simple PDF creation
- **pdfplumber**: Table extraction from PDFs
- **python-docx 0.8.11+**: Word document generation

### Security & Authentication
- **PyJWT 2.10.1**: JWT token generation and validation
- **bcrypt 4.3.0**: Password hashing
- **python-jose 3.5.0**: JOSE implementation for JWT

### Observability
- **Sentry SDK 2.20.0**: Error tracking, performance monitoring, profiling
- **APScheduler 3.10.4**: Background job scheduling
- **Python logging**: Structured JSON logging

### Development Tools
- **Black 25.1.0**: Code formatting
- **Flake8 7.3.0**: Linting
- **MyPy 1.17.1**: Static type checking
- **Pytest 8.4.1**: Testing framework

---

## Environment Configuration

### Required Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Copy from example
cp .env.example .env
```

#### MongoDB Configuration
```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=osprey_db
```

#### Authentication
```bash
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
```

#### AI / LLM Providers
```bash
# OpenAI (Required for GPT-4, GPT-3.5)
OPENAI_API_KEY=sk-...

# Google Gemini (Required for multi-modal AI)
GEMINI_API_KEY=...

# Emergent LLM (Optional alternative provider)
EMERGENT_LLM_KEY=...

# Google Cloud (Required for Document AI and Vision)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us
```

#### Stripe Payment Processing
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_API_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

#### Email (Resend)
```bash
RESEND_API_KEY=re_...
SENDER_EMAIL=noreply@yourdomain.com
```

#### CORS Configuration
```bash
# Development: allow frontend on different port
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Production: specific domain only
CORS_ORIGINS=https://yourdomain.com
```

#### Logging Configuration
```bash
# Log Level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Development: pretty, colorized logs
LOG_PRETTY=true
LOG_FORMAT=plain

# Production: structured JSON logs
LOG_PRETTY=false
LOG_FORMAT=json

# Backup directory for MongoDB exports
BACKUP_DIR=/var/backups/osprey
```

#### Sentry Configuration (Production Monitoring)
```bash
# Required for error tracking
SENTRY_DSN=https://...@sentry.io/...

# Environment identifier
SENTRY_ENVIRONMENT=production

# Service identification
SENTRY_SERVICE_NAME=osprey-backend
SENTRY_SERVER_NAME=api-server-01

# Release tracking
SENTRY_RELEASE=v2.1.0

# Sampling rates (0.0 to 1.0)
SENTRY_TRACES_SAMPLE_RATE=0.1      # 10% of requests traced
SENTRY_PROFILES_SAMPLE_RATE=0.05   # 5% of requests profiled

# Debug mode (development only)
SENTRY_DEBUG=false

# Send PII (be careful in production)
SENTRY_SEND_PII=false

# Custom tags (JSON format)
SENTRY_TAGS={"team":"backend","region":"us-east-1"}
```

### Environment File Structure

See `.env.example` for complete configuration template with descriptions.

---

## Project Structure

```
backend/
├── server.py                    # FastAPI app initialization, router registration
│
├── core/                        # Core infrastructure utilities
│   ├── __init__.py
│   ├── auth.py                 # JWT authentication, password hashing
│   ├── database.py             # MongoDB lifecycle, schedulers, DBProxy
│   ├── logging.py              # Structured logging setup
│   ├── serialization.py        # MongoDB-safe response serialization
│   └── sentry.py               # Sentry initialization and integrations
│
├── api/                         # API route handlers (domain-organized)
│   ├── __init__.py
│   ├── auth.py                 # POST /login, /register, /verify-token
│   ├── education.py            # Education history endpoints
│   ├── documents.py            # Document upload, OCR, analysis
│   ├── payments.py             # Stripe checkout, webhooks, vouchers
│   ├── admin_products.py       # Admin product management (uses backend.admin.products)
│   ├── owl_agent.py            # Intelligent Owl AI agent flows
│   ├── auto_application.py     # Auto-application CRUD operations
│   ├── auto_application_ai.py  # AI processing, QA, validation
│   ├── auto_application_packages.py  # Package generation, instructions
│   ├── auto_application_downloads.py # Case package downloads
│   ├── uscis_forms.py          # USCIS form generation, field mapping
│   ├── knowledge_base.py       # Admin knowledge base management (uses backend.admin.security)
│   ├── downloads.py            # Generic download endpoints
│   ├── email_packages.py       # Email delivery via Resend
│   ├── agents.py               # Agent coordination endpoints
│   ├── specialized_agents.py   # Specialized agent invocation
│   ├── completeness.py         # Case completeness analysis
│   ├── friendly_form.py        # User-friendly form submission
│   ├── voice.py                # Voice websocket, transcription
│   ├── oracle.py               # Oracle consultant AI
│   └── visa_updates_admin.py   # Admin visa update management
│
├── models/                      # Pydantic models (request/response schemas)
│   ├── __init__.py
│   ├── auto_application.py     # CaseStatus, AutoApplicationCase, CaseCreate
│   ├── documents.py            # Document models
│   ├── education.py            # Education models
│   ├── enums.py                # VisaType, DifficultyLevel, USCISForm, etc.
│   └── user.py                 # User, UserProgress models
│
├── services/                    # Business logic layer
│   ├── __init__.py
│   ├── cases.py                # Case status, progress tracking
│   ├── documents.py            # Document processing logic
│   └── education.py            # Education validation logic
│
├── policies/                    # Policy definitions (YAML)
│   └── *.yaml                  # Immigration policy rules
│
├── .env                         # Environment configuration (DO NOT COMMIT)
├── .env.example                # Example environment file
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Legacy/Standalone Files (to be refactored)

These files contain agent logic and utilities that will eventually be moved into `services/` or `api/`:

- **AI Agents**: `maria_agent.py`, `oracle_consultant.py`, `specialized_agents.py`, `conversational_assistant.py`
- **Document Processing**: `document_analyzer_agent.py`, `document_data_extractor.py`, `enhanced_document_recognition.py`
- **Form Filling**: `form_filler_agent.py`, `uscis_form_filler.py`, `friendly_form_structures.py`
- **QA System**: `professional_qa_agent.py`, `qa_feedback_orchestrator.py`, `advanced_immigration_reviewer.py`
- **Learning Systems**: `agent_learning_system.py`, `iterative_learning_system.py`, `feedback_system.py`
- **Admin Tools**: `backend/admin/knowledge_base.py`, `backend/admin/products.py`, `backend/admin/security.py`
- **Utilities**: `input_sanitizer.py`, `validators.py`, `rate_limiter.py`, `translation_agent.py`
- **Scripts**: `create_admin_user.py`, `create_superadmin.py`, `mongodb_backup.py`

---

## Core Modules

### `core/auth.py`
JWT-based authentication system.

**Key Functions**:
```python
def hash_password(password: str) -> str
def verify_password(password: str, hashed: str) -> bool
def create_jwt_token(user_id: str, email: str) -> str
def verify_jwt_token(token: str) -> dict | None
async def get_current_user(credentials) -> dict  # FastAPI dependency
```

**Usage Pattern**:
```python
from fastapi import Depends
from core.auth import get_current_user

@router.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"user_id": user["id"], "email": user["email"]}
```

### `core/database.py`
MongoDB connection lifecycle management with async support.

**Key Components**:
- `startup_db_client()`: Initialize MongoDB connection on app startup
- `shutdown_db_client()`: Gracefully close connection on shutdown
- `DBProxy`: Proxy object to prevent `None` database errors
- Schedulers: APScheduler integration for background jobs

**Usage Pattern**:
```python
from core.database import db

# In route handlers
case = await db.auto_cases.find_one({"case_id": case_id})
await db.users.update_one({"id": user_id}, {"$set": {"verified": True}})
```

### `core/logging.py`
Structured logging with environment-based configuration.

**Configuration**:
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LOG_PRETTY`: true (colorized) / false (plain)
- `LOG_FORMAT`: plain / json (for production)

**Usage Pattern**:
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Case created", extra={"case_id": case_id, "user_id": user_id})
logger.warning("Payment failed", extra={"error": str(e)})
logger.error("Database connection lost", exc_info=True)
```

### `core/serialization.py`
MongoDB-safe response serialization (handles ObjectId, datetime).

**Key Functions**:
```python
def serialize_doc(doc: dict) -> dict
```

**Usage Pattern**:
```python
from core.serialization import serialize_doc

case = await db.auto_cases.find_one({"case_id": case_id})
return serialize_doc(case)  # Converts ObjectId to string, datetime to ISO
```

### `core/sentry.py`
Sentry initialization for error tracking and performance monitoring.

**Integrations**:
- FastAPI (request tracking, error capture)
- Starlette (middleware integration)
- AioHTTP (async HTTP client tracing)
- Asyncio (task monitoring)
- HTTPX (modern HTTP client tracing)
- Logging (breadcrumb capture)

**Configuration**: See [Environment Configuration](#environment-configuration) for Sentry env vars.

---

## API Modules

### Authentication - `api/auth.py`

**Endpoints**:
- `POST /api/login`: User login, returns JWT token
- `POST /api/register`: User registration
- `POST /api/verify-token`: Verify JWT token validity

**Request/Response**:
```python
# POST /api/login
Request: {"email": "user@example.com", "password": "secret"}
Response: {"token": "eyJ...", "user": {...}}

# POST /api/verify-token
Headers: {"Authorization": "Bearer eyJ..."}
Response: {"valid": true, "user": {...}}
```

### Documents - `api/documents.py`

**Endpoints**:
- `POST /api/documents/upload`: Upload and analyze document
- `GET /api/documents/{doc_id}`: Retrieve document metadata
- `DELETE /api/documents/{doc_id}`: Delete document
- `POST /api/documents/analyze`: Trigger AI document analysis

**Features**:
- OCR via Google Document AI
- Document classification (passport, birth certificate, etc.)
- Field extraction (name, date of birth, etc.)
- Quality validation
- Dr. Miguel agent integration for medical documents

### Auto Application - `api/auto_application.py`

**Endpoints**:
- `POST /api/auto-application/cases`: Create new case
- `GET /api/auto-application/cases/{case_id}`: Retrieve case
- `PATCH /api/auto-application/cases/{case_id}`: Update case
- `GET /api/auto-application/cases`: List user's cases

**Case Lifecycle**:
1. `created` → User selects visa form
2. `form_selected` → Story/background recorded
3. `friendly_form_partial` → User fills friendly form
4. `friendly-form-complete` → Documents uploaded
5. `ai_processing` → AI agents analyze and validate
6. `form_generated` → USCIS forms generated
7. `qa_passed` → Quality assurance complete
8. `finalized` → Package ready for submission

### Auto Application AI - `api/auto_application_ai.py`

**Endpoints**:
- `POST /api/auto-application/cases/{case_id}/process-ai`: Trigger AI processing
- `POST /api/auto-application/cases/{case_id}/qa`: Run QA validation
- `POST /api/auto-application/cases/{case_id}/directives`: Generate cover letter directives
- `POST /api/auto-application/cases/{case_id}/review-letter`: Review cover letter
- `POST /api/auto-application/cases/{case_id}/generate-letter`: Generate final letter

**AI Agent Workflow**:
1. **Document Validator**: Verify all required documents present and valid
2. **Form Validator**: Check data completeness and consistency
3. **Eligibility Analyst**: Assess visa eligibility based on user data
4. **Compliance Checker**: Verify USCIS policy compliance
5. **Letter Writer**: Generate compelling cover letter
6. **USCIS Translator**: Map data to official form fields
7. **QA Agent**: Final quality assurance check

### Payments - `api/payments.py`

**Endpoints**:
- `POST /api/payments/create-checkout-session`: Create Stripe checkout
- `POST /api/payments/webhook`: Stripe webhook handler
- `POST /api/payments/apply-voucher`: Apply discount voucher
- `POST /api/payments/process-payment`: Process auto-application payment

**Payment Flow**:
1. Frontend creates checkout session
2. User redirected to Stripe Checkout
3. User completes payment
4. Stripe sends webhook to backend
5. Backend updates case status and grants access

### USCIS Forms - `api/uscis_forms.py`

**Endpoints**:
- `POST /api/uscis-forms/generate`: Generate filled USCIS form PDF
- `GET /api/uscis-forms/{form_code}/fields`: Get form field metadata
- `POST /api/uscis-forms/{form_code}/validate`: Validate form data

**Supported Forms**:
- I-130 (Petition for Alien Relative)
- I-539 (Application to Extend/Change Nonimmigrant Status)
- I-765 (Application for Employment Authorization)
- I-90 (Application to Replace Permanent Resident Card)
- I-485 (Application to Register Permanent Residence)
- N-400 (Application for Naturalization)

---

## Models

### `models/enums.py`

Standard enums used throughout the application.

**VisaType**:
```python
class VisaType(str, Enum):
    h1b = "h1b"
    l1 = "l1"
    o1 = "o1"
    eb5 = "eb5"
    f1 = "f1"
    b1b2 = "b1b2"
    green_card = "green_card"
    family = "family"
```

**USCISForm**:
```python
class USCISForm(str, Enum):
    N400 = "N-400"
    I130 = "I-130"
    I765 = "I-765"
    I485 = "I-485"
    I90 = "I-90"
    I539 = "I-539"
    # ... and more
```

**DifficultyLevel**:
```python
class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
```

### `models/auto_application.py`

**CaseStatus**:
```python
class CaseStatus(str, Enum):
    created = "created"
    form_selected = "form_selected"
    in_progress = "in_progress"
    processing = "processing"
    ready_for_submission = "ready_for_submission"
    completed = "completed"
```

**AutoApplicationCase**:
```python
class AutoApplicationCase(BaseModel):
    case_id: str
    user_id: str
    form_code: USCISForm
    status: CaseStatus
    current_step: str
    progress_percentage: int
    basic_data: dict | None
    friendly_form_data: dict | None
    documents: list[dict]
    ai_analysis: dict | None
    qa_results: dict | None
    created_at: datetime
    updated_at: datetime
```

---

## Services

### `services/cases.py`

Business logic for case management.

**Key Functions**:
```python
def get_progress_percentage(step: str) -> int
    """Calculate progress percentage based on current step."""

async def update_case_status_and_progress(
    case_id: str,
    new_step: str,
    collection_name: str = "auto_cases"
):
    """Update case status and progress in database."""
```

**Usage**:
```python
from services.cases import update_case_status_and_progress

await update_case_status_and_progress(
    case_id="OSP-12345",
    new_step="documents_uploaded"
)
# Sets progress to 60%, status to "in_progress"
```

---

## AI Agent System

Osprey uses a **multi-agent architecture** where specialized AI agents collaborate to process immigration cases.

### Agent Coordinator

The `SpecializedAgentCoordinator` orchestrates agent execution based on case requirements.

```python
from specialized_agents import SpecializedAgentCoordinator

coordinator = SpecializedAgentCoordinator()
result = await coordinator.process_case(case_data)
```

### Specialized Agents

#### 1. Document Validation Agent
**Purpose**: Verify document authenticity, completeness, and quality.

**Capabilities**:
- OCR quality assessment
- Document type classification
- Missing information detection
- Fraud detection indicators

**Creation**:
```python
from specialized_agents import create_document_validator

agent = create_document_validator()
result = await agent.validate(documents)
```

#### 2. Form Validator Agent
**Purpose**: Ensure form data is complete and consistent.

**Capabilities**:
- Required field validation
- Data format verification
- Cross-field consistency checks
- USCIS requirement compliance

#### 3. Eligibility Analyst Agent
**Purpose**: Assess visa eligibility based on user profile.

**Capabilities**:
- Visa category recommendation
- Qualification assessment
- Alternative visa suggestions
- Risk factor identification

#### 4. Compliance Checker Agent
**Purpose**: Verify USCIS policy and regulation compliance.

**Capabilities**:
- Policy rule validation
- Inadmissibility screening
- Fee verification
- Processing time estimation

#### 5. Immigration Letter Writer Agent
**Purpose**: Generate compelling cover letters and supporting documents.

**Capabilities**:
- Personalized narrative generation
- Evidence highlighting
- Legal argument structuring
- Tone and style optimization

#### 6. USCIS Form Translator Agent
**Purpose**: Map user-friendly data to official USCIS form fields.

**Capabilities**:
- Field mapping (friendly → official)
- Data transformation (formats, codes)
- Multi-form coordination
- PDF generation and filling

#### 7. Professional QA Agent
**Purpose**: Final quality assurance before submission.

**Capabilities**:
- End-to-end validation
- Common mistake detection
- Submission readiness scoring
- Improvement recommendations

### Agent Communication Pattern

Agents communicate via structured JSON messages:

```json
{
  "agent": "document_validator",
  "status": "completed",
  "confidence": 0.95,
  "findings": [
    {
      "type": "warning",
      "message": "Passport photo quality is low",
      "recommendation": "Re-upload higher resolution image"
    }
  ],
  "data": {
    "documents_valid": true,
    "missing_documents": []
  }
}
```

---

## Database Schema

### Collections

#### `users`
User accounts and profiles.

```javascript
{
  _id: ObjectId,
  id: "uuid-v4",
  email: "user@example.com",
  password_hash: "bcrypt-hash",
  first_name: "John",
  last_name: "Doe",
  verified: true,
  created_at: ISODate,
  updated_at: ISODate
}
```

#### `auto_cases` / `auto_application_cases`
Immigration case tracking.

```javascript
{
  _id: ObjectId,
  case_id: "OSP-ABC123",
  user_id: "uuid-v4",
  form_code: "I-539",
  status: "in_progress",
  current_step: "documents_uploaded",
  progress_percentage: 60,
  basic_data: {
    firstName: "John",
    lastName: "Doe",
    dateOfBirth: "1990-01-01",
    // ... more fields
  },
  friendly_form_data: { /* friendly form responses */ },
  documents: [
    {
      id: "doc-uuid",
      type: "passport",
      url: "s3://...",
      status: "validated"
    }
  ],
  ai_analysis: { /* AI agent results */ },
  qa_results: { /* QA validation results */ },
  created_at: ISODate,
  updated_at: ISODate
}
```

#### `documents`
Document metadata and analysis results.

```javascript
{
  _id: ObjectId,
  id: "doc-uuid",
  user_id: "uuid-v4",
  case_id: "OSP-ABC123",
  file_name: "passport.pdf",
  file_type: "application/pdf",
  file_size: 1024000,
  storage_url: "s3://bucket/path",
  document_type: "passport",
  ocr_text: "extracted text",
  extracted_data: {
    passport_number: "123456789",
    issue_date: "2020-01-01",
    expiry_date: "2030-01-01"
  },
  validation_status: "valid",
  uploaded_at: ISODate
}
```

#### `payments`
Payment transactions and status.

```javascript
{
  _id: ObjectId,
  payment_id: "pay-uuid",
  user_id: "uuid-v4",
  case_id: "OSP-ABC123",
  stripe_session_id: "cs_...",
  stripe_payment_intent: "pi_...",
  amount: 29900,  // cents
  currency: "usd",
  status: "succeeded",
  product_id: "prod-uuid",
  created_at: ISODate,
  paid_at: ISODate
}
```

#### `visa_updates`
Admin-managed visa information updates.

```javascript
{
  _id: ObjectId,
  id: "update-uuid",
  form_code: "I-539",
  update_type: "processing_time",
  source: "uscis",
  detected_date: ISODate,
  effective_date: ISODate,
  title: "Processing time update",
  description: "Average processing reduced to 6 months",
  old_value: {"months": 8},
  new_value: {"months": 6},
  confidence_score: 0.95,
  status: "approved",
  approved_by: "admin-uuid",
  created_at: ISODate
}
```

#### `admins`
Admin user accounts with RBAC.

```javascript
{
  _id: ObjectId,
  id: "admin-uuid",
  email: "admin@osprey.com",
  password_hash: "bcrypt-hash",
  role: "superadmin",  // or "admin"
  permissions: ["users:read", "cases:write", "knowledge_base:admin"],
  created_at: ISODate
}
```

---

## Authentication & Security

### JWT Authentication

**Token Structure**:
```json
{
  "user_id": "uuid-v4",
  "email": "user@example.com",
  "exp": 1735689600  // 30 days from issue
}
```

**Token Validation**:
```python
from core.auth import get_current_user
from fastapi import Depends

@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    # user is automatically populated from JWT
    return {"email": user["email"]}
```

### Admin RBAC

**Roles**:
- `admin`: Standard admin access (read/write)
- `superadmin`: Full access including admin management

**Decorators**:
```python
from backend.admin.security import require_admin, require_superadmin

@router.post("/knowledge-base")
async def create_kb_entry(
    data: dict,
    admin: dict = Depends(require_admin)
):
    # Only admins can access
    pass

@router.delete("/admin/{admin_id}")
async def delete_admin(
    admin_id: str,
    admin: dict = Depends(require_superadmin)
):
    # Only superadmins can access
    pass
```

### Rate Limiting

**Implementation**:
```python
from rate_limiter import check_rate_limit

@router.post("/api/expensive-operation")
async def operation(user: dict = Depends(get_current_user)):
    await check_rate_limit(user["id"], "expensive_op", limit=10, window=60)
    # Raises HTTPException if limit exceeded
```

### Input Sanitization

**Usage**:
```python
from input_sanitizer import sanitize_input, validate_email

email = sanitize_input(user_input["email"])
if not validate_email(email):
    raise HTTPException(400, "Invalid email format")
```

---

## External Integrations

### OpenAI API

**Configuration**:
```python
import openai
openai.api_key = os.environ.get("OPENAI_API_KEY")
```

**Usage**:
```python
response = await openai.ChatCompletion.acreate(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are an immigration expert."},
        {"role": "user", "content": "What documents are required for I-539?"}
    ],
    temperature=0.3
)
```

### Google Gemini

**Usage**:
```python
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content([
    "Analyze this passport image for authenticity",
    {"mime_type": "image/jpeg", "data": image_bytes}
])
```

### Google Document AI

**Configuration**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Usage**:
```python
from google.cloud import documentai

client = documentai.DocumentProcessorServiceClient()
name = client.processor_path(
    project_id, location, processor_id
)

document = client.process_document(
    request={"name": name, "raw_document": {"content": pdf_bytes}}
)
```

### Stripe

**Checkout Session**:
```python
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    line_items=[{
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Visa Application Package"},
            "unit_amount": 29900,
        },
        "quantity": 1,
    }],
    mode="payment",
    success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url="https://yourdomain.com/cancel",
)
```

**Webhook Handling**:
```python
from stripe_integration import handle_stripe_webhook

@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    await handle_stripe_webhook(payload, sig_header)
    return {"status": "success"}
```

### Resend Email

**Configuration**:
```python
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")
```

**Usage**:
```python
email = resend.Emails.send({
    "from": os.environ.get("SENDER_EMAIL"),
    "to": user_email,
    "subject": "Your Visa Package is Ready",
    "html": "<p>Download your package here: <a href='...'>Link</a></p>"
})
```

---

## Logging & Observability

### Structured Logging

**Configuration**:
```bash
# .env
LOG_LEVEL=INFO
LOG_PRETTY=true
LOG_FORMAT=plain
```

**Usage**:
```python
import logging

logger = logging.getLogger(__name__)

# Info with context
logger.info(
    "Case created successfully",
    extra={
        "case_id": case_id,
        "user_id": user_id,
        "form_code": "I-539"
    }
)

# Warning
logger.warning(
    "Payment verification delayed",
    extra={"payment_id": payment_id, "delay_seconds": 30}
)

# Error with exception
try:
    result = await dangerous_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True, extra={"user_id": user_id})
```

**JSON Output** (production):
```json
{
  "timestamp": "2026-01-13T10:30:00.123Z",
  "level": "INFO",
  "logger": "api.auto_application",
  "message": "Case created successfully",
  "case_id": "OSP-ABC123",
  "user_id": "user-uuid",
  "form_code": "I-539"
}
```

### Sentry Integration

**Automatic Error Capture**:
All unhandled exceptions are automatically sent to Sentry.

**Manual Error Capture**:
```python
import sentry_sdk

try:
    risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)
```

**Custom Context**:
```python
with sentry_sdk.configure_scope() as scope:
    scope.set_user({"id": user_id, "email": email})
    scope.set_tag("case_id", case_id)
    scope.set_context("case_data", case_dict)
```

**Performance Monitoring**:
```python
with sentry_sdk.start_transaction(op="process_case", name="AI Processing"):
    with sentry_sdk.start_span(op="ai", description="Document Validation"):
        await validate_documents()

    with sentry_sdk.start_span(op="ai", description="Form Generation"):
        await generate_forms()
```

---

## Development Guide

### Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd osprey/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start MongoDB (if local)
mongod --dbpath /usr/local/var/mongodb

# Run development server
python3 server.py
```

### Code Style

**Formatting**:
```bash
black .
```

**Linting**:
```bash
flake8 .
```

**Type Checking**:
```bash
mypy server.py api/ core/ models/ services/
```

### Adding a New API Endpoint

1. **Create or update router in `api/`**:
```python
# api/my_feature.py
from fastapi import APIRouter, Depends
from core.auth import get_current_user
from core.database import db

router = APIRouter(prefix="/api/my-feature", tags=["My Feature"])

@router.post("/create")
async def create_item(data: dict, user: dict = Depends(get_current_user)):
    item = {
        "user_id": user["id"],
        "data": data,
        "created_at": datetime.now(timezone.utc)
    }
    await db.my_items.insert_one(item)
    return {"status": "created", "id": item["_id"]}
```

2. **Register router in `server.py`**:
```python
# server.py
from api.my_feature import router as my_feature_router

app.include_router(my_feature_router)
```

3. **Add models in `models/`** (if needed):
```python
# models/my_feature.py
from pydantic import BaseModel
from datetime import datetime

class MyItem(BaseModel):
    id: str
    user_id: str
    data: dict
    created_at: datetime
```

4. **Add business logic in `services/`** (if needed):
```python
# services/my_feature.py
from core.database import db

async def process_item(item_id: str):
    item = await db.my_items.find_one({"_id": item_id})
    # ... processing logic
    return processed_item
```

### Database Migrations

MongoDB is schemaless, but for consistency:

1. **Document schema changes in code comments**
2. **Create migration scripts in `migrations/`** (create this directory)
3. **Run migrations manually** (no automated tool yet)

Example migration script:
```python
# migrations/001_add_verification_field.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

async def migrate():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB")]

    # Add 'verified' field to all users without it
    result = await db.users.update_many(
        {"verified": {"$exists": False}},
        {"$set": {"verified": False}}
    )

    print(f"Updated {result.modified_count} users")
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate())
```

---

## Deployment

### Production Checklist

- [ ] Set strong `JWT_SECRET` (64+ random characters)
- [ ] Configure `CORS_ORIGINS` with actual domain (not `*`)
- [ ] Set `SENTRY_DSN` and `SENTRY_ENVIRONMENT=production`
- [ ] Configure `LOG_LEVEL=WARNING` and `LOG_FORMAT=json`
- [ ] Use MongoDB Atlas or managed MongoDB (not local)
- [ ] Enable MongoDB authentication and TLS
- [ ] Set up Stripe webhook endpoint with valid `STRIPE_WEBHOOK_SECRET`
- [ ] Configure Google Cloud credentials securely (not in repo)
- [ ] Set up rate limiting (Redis recommended)
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Set up monitoring (Sentry, Datadog, etc.)
- [ ] Configure backup strategy for MongoDB
- [ ] Set up CI/CD pipeline
- [ ] Review and test all error handlers
- [ ] Load test API endpoints
- [ ] Set up health check endpoint

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python3", "server.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - MONGODB_URI=mongodb://mongo:27017
      - MONGODB_DB=osprey_db
    env_file:
      - ./backend/.env
    depends_on:
      - mongo

  mongo:
    image: mongo:6.0
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"

volumes:
  mongo-data:
```

### Deployment Commands

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

---

## Troubleshooting

### Common Issues

#### 1. "Database not initialized" Error
**Cause**: MongoDB connection failed or not started.

**Solution**:
```bash
# Check MongoDB is running
mongosh --eval "db.stats()"

# Verify MONGODB_URI in .env
cat backend/.env | grep MONGODB_URI

# Check logs for connection errors
tail -f backend/logs/app.log
```

#### 2. "Invalid token" / 401 Errors
**Cause**: JWT token expired or invalid.

**Solution**:
- Frontend should refresh token or re-login
- Check `JWT_SECRET` is consistent
- Verify token format: `Bearer <token>`

#### 3. Stripe Webhook Verification Failed
**Cause**: `STRIPE_WEBHOOK_SECRET` mismatch.

**Solution**:
```bash
# Get webhook signing secret from Stripe Dashboard
# Webhooks → Select endpoint → Signing secret

# Update .env
STRIPE_WEBHOOK_SECRET=whsec_...

# Test webhook locally with Stripe CLI
stripe listen --forward-to localhost:8001/api/webhooks/stripe
```

#### 4. OpenAI API Rate Limit
**Cause**: Too many API calls to OpenAI.

**Solution**:
- Implement caching for repeated queries
- Add rate limiting per user
- Use cheaper models (gpt-3.5-turbo) for non-critical tasks
- Implement retry with exponential backoff

#### 5. Google Cloud Authentication Failed
**Cause**: Service account JSON file not found or invalid.

**Solution**:
```bash
# Set correct path
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Verify file exists and is valid JSON
cat $GOOGLE_APPLICATION_CREDENTIALS | jq

# Test authentication
gcloud auth application-default login
```

#### 6. Port Already in Use
**Cause**: Another process using port 8001.

**Solution**:
```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>

# Or use different port
uvicorn server:app --port 8002
```

---

## Design Patterns

### 1. Dependency Injection

FastAPI's dependency system is used extensively:

```python
from fastapi import Depends
from core.auth import get_current_user
from core.database import db

async def get_case_or_404(case_id: str, user: dict = Depends(get_current_user)):
    case = await db.auto_cases.find_one({"case_id": case_id, "user_id": user["id"]})
    if not case:
        raise HTTPException(404, "Case not found")
    return case

@router.get("/cases/{case_id}")
async def get_case(case: dict = Depends(get_case_or_404)):
    return serialize_doc(case)
```

### 2. Repository Pattern

Services act as repositories for business logic:

```python
# services/cases.py
class CaseRepository:
    @staticmethod
    async def create(user_id: str, form_code: str) -> dict:
        case = {
            "case_id": generate_case_id(),
            "user_id": user_id,
            "form_code": form_code,
            "status": "created",
            "created_at": datetime.now(timezone.utc)
        }
        await db.auto_cases.insert_one(case)
        return case
```

### 3. Agent Pattern

AI agents are independent, specialized processors:

```python
class BaseAgent:
    async def process(self, data: dict) -> dict:
        raise NotImplementedError

class DocumentValidatorAgent(BaseAgent):
    async def process(self, data: dict) -> dict:
        # Validate documents
        return {"status": "valid", "findings": [...]}
```

### 4. Command Pattern

Complex operations are encapsulated as commands:

```python
class ProcessCaseCommand:
    def __init__(self, case_id: str):
        self.case_id = case_id

    async def execute(self):
        case = await self.load_case()
        await self.validate_documents(case)
        await self.generate_forms(case)
        await self.run_qa(case)
        await self.finalize(case)
```

### 5. Factory Pattern

Agent creation uses factory pattern:

```python
def create_agent(agent_type: str) -> BaseAgent:
    agents = {
        "document_validator": DocumentValidatorAgent,
        "form_validator": FormValidatorAgent,
        "eligibility_analyst": EligibilityAnalystAgent,
    }
    agent_class = agents.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return agent_class()
```

---

## API Documentation

### Interactive API Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

### Example API Calls

**Create Case**:
```bash
curl -X POST http://localhost:8001/api/auto-application/cases \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "form_code": "I-539",
    "case_type": "extension_of_stay"
  }'
```

**Upload Document**:
```bash
curl -X POST http://localhost:8001/api/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@passport.pdf" \
  -F "case_id=OSP-ABC123" \
  -F "document_type=passport"
```

**Process Payment**:
```bash
curl -X POST http://localhost:8001/api/payments/create-checkout-session \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "prod-visa-i539",
    "success_url": "https://app.com/success",
    "cancel_url": "https://app.com/cancel"
  }'
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=api --cov=core --cov=services

# Run verbose
pytest -v
```

### Writing Tests

**Example Test**:
```python
# tests/test_auth.py
import pytest
from core.auth import hash_password, verify_password, create_jwt_token

def test_password_hashing():
    password = "secret123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_jwt_creation():
    token = create_jwt_token("user-123", "user@example.com")
    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long
```

---

## Recent Fixes (2026-01-13)

### 1. Modular Architecture Refactoring
- **Issue**: Monolithic `server.py` file (4000+ lines)
- **Fix**: Split into `core/`, `api/`, `models/`, `services/` modules
- **Impact**: Improved maintainability, testability, and code organization

### 2. Sentry Integration
- **Issue**: No production error tracking or performance monitoring
- **Fix**: Added `core/sentry.py` with FastAPI, Starlette, AioHTTP integrations
- **Configuration**: 11 new environment variables in `.env.example`
- **Impact**: Real-time error alerts, performance insights, user session tracking

### 3. Structured Logging
- **Issue**: Inconsistent logging with print statements
- **Fix**: Implemented `core/logging.py` with JSON/plain formatters
- **Configuration**: `LOG_LEVEL`, `LOG_PRETTY`, `LOG_FORMAT` env vars
- **Impact**: Centralized logging, production-ready JSON logs, better debugging

### 4. Stripe Error Handling
- **Issue**: Crashes when Stripe API keys missing
- **Fix**: Graceful 503 Service Unavailable response
- **Impact**: Safer development environment, clearer error messages

### 5. MongoDB Connection Lifecycle
- **Issue**: Database connection not properly initialized/closed
- **Fix**: `core/database.py` with startup/shutdown hooks, DBProxy
- **Impact**: Prevents "None" database errors, cleaner resource management

### 6. Datetime Deprecation Warnings
- **Issue**: `datetime.utcnow()` deprecated in Python 3.12+
- **Fix**: Replaced with `datetime.now(timezone.utc)` across all files
- **Impact**: Future-proof codebase, no deprecation warnings

---

## AI Agent Guidelines

### For AI Coding Assistants

When working with this codebase:

1. **Always use async/await** for database operations and external API calls
2. **Use Pydantic models** for request/response validation
3. **Follow the repository pattern**: Business logic in `services/`, HTTP in `api/`
4. **Import from core modules**: Don't reimplement auth, logging, or serialization
5. **Use structured logging**: `logger.info("message", extra={...})`
6. **Handle errors gracefully**: Return proper HTTP status codes, don't expose internals
7. **Validate user input**: Use Pydantic, validators, and input sanitization
8. **Use dependency injection**: `Depends(get_current_user)` for auth
9. **Serialize MongoDB docs**: Always use `serialize_doc()` before returning
10. **Type hint everything**: Use Python 3.11+ type hints for all functions

### Common Patterns to Follow

**Creating a new endpoint**:
```python
@router.post("/api/resource")
async def create_resource(
    data: ResourceCreate,  # Pydantic model
    user: dict = Depends(get_current_user)  # Auth
):
    logger.info("Creating resource", extra={"user_id": user["id"]})

    try:
        resource = await ResourceService.create(data, user["id"])
        return serialize_doc(resource)
    except Exception as e:
        logger.error("Failed to create resource", exc_info=True)
        raise HTTPException(500, "Internal server error")
```

**Database queries**:
```python
from core.database import db

# Find one
case = await db.auto_cases.find_one({"case_id": case_id})

# Find many
cases = await db.auto_cases.find({"user_id": user_id}).to_list(100)

# Insert
result = await db.auto_cases.insert_one(document)

# Update
await db.auto_cases.update_one(
    {"case_id": case_id},
    {"$set": {"status": "completed"}}
)

# Delete
await db.auto_cases.delete_one({"case_id": case_id})
```

**Error handling**:
```python
from fastapi import HTTPException

# 400 Bad Request
raise HTTPException(400, "Invalid input")

# 401 Unauthorized
raise HTTPException(401, "Authentication required")

# 403 Forbidden
raise HTTPException(403, "Insufficient permissions")

# 404 Not Found
raise HTTPException(404, "Resource not found")

# 500 Internal Server Error
raise HTTPException(500, "Internal server error")
```

---

## Contributing

### Pull Request Process

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes following code style guidelines
3. Add tests for new functionality
4. Run linters: `black .` and `flake8 .`
5. Update documentation if needed
6. Commit with descriptive message
7. Push and create pull request
8. Wait for code review

### Code Review Checklist

- [ ] Code follows style guidelines (Black + Flake8)
- [ ] Type hints added for all functions
- [ ] Docstrings added for public functions
- [ ] Tests written and passing
- [ ] No secrets or credentials in code
- [ ] Error handling implemented
- [ ] Logging added for important operations
- [ ] Database queries optimized
- [ ] API documentation updated

---

## License

Proprietary - All rights reserved.

---

## Support

For questions or issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [API Documentation](#api-documentation)
3. Contact the development team
4. Create an issue in the repository

---

**Last Updated**: 2026-01-13
**Version**: 2.0.0
**Maintainers**: Osprey Development Team
