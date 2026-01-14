# Refactor Improvement Plan

## Goal
Split the monolithic `backend/server.py` into focused, PEP-8-friendly modules while keeping behavior and API surface stable.

## Current Status (Completed Work)
Major route groups and helpers have been extracted into new modules and wired back into the app. These routers are now included in `backend/server.py` and removed from the server file.

### New Core Modules
- `backend/core/logging.py`: `setup_logging`, JSON/Plain formatters, env-based logging.
- `backend/core/auth.py`: JWT, hashing, auth dependencies, `set_db` support.
- `backend/core/database.py`: startup/shutdown, schedulers, `DBProxy` to avoid `None` db errors.
- `backend/core/serialization.py`: `serialize_doc` helper moved out of `server.py`.
- `backend/core/sentry.py`: Sentry initialization with FastAPI/Starlette/AioHTTP/Asyncio/HTTPX/Logging integrations.

### New Routers (already wired into server)
- `backend/api/auth.py`: auth routes.
- `backend/api/education.py`: education endpoints.
- `backend/api/documents.py`: document endpoints + Dr. Miguel logic.
- `backend/api/payments.py`: Stripe payment endpoints + vouchers + auto-application process-payment.
- `backend/api/admin_products.py`: admin product management.
- `backend/api/owl_agent.py`: Owl agent flows + helpers.
- `backend/api/auto_application.py`: auto-application CRUD.
- `backend/api/auto_application_ai.py`: auto-application AI/QA endpoints.
- `backend/api/auto_application_packages.py`: package generation + submission instructions + helpers.
- `backend/api/uscis_forms.py`: USCIS form generation/download + form data endpoints.
- `backend/api/knowledge_base.py`: knowledge base admin endpoints.
- `backend/api/auto_application_downloads.py`: case-based package downloads.
- `backend/api/downloads.py`: `/download/*` endpoints.
- `backend/api/email_packages.py`: package email endpoints + Resend config.
- `backend/api/specialized_agents.py`: specialized agent endpoints.
- `backend/api/completeness.py`: completeness analysis endpoints.
- `backend/api/friendly_form.py`: friendly form submission + structure endpoints.
- `backend/api/voice.py`: voice websocket + validate/analyze/status endpoints.

### New Models
- `backend/models/auto_application.py`: `CaseStatus`, `AutoApplicationCase`, `CaseCreate`, `CaseUpdate`.
- `backend/models/enums.py`: added `USCISForm` enum (moved from server).

### Other Fixes (already done)
- Replaced `datetime.utcnow()` with `datetime.now(timezone.utc)` across backend.
- Added missing deps to `backend/requirements.txt` (e.g., `beautifulsoup4`, `emergentintegrations` uncommented).
- Stripe guard returns 503 when `STRIPE_API_KEY` missing.
- Added logging env vars: `LOG_LEVEL`, `LOG_PRETTY`, `LOG_FORMAT`, `BACKUP_DIR` to `.env`/`.env.example`.
- Replaced stdout prints in `backend/*.py` with `logger.*` calls (info/warning/error).
- Integrated Sentry via `backend/core/sentry.py` and new env vars in `.env`/`.env.example`.
- Added `backend/README.md` for backend-specific operational details.
- Fixed duplicate specialist registration in `case_finalizer_complete.py` (via safe import).

## Recent Cleanups to Keep in Mind
- `backend/server.py` now imports `serialize_doc` from `backend/core/serialization.py`.
- Several endpoint blocks removed from `backend/server.py` as they were moved to routers above.
- Owl agent and knowledge base endpoints are fully removed from `server.py`.
- Payments endpoints were consolidated; only the Owl webhook and general webhook handling remain in `server.py`.

## Remaining Work (Next Refactor Targets)
The following groups are still defined inside `backend/server.py` and should be moved into routers. Suggested order:

1) Demo/HTML endpoints near bottom of `server.py`
   - `/api/*-demo` and sample PDF endpoints

## Known Hotspots / Dependencies
- `server.py` still owns globals and initialization that some routers rely on:
  - `oracle`, `document_analyzer`, `form_filler`, `translator` (imported after logging setup)
  - These may need a `core/agents.py` or dependency injection to avoid import cycles.
- `RequestPackageEmailRequest` and `SendPackageEmailRequest` moved to `backend/api/email_packages.py`.
- Some endpoints reference `db.auto_application_cases` and others `db.auto_cases`.
  - Check consistency and standardize naming later.

## Router Includes in `backend/server.py`
Make sure these are still included:
- `auth_router`, `education_router`, `documents_router`, `payments_router`, `admin_products_router`
- `owl_agent_router`, `auto_application_router`, `auto_application_ai_router`
- `auto_application_packages_router`, `uscis_forms_router`, `knowledge_base_router`
- `auto_application_downloads_router`, `downloads_router`, `email_packages_router`
- `agents_router`, `oracle_router`, `visa_updates_admin_router`, `specialized_agents_router`
- `completeness_router`, `friendly_form_router`
- `voice_router`, `voice_ws_router`

## Suggested Next Steps When Resuming
1) Create new router modules for the remaining endpoint groups (Visa updates, Agents, Oracle, Specialized agents, Completeness).
2) Move any helper functions used by those endpoints into `backend/services/` or `backend/core/` as needed.
3) Keep `backend/server.py` only for app initialization, middleware, global setup, and router includes.
4) Run search for leftover endpoint definitions using:
   - `rg -n "@api_router" backend/server.py`
5) Verify no duplicate routes remain after each move.

## Files to Inspect When Resuming
- `backend/server.py` (remaining endpoints)
- `backend/api/*` (new routers)
- `backend/models/*` (new model defs)
- `backend/services/*` (helpers)
