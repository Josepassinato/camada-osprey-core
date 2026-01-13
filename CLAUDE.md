# Claude AI Agent Guide - Osprey Platform

**Last Updated**: 2026-01-13
**For**: Claude AI (Anthropic)
**Project**: Osprey - Enterprise Immigration AI System

---

## Quick Reference

- **Language**: Backend (Python 3.11+), Frontend (TypeScript 5.8+)
- **Frameworks**: FastAPI 0.128.0, React 18.3.1
- **Database**: MongoDB 6.0+ (Motor async driver)
- **AI Providers**: OpenAI GPT-4o, Google Gemini 1.5 Pro
- **Primary Docs**: [Root README](README.md), [Backend README](backend/README.md), [Frontend README](frontend/README.md)

---

## Project Overview

Osprey is a **production-ready, multi-agent AI platform** for automating US immigration case processing. The system combines:
- **Document processing** via Google Document AI (OCR)
- **Multi-agent orchestration** for validation, QA, and compliance
- **USCIS form generation** with intelligent field mapping
- **Payment processing** via Stripe
- **Real-time guidance** through conversational AI

**Target Users**: Individual visa applicants, immigration attorneys, corporate teams
**Supported Visas**: B-2, F-1, H-1B, I-130, I-539, I-765, EB-2 NIW, EB-1A, and more

---

## Repository Structure

```
camada-osprey-core/
├── backend/                    # FastAPI backend (Python 3.11+)
│   ├── server.py              # Main app initialization
│   ├── core/                  # Infrastructure (auth, db, logging, sentry)
│   ├── api/                   # API routers (23 modules, domain-organized)
│   ├── models/                # Pydantic schemas
│   ├── services/              # Business logic layer
│   ├── requirements.txt       # Python dependencies (462 lines, 18 categories)
│   └── README.md             # Backend docs (1830 lines)
│
├── frontend/                   # React + Vite frontend (TypeScript 5.8+)
│   ├── src/
│   │   ├── pages/            # 25+ page components
│   │   ├── components/       # 35+ reusable UI components
│   │   ├── lib/              # API client, utilities
│   │   └── hooks/            # Custom React hooks
│   ├── package.json          # npm dependencies
│   └── README.md            # Frontend docs (1080 lines)
│
├── README.md                  # Root documentation (1014 lines)
├── SECURITY_AUDIT_2026-01-13.md  # Latest security audit
└── CLAUDE.md                 # This file
```

---

## Critical Patterns & Conventions

### Backend (Python/FastAPI)

#### 1. **Async/Await Everywhere**
```python
# ✅ CORRECT - Always use async for database and external APIs
async def get_case(case_id: str) -> dict:
    case = await db.auto_cases.find_one({"case_id": case_id})
    return case

# ❌ WRONG - Don't use synchronous operations
def get_case(case_id: str) -> dict:
    case = db.auto_cases.find_one({"case_id": case_id})  # Blocks event loop!
    return case
```

#### 2. **Pydantic Models for Validation**
```python
# ✅ CORRECT - Use Pydantic for request/response
from pydantic import BaseModel, EmailStr

class CaseCreate(BaseModel):
    form_code: USCISForm
    user_email: EmailStr
    visa_type: VisaType

@router.post("/cases")
async def create_case(data: CaseCreate):  # Auto-validated
    ...

# ❌ WRONG - Don't use raw dicts without validation
@router.post("/cases")
async def create_case(data: dict):  # No validation!
    ...
```

#### 3. **MongoDB Serialization (ObjectId Handling)**
```python
# ✅ CORRECT - Always serialize before returning
from core.serialization import serialize_doc

case = await db.auto_cases.find_one({"case_id": case_id})
return serialize_doc(case)  # Converts ObjectId to string, datetime to ISO

# ❌ WRONG - Don't return raw MongoDB documents
case = await db.auto_cases.find_one({"case_id": case_id})
return case  # ObjectId not JSON serializable!
```

