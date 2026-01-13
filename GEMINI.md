# Gemini AI Agent Guide - Osprey Platform

**Last Updated**: 2026-01-13
**For**: Google Gemini 1.5 Pro / Gemini 2.0
**Project**: Osprey - Enterprise Immigration AI System
**Context Window**: Optimized for 2M token context

---

## 🎯 Project Identity

**Osprey** is a production-grade, multi-agent AI platform that automates end-to-end US immigration case processing. Built with FastAPI (backend) and React+TypeScript (frontend), it combines document AI, LLM orchestration, and USCIS compliance automation.

### Core Technologies
- **Backend**: Python 3.11+ | FastAPI 0.128.0 | MongoDB 6.0+ (Motor async) | OpenAI GPT-4o | **Google Gemini 1.5 Pro** ⭐
- **Frontend**: TypeScript 5.8+ | React 18.3 | Vite 5.4 | Tailwind CSS 3.4 | shadcn/ui
- **Infrastructure**: Stripe payments | Resend email | Sentry monitoring | Google Cloud (Document AI, Vision, Speech)

### Key Capabilities
✅ **Multi-agent orchestration**: 7 specialized AI agents (Document Validator, Form Validator, Eligibility Analyst, Compliance Checker, Letter Writer, USCIS Translator, QA Agent)
✅ **Document processing**: OCR + classification via Google Document AI
✅ **Multi-modal analysis**: Passport validation, photo verification (uses **Gemini** for visual understanding)
✅ **USCIS form generation**: I-130, I-539, I-765, I-90, I-485, N-400, and more
✅ **Payment processing**: Stripe integration with webhooks
✅ **Conversational AI**: Maria assistant for user guidance

---

## 📁 Repository Structure

```
camada-osprey-core/
├── backend/                        # FastAPI async backend
│   ├── server.py                  # Main application entry point
│   ├── core/                      # Infrastructure layer
│   │   ├── auth.py               # JWT authentication
│   │   ├── database.py           # MongoDB async lifecycle
│   │   ├── logging.py            # Structured JSON logging
│   │   ├── serialization.py     # MongoDB-safe JSON serialization
│   │   └── sentry.py             # Error tracking integration
│   ├── api/                       # API routers (23 modules)
│   │   ├── auth.py               # Login, registration
│   │   ├── documents.py          # Upload, OCR, analysis
│   │   ├── auto_application*.py  # Case management, AI processing
│   │   ├── payments.py           # Stripe checkout, webhooks
│   │   ├── uscis_forms.py        # Form generation
│   │   └── ...                   # 18 more routers
│   ├── models/                    # Pydantic schemas
│   │   ├── enums.py              # VisaType, USCISForm, etc.
│   │   ├── auto_application.py   # Case models
│   │   └── user.py               # User models
│   ├── services/                  # Business logic
│   │   ├── cases.py              # Case status management
│   │   ├── documents.py          # Document processing logic
│   │   └── education.py          # Education validation
│   ├── requirements.txt           # 462 lines, 18 categories, 25 CVEs patched
│   └── README.md                 # 1830 lines of documentation
│
├── frontend/                      # React + TypeScript SPA
│   ├── src/
│   │   ├── pages/                # 25+ page components
│   │   │   ├── NewHomepage.tsx  # Landing page
│   │   │   ├── SelectForm.tsx   # Visa selection
│   │   │   ├── BasicData.tsx    # Personal data collection
│   │   │   ├── CoverLetterModule.tsx  # AI letter generation
│   │   │   ├── EmbeddedCheckout.tsx   # Stripe payment
│   │   │   └── Dashboard.tsx    # User case management
│   │   ├── components/           # 35+ reusable UI components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── ProgressTracker.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── BetaBanner.tsx
│   │   ├── lib/                  # Utilities
│   │   │   ├── api.ts           # makeApiCall (CRITICAL)
│   │   │   ├── utils.ts         # Helper functions
│   │   │   └── validation.ts    # Zod schemas
│   │   └── hooks/                # Custom React hooks
│   ├── package.json              # npm dependencies
│   └── README.md                # 1080 lines of documentation
│
├── README.md                     # Root docs (1014 lines, Mermaid diagrams)
├── SECURITY_AUDIT_2026-01-13.md # Latest security audit (465 lines)
├── CLAUDE.md                     # Claude AI guide
└── GEMINI.md                     # This file
```

