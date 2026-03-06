# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Osprey is an enterprise-grade B2C immigration platform that combines AI-powered document processing, intelligent form generation, and multi-agent orchestration to streamline the immigration application process. It processes visa applications (B-2, F-1, H-1B, I-130, I-539, I-765, I-90, EB-2 NIW, EB-1A) with unprecedented speed and accuracy.

**Key Value Propositions:**
- 10x Faster Processing: AI-powered form filling reduces manual work from weeks to hours
- 95%+ Accuracy: Multi-agent QA ensures USCIS compliance before submission
- Cost Reduction: Automates repetitive tasks, reducing paralegal workload by 70%
- Scalability: Cloud-native architecture handles 1000+ concurrent cases

**Stack:**
- Backend: FastAPI 0.110.1 + Python 3.11+ + MongoDB 6.0+
- Frontend: React 18.3.1 + TypeScript 5.8.3 + Vite 5.4.19
- UI: Tailwind CSS 3.4.17 + shadcn/ui + Radix UI
- AI/LLM: OpenAI GPT-4o, Google Gemini 1.5 Pro, LiteLLM
- Document Processing: Google Document AI, PyMuPDF, ReportLab
- Payment: Stripe 12.5.1
- Email: Resend 2.17.0
- Monitoring: Sentry 2.20.0

## Repository Structure

```
/
├── backend/                    # FastAPI backend application
│   ├── server.py              # App initialization, router registration
│   ├── core/                  # Infrastructure (auth, database, logging, sentry)
│   ├── api/                   # API routers (domain-organized endpoints)
│   ├── models/                # Pydantic schemas (request/response models)
│   ├── services/              # Business logic layer
│   ├── policies/              # Immigration policy definitions (YAML)
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment template
│   └── README.md              # Backend documentation (1830+ lines)
│
├── frontend/                   # React + Vite frontend application
│   ├── src/
│   │   ├── pages/            # Page components (50+ pages)
│   │   ├── components/       # Reusable UI components (40+ components)
│   │   │   └── ui/           # shadcn/ui components (35+ components)
│   │   ├── contexts/         # React Context providers
│   │   ├── hooks/            # Custom React hooks
│   │   ├── utils/            # Utilities and API client
│   │   └── App.tsx           # Root component
│   ├── public/               # Static assets
│   ├── package.json          # npm dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── tailwind.config.ts    # Tailwind CSS config
│   ├── .env.example          # Environment template
│   └── README.md             # Frontend documentation (1080+ lines)
│
├── .kiro/                      # Project documentation and patterns
│   ├── README.md              # .kiro/ overview
│   ├── QUICK_START.md         # Onboarding guide
│   ├── SETUP_SUMMARY.md       # Environment setup
│   ├── steering/              # Development patterns
│   └── specs/                 # Refactoring requirements
│
├── immigration_resources/      # Curated knowledge and documents
├── samples/                    # Sample PDFs and test artifacts
├── tests/                      # Test files (integration, e2e, unit)
├── IMPROVEMENT_PLAN.md         # Backend refactor roadmap
└── README.md                   # Root documentation (1000+ lines)
```

## Repository Structure

```
/
├── docs/                    # Documentation
│   ├── architecture/        # Technical architecture docs
│   ├── guides/              # Setup and quick reference guides
│   ├── reports/             # Business reports and analysis
│   └── features/            # Feature documentation
├── tests/                   # Test files
│   ├── integration/         # Integration tests
│   ├── e2e/                 # End-to-end tests
│   ├── unit/                # Unit tests
│   └── results/             # Test result JSON files
├── scripts/                 # Utility scripts
│   ├── generators/          # Package generators
│   └── utilities/           # Utility scripts
├── samples/                 # Sample generated packages (PDFs)
│   ├── h1b/                 # H-1B visa samples
│   ├── i539/                # I-539 (B-2) samples
│   ├── i765/                # I-765 (EAD) samples
│   └── archive/             # Old iterations
├── backend/                 # FastAPI backend
├── frontend/                # React frontend
├── visa_specialists/        # Multi-agent system
└── archive/                 # Deprecated code
```

