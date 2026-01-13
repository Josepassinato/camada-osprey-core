# GitHub Copilot Instructions - Osprey Platform

## Project Context

**Osprey** is an enterprise-grade B2C immigration AI platform that automates US visa application processing. The system combines multi-agent AI orchestration, document OCR, USCIS form generation, and payment processing.

### Tech Stack
- **Backend**: Python 3.11+ | FastAPI 0.128.0 | MongoDB 6.0+ (Motor async) | OpenAI GPT-4o | Google Gemini 1.5 Pro
- **Frontend**: TypeScript 5.8+ | React 18.3 | Vite 5.4 | Tailwind CSS 3.4 | shadcn/ui
- **Infrastructure**: Stripe | Resend | Sentry | Google Cloud (Document AI, Vision, Speech)

### Project Structure
```
camada-osprey-core/
├── backend/          # FastAPI async backend
│   ├── core/        # Infrastructure (auth, database, logging)
│   ├── api/         # API routers (23 modules, domain-organized)
│   ├── models/      # Pydantic schemas
│   └── services/    # Business logic
├── frontend/        # React + TypeScript SPA
│   ├── src/pages/   # 25+ page components
│   ├── src/components/  # 35+ UI components
│   └── src/lib/     # API client, utilities
```

---

## Code Generation Rules

### Backend (Python/FastAPI)

#### 1. Always Use Async/Await
```python
# ✅ Generate this
async def get_case(case_id: str) -> dict:
    case = await db.auto_cases.find_one({"case_id": case_id})
    return serialize_doc(case)

# ❌ Never generate this
def get_case(case_id: str):
    case = db.auto_cases.find_one({"case_id": case_id})
    return case
```

#### 2. Use Pydantic for Validation
```python
# ✅ Generate this
from pydantic import BaseModel, EmailStr, Field

class CaseCreate(BaseModel):
    form_code: str = Field(..., pattern=r"^(I|N)-\d+$")
    user_email: EmailStr
    visa_type: str

@router.post("/cases", response_model=CaseResponse)
async def create_case(data: CaseCreate):
    ...

# ❌ Never generate this
@router.post("/cases")
async def create_case(data: dict):  # No validation!
    ...
```

#### 3. Use Structured Logging
```python
# ✅ Generate this
import logging
logger = logging.getLogger(__name__)

logger.info(
    "Case created",
    extra={"case_id": case_id, "user_id": user_id}
)

# ❌ Never generate this
print(f"Case {case_id} created")
```

#### 4. Always Serialize MongoDB Documents
```python
# ✅ Generate this
from core.serialization import serialize_doc

case = await db.cases.find_one({"case_id": case_id})
return serialize_doc(case)  # Converts ObjectId to string

# ❌ Never generate this
case = await db.cases.find_one({"case_id": case_id})
return case  # ObjectId not JSON serializable!
```

#### 5. Use datetime.now(timezone.utc)
```python
# ✅ Generate this
from datetime import datetime, timezone

created_at = datetime.now(timezone.utc)

# ❌ Never generate this
created_at = datetime.utcnow()  # Deprecated in Python 3.12+
```

#### 6. Proper Error Handling
```python
# ✅ Generate this
from fastapi import HTTPException

if not case:
    raise HTTPException(404, "Case not found")

if not user.has_permission("admin"):
    raise HTTPException(403, "Insufficient permissions")

# ❌ Never generate this
if not case:
    return {"error": "Case not found"}  # Still HTTP 200!
```

---

### Frontend (React/TypeScript)

#### 1. Use makeApiCall for All API Requests
```typescript
// ✅ Generate this
import { makeApiCall } from '@/lib/api';

const cases = await makeApiCall<Case[]>('/cases', 'GET');

const newCase = await makeApiCall<Case>('/cases', 'POST', {
  form_code: 'I-539',
  visa_type: 'b2'
});

// ❌ Never generate this
const response = await fetch('/api/cases');
const cases = await response.json();
```