#### 4. **Dependency Injection for Auth**
```python
# ✅ CORRECT - Use FastAPI dependencies
from core.auth import get_current_user

@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    return {"email": user["email"], "id": user["id"]}

# ❌ WRONG - Don't manually parse tokens
@router.get("/profile")
async def get_profile(authorization: str = Header()):
    token = authorization.split("Bearer ")[1]  # Error-prone!
    ...
```

#### 5. **Structured Logging (Not Print)**
```python
# ✅ CORRECT - Use structured logging with context
import logging
logger = logging.getLogger(__name__)

logger.info(
    "Case created successfully",
    extra={
        "case_id": case_id,
        "user_id": user_id,
        "form_code": "I-539"
    }
)

# ❌ WRONG - Don't use print statements
print(f"Case {case_id} created")  # Lost in production, no context
```

#### 6. **Error Handling**
```python
# ✅ CORRECT - Return proper HTTP status codes
from fastapi import HTTPException

if not case:
    raise HTTPException(404, "Case not found")

if not user.has_permission("admin"):
    raise HTTPException(403, "Insufficient permissions")

# ❌ WRONG - Don't return error messages as 200 OK
if not case:
    return {"error": "Case not found"}  # Still HTTP 200!
```

#### 7. **Database Queries**
```python
# ✅ CORRECT - Use proper MongoDB async patterns
from core.database import db

# Find one
case = await db.auto_cases.find_one({"case_id": case_id})

# Find many with limit
cases = await db.auto_cases.find({"user_id": user_id}).to_list(100)

# Update
await db.auto_cases.update_one(
    {"case_id": case_id},
    {"$set": {"status": "completed"}}
)

# ❌ WRONG - Don't forget to await or convert cursor
cases = db.auto_cases.find({"user_id": user_id})  # Returns cursor, not results!
```

---

### Frontend (React/TypeScript)

#### 1. **API Calls via makeApiCall**
```typescript
// ✅ CORRECT - Use makeApiCall utility
import { makeApiCall } from '@/lib/api';

// GET request
const cases = await makeApiCall<Case[]>('/cases', 'GET');

// POST request
const newCase = await makeApiCall<Case>('/cases', 'POST', {
  form_code: 'I-539',
  visa_type: 'b2'
});

// makeApiCall returns parsed JSON data directly, handles errors, and auto-prefixes /api

// ❌ WRONG - Don't use fetch directly
const response = await fetch('/api/cases');
const cases = await response.json();  // No error handling!
```

#### 2. **Controlled Inputs (Never Undefined)**
```typescript
// ✅ CORRECT - Always initialize with empty string
const [formData, setFormData] = useState({
  firstName: data?.firstName || '',  // Never undefined
  lastName: data?.lastName || '',
  email: data?.email || ''
});

// ❌ WRONG - Don't leave values undefined
const [formData, setFormData] = useState({
  firstName: data?.firstName,  // Can be undefined!
  lastName: data?.lastName
});
```

#### 3. **Type Safety**
```typescript
// ✅ CORRECT - Define proper interfaces
interface Case {
  case_id: string;
  user_id: string;
  status: CaseStatus;
  form_code: string;
  created_at: string;
}

async function getCase(caseId: string): Promise<Case> {
  return await makeApiCall<Case>(`/cases/${caseId}`, 'GET');
}

// ❌ WRONG - Don't use `any`
async function getCase(caseId: string): Promise<any> {  // Loses type safety!
  return await makeApiCall(`/cases/${caseId}`, 'GET');
}
```

#### 4. **Button Styling (Native vs shadcn/ui)**
```typescript
// ✅ CORRECT - Use native <button> for custom styles
<button
  className="bg-black text-white hover:bg-gray-800 px-4 py-2 rounded"
  onClick={handleClick}
>
  Custom Button
</button>

// ✅ ALSO CORRECT - Use shadcn Button for standard styles
import { Button } from '@/components/ui/button';

<Button variant="default" onClick={handleClick}>
  Standard Button
</Button>

// ⚠️ ISSUE - shadcn Button overrides custom className hover states
<Button className="bg-purple-500 hover:bg-purple-600">
  Won't Work
</Button>
// Use native <button> instead for full CSS control
```