## Development Commands

### Backend (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start development server
python3 server.py

# Alternative: Run with uvicorn directly
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Backend URLs:**
- API Server: http://localhost:8001
- API Docs (Swagger): http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

### Frontend (React + Vite)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL and Stripe keys

# Start development server (port 3000)
npm run dev

# Build for production
npm run build

# Build for development (with source maps)
npm run build:dev

# Preview production build
npm run preview

# Lint
npm run lint

# Type check
npx tsc --noEmit
```

**Frontend URLs:**
- Development: http://localhost:3000 (or http://localhost:5173)
- Production: https://formfiller-26.preview.emergentagent.com

### Testing
```bash
# Backend tests (from repository root)
python3 tests/integration/test_agent_integration.py
python3 tests/integration/test_all_agents.py
python3 tests/e2e/comprehensive_visa_test.py

# Run all tests in a category with pytest
python3 -m pytest tests/integration/
python3 -m pytest tests/e2e/
python3 -m pytest tests/unit/

# Run with coverage
pytest --cov=backend/api --cover=backend/core

# Frontend tests
cd frontend
npm run test          # Unit tests (if configured)
npm run lint          # ESLint
npm run type-check    # TypeScript checking
```

### Services Management (Supervisor)
```bash
# Check status of all services
sudo supervisorctl status

# Restart services
sudo supervisorctl restart all
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# View logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

### MongoDB
```bash
# Connect to database
mongosh mongodb://localhost:27017/test_database

# View users
mongosh --eval "db.users.find({}, {email:1, role:1, first_name:1}).pretty()" test_database

# View admin users
mongosh --eval "db.users.find({role:{\$in:['admin','superadmin']}}, {email:1, role:1}).pretty()" test_database
```

### Admin User Management
```bash
cd backend
python3 create_admin_user.py          # Interactive admin creation
python3 create_test_admin.py          # Auto-create test admin
python3 create_superadmin.py          # Auto-create superadmin
python3 create_admin_user.py --list   # List all admins
```

## Architecture

### High-Level System Flow

Osprey follows a modern, decoupled architecture with clear separation between frontend, backend, and external services:

```
User → Frontend (React SPA) → Backend (FastAPI) → MongoDB
                                ├→ AI Providers (OpenAI, Gemini)
                                ├→ Google Document AI (OCR)
                                ├→ Stripe (Payments)
                                ├→ Resend (Email)
                                └→ Sentry (Monitoring)
```

### Backend Module Boundaries

```
server.py (App Init + Routers)
  ├→ core/ (Auth, Database, Logging, Sentry)
  ├→ api/ (Route Handlers)
  │   ├→ auth.py (Login, Register)
  │   ├→ documents.py (Upload, OCR, Analysis)
  │   ├→ auto_application*.py (Case Management)
  │   ├→ payments.py (Stripe Integration)
  │   ├→ uscis_forms.py (Form Generation)
  │   └→ specialized_agents.py (AI Agents)
  ├→ models/ (Pydantic Schemas)
  ├→ services/ (Business Logic)
  └→ policies/ (Immigration Rules)
```

### Multi-Agent System
The core innovation is a supervisor-specialist architecture:

**SupervisorAgent** (`visa_specialists/supervisor/supervisor_agent.py`):
- Analyzes user requests using regex patterns
- Detects visa type from natural language
- Delegates to appropriate specialist agent
- Validates final package quality

**Specialist Agents** (8 total):
- `b2_extension/` - B-2 Tourist Visa Extensions (I-539)
- `f1_student/` - F-1 Student Visa
- `h1b_worker/` - H-1B Work Visa
- `i130_family/` - I-130 Family-Based Immigration
- `i765_ead/` - I-765 Employment Authorization
- `i90_greencard/` - I-90 Green Card Renewal/Replace
- `eb2_niw/` - EB-2 National Interest Waiver
- `eb1a_extraordinary/` - EB-1A Extraordinary Ability