---

## 🧠 Gemini-Specific Integration Points

### Where Gemini is Used in Osprey

1. **Document Analysis** (`document_analyzer_agent.py`):
   - Multi-modal understanding of passport photos, birth certificates, medical documents
   - Visual quality assessment (image clarity, completeness)
   - Fraud detection indicators

2. **Dr. Miguel Agent** (`gemini_dra_paula_agent.py`):
   - Medical document interpretation
   - Brazilian doctor credentials validation
   - Portuguese ↔ English translation

3. **Maria Chat Assistant** (`maria_gemini_chat.py`):
   - Conversational guidance for visa applicants
   - Multi-turn context understanding
   - Policy explanation in plain language

### Gemini API Usage Pattern

```python
import google.generativeai as genai

# Configuration
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# Text generation
response = model.generate_content("Analyze this visa eligibility...")
result = response.text

# Multi-modal (text + image)
response = model.generate_content([
    "Is this passport photo acceptable for USCIS submission?",
    {"mime_type": "image/jpeg", "data": image_bytes}
])

# Structured output
response = model.generate_content(
    "Extract data from this document...",
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=DocumentData
    )
)
```

---

## 🔧 Critical Patterns

### Backend (Python/FastAPI)

#### 1. Async/Await is Mandatory
```python
# ✅ CORRECT
async def process_document(doc_id: str) -> dict:
    doc = await db.documents.find_one({"id": doc_id})
    analysis = await analyze_with_gemini(doc["image_url"])
    await db.documents.update_one(
        {"id": doc_id},
        {"$set": {"analysis": analysis}}
    )
    return analysis

# ❌ WRONG - Blocks event loop
def process_document(doc_id: str) -> dict:
    doc = db.documents.find_one({"id": doc_id})  # Synchronous!
    return doc
```

#### 2. Pydantic Validation
```python
# ✅ CORRECT
from pydantic import BaseModel, Field
from typing import Literal

class DocumentAnalysis(BaseModel):
    document_type: Literal["passport", "birth_certificate", "diploma"]
    quality_score: float = Field(ge=0, le=1)
    extracted_data: dict
    fraud_indicators: list[str] = []

@router.post("/analyze", response_model=DocumentAnalysis)
async def analyze_document(doc_id: str):
    result = await gemini_analyze(doc_id)
    return DocumentAnalysis(**result)  # Auto-validated

# ❌ WRONG - No validation
@router.post("/analyze")
async def analyze_document(doc_id: str):
    return await gemini_analyze(doc_id)  # Might be malformed
```

#### 3. MongoDB Serialization
```python
# ✅ CORRECT
from core.serialization import serialize_doc

case = await db.auto_cases.find_one({"case_id": case_id})
return serialize_doc(case)  # Converts ObjectId → str, datetime → ISO

# ❌ WRONG
case = await db.auto_cases.find_one({"case_id": case_id})
return case  # ObjectId not JSON serializable!
```

#### 4. Structured Logging
```python
# ✅ CORRECT
import logging
logger = logging.getLogger(__name__)

logger.info(
    "Gemini analysis completed",
    extra={
        "doc_id": doc_id,
        "model": "gemini-1.5-pro",
        "confidence": 0.95,
        "processing_time_ms": 1234
    }
)

# ❌ WRONG
print(f"Analysis done for {doc_id}")  # Lost in production
```

#### 5. Error Handling
```python
# ✅ CORRECT
from fastapi import HTTPException

try:
    analysis = await gemini_analyze(image_data)
except gemini.ResourceExhausted:
    logger.warning("Gemini rate limit hit", extra={"doc_id": doc_id})
    raise HTTPException(429, "Rate limit exceeded, please retry")
except Exception as e:
    logger.error("Gemini analysis failed", exc_info=True)
    raise HTTPException(500, "Analysis failed")

# ❌ WRONG
analysis = await gemini_analyze(image_data)  # Unhandled exceptions crash server
```

---

### Frontend (React/TypeScript)

