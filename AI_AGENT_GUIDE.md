# AI Agent Guide - Osprey Platform
**Universal Guide for AI Coding Assistants**

**Last Updated**: 2026-01-13
**For**: All AI coding agents (Claude, Gemini, GPT-4, GitHub Copilot, Cursor, Codeium, Tabnine, etc.)
**Project**: Osprey - Enterprise Immigration AI System

---

## 📌 Quick Start for AI Agents

### What is Osprey?
Osprey is a **production-ready, enterprise-grade B2C immigration platform** that automates US visa application processing using multi-agent AI orchestration. The system combines OCR document processing, LLM-powered validation, USCIS form generation, and Stripe payment processing.

### Project Stats
- **Lines of Code**: ~50,000+ (Backend: ~30K, Frontend: ~20K)
- **Documentation**: 7,000+ lines across READMEs and guides
- **Backend**: Python 3.11+ | FastAPI 0.128.0 | MongoDB 6.0+ (Motor async)
- **Frontend**: TypeScript 5.8+ | React 18.3 | Vite 5.4 | Tailwind CSS 3.4
- **AI Integration**: OpenAI GPT-4o | Google Gemini 1.5 Pro | Google Document AI
- **Status**: Production-ready with active development

### Repository Layout
```
camada-osprey-core/
├── backend/                    # FastAPI async backend (Python 3.11+)
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
├── README.md                  # Root documentation (1014 lines + Mermaid diagrams)
├── SECURITY_AUDIT_2026-01-13.md  # Latest security audit (465 lines)
├── CLAUDE.md                  # Claude-specific guide
├── GEMINI.md                  # Gemini-specific guide
├── .cursorrules               # Cursor IDE rules
├── .github/copilot-instructions.md  # GitHub Copilot instructions
└── AI_AGENT_GUIDE.md         # This file (universal guide)
```

---

## 🎯 Core Architecture Patterns

### Backend Architecture (FastAPI + MongoDB)

```
┌─────────────────────────────────────────────────────────────┐
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

### Frontend Architecture (React + TypeScript)

```
┌─────────────────────────────────────────────────────────────┐
│                    React Application                         │
│                      (App.tsx)                              │
├─────────────────────────────────────────────────────────────┤
│  React Router | Zustand State | React Query | Toast        │
└─────┬────────┬────────┬────────┬────────┬──────────────────┘
      │        │        │        │        │
┌─────▼────┐ ┌▼────┐ ┌─▼─────┐ ┌▼─────┐ ┌▼──────┐
│  Pages   │ │Comp │ │Hooks  │ │ Lib  │ │Types  │
│ 25+      │ │35+  │ │Custom │ │Utils │ │TS    │
└─────┬────┘ └┬────┘ └───────┘ └┬─────┘ └───────┘
      │       │                  │
      └───────┴──────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼───┐  ┌────▼────┐  ┌───▼────┐
    │FastAPI │  │Stripe   │  │Browser │
    │Backend │  │Checkout │  │Storage │
    └────────┘  └─────────┘  └────────┘
```

---

## 🔑 Critical Patterns (MUST FOLLOW)

### Backend (Python/FastAPI)

#### 1. **Async/Await is MANDATORY**
```python
# ✅ CORRECT - Always use async for I/O
async def get_case(case_id: str) -> dict:
    case = await db.auto_cases.find_one({"case_id": case_id})
    if not case:
        raise HTTPException(404, "Case not found")
    return serialize_doc(case)

# ❌ WRONG - Synchronous operations block event loop
def get_case(case_id: str):
    case = db.auto_cases.find_one({"case_id": case_id})  # BLOCKS!
    return case
```

#### 2. **Pydantic Validation REQUIRED**
```python
# ✅ CORRECT - Use Pydantic for all API requests/responses
from pydantic import BaseModel, EmailStr, Field

class CaseCreate(BaseModel):
    form_code: str = Field(..., pattern=r"^(I|N)-\d+$")
    user_email: EmailStr
    visa_type: str

@router.post("/cases", response_model=CaseResponse)
async def create_case(data: CaseCreate):
    # Auto-validated by Pydantic
    ...

# ❌ WRONG - No validation, security risk
@router.post("/cases")
async def create_case(data: dict):
    # No validation!
    ...