Each agent directory contains:
- `*_agent.py` - Agent implementation
- `knowledge_base/` - USCIS requirements and documents
- `lessons_learned.md` - Self-improvement documentation
- `uscis_requirements.md` - Official requirements

**Base Agent** (`visa_specialists/base_agent.py`):
- Parent class for all specialist agents
- Defines interface: `generate_package()`, `validate_package()`
- Shared functionality across specialists

**Supporting Agents**:
- `qa_agent.py` - Quality assurance validation (0-100% score)
- `metrics_tracker.py` - Performance tracking
- Learning system that reads `lessons_learned.md` to avoid past mistakes

### Backend Structure
`backend/` - Modular FastAPI application with clear separation of concerns:

**Core Infrastructure** (`core/`):
- `auth.py` - JWT authentication, password hashing, user verification
- `database.py` - MongoDB lifecycle, schedulers, DBProxy
- `logging.py` - Structured logging (JSON/plain)
- `serialization.py` - MongoDB-safe response serialization
- `sentry.py` - Sentry initialization with full integrations

**API Routers** (`api/` - domain-organized):
- `auth.py` - Login, registration, token validation
- `documents.py` - Document upload, OCR, analysis
- `auto_application*.py` - Case management, AI processing, packages
- `payments.py` - Stripe integration, webhooks, vouchers
- `uscis_forms.py` - USCIS form generation and validation
- `email_packages.py` - Email delivery via Resend
- `knowledge_base.py` - Admin knowledge management
- `specialized_agents.py` - AI agent orchestration
- `voice.py`, `oracle.py`, `completeness.py` - Additional features

**Models** (`models/`):
- `enums.py` - VisaType, USCISForm, DifficultyLevel, CaseStatus
- `auto_application.py` - Case schemas
- `user.py` - User and admin models
- `documents.py`, `education.py` - Domain models

**Services** (`services/` - business logic):
- `cases.py` - Case status, progress tracking
- `documents.py` - Document processing logic
- `education.py` - Education validation

**Legacy Files** (to be refactored):
- AI agents, document processors, form fillers, QA systems
- Admin tools, utilities, scripts

### Frontend Structure
`frontend/src/` - React 18 + TypeScript application:

**Pages** (`pages/` - 50+ pages):
- `Index.tsx`, `NewHomepage.tsx` - Landing pages
- `Login.tsx` - Authentication (login/register)
- `SelectForm.tsx` - Visa type selection with pricing
- `EmbeddedCheckout.tsx` - Stripe payment with vouchers
- `BasicData.tsx` - Personal information collection
- `FriendlyForm.tsx` - Simplified question interface
- `DocumentUploadAuto.tsx` - Document upload with AI extraction
- `StoryTelling.tsx` - User story narrative input
- `CoverLetterModule.tsx` - AI-generated cover letters
- `AIReviewAndTranslation.tsx` - Completeness review
- `CaseFinalizer.tsx` - Final package generation
- `Dashboard.tsx` - User case management
- Admin pages: `AdminVisaUpdatesPanel.tsx`, `AdminProductManagement.tsx`, `AdminKnowledgeBase.tsx`

**Components** (`components/` - 40+ components):
- `ui/` - shadcn/ui components (35+): button, card, dialog, form, input, etc.
- `BetaBanner.tsx`, `Hero.tsx`, `VisaRequirements.tsx`
- Form validation: React Hook Form + Zod

**Contexts** (`contexts/`):
- `LanguageContext.tsx` - Multi-language support (en/pt)
- `LocaleContext.tsx` - Localization and formatting
- `ProcessTypeContext.tsx` - Process flow state

