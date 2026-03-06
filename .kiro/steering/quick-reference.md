---
inclusion: always
---

# Quick Reference

## File Structure

### Backend Files
- **Main Entry**: `backend/server.py` (DO NOT add routes here)
- **Core Infrastructure**: `backend/core/{auth,database,logging,serialization,sentry}.py`
- **API Routers**: `backend/api/*.py` (23 modules)
- **Pydantic Models**: `backend/models/*.py`
- **Business Logic**: `backend/services/*.py`
- **Dependencies**: `backend/requirements.txt`

### Frontend Files
- **Main Entry**: `frontend/src/App.tsx`
- **Pages**: `frontend/src/pages/*.tsx` (25+ components)
- **Components**: `frontend/src/components/**/*.tsx` (35+ components)
- **API Client**: `frontend/src/lib/api.ts` **← CRITICAL**
- **Utilities**: `frontend/src/lib/utils.ts`
- **Hooks**: `frontend/src/hooks/*.ts`

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

## Success Metrics

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

## Key Principles

### When Writing Code:
1. Always check if a similar file exists before creating a new one
2. Prefer editing existing files over creating new ones
3. Follow established patterns in the codebase
4. Use type hints everywhere (Python + TypeScript)
5. Include error handling in all async operations
6. Add logging for important operations
7. Write tests for new functionality

### When Refactoring:
1. Understand existing code before modifying
2. Maintain backward compatibility unless explicitly asked to break it
3. Update tests to reflect changes
4. Update documentation if API changes

### When Debugging:
1. Check logs in Sentry dashboard
2. Review API docs at `/docs` for endpoint signatures
3. Verify environment variables in `.env` files
4. Check database with MongoDB queries
5. Test API endpoints with curl or Postman