#### 5. **Error Boundaries**
```typescript
// ✅ CORRECT - Always handle API errors
try {
  const data = await makeApiCall('/cases', 'POST', formData);
  toast.success('Case created successfully');
} catch (error) {
  console.error('Failed to create case:', error);
  toast.error('Failed to create case. Please try again.');
}

// ❌ WRONG - Don't ignore errors
const data = await makeApiCall('/cases', 'POST', formData);
// No error handling!
```

---

## Common Tasks

### Task: Add a New API Endpoint

**Backend** (`backend/api/my_feature.py`):
```python
from fastapi import APIRouter, Depends
from core.auth import get_current_user
from core.database import db
from models.my_feature import MyFeatureCreate, MyFeatureResponse

router = APIRouter(prefix="/api/my-feature", tags=["My Feature"])

@router.post("/", response_model=MyFeatureResponse)
async def create_feature(
    data: MyFeatureCreate,
    user: dict = Depends(get_current_user)
):
    logger.info("Creating feature", extra={"user_id": user["id"]})

    feature = {
        "user_id": user["id"],
        "data": data.model_dump(),
        "created_at": datetime.now(timezone.utc)  # Not datetime.utcnow()!
    }

    result = await db.my_features.insert_one(feature)
    feature["_id"] = result.inserted_id

    return serialize_doc(feature)
```

**Register in `server.py`**:
```python
from api.my_feature import router as my_feature_router

app.include_router(my_feature_router)
```

**Frontend** (`src/lib/api.ts`):
```typescript
export interface MyFeature {
  id: string;
  user_id: string;
  data: any;
  created_at: string;
}

export async function createFeature(data: any): Promise<MyFeature> {
  return await makeApiCall<MyFeature>('/my-feature', 'POST', data);
}
```

---

### Task: Add Database Migration

MongoDB is schemaless, but for consistency:

1. **Create script** in `backend/migrations/`:
```python
# migrations/002_add_verification_field.py
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

async def migrate():
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("MONGODB_DB")]

    # Add 'verified' field to all users
    result = await db.users.update_many(
        {"verified": {"$exists": False}},
        {"$set": {"verified": False}}
    )

    print(f"Updated {result.modified_count} users")
    client.close()

if __name__ == "__main__":
    asyncio.run(migrate())
```

2. **Run manually**: `python3 migrations/002_add_verification_field.py`

---

### Task: Add AI Agent

1. **Create agent file** in `backend/`:
```python
# my_specialist_agent.py
from typing import Dict, Any
import openai

async def process_with_my_agent(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Specialized agent for specific task.

    Args:
        data: Input data for processing

    Returns:
        dict: Processing results with confidence score
    """
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in..."},
            {"role": "user", "content": f"Process: {data}"}
        ],
        temperature=0.3
    )

    return {
        "status": "completed",
        "result": response.choices[0].message.content,
        "confidence": 0.95
    }
```

2. **Add API endpoint** in `backend/api/agents.py`:
```python
from my_specialist_agent import process_with_my_agent

@router.post("/my-agent/process")
async def process_my_agent(
    data: dict,
    user: dict = Depends(get_current_user)
):
    result = await process_with_my_agent(data)
    return result
```

---

## Anti-Patterns (Don't Do This!)

### ❌ **Don't Use Synchronous Operations**
```python
# WRONG
def get_case(case_id: str):
    case = db.auto_cases.find_one({"case_id": case_id})  # Blocks!
    return case
```

### ❌ **Don't Ignore Type Hints**
```python
# WRONG
def process_case(case):  # No type hints!
    return case.get("data")  # Might not exist!
```

### ❌ **Don't Use datetime.utcnow() (Deprecated)**
```python
# WRONG
from datetime import datetime
created_at = datetime.utcnow()  # Deprecated in Python 3.12+

# RIGHT
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

### ❌ **Don't Create Files Unnecessarily**
```python
# WRONG - Creating new file when editing would work
# If file exists, use Edit tool
# If file doesn't exist, use Write tool
# ALWAYS prefer editing existing files over creating new ones
```

### ❌ **Don't Use Print for Logging**
```python
# WRONG
print(f"Case {case_id} created")