#### 1. API Calls via makeApiCall
```typescript
// ✅ CORRECT - Centralized error handling, auto /api prefix
import { makeApiCall } from '@/lib/api';

const analysis = await makeApiCall<DocumentAnalysis>(
  `/documents/${docId}/analyze`,
  'POST',
  { model: 'gemini-1.5-pro' }
);

// makeApiCall returns parsed JSON, throws on errors, auto-retries

// ❌ WRONG - Manual fetch, no error handling
const res = await fetch(`/api/documents/${docId}/analyze`);
const data = await res.json();  // Might fail silently
```

#### 2. Controlled Inputs (Never Undefined)
```typescript
// ✅ CORRECT
const [formData, setFormData] = useState({
  passportNumber: caseData?.passportNumber || '',  // Always string
  issueDate: caseData?.issueDate || '',
  expiryDate: caseData?.expiryDate || ''
});

<input
  value={formData.passportNumber}  // Never undefined
  onChange={(e) => setFormData({...formData, passportNumber: e.target.value})}
/>

// ❌ WRONG - Uncontrolled to controlled warning
const [formData, setFormData] = useState({
  passportNumber: caseData?.passportNumber  // Can be undefined!
});
```

#### 3. Type Safety
```typescript
// ✅ CORRECT
interface GeminiAnalysisResponse {
  document_type: 'passport' | 'birth_certificate' | 'diploma';
  quality_score: number;
  extracted_data: Record<string, string>;
  fraud_indicators: string[];
}

async function analyzeDocument(docId: string): Promise<GeminiAnalysisResponse> {
  return await makeApiCall<GeminiAnalysisResponse>(
    `/documents/${docId}/analyze`,
    'POST'
  );
}

// ❌ WRONG - Loses type safety
async function analyzeDocument(docId: string): Promise<any> {
  return await makeApiCall(`/documents/${docId}/analyze`, 'POST');
}
```

---

## 📋 Common Tasks

### Task: Add Gemini-Powered Analysis Endpoint

**Backend** (`backend/api/gemini_analysis.py`):
```python
from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from core.database import db
from models.analysis import AnalysisRequest, AnalysisResponse
import google.generativeai as genai
import logging

router = APIRouter(prefix="/api/gemini-analysis", tags=["Gemini Analysis"])
logger = logging.getLogger(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

@router.post("/document", response_model=AnalysisResponse)
async def analyze_document_with_gemini(
    request: AnalysisRequest,
    user: dict = Depends(get_current_user)
):
    """
    Analyze document using Gemini 1.5 Pro multi-modal capabilities.
    """
    logger.info("Starting Gemini analysis", extra={"doc_id": request.doc_id})

    # Fetch document
    doc = await db.documents.find_one({"id": request.doc_id, "user_id": user["id"]})
    if not doc:
        raise HTTPException(404, "Document not found")

    try:
        # Multi-modal analysis
        response = model.generate_content([
            f"Analyze this {request.document_type} for USCIS submission. "
            f"Check quality, completeness, and fraud indicators.",
            {"mime_type": doc["mime_type"], "data": doc["image_data"]}
        ])

        analysis = {
            "document_type": request.document_type,
            "analysis_text": response.text,
            "model_used": "gemini-1.5-pro",
            "analyzed_at": datetime.now(timezone.utc)
        }

        # Store results
        await db.documents.update_one(
            {"id": request.doc_id},
            {"$set": {"gemini_analysis": analysis}}
        )

        logger.info(
            "Gemini analysis completed",
            extra={"doc_id": request.doc_id, "confidence": 0.95}
        )

        return AnalysisResponse(**analysis)

    except Exception as e:
        logger.error("Gemini analysis failed", exc_info=True, extra={"doc_id": request.doc_id})
        raise HTTPException(500, f"Analysis failed: {str(e)}")
```

**Register in `server.py`**:
```python
from api.gemini_analysis import router as gemini_analysis_router

app.include_router(gemini_analysis_router)
```