```

#### 3. **MongoDB Serialization MANDATORY**
```python
# ✅ CORRECT - Always serialize before returning
from core.serialization import serialize_doc

case = await db.auto_cases.find_one({"case_id": case_id})
return serialize_doc(case)  # Converts ObjectId → str, datetime → ISO

# ❌ WRONG - ObjectId not JSON serializable!
case = await db.auto_cases.find_one({"case_id": case_id})
return case  # FAILS with serialization error
```

#### 4. **Structured Logging REQUIRED**
```python
# ✅ CORRECT - Use structured logging with context
import logging
logger = logging.getLogger(__name__)

logger.info(
    "Case created successfully",
    extra={
        "case_id": case_id,
        "user_id": user_id,
        "form_code": "I-539",
        "duration_ms": 234
    }
)

# ❌ WRONG - print() statements lost in production
print(f"Case {case_id} created")
```

#### 5. **Use datetime.now(timezone.utc)**
```python
# ✅ CORRECT - Timezone-aware datetime
from datetime import datetime, timezone

created_at = datetime.now(timezone.utc)

# ❌ WRONG - Deprecated in Python 3.12+
created_at = datetime.utcnow()
```

#### 6. **Proper HTTP Status Codes**
```python
# ✅ CORRECT - Return proper status codes
from fastapi import HTTPException

if not case:
    raise HTTPException(404, "Case not found")

if not user.has_permission("admin"):
    raise HTTPException(403, "Insufficient permissions")

# ❌ WRONG - All errors return 200 OK
if not case:
    return {"error": "Case not found"}  # Still HTTP 200!
```

---

### Frontend (React/TypeScript)

#### 1. **Use makeApiCall for ALL API Requests**
```typescript
// ✅ CORRECT - Centralized API client
import { makeApiCall } from '@/lib/api';

// GET request
const cases = await makeApiCall<Case[]>('/cases', 'GET');

// POST request
const newCase = await makeApiCall<Case>('/cases', 'POST', {
  form_code: 'I-539',
  visa_type: 'b2'
});

// makeApiCall:
// - Returns parsed JSON directly
// - Auto-prefixes /api
// - Handles errors centrally
// - Auto-retries on network errors

// ❌ WRONG - Direct fetch() bypasses error handling
const response = await fetch('/api/cases');
const cases = await response.json();
```

#### 2. **Controlled Inputs MUST NOT Be Undefined**
```typescript
// ✅ CORRECT - Always initialize with empty string
const [formData, setFormData] = useState({
  firstName: data?.firstName || '',  // Never undefined
  lastName: data?.lastName || '',
  email: data?.email || ''
});

<input
  value={formData.firstName}  // Always string
  onChange={(e) => setFormData({...formData, firstName: e.target.value})}
/>

// ❌ WRONG - React warning: uncontrolled to controlled
const [formData, setFormData] = useState({
  firstName: data?.firstName  // Can be undefined!
});
```

#### 3. **TypeScript Types REQUIRED**
```typescript
// ✅ CORRECT - Define proper interfaces
interface Case {
  case_id: string;
  user_id: string;
  status: 'created' | 'in_progress' | 'completed';
  form_code: string;
  created_at: string;
}

async function getCase(caseId: string): Promise<Case> {
  return await makeApiCall<Case>(`/cases/${caseId}`, 'GET');
}

// ❌ WRONG - Loses all type safety
async function getCase(caseId: string): Promise<any> {
  return await makeApiCall(`/cases/${caseId}`, 'GET');
}
```

#### 4. **Error Handling REQUIRED**
```typescript
// ✅ CORRECT - Handle all API errors
try {
  const data = await makeApiCall('/cases', 'POST', formData);
  toast.success('Case created successfully');
  navigate(`/cases/${data.case_id}`);
} catch (error) {
  console.error('Failed to create case:', error);
  toast.error('Failed to create case. Please try again.');
}

// ❌ WRONG - Unhandled errors crash UI
const data = await makeApiCall('/cases', 'POST', formData);
```

#### 5. **Button Styling (shadcn vs Native)**
```typescript
// ✅ CORRECT - Use native <button> for custom hover states
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
  Won't Work as Expected
</Button>
// Solution: Use native <button> for full CSS control
```

---

## 🚫 Anti-Patterns (NEVER DO THIS!)

### Backend

❌ **Synchronous Database Calls**
```python
def get_case(case_id):
    return db.cases.find_one({"case_id": case_id})  # Blocks event loop!
