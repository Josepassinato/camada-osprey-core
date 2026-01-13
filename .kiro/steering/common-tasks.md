---
inclusion: manual
---

# Common Development Tasks

## Task 1: Add a New API Endpoint

**Step 1**: Create router in `backend/api/my_feature.py`
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

## Task 2: Add a Database Collection

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

## Task 3: Add an AI Agent

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

## Task 4: Add a New React Page

1. **Create page component** in `frontend/src/pages/MyPage.tsx`
2. **Add route** in `frontend/src/App.tsx`
3. **Add navigation link** if needed in sidebar/header

## Task 5: Run Tests

```bash
# Backend
cd backend
pytest                              # Run all tests
pytest tests/test_auth.py          # Run specific test
pytest --cov=api --cov=core        # With coverage

# Frontend
cd frontend
npm test          # Unit tests
npm run lint      # ESLint
npm run type-check # TypeScript
```
