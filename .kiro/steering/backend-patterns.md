---
inclusion: fileMatch
fileMatchPattern: 'backend/**/*.py'
---

# Backend Coding Patterns (Python/FastAPI)

## CRITICAL RULES - MUST FOLLOW

### 1. Async/Await is MANDATORY
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
```

### 2. Pydantic Validation REQUIRED
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
```

### 3. MongoDB Serialization MANDATORY
```python
# ✅ CORRECT - Always serialize before returning
from core.serialization import serialize_doc

case = await db.auto_cases.find_one({"case_id": case_id})
return serialize_doc(case)  # Converts ObjectId → str, datetime → ISO

# ❌ WRONG - ObjectId not JSON serializable!
case = await db.auto_cases.find_one({"case_id": case_id})
return case  # FAILS with serialization error
```

### 4. Structured Logging REQUIRED
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

### 5. Use datetime.now(timezone.utc)
```python
# ✅ CORRECT - Timezone-aware datetime
from datetime import datetime, timezone

created_at = datetime.now(timezone.utc)

# ❌ WRONG - Deprecated in Python 3.12+
created_at = datetime.utcnow()
```

### 6. Proper HTTP Status Codes
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

## API Router Template
```python
from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from core.database import db
from core.serialization import serialize_doc
from models.my_feature import MyFeatureCreate, MyFeatureResponse
from datetime import datetime, timezone
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

## Anti-Patterns (NEVER DO THIS!)
- ❌ Synchronous database calls
- ❌ Using print() instead of logging
- ❌ Missing serialization on MongoDB documents
- ❌ datetime.utcnow() (deprecated)
- ❌ No error handling on async operations
- ❌ Hardcoded secrets or API keys
- ❌ Adding routes directly to server.py (use routers in api/)