**Hooks** (`hooks/`):
- `useFormSnapshot.ts` - Auto-save form data
- `useGoogleAuth.ts` - Google OAuth
- `useSessionManager.ts` - JWT session management
- `use-toast.ts` - Toast notifications

**Utilities** (`utils/`):
- `api.ts` - API client with makeApiCall utility

### Database Schema (MongoDB)
**Database:** `test_database`

**Collections:**
- `users` - User accounts (email, hashed_password, user_id, role)
- `auto_cases` - Main case data
  - `case_id`, `user_id`, `form_code` (visa type)
  - `basic_data` - Personal information
  - `simplified_form_responses` - Friendly form answers
  - `user_story_text` - User narrative
  - `uploaded_documents` - Document references
  - `payment_status`, `status`, `created_at`
- `payments` - Stripe payment records
- `sessions` - JWT session management

### API Endpoints
Backend runs on port 8001. Interactive documentation available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

**Authentication:**
- `POST /api/login` - User login → JWT token
- `POST /api/register` - User registration
- `POST /api/verify-token` - Validate JWT token

**Cases:**
- `POST /api/auto-application/cases` - Create new case
- `GET /api/auto-application/cases/{case_id}` - Get case details
- `PATCH /api/auto-application/cases/{case_id}` - Update case
- `GET /api/auto-application/cases` - List user's cases
- `POST /api/auto-application/cases/{case_id}/process-ai` - Trigger AI processing
- `POST /api/auto-application/cases/{case_id}/qa` - Run QA validation

**Documents:**
- `POST /api/documents/upload` - Upload and analyze document
- `GET /api/documents/{doc_id}` - Get document metadata
- `DELETE /api/documents/{doc_id}` - Delete document

**Payments:**
- `POST /api/payments/create-checkout-session` - Create Stripe checkout
- `POST /api/payments/webhook` - Stripe webhook handler
- `POST /api/payments/apply-voucher` - Apply discount voucher

**USCIS Forms:**
- `POST /api/uscis-forms/generate` - Generate filled form PDF
- `GET /api/uscis-forms/{form_code}/fields` - Get form fields

**Admin (requires admin/superadmin role):**
- `GET /api/admin/visa-updates/pending` - Pending policy updates
- `POST /api/admin/visa-updates/{id}/approve` - Approve update
- `GET /api/admin/products` - List products
- `POST /api/admin/products` - Create product
- `POST /api/admin/vouchers` - Create voucher

## Important Patterns

### Agent Execution Flow
1. User completes forms → saved to MongoDB `auto_cases`
2. Payment processed via Stripe
3. Case finalizer called → triggers SupervisorAgent
4. SupervisorAgent detects visa type from `form_code` or user text
5. SupervisorAgent delegates to specialist (e.g., B2ExtensionAgent)
6. Specialist:
   - Reads `lessons_learned.md` and `uscis_requirements.md`
   - Transforms MongoDB data to USCIS format
   - Generates PDF package using ReportLab
   - Validates required documents
7. QA Agent validates package (quality score)
8. Metrics tracked for performance monitoring
9. PDF saved to `/tmp/visa_packages/`
10. User receives download link + email notification

### LLM Integration
Uses multiple LLM providers via:
- **OpenAI API** - Direct for chatbot (`intelligent_owl_agent.py`)
- **Emergent Universal Key** (`emergentintegrations` library) - Unified access to OpenAI, Anthropic Claude, Google Gemini
- Key in environment: `EMERGENT_LLM_KEY=sk-emergent-aE5F536B80dFf0bA6F`

### Document Processing
1. **Upload** - User uploads documents via frontend
2. **Google Document AI** - Extracts text/data using OCR
3. **Validation** - `DocumentValidationAgent` checks completeness
4. **Classification** - AI categorizes document type
5. **Storage** - References stored in MongoDB `uploaded_documents` array