#### 2. Always Initialize Controlled Inputs
```typescript
// ✅ Generate this
const [formData, setFormData] = useState({
  firstName: data?.firstName || '',  // Never undefined
  lastName: data?.lastName || '',
  email: data?.email || ''
});

// ❌ Never generate this
const [formData, setFormData] = useState({
  firstName: data?.firstName  // Can be undefined!
});
```

#### 3. Define Proper TypeScript Interfaces
```typescript
// ✅ Generate this
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

// ❌ Never generate this
async function getCase(caseId: string): Promise<any> {
  return await makeApiCall(`/cases/${caseId}`, 'GET');
}
```

#### 4. Handle Errors Gracefully
```typescript
// ✅ Generate this
try {
  const data = await makeApiCall('/cases', 'POST', formData);
  toast.success('Case created successfully');
  navigate(`/cases/${data.case_id}`);
} catch (error) {
  console.error('Failed to create case:', error);
  toast.error('Failed to create case. Please try again.');
}

// ❌ Never generate this
const data = await makeApiCall('/cases', 'POST', formData);
// No error handling!
```

#### 5. Use Native Buttons for Custom Styles
```typescript
// ✅ Generate this for custom styling
<button
  className="bg-black text-white hover:bg-gray-800 px-4 py-2 rounded"
  onClick={handleClick}
>
  Custom Button
</button>

// ✅ OR use shadcn Button for standard styles
import { Button } from '@/components/ui/button';

<Button variant="default" onClick={handleClick}>
  Standard Button
</Button>

// ⚠️ Note: shadcn Button overrides custom className hover states
```

---

## API Endpoint Template

When generating a new API endpoint, use this template:

```python
# backend/api/my_feature.py
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
    """
    Create a new feature.

    Args:
        data: Feature creation data
        user: Current authenticated user

    Returns:
        MyFeatureResponse: Created feature

    Raises:
        HTTPException: 400 if validation fails, 500 for server errors
    """
    logger.info("Creating feature", extra={"user_id": user["id"]})

    try:
        feature = {
            "user_id": user["id"],
            "data": data.model_dump(),
            "created_at": datetime.now(timezone.utc)
        }

        result = await db.my_features.insert_one(feature)
        feature["_id"] = result.inserted_id

        logger.info(
            "Feature created successfully",
            extra={"feature_id": str(feature["_id"]), "user_id": user["id"]}
        )

        return serialize_doc(feature)

    except Exception as e:
        logger.error(
            "Failed to create feature",
            exc_info=True,
            extra={"user_id": user["id"]}
        )
        raise HTTPException(500, "Failed to create feature")
```

---

## React Component Template

When generating a new React component, use this template:

```typescript
// frontend/src/components/MyComponent.tsx
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { makeApiCall } from '@/lib/api';
import { cn } from '@/lib/utils';

interface MyComponentProps {
  initialValue?: string;
  onSubmit?: (value: string) => void;
  className?: string;
}

export function MyComponent({
  initialValue = '',
  onSubmit,
  className
}: MyComponentProps) {
  const [value, setValue] = useState(initialValue);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch data on mount if needed
    async function fetchData() {
      try {
        const data = await makeApiCall<DataType>('/endpoint', 'GET');
        setValue(data.value);
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Failed to load data');
      }
    }

    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await makeApiCall('/endpoint', 'POST', { value });
      onSubmit?.(value);
    } catch (err) {
      console.error('Failed to submit:', err);
      setError('Failed to submit. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn('p-4', className)}>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="border rounded px-3 py-2"
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Submit'}
        </Button>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </form>
    </div>
  );
}
```

---

## Security Guidelines

### Never Generate Code That:
- ❌ Hardcodes API keys, passwords, or secrets
- ❌ Uses `eval()` or `exec()` on user input
- ❌ Trusts user input without validation
- ❌ Uses `dangerouslySetInnerHTML` without sanitization
- ❌ Exposes internal error details to users