**Frontend** (`src/lib/api.ts`):
```typescript
export interface GeminiAnalysisRequest {
  doc_id: string;
  document_type: 'passport' | 'birth_certificate' | 'diploma';
}

export interface GeminiAnalysisResponse {
  document_type: string;
  analysis_text: string;
  model_used: string;
  analyzed_at: string;
}

export async function analyzeDocumentWithGemini(
  request: GeminiAnalysisRequest
): Promise<GeminiAnalysisResponse> {
  return await makeApiCall<GeminiAnalysisResponse>(
    '/gemini-analysis/document',
    'POST',
    request
  );
}
```

---

### Task: Implement Multi-Turn Conversation

```python
# Backend (conversation_agent.py)
async def gemini_conversation(user_id: str, message: str) -> str:
    """Multi-turn conversation with context."""

    # Fetch conversation history
    history = await db.conversations.find_one({"user_id": user_id})

    # Build context
    chat = model.start_chat(history=history.get("messages", []))

    # Send message
    response = chat.send_message(message)

    # Store updated history
    await db.conversations.update_one(
        {"user_id": user_id},
        {
            "$set": {"messages": chat.history},
            "$push": {
                "turns": {
                    "user": message,
                    "assistant": response.text,
                    "timestamp": datetime.now(timezone.utc)
                }
            }
        },
        upsert=True
    )

    return response.text
```

---

## ⚠️ Anti-Patterns (Don't Do This!)

### ❌ Synchronous Database Calls
```python
# WRONG
def get_case(case_id: str):
    return db.cases.find_one({"case_id": case_id})  # Blocks event loop!
```

### ❌ Ignoring Gemini Rate Limits
```python
# WRONG - No rate limit handling
for doc in documents:
    analysis = model.generate_content(doc)  # Will hit rate limit!

# RIGHT - Implement exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def analyze_with_retry(doc):
    return model.generate_content(doc)
```

### ❌ Not Sanitizing LLM Output
```python
# WRONG - Trusting LLM output directly
analysis = model.generate_content("Extract name from document")
db.users.update_one({"id": user_id}, {"$set": {"name": analysis.text}})

# RIGHT - Validate with Pydantic
class ExtractedName(BaseModel):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)

analysis_text = model.generate_content("Extract name...")
validated_name = ExtractedName.model_validate_json(analysis_text)
```

### ❌ Using datetime.utcnow() (Deprecated)
```python
# WRONG
from datetime import datetime
created_at = datetime.utcnow()  # Deprecated in Python 3.12+

# RIGHT
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

### ❌ Returning Raw MongoDB Documents
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

## 🔐 Security Best Practices

### 1. API Key Management
```python
# ✅ CORRECT - Use environment variables
import os
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# ❌ WRONG - Hardcoded keys
genai.configure(api_key="AIzaSy...")  # Leaked in git!
```

### 2. Input Validation
```python
# ✅ CORRECT - Validate before sending to Gemini
from input_sanitizer import sanitize_input

user_query = sanitize_input(request.query)
response = model.generate_content(user_query)

# ❌ WRONG - Raw user input
response = model.generate_content(request.query)  # Prompt injection risk!
```

### 3. Rate Limiting
```python
# ✅ CORRECT - Apply rate limits
from rate_limiter import check_rate_limit

await check_rate_limit(user["id"], "gemini_analysis", limit=10, window=60)
analysis = model.generate_content(prompt)

# ❌ WRONG - No rate limiting
analysis = model.generate_content(prompt)  # Abuse potential!
```

### 4. Content Filtering
```python
# ✅ CORRECT - Check safety ratings
response = model.generate_content(
    prompt,
    safety_settings={
        gemini.HarmCategory.HARM_CATEGORY_HATE_SPEECH: gemini.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        gemini.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: gemini.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    }
)

if response.prompt_feedback.block_reason:
    raise HTTPException(400, "Content filtered by safety settings")
```

---

## 📊 Monitoring Gemini Usage

### Log Gemini API Calls
```python
logger.info(
    "Gemini API call",
    extra={
        "model": "gemini-1.5-pro",
        "input_tokens": len(prompt.split()),
        "output_tokens": len(response.text.split()),
        "latency_ms": latency,
        "user_id": user["id"],
        "endpoint": "document_analysis"
    }
)
```

### Track Costs
```python
# Estimate cost (Gemini 1.5 Pro pricing as of 2026-01-13)
input_cost_per_1k = 0.0035  # $0.0035 per 1K input tokens
output_cost_per_1k = 0.0105  # $0.0105 per 1K output tokens