### Form Code Mapping
The `form_code` field maps user selections to USCIS forms:
- "I-539" → B-2 Extension
- "F-1" → F-1 Student
- "H-1B" → H-1B Worker
- "I-130" → Family-Based
- "I-765" → EAD
- "I-90" → Green Card Renewal
- "EB-2 NIW" → National Interest Waiver
- "EB-1A" → Extraordinary Ability

### Testing Strategy
Tests are organized in the `tests/` directory:
- `tests/integration/` - Integration tests for agents, backend, and document processing
- `tests/e2e/` - End-to-end visa application flows
- `tests/unit/` - Unit tests for forms, API endpoints, and utilities
- `tests/results/` - Test output JSON files and reports

Run tests from the repository root using relative paths.

## Environment Configuration

### Backend (.env in backend/)
```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=osprey_db

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256

# AI Providers (Required)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
EMERGENT_LLM_KEY=sk-emergent-...  # Optional alternative

# Google Cloud (Required for Document AI)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us

# Stripe (Use test keys in development)
STRIPE_SECRET_KEY=sk_test_...  # Production: sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Production: pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (Resend)
RESEND_API_KEY=re_...
SENDER_EMAIL=noreply@yourdomain.com

# CORS (Development: allow all, Production: specific domain)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
# Production: CORS_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_PRETTY=true  # Development: true, Production: false
LOG_FORMAT=plain  # Development: plain, Production: json

# Sentry (Production Monitoring)
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% of requests traced
SENTRY_PROFILES_SAMPLE_RATE=0.05  # 5% of requests profiled
```

### Frontend (.env in frontend/)
```bash
# Backend API Configuration
VITE_BACKEND_URL=http://localhost:8001
VITE_API_URL=http://localhost:8001

# Stripe (Use test keys in development)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...  # Production: pk_live_...

# Environment
NODE_ENV=development
```

**Security Notes:**
- ✅ `.env` files are in `.gitignore` - NEVER commit secrets
- ✅ Use test keys (`pk_test_`, `sk_test_`) in development
- ✅ Use live keys (`pk_live_`, `sk_live_`) only in production
- ✅ Change `JWT_SECRET` to a strong random value in production
- ✅ Restrict `CORS_ORIGINS` to specific domains in production

## Development URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Backend Docs**: http://localhost:8001/docs (Swagger UI)
- **MongoDB**: mongodb://localhost:27017

## Key Files Reference

### Must-Read Documentation
- `README.md` - Root documentation (1000+ lines)
- `backend/README.md` - Backend documentation (1830+ lines)
- `frontend/README.md` - Frontend documentation (1080+ lines)
- `.kiro/README.md` - Project patterns and guides
- `.kiro/QUICK_START.md` - Onboarding guide
- `IMPROVEMENT_PLAN.md` - Backend refactor roadmap

### Critical Backend Files
- `backend/server.py` - FastAPI app initialization
- `backend/core/auth.py` - JWT authentication
- `backend/core/database.py` - MongoDB lifecycle
- `backend/core/logging.py` - Structured logging
- `backend/core/sentry.py` - Error tracking
- `backend/api/auto_application*.py` - Case management
- `backend/models/enums.py` - Visa types and statuses

### Critical Frontend Files
- `frontend/src/App.tsx` - Root component with routing
- `frontend/src/utils/api.ts` - API client (makeApiCall)
- `frontend/src/pages/SelectForm.tsx` - Visa selection
- `frontend/src/pages/EmbeddedCheckout.tsx` - Stripe payment
- `frontend/src/pages/CaseFinalizer.tsx` - Package generation

### Configuration Files
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node.js dependencies
- `backend/.env.example` - Backend environment template
- `frontend/.env.example` - Frontend environment template
- `frontend/tailwind.config.ts` - Tailwind CSS config
- `frontend/vite.config.ts` - Vite build config

## Common Pitfalls

