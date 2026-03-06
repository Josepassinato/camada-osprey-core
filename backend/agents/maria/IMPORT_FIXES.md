# Maria Agent Import Fixes

## Issue
After migrating Maria agent to `backend/agents/maria/`, the server failed to start with:
```
NameError: name 'maria_api' is not defined
```

## Root Cause
Two files were still importing Maria modules from the old location:
1. `backend/server.py` - Missing import for Maria API router
2. `backend/core/database.py` - Importing `maria_api` from old location

## Fixes Applied

### 1. backend/server.py

**Added import:**
```python
from backend.agents.maria.api import router as maria_api_router
```

**Updated router registration:**
```python
# Before:
app.include_router(maria_api.router)

# After:
app.include_router(maria_api_router)
```

**Location:** Line ~138 (imports section) and line ~4584 (router registration)

### 2. backend/core/database.py

**Updated import:**
```python
# Before:
import maria_api

# After:
from backend.agents.maria import api as maria_api
```

**Usage remains the same:**
```python
maria_api.init_db(db)  # Still works correctly
```

**Location:** Line ~11 (imports section)

## Verification

✅ Server imports successfully:
```bash
python3 -c "import sys; sys.path.insert(0, '.'); from backend.server import app"
```

✅ No errors during import
✅ Maria API router properly registered
✅ Database initialization works correctly

## Files Modified

1. `backend/server.py`
   - Added: `from backend.agents.maria.api import router as maria_api_router`
   - Changed: `app.include_router(maria_api.router)` → `app.include_router(maria_api_router)`

2. `backend/core/database.py`
   - Changed: `import maria_api` → `from backend.agents.maria import api as maria_api`

## Remaining Work

The old Maria files still exist in `backend/`:
- `backend/maria_agent.py`
- `backend/maria_api.py`
- `backend/maria_voice.py`
- `backend/maria_whatsapp.py`
- `backend/maria_gemini_chat.py`

These will be removed in Phase 11 (Task 42) after confirming all functionality works correctly.

## Testing Checklist

- [x] Server starts without import errors
- [x] Maria API router is registered
- [x] Database initialization includes Maria
- [ ] Maria chat endpoint works (integration test)
- [ ] Maria voice endpoints work (integration test)
- [ ] Maria WhatsApp integration works (integration test)

## Next Steps

1. Run integration tests to verify Maria functionality (Phase 9, Task 35)
2. Update any remaining imports in other files if discovered
3. Remove old Maria files after full verification (Phase 11, Task 42)