```

❌ **Using print() Instead of Logging**
```python
print(f"Processing case {case_id}")  # Lost in production
```

❌ **Missing Serialization**
```python
case = await db.cases.find_one({"case_id": case_id})
return case  # ObjectId not JSON serializable!
```

❌ **datetime.utcnow() (Deprecated)**
```python
created_at = datetime.utcnow()  # Deprecated in Python 3.12+
```

❌ **No Error Handling**
```python
result = await external_api_call(prompt)  # What if it fails?
```

### Frontend

❌ **Direct fetch() Instead of makeApiCall**
```typescript
const response = await fetch('/api/cases');  # Use makeApiCall!
```

❌ **Undefined Controlled Inputs**
```typescript
const [value, setValue] = useState(data?.field);  # Can be undefined!
```

❌ **Using `any` Type**
```typescript
async function getData(): Promise<any> {  # Loses type safety!
```

❌ **No Error Handling**
```typescript
const data = await makeApiCall('/endpoint', 'POST', body);  # No try/catch!
```

---

## 📚 Common Tasks

### Task 1: Add a New API Endpoint

**Step 1**: Create router in `backend/api/my_feature.py`
```python
from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from core.database import db
from core.serialization import serialize_doc
from models.my_feature import MyFeatureCreate, MyFeatureResponse
import logging

router = APIRouter(prefix="/api/my-feature", tags=["My Feature"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=MyFeatureResponse)
async def create_feature(
    data: MyFeatureCreate,
    user: dict = Depends(get_current_user)
):
    logger.info("Creating feature", extra={"user_id": user["id"]})

    feature = {
        "user_id": user["id"],
        "data": data.model_dump(),
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.my_features.insert_one(feature)
    feature["_id"] = result.inserted_id

    return serialize_doc(feature)
```

**Step 2**: Register router in `backend/server.py`
```python
from api.my_feature import router as my_feature_router

app.include_router(my_feature_router)
```

**Step 3**: Create TypeScript types and API functions in `frontend/src/lib/api.ts`
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

### Task 2: Add a Database Collection

MongoDB is schemaless, so:

1. **Access directly via `db.collection_name`**:
```python
from core.database import db

# Insert
result = await db.my_collection.insert_one(document)

# Find
docs = await db.my_collection.find({"user_id": user_id}).to_list(100)

# Update
await db.my_collection.update_one(
    {"_id": doc_id},
    {"$set": {"status": "completed"}}
)
```

2. **Document the schema** in `backend/README.md` under "Database Schema" section

---

### Task 3: Add an AI Agent

1. **Create agent file** in `backend/`:
```python
# my_specialist_agent.py
import openai
from typing import Dict, Any

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

2. **Add API endpoint** in `backend/api/agents.py`
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

## 🔐 Security Checklist

### NEVER:
- ❌ Hardcode API keys, passwords, or secrets
- ❌ Use `eval()` or `exec()` on user input
- ❌ Return raw error messages to users (info leak)
- ❌ Trust user input without validation
- ❌ Use `dangerouslySetInnerHTML` without sanitization
- ❌ Commit `.env` files to git

### ALWAYS:
- ✅ Use environment variables for secrets
- ✅ Validate all user input (Pydantic models, Zod schemas)
- ✅ Use parameterized queries (MongoDB prevents injection by default)
- ✅ Apply rate limiting to expensive operations
- ✅ Log security events (failed logins, permission denials)
- ✅ Use HTTPS in production
- ✅ Sanitize all user-generated content before displaying

---

## 📊 File Structure Reference

### Backend Files
- **Main Entry**: `backend/server.py` (DO NOT add routes here)
- **Core Infrastructure**: `backend/core/{auth,database,logging,serialization,sentry}.py`
- **API Routers**: `backend/api/*.py` (23 modules)
- **Pydantic Models**: `backend/models/*.py`
- **Business Logic**: `backend/services/*.py`
- **Dependencies**: `backend/requirements.txt` (462 lines, 18 categories)

### Frontend Files
- **Main Entry**: `frontend/src/App.tsx`
- **Pages**: `frontend/src/pages/*.tsx` (25+ components)
- **Components**: `frontend/src/components/**/*.tsx` (35+ components)
- **API Client**: `frontend/src/lib/api.ts` **← CRITICAL**
- **Utilities**: `frontend/src/lib/utils.ts`
- **Hooks**: `frontend/src/hooks/*.ts`
- **Dependencies**: `frontend/package.json`

---

## 🧪 Testing

### Backend (pytest)
```bash
cd backend
pytest                              # Run all tests
pytest tests/test_auth.py          # Run specific test
pytest --cov=api --cov=core        # With coverage
```

### Frontend
```bash
cd frontend
npm test          # Unit tests (if configured)
npm run lint      # ESLint
npm run type-check # TypeScript
```

---

## 📖 Documentation Hierarchy

1. **Start Here**: [README.md](README.md) - System architecture + Mermaid diagrams
2. **Backend Deep Dive**: [backend/README.md](backend/README.md) - 1830 lines
3. **Frontend Deep Dive**: [frontend/README.md](frontend/README.md) - 1080 lines
4. **Security**: [SECURITY_AUDIT_2026-01-13.md](backend/SECURITY_AUDIT_2026-01-13.md) - Latest audit
5. **AI-Specific**:
   - [CLAUDE.md](CLAUDE.md) - Claude-specific patterns
   - [GEMINI.md](GEMINI.md) - Gemini-specific patterns
   - [.cursorrules](.cursorrules) - Cursor IDE rules
   - [.github/copilot-instructions.md](.github/copilot-instructions.md) - GitHub Copilot
6. **API Reference**: http://localhost:8001/docs - Swagger UI

---

## 🚀 Quick Commands

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 server.py

# Frontend
cd frontend
npm install
npm run dev

# Tests
pytest                    # Backend
npm test                 # Frontend

# Lint & Format
black . && flake8 .      # Backend
npm run lint            # Frontend

# Security
pip-audit               # Check vulnerabilities

# Git
git status
git add .
git commit -m "feat(module): description"
```

---

## 🎓 Learning Path for AI Agents

1. **Read Root README** → Understand system architecture
2. **Review Backend README** → Learn FastAPI patterns
3. **Review Frontend README** → Learn React+TypeScript patterns
4. **Explore API Docs** → See all endpoints at `http://localhost:8001/docs`
5. **Review Security Audit** → Understand vulnerabilities and fixes
6. **Try Example Tasks** → Follow "Common Tasks" section above

---

## 💡 Tips for AI Agents

### When Writing Code:
1. **Always check** if a similar file exists before creating a new one
2. **Prefer editing** existing files over creating new ones
3. **Follow established patterns** in the codebase
4. **Use type hints** everywhere (Python + TypeScript)
5. **Include error handling** in all async operations
6. **Add logging** for important operations
7. **Write tests** for new functionality

### When Refactoring:
1. **Understand existing code** before modifying
2. **Maintain backward compatibility** unless explicitly asked to break it
3. **Update tests** to reflect changes
4. **Update documentation** if API changes

### When Debugging:
1. **Check logs** in Sentry dashboard
2. **Review API docs** at `/docs` for endpoint signatures
3. **Verify environment variables** in `.env` files
4. **Check database** with MongoDB queries
5. **Test API endpoints** with curl or Postman

---

## 📞 Support

- **Interactive API Docs**: http://localhost:8001/docs
- **Root README**: [README.md](README.md)
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **Security Audit**: [SECURITY_AUDIT_2026-01-13.md](backend/SECURITY_AUDIT_2026-01-13.md)

---

**Last Updated**: 2026-01-13
**Version**: 2.0.0
**Status**: Production-ready with active development
**Maintained By**: Osprey Development Team

---

## 🏆 Success Metrics

When working with this codebase, aim for:
- ✅ **Zero** hardcoded secrets
- ✅ **100%** type hints on new functions
- ✅ **100%** async operations for I/O
- ✅ **100%** Pydantic validation on API endpoints
- ✅ **100%** MongoDB serialization before JSON return
- ✅ **90%+** test coverage on new code
- ✅ **Zero** `print()` statements (use logging)
- ✅ **Zero** `any` types in TypeScript
- ✅ **All** API calls via `makeApiCall`
- ✅ **All** controlled inputs initialized

---

*This guide is optimized for AI coding agents of all types. For specific AI-optimized instructions, see CLAUDE.md, GEMINI.md, .cursorrules, or .github/copilot-instructions.md.*