### Backend Development
- **MongoDB Serialization**: `ObjectId` must be serialized to strings before JSON response
  - Use `serialize_doc()` from `core/serialization.py`
- **Async Operations**: Always use `await` with Motor (async MongoDB driver)
- **JWT Tokens**: Check expiration in authentication middleware
- **Datetime**: Use `datetime.now(timezone.utc)` not deprecated `utcnow()`
- **Database Name**: Collection is `auto_cases` not `cases`
- **Indexes**: Ensure indexes on `user_id` and `case_id` for performance

### Frontend Development
- **API Calls**: ALWAYS use `makeApiCall` from `src/utils/api.ts`
  - Signature: `makeApiCall(endpoint: string, method: string = 'GET', body?: any)`
  - Returns parsed JSON data (NOT Response object)
  - Example: `const data = await makeApiCall('/cases', 'GET');`
- **Controlled Inputs**: Always provide fallback: `value={state || ''}` not `value={state}`
- **Form Validation**: Use React Hook Form + Zod schemas
- **Button Hover**: Use native `<button>` if you need full control over hover styles
  - shadcn Button component overrides custom hover classes
- **Environment Variables**: Use `import.meta.env.VITE_*` prefix
- **Stripe**: Wait for `onReady` callback before enabling submit button

### Agent Development
- Each agent MUST read its `lessons_learned.md` before generating packages
- Always validate REQUIRED_DOCUMENTS and check FORBIDDEN_DOCUMENTS
- Update `lessons_learned.md` after fixing bugs in agent behavior

### Testing
- Test files organized in `tests/` subdirectories (integration, e2e, unit)
- Run tests from repository root: `python3 tests/integration/test_*.py`
- Use pytest for organized test runs: `pytest tests/integration/`
- Test results automatically saved to `tests/results/`

### Deployment
- **Security**: Change `JWT_SECRET`, restrict `CORS_ORIGINS`
- **Logging**: Use `LOG_FORMAT=json` and `LOG_PRETTY=false` in production
- **Sentry**: Configure `SENTRY_DSN` and set appropriate sample rates
- **Stripe**: Use live keys (`sk_live_`, `pk_live_`) only in production

## Code Style

### Python (Backend)
- **Framework**: FastAPI with Pydantic v2 models
- **Type Hints**: Required for all function signatures
- **Async/Await**: Use for all database operations (Motor driver)
- **Formatting**: Black (line length 100)
- **Linting**: Flake8
- **Type Checking**: MyPy
- **Environment**: Load via `python-dotenv`
- **Serialization**: Always serialize MongoDB docs (ObjectId → string)
- **Datetime**: Use `datetime.now(timezone.utc)` not `utcnow()`

### TypeScript/React (Frontend)
- **Components**: Functional components with hooks
- **TypeScript**: Strict mode enabled
- **Validation**: Zod for runtime type validation
- **Forms**: React Hook Form (uncontrolled pattern)
- **Styling**: Tailwind CSS utility classes (no CSS modules)
- **State**: TanStack Query for server state, Context for global state
- **Formatting**: Prettier
- **Linting**: ESLint with TypeScript plugin
- **Imports**: Grouped (external, internal, types)
- **Controlled Inputs**: Always provide fallback: `value={state || ''}`

## Security Notes
- JWT_SECRET must be changed in production
- Stripe is in LIVE MODE - be cautious with webhook handling
- Admin endpoints protected by `@require_admin` or `@require_superadmin` decorators
- Never commit `.env` files (already in .gitignore)
- Password hashing uses bcrypt with proper salt rounds
- API keys for Google Cloud, OpenAI, Emergent, and Resend are sensitive

## Deployment
System runs on Kubernetes with:
- Frontend on port 3000
- Backend on port 8001
- MongoDB on port 27017
- Ingress routing: `/api/*` → Backend, `/*` → Frontend
- Process management via Supervisor
- Production URL: `https://formfiller-26.preview.emergentagent.com`