# RIGHT
logger.info("Case created", extra={"case_id": case_id})
```

### ❌ **Don't Return Raw MongoDB Documents**
```python
# WRONG
case = await db.cases.find_one({"case_id": case_id})
return case  # ObjectId not JSON serializable!

# RIGHT
from core.serialization import serialize_doc
case = await db.cases.find_one({"case_id": case_id})
return serialize_doc(case)
```

---

## Security Guidelines

### 1. **Never Commit Secrets**
- ✅ Use `.env` files (excluded from git)
- ❌ Never hardcode API keys, passwords, or tokens

### 2. **Always Validate Input**
```python
# ✅ Use Pydantic models
class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    password: str = Field(min_length=8)  # Validates length

# ✅ Use input sanitizer for additional safety
from input_sanitizer import sanitize_input

email = sanitize_input(user_input["email"])
```

### 3. **Use Prepared Queries (NoSQL Injection Prevention)**
```python
# ✅ CORRECT - MongoDB automatically prevents injection
case = await db.cases.find_one({"email": user_email})

# ⚠️ CAREFUL - Don't use eval or exec on user input
# ❌ NEVER DO THIS
eval(user_input)  # Arbitrary code execution!
```

### 4. **Rate Limiting**
```python
# ✅ Apply rate limits to expensive operations
from rate_limiter import check_rate_limit

await check_rate_limit(user["id"], "ai_processing", limit=10, window=60)
```

---

## Environment Variables

### Backend (`.env`)
```bash
# Required
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=osprey_db
JWT_SECRET=your-secret-key
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
STRIPE_SECRET_KEY=sk_test_...

# Optional (Production)
SENTRY_DSN=https://...@sentry.io/...
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Frontend (`.env`)
```bash
VITE_API_URL=http://localhost:8001
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## Testing

### Backend Tests (pytest)
```bash
cd backend
pytest                              # Run all tests
pytest tests/test_auth.py          # Run specific test
pytest --cov=api --cov=core        # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run test          # Unit tests
npm run lint          # ESLint
npm run type-check    # TypeScript
```

---

## Deployment Checklist

- [ ] Update `requirements.txt` / `package.json`
- [ ] Run security audit: `pip-audit`
- [ ] Run tests: `pytest` / `npm test`
- [ ] Update environment variables
- [ ] Check Sentry configuration
- [ ] Verify database backups
- [ ] Review API documentation at `/docs`
- [ ] Test in staging environment
- [ ] Monitor Sentry dashboard post-deployment

---

## Recent Changes (2026-01-13)

1. **Backend Refactoring**: Modularized `server.py` into `core/`, `api/`, `models/`, `services/`
2. **Security Fixes**: Patched 25 CVEs across 10 packages
3. **Documentation**: Added comprehensive READMEs (3900+ lines total)
4. **Dependency Management**: Organized `requirements.txt` into 18 categories
5. **Sentry Integration**: Full error tracking and performance monitoring

---

## Key Files to Reference

- **Architecture**: [README.md](README.md) (Mermaid diagrams, system flow)
- **Backend Patterns**: [backend/README.md](backend/README.md) (1830 lines)
- **Frontend Patterns**: [frontend/README.md](frontend/README.md) (1080 lines)
- **Security Audit**: [SECURITY_AUDIT_2026-01-13.md](backend/SECURITY_AUDIT_2026-01-13.md)
- **API Docs**: `http://localhost:8001/docs` (Swagger UI)

---

## Quick Commands

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py

# Frontend
cd frontend
npm install
npm run dev

# Tests
pytest                    # Backend
npm test                 # Frontend

# Linting
black .                  # Backend format
flake8 .                 # Backend lint
npm run lint            # Frontend lint

# Security
pip-audit               # Check vulnerabilities
```

---

## Support

- **Interactive API Docs**: `http://localhost:8001/docs`
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **Architecture Diagrams**: [README.md](README.md)

---

**Last Updated**: 2026-01-13
**Version**: 2.0.0
**Status**: Production-ready with active development
