# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Osprey B2C is a multi-agent AI-powered immigration case processing system. It uses specialized AI agents to generate complete visa application packages for 8 different visa types (B-2, F-1, H-1B, I-130, I-765, I-90, EB-2 NIW, EB-1A).

**Stack:**
- Backend: FastAPI (Python 3.x) + MongoDB
- Frontend: React 18.3.1 + TypeScript 5.8.3 + Vite
- AI/LLM: OpenAI GPT-4, Google Gemini, Emergent Universal Key
- Infrastructure: Kubernetes, Supervisor (process management)

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
# Start backend server
cd backend
python3 server.py

# Install dependencies
pip install -r requirements.txt

# Run backend with uvicorn directly
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend (React + Vite)
```bash
# Start development server
cd frontend
npm run dev

# Build for production
npm run build

# Build for development
npm run build:dev

# Lint
npm run lint

# Install dependencies
npm install
```

### Testing
```bash
# Integration tests
python3 tests/integration/test_agent_integration.py
python3 tests/integration/test_all_agents.py

# End-to-end tests
python3 tests/e2e/comprehensive_visa_test.py
python3 tests/e2e/visa_types_e2e_test.py
python3 tests/e2e/friendly_forms_e2e_test.py

# Unit tests
python3 tests/unit/test_visa_api_simple.py
python3 tests/unit/friendly_form_test.py

# Run all tests in a category
python3 -m pytest tests/integration/
python3 -m pytest tests/e2e/
python3 -m pytest tests/unit/
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

### Multi-Agent System
The core innovation is a supervisor-specialist architecture in `visa_specialists/`:

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
`backend/` contains 51 Python files:

**Core Files:**
- `server.py` - Main FastAPI application (8000+ lines)
- `visa_api.py` - Multi-agent system API
- `case_finalizer_complete.py` - Final case processing with agents

**Integration Files:**
- `google_document_ai_integration.py` - OCR and document extraction
- `intelligent_owl_agent.py` - Chatbot assistant
- `stripe_integration.py` - Payment processing
- `payment_packages.py` - Visa package pricing
- `voucher_system.py` - Discount vouchers

**Specialized Systems:**
- `specialized_agents.py` - Document validation, form validation, eligibility analysis
- `immigration_legal_rules.py` - Legal compliance checking
- `professional_qa_agent.py` - Quality assurance system
- `document_classifier.py` - AI-powered document classification
- `uscis_form_filler.py` - Automated form filling

**Admin & Security:**
- `admin_security.py` - Role-based access control (admin/superadmin)
- `admin_products.py` - Product management
- `visa_auto_updater.py` - Automatic USCIS policy updates

### Frontend Structure
`frontend/src/` React application:

**Pages** (`pages/`):
- `SelectForm.tsx` - Visa type selection (8 types)
- `BasicData.tsx` - Personal information collection
- `FriendlyForm.tsx` - Simplified question interface
- `DocumentUploadAuto.tsx` - Document upload with AI extraction
- `CoverLetterModule.tsx` - AI-generated cover letters
- `CaseFinalizer.tsx` - Final package generation
- `AIReviewAndTranslation.tsx` - AI review and translation
- `Payment.tsx` - Stripe checkout integration

**Components** (`components/`):
- Radix UI components (20+ components)
- Tailwind CSS + shadcn/ui
- Form validation with React Hook Form + Zod

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
Backend runs on port 8001, key endpoints:

**Authentication:**
- `POST /api/auth/login` - JWT authentication
- `POST /api/auth/register` - User registration

**Cases:**
- `GET /api/cases` - List user cases
- `POST /api/cases` - Create new case
- `GET /api/cases/{id}` - Get case details
- `PUT /api/cases/{id}` - Update case
- `POST /api/cases/{id}/finalize/start` - Generate package with agents

**Visa Generation:**
- `POST /api/visa/generate` - Multi-agent visa package generation

**Documents:**
- `POST /api/google-document-ai/*` - OCR and extraction

**Admin:**
- `GET /api/admin/visa-updates/pending` - Pending policy updates
- Requires JWT token with admin/superadmin role

**Payment:**
- `POST /api/payment/webhook` - Stripe webhooks

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
MONGODB_DB=test_database

# JWT
JWT_SECRET=osprey-b2c-secure-jwt-key-production-ready-2025

# OpenAI
OPENAI_API_KEY=<key>

# Emergent Universal LLM
EMERGENT_LLM_KEY=sk-emergent-aE5F536B80dFf0bA6F

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=<path-to-service-account-json>
GOOGLE_CLOUD_PROJECT_ID=891629358081
GOOGLE_CLOUD_LOCATION=us

# Stripe (LIVE MODE)
STRIPE_SECRET_KEY=sk_live_51PByv6AfnK9GyzVJ...
STRIPE_PUBLISHABLE_KEY=pk_live_51PByv6AfnK9GyzVJ...
STRIPE_WEBHOOK_SECRET=<webhook-secret>

# Resend Email
RESEND_API_KEY=re_Hqp3VrM5_DjqoAsZqSKVridC123W5NMPu

# CORS
CORS_ORIGINS=*
```

### Frontend (.env in frontend/)
```bash
VITE_API_URL=http://localhost:8001
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_51PByv6AfnK9GyzVJ...
```

## Development URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Backend Docs**: http://localhost:8001/docs (Swagger UI)
- **MongoDB**: mongodb://localhost:27017

## Key Files Reference

### Must-Read Documentation
- `docs/architecture/ARQUITETURA_TECNICA.md` - Complete technical architecture
- `docs/guides/COMANDOS_RAPIDOS.md` - Quick command reference
- `docs/guides/GUIA_RAPIDO_SETUP.md` - Setup guide
- `visa_specialists/README.md` - Multi-agent architecture explanation

### Critical Backend Files
- `backend/server.py` - Main app entry point (13000+ lines)
- `backend/case_finalizer_complete.py` - Package generation orchestrator
- `visa_specialists/supervisor/supervisor_agent.py` - Agent coordinator
- `visa_specialists/base_agent.py` - Base class for all agents

### Configuration Files
- `backend/requirements.txt` - Python dependencies (150 lines)
- `frontend/package.json` - Node.js dependencies
- `backend/visa_directive_guides_informative.yaml` - Visa specifications

## Common Pitfalls

### Agent Development
- Each agent MUST read its `lessons_learned.md` before generating packages
- Always validate REQUIRED_DOCUMENTS and check FORBIDDEN_DOCUMENTS
- Update `lessons_learned.md` after fixing bugs in agent behavior

### API Development
- MongoDB documents contain `ObjectId` which must be serialized to strings before JSON response
- Use `serialize_doc()` helper function in `server.py`
- JWT tokens expire; check expiration in authentication middleware

### Frontend Development
- Form validation uses Zod schemas with React Hook Form
- Axios base URL configured via VITE_API_URL environment variable
- Document uploads must include proper MIME type detection

### Database
- Collection name is `auto_cases` not `cases`
- Always use async MongoDB operations with Motor driver
- Index on `user_id` and `case_id` for performance

### Testing
- Test files are organized in `tests/` subdirectories
- MongoDB test database is `test_database`
- Run tests with Python from root directory: `python3 tests/integration/test_*.py`
- Test results are automatically saved to `tests/results/`

## Code Style

### Python
- FastAPI with Pydantic v2 models
- Type hints required for function signatures
- Environment variables loaded via `python-dotenv`
- Async/await for database operations with Motor
- Document serialization for ObjectId → string conversion

### TypeScript/React
- Functional components with hooks
- TypeScript strict mode enabled
- Zod for runtime type validation
- React Hook Form for form management
- Tailwind CSS for styling (no CSS modules)

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
