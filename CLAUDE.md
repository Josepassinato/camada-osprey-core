# Osprey - AI Immigration Platform

## Project Overview

Osprey is a B2C SaaS platform that automates U.S. visa application packages using 12 specialized AI agents. It handles highly sensitive immigration data (PII, A-Numbers, passport info) and processes real payments via Stripe in LIVE mode.

## Architecture

- **Frontend**: React 18 + TypeScript + Vite (port 3000)
- **Backend**: FastAPI + Python (port 8001)
- **Database**: MongoDB (Motor async driver)
- **WhatsApp**: Node.js + Baileys (baileys-server/)
- **AI**: OpenAI GPT-4 + Google Gemini + Emergent LLM

## Key Files

- `backend/server.py` - Main API server (13K+ lines, 60+ endpoints)
- `backend/visa_api.py` - Multi-agent orchestration
- `backend/stripe_integration.py` - Payment processing (LIVE MODE)
- `backend/google_document_ai_integration.py` - Document OCR
- `visa_specialists/` - 8 visa-specific AI agents
- `frontend/src/` - React frontend components

## Security Tools Available

The following security scanning tools are installed on this VPS and available for Claude Code to use:

### Quick Commands

```bash
# Quick scan (< 30 seconds) - run during development
./security/scan-quick.sh

# Full comprehensive scan - run before releases
./security/scan-all.sh

# Scan a specific file you just edited
./security/scan-file.sh backend/server.py

# Run Semgrep with Osprey-specific rules
./security/scan-semgrep.sh --custom-only

# Run Semgrep with community rules too (slower, needs internet)
./security/scan-semgrep.sh --full
```

### Individual Tools

```bash
# Bandit - Python security linter
bandit -r backend/ --severity-level medium

# Semgrep - Pattern-based vulnerability scanner
semgrep scan --config security/semgrep-osprey-rules.yaml backend/

# pip-audit - Python dependency vulnerability check
pip-audit -r backend/requirements.txt

# npm audit - Frontend dependency check
cd frontend && npm audit

# Safety - Python dependency vulnerability database
safety check -r backend/requirements.txt
```

### Reports

Security scan reports are saved to `security/reports/` with timestamps.

## Security Guidelines for Development

### CRITICAL - Always Follow These Rules

1. **NEVER hardcode secrets** - Always use `os.environ.get()` or `os.getenv()`
2. **NEVER use CORS wildcard in production** - Restrict `allow_origins` to specific domains
3. **ALWAYS validate user ownership** - When querying cases, ALWAYS filter by `user_id`:
   ```python
   # WRONG - IDOR vulnerability
   case = await db.auto_cases.find_one({"case_id": case_id})

   # CORRECT - validates ownership
   case = await db.auto_cases.find_one({"case_id": case_id, "user_id": current_user["user_id"]})
   ```
4. **ALWAYS require authentication** on sensitive endpoints (`/api/admin/*`, `/api/case/*`, `/api/documents/*`, `/api/payment/*`)
5. **NEVER trust client-provided payment amounts** - Calculate server-side from product catalog
6. **ALWAYS verify Stripe webhook signatures** with `stripe.Webhook.construct_event()`
7. **ALWAYS sanitize file uploads** - Validate file types, size limits, and sanitize filenames
8. **NEVER log sensitive data** - Mask A-Numbers, SSNs, passport numbers in logs
9. **ALWAYS use parameterized queries** - Never string-concatenate user input into MongoDB queries

### When Modifying Code

Before committing changes to security-sensitive files, run:
```bash
./security/scan-file.sh <changed_file>
```

Security-sensitive files include:
- `backend/server.py` (auth, endpoints)
- `backend/stripe_integration.py` (payments)
- `backend/admin_security.py` (admin auth)
- `backend/visa_api.py` (case processing)
- Any file handling user input or database queries

## Service Management

```bash
# Check service status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all
```

## Testing

```bash
# Backend tests
cd backend && python -m pytest tests/

# Frontend build check
cd frontend && npm run build
```

## Environment Variables Required

The following must be set (never hardcoded):
- `JWT_SECRET` - JWT signing secret
- `STRIPE_API_KEY` / `STRIPE_SECRET_KEY` - Stripe keys
- `STRIPE_WEBHOOK_SECRET` - Webhook verification
- `OPENAI_API_KEY` - OpenAI GPT-4
- `GOOGLE_APPLICATION_CREDENTIALS` - Google Cloud services
- `MONGODB_URI` - Database connection
- `RESEND_API_KEY` - Email service