### Always Generate Code That:
- ✅ Uses environment variables for secrets
- ✅ Validates all user input (Pydantic/Zod)
- ✅ Uses parameterized queries
- ✅ Applies rate limiting to expensive operations
- ✅ Logs security events (failed logins, permission denials)

---

## Common Patterns

### Database Query Patterns
```python
# Find one
case = await db.auto_cases.find_one({"case_id": case_id})

# Find many with limit
cases = await db.auto_cases.find({"user_id": user_id}).to_list(100)

# Update
await db.auto_cases.update_one(
    {"case_id": case_id},
    {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc)}}
)

# Delete
await db.auto_cases.delete_one({"case_id": case_id})

# Aggregation
pipeline = [
    {"$match": {"user_id": user_id}},
    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
]
results = await db.auto_cases.aggregate(pipeline).to_list(None)
```

### Authentication Pattern
```python
# Protected endpoint
from core.auth import get_current_user

@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    return {
        "email": user["email"],
        "id": user["id"],
        "verified": user.get("verified", False)
    }
```

### React Hook Pattern
```typescript
// Custom hook for data fetching
function useCase(caseId: string) {
  const [case, setCase] = useState<Case | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCase() {
      try {
        setIsLoading(true);
        const data = await makeApiCall<Case>(`/cases/${caseId}`, 'GET');
        setCase(data);
      } catch (err) {
        console.error('Failed to fetch case:', err);
        setError('Failed to load case');
      } finally {
        setIsLoading(false);
      }
    }

    fetchCase();
  }, [caseId]);

  return { case, isLoading, error };
}
```

---

## Import Organization

### Backend (Python)
```python
# Standard library
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

# Local
from core.auth import get_current_user
from core.database import db
from core.serialization import serialize_doc
from models.case import CaseCreate, CaseResponse
```

### Frontend (TypeScript)
```typescript
// React
import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

// UI Components
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

// Utilities
import { makeApiCall } from '@/lib/api';
import { cn } from '@/lib/utils';

// Types
import type { Case, CaseStatus } from '@/types';
```

---

## Naming Conventions

### Backend
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Frontend
- **Files**: `PascalCase.tsx` (components), `kebab-case.ts` (utilities)
- **Components**: `PascalCase`
- **Functions**: `camelCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Hooks**: `useCamelCase`

---

## Testing Patterns

### Backend (pytest)
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_case(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/cases",
        json={"form_code": "I-539", "visa_type": "b2"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["form_code"] == "I-539"
    assert "case_id" in data
```

### Frontend (Jest + React Testing Library)
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MyComponent } from './MyComponent';

test('submits form with valid data', async () => {
  const handleSubmit = jest.fn();
  render(<MyComponent onSubmit={handleSubmit} />);

  fireEvent.change(screen.getByLabelText('Input'), {
    target: { value: 'test value' }
  });

  fireEvent.click(screen.getByText('Submit'));

  await waitFor(() => {
    expect(handleSubmit).toHaveBeenCalledWith('test value');
  });
});
```

---

## Documentation References

- **Root README**: [README.md](../README.md) - System architecture
- **Backend README**: [backend/README.md](../backend/README.md) - 1830 lines
- **Frontend README**: [frontend/README.md](../frontend/README.md) - 1080 lines
- **Claude Guide**: [CLAUDE.md](../CLAUDE.md)
- **Gemini Guide**: [GEMINI.md](../GEMINI.md)
- **Cursor Rules**: [.cursorrules](../.cursorrules)
- **API Docs**: http://localhost:8001/docs

---

## Quick Reference

### Start Development
```bash
# Backend
cd backend && python3 server.py

# Frontend
cd frontend && npm run dev
```

### Run Tests
```bash
# Backend
pytest

# Frontend
npm test
```

### Lint & Format
```bash
# Backend
black . && flake8 .

# Frontend
npm run lint
```

---

**Last Updated**: 2026-01-13
**Version**: 2.0.0
**GitHub Copilot**: Optimized for inline code suggestions