cost = (
    (input_tokens / 1000) * input_cost_per_1k +
    (output_tokens / 1000) * output_cost_per_1k
)

logger.info("Gemini cost", extra={"cost_usd": cost, "user_id": user["id"]})
```

---

## 🚀 Performance Optimization

### 1. Batch Processing
```python
# ✅ EFFICIENT - Batch similar requests
documents = await db.documents.find({"status": "pending"}).to_list(100)

batch_prompts = [
    f"Analyze document {doc['id']}: {doc['type']}"
    for doc in documents
]

# Process in parallel with rate limit
from asyncio import Semaphore
semaphore = Semaphore(5)  # Max 5 concurrent requests

async def analyze_with_semaphore(prompt):
    async with semaphore:
        return model.generate_content(prompt)

results = await asyncio.gather(*[analyze_with_semaphore(p) for p in batch_prompts])
```

### 2. Caching
```python
# ✅ EFFICIENT - Cache common queries
from cachetools import TTLCache

gemini_cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL

async def cached_gemini_query(prompt: str) -> str:
    if prompt in gemini_cache:
        logger.info("Cache hit", extra={"prompt_length": len(prompt)})
        return gemini_cache[prompt]

    response = model.generate_content(prompt)
    gemini_cache[prompt] = response.text
    return response.text
```

### 3. Stream Responses for Long Content
```python
# ✅ EFFICIENT - Stream for better UX
response = model.generate_content(prompt, stream=True)

async def stream_response():
    for chunk in response:
        yield chunk.text

@router.get("/stream-analysis")
async def stream_gemini_analysis(prompt: str):
    return StreamingResponse(stream_response(), media_type="text/plain")
```

---

## 🧪 Testing Gemini Integration

### Unit Test Example
```python
# tests/test_gemini_analysis.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_analyze_document_success():
    mock_response = AsyncMock()
    mock_response.text = "Document is valid passport, quality score: 0.95"

    with patch('google.generativeai.GenerativeModel.generate_content', return_value=mock_response):
        result = await analyze_document_with_gemini("doc-123")

    assert result["model_used"] == "gemini-1.5-pro"
    assert "valid passport" in result["analysis_text"]

@pytest.mark.asyncio
async def test_analyze_document_rate_limit():
    with patch('google.generativeai.GenerativeModel.generate_content', side_effect=ResourceExhausted):
        with pytest.raises(HTTPException) as exc:
            await analyze_document_with_gemini("doc-123")

    assert exc.value.status_code == 429
```

---

## 📚 Key Resources

- **Root README**: [README.md](README.md) - System architecture with Mermaid diagrams
- **Backend README**: [backend/README.md](backend/README.md) - 1830 lines of backend patterns
- **Frontend README**: [frontend/README.md](frontend/README.md) - 1080 lines of frontend patterns
- **Security Audit**: [SECURITY_AUDIT_2026-01-13.md](backend/SECURITY_AUDIT_2026-01-13.md) - Latest vulnerability report
- **API Docs**: `http://localhost:8001/docs` - Interactive Swagger UI
- **Gemini Docs**: https://ai.google.dev/gemini-api/docs

---

## 🎓 Learning Path for New Contributors

1. **Read Root README** → Understand overall architecture
2. **Review Backend README** → Learn FastAPI patterns
3. **Review Frontend README** → Learn React+TypeScript patterns
4. **Explore API Docs** → See all endpoints at `/docs`
5. **Run Security Audit** → `pip-audit` to check vulnerabilities
6. **Try Example Tasks** → Follow "Common Tasks" section above

---

## ⚡ Quick Commands

```bash
# Backend
cd backend && source venv/bin/activate
pip install -r requirements.txt
python3 server.py

# Frontend
cd frontend && npm install && npm run dev

# Tests
pytest                    # Backend
npm test                 # Frontend

# Security
pip-audit               # Check vulnerabilities

# Lint & Format
black . && flake8 .     # Backend
npm run lint            # Frontend
```

---

**Last Updated**: 2026-01-13
**Version**: 2.0.0
**Gemini Version**: 1.5 Pro (2M context)
**Status**: Production-ready with active Gemini integration
