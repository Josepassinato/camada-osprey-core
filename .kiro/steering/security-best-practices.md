---
inclusion: always
---

# Security Best Practices

## NEVER:
- ❌ Hardcode API keys, passwords, or secrets
- ❌ Use `eval()` or `exec()` on user input
- ❌ Return raw error messages to users (info leak)
- ❌ Trust user input without validation
- ❌ Use `dangerouslySetInnerHTML` without sanitization
- ❌ Commit `.env` files to git

## ALWAYS:
- ✅ Use environment variables for secrets
- ✅ Validate all user input (Pydantic models, Zod schemas)
- ✅ Use parameterized queries (MongoDB prevents injection by default)
- ✅ Apply rate limiting to expensive operations
- ✅ Log security events (failed logins, permission denials)
- ✅ Use HTTPS in production
- ✅ Sanitize all user-generated content before displaying

## Environment Variables
```python
# Backend - Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
```

```typescript
// Frontend - Use Vite env variables
const API_URL = import.meta.env.VITE_API_URL;
```

## Input Validation
```python
# Backend - Pydantic validation
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        return v
```

## Error Handling
```python
# ✅ CORRECT - Generic error messages
try:
    user = await authenticate(email, password)
except Exception as e:
    logger.error("Authentication failed", extra={"email": email, "error": str(e)})
    raise HTTPException(401, "Invalid credentials")

# ❌ WRONG - Leaks implementation details
try:
    user = await authenticate(email, password)
except Exception as e:
    raise HTTPException(500, f"Database error: {str(e)}")
```

## Latest Security Audit
Refer to SECURITY_AUDIT_2026-01-13.md for comprehensive security review and fixes.
