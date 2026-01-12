# Osprey B2C - AI-Powered Immigration Case Processing System

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.3.1-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-green.svg)](https://www.mongodb.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.3-blue.svg)](https://www.typescriptlang.org)

Osprey B2C is a multi-agent AI-powered immigration case processing system that generates complete, USCIS-ready visa application packages. Using specialized AI agents, it automates the complex process of preparing immigration documents for 8 different visa types.

## 🎯 What It Does

- **Automates Visa Applications**: End-to-end automation for B-2, F-1, H-1B, I-130, I-765, I-90, EB-2 NIW, and EB-1A visas
- **Multi-Agent AI System**: 8 specialized agents, each expert in a specific visa type
- **Document Generation**: Creates complete PDF packages with cover letters, forms, and supporting documents
- **Quality Assurance**: Built-in QA agent validates every package (0-100% quality score)
- **Document Processing**: OCR and AI-powered document extraction using Google Document AI
- **Payment Integration**: Stripe checkout with multiple payment packages
- **Admin Dashboard**: RBAC-protected admin panel for managing cases and updates

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI (Python 3.13+)
- MongoDB with Motor (async driver)
- OpenAI GPT-4, Google Gemini, Emergent Universal Key
- ReportLab for PDF generation
- Google Cloud Document AI for OCR
- Stripe for payments

**Frontend:**
- React 18.3.1 + TypeScript 5.8.3
- Vite (build tool)
- Radix UI + Tailwind CSS + shadcn/ui
- React Hook Form + Zod validation
- Axios for API communication

**Infrastructure:**
- MongoDB 7.0+
- Kubernetes deployment
- Supervisor for process management

### Multi-Agent System

The system uses a **supervisor-specialist architecture**:

```
                    ┌─────────────────────┐
                    │  SupervisorAgent    │
                    │  (Orchestrator)     │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ B2Extension  │      │  H1BWorker   │      │  F1Student   │
│    Agent     │      │    Agent     │      │    Agent     │
└──────────────┘      └──────────────┘      └──────────────┘
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    QA Agent +       │
                    │  Metrics Tracker    │
                    └─────────────────────┘
```

**8 Specialist Agents:**
1. B-2 Extension (I-539)
2. F-1 Student Visa
3. H-1B Work Visa
4. I-130 Family-Based Immigration
5. I-765 Employment Authorization
6. I-90 Green Card Renewal
7. EB-2 NIW (National Interest Waiver)
8. EB-1A (Extraordinary Ability)

## 📁 Repository Structure

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
├── backend/                 # FastAPI backend (51 Python files)
├── frontend/                # React frontend
├── visa_specialists/        # Multi-agent system (8 specialist agents)
└── archive/                 # Deprecated code
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **Node.js 18+** and npm
- **MongoDB 7.0+**
- **Git**

### 1. Install MongoDB

```bash
# macOS (Homebrew)
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Verify installation
mongosh --eval "db.version()"
```

### 2. Clone and Setup Backend

```bash
# Clone the repository
git clone <repository-url>
cd camada-osprey-core

# Install Python dependencies
cd backend
pip3 install -r requirements.txt

# Create .env file
cp .env.example .env  # Or create manually (see Configuration section)

# Create admin user
python3 create_test_admin.py

# Start backend server
python3 server.py
```

Backend runs on: **http://localhost:8001**

### 3. Setup Frontend

In a new terminal:

```bash
cd frontend

# Install Node.js dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8001" > .env

# Start development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8001/docs (Swagger UI)
- **Admin Panel**: http://localhost:3000/admin/visa-updates

**Default Admin Credentials:**
- Email: `admin@osprey.com`
- Password: `admin123`

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=test_database

# JWT
JWT_SECRET=osprey-b2c-secure-jwt-key-production-ready-2025

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Emergent Universal LLM
EMERGENT_LLM_KEY=sk-emergent-aE5F536B80dFf0bA6F

# Google Cloud (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT_ID=891629358081
GOOGLE_CLOUD_LOCATION=us

# Stripe (use test keys for development)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Resend Email
RESEND_API_KEY=re_...

# CORS
CORS_ORIGINS=*
```

### Frontend Environment Variables

Create `frontend/.env`:

```bash
VITE_API_URL=http://localhost:8001
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 🧪 Running Tests

### All Tests

```bash
# Run all tests with pytest
python3 -m pytest tests/

# Run specific test categories
python3 -m pytest tests/integration/
python3 -m pytest tests/e2e/
python3 -m pytest tests/unit/
```

### Individual Tests

```bash
# Integration tests
python3 tests/integration/test_agent_integration.py
python3 tests/integration/test_all_agents.py

# End-to-end tests
python3 tests/e2e/comprehensive_visa_test.py
python3 tests/e2e/visa_types_e2e_test.py

# Unit tests
python3 tests/unit/test_visa_api_simple.py
python3 tests/unit/friendly_form_test.py
```

Test results are automatically saved to `tests/results/`

## 🏗️ Building for Production

### Backend

```bash
cd backend

# Install production dependencies
pip3 install -r requirements.txt

# Run with production ASGI server
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
```

### Frontend

```bash
cd frontend

# Production build
npm run build

# Preview production build
npm run preview

# Build output in: frontend/dist/
```

## 📦 Root Directory Utilities

The root directory contains essential utilities and data models:

### Data Models
- `b2_extension_data_model.py` - B-2 visa extension data structures
- `f1_student_data_model.py` - F-1 student visa data structures
- `h1b_data_model.py` - H-1B visa data structures

### Core Utilities
- `apply_admin_security.py` - Admin RBAC setup
- `knowledge_base_integration.py` - KB integration module
- `official_forms_repository.py` - USCIS forms repository
- `fill_official_i129.py` - I-129 form auto-fill utility
- `update_all_agents_with_kb.py` - Update all agents with knowledge base
- `extract_and_organize_all.py` - Data organization utility

### Demo & Testing
- `demo_complete_flow.py` - Complete flow demonstration
- `simulated_case_data.py` - Test case data generator

### Data Files
- `knowledge_base_documents.json` - Knowledge base reference data
- `immigration_lessons_h_1b.json` - H-1B lessons learned

## 🛠️ Development Commands

### Backend

```bash
cd backend

# Start development server
python3 server.py

# Start with auto-reload
uvicorn server:app --reload --port 8001

# Create admin user
python3 create_admin_user.py          # Interactive
python3 create_test_admin.py          # Auto-create test admin
python3 create_superadmin.py          # Auto-create superadmin
```

### Frontend

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Build for development
npm run build:dev

# Lint
npm run lint
```

### Database Management

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017/test_database

# View users
mongosh --eval "db.users.find({}, {email:1, role:1}).pretty()" test_database

# View cases
mongosh --eval "db.auto_cases.countDocuments()" test_database
```

### Utility Scripts

```bash
# Package generators (create sample visa packages)
python3 scripts/generators/generate_b2_complete_package.py
python3 scripts/generators/generate_f1_complete_package.py
python3 scripts/generators/generate_final_perfect_package.py

# Debug utilities
python3 scripts/utilities/check_pdf_text.py          # Verify PDF text extraction
python3 scripts/utilities/debug_generated_pdf.py     # Debug PDF generation
python3 scripts/utilities/uscis_form_filling_audit.py  # Audit form filling

# Image generators
python3 scripts/utilities/b2_image_generator.py
python3 scripts/utilities/document_image_generator.py
```

### Using Supervisor (Production)

```bash
# Check status
sudo supervisorctl status

# Restart services
sudo supervisorctl restart all
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# View logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

## 📚 Documentation

### Architecture & Guides
- **Architecture**: `docs/architecture/ARQUITETURA_TECNICA.md` - Complete technical architecture
- **Visual Diagram**: `docs/architecture/DIAGRAMA_VISUAL.txt` - System architecture diagram
- **Quick Commands**: `docs/guides/COMANDOS_RAPIDOS.md` - Common commands reference
- **Setup Guide**: `docs/guides/GUIA_RAPIDO_SETUP.md` - Detailed setup instructions
- **Multi-Agent System**: `visa_specialists/README.md` - Agent architecture explanation
- **WARP Guide**: `WARP.md` - Guide for Warp AI development environment

### Documentation Directories
- **`docs/architecture/`** - Technical architecture and system design
- **`docs/guides/`** - Setup guides and quick reference
- **`docs/reports/`** - Business reports and analysis
- **`docs/features/`** - Feature documentation and status updates
- **`tests/README.md`** - Testing documentation
- **`scripts/README.md`** - Scripts documentation
- **`samples/README.md`** - Sample packages documentation

## 📎 Sample Packages

The `samples/` directory contains example PDF packages generated by the system:

- **`samples/h1b/`** - 13 H-1B visa petition packages
  - Complete USCIS-ready packages
  - Multiple test cases (Fernanda Santos examples)
  - Archived iterations in `h1b/archive/`

- **`samples/i539/`** - 6 I-539 (B-2 extension) packages
  - Complete tourist visa extension packages
  - Example: Maria Santos, Roberto Silva cases
  - 164-page comprehensive package

- **`samples/i765/`** - I-765 EAD packages
  - Employment Authorization Document examples
  - Example: Carlos Eduardo Ferreira case

- **`samples/archive/`** - Old test packages and miscellaneous PDFs

These samples demonstrate the system's output quality and can be used for:
- Quality assurance testing
- Client demonstrations
- Reference for expected output format
- PDF structure validation

## 🔑 Key Features

### Multi-Agent Architecture
- **SupervisorAgent**: Analyzes requests, detects visa types, delegates to specialists
- **Specialist Agents**: Each expert in one visa type with dedicated knowledge base
- **QA Agent**: Validates every generated package with quality scoring
- **Learning System**: Agents read `lessons_learned.md` to avoid past mistakes

### Document Processing
- **Google Document AI**: OCR and data extraction from uploaded documents
- **AI Classification**: Automatic document type detection
- **Validation**: DocumentValidationAgent ensures completeness

### Payment System
- **Stripe Integration**: Full checkout flow with multiple packages
- **Voucher System**: Discount codes and pro-bono vouchers
- **Webhook Handling**: Automatic payment confirmation

### Admin Features
- **RBAC**: Role-based access control (user/admin/superadmin)
- **Visa Updates**: Track and approve USCIS policy changes
- **Knowledge Base**: Manage agent training documents
- **Audit Logs**: Complete admin action tracking

## 🚨 Common Issues

### MongoDB Connection Error

```bash
# Start MongoDB
brew services start mongodb-community@7.0

# Check status
brew services list | grep mongodb
```

### Port Already in Use

```bash
# Kill process on port 8001 (backend)
lsof -ti:8001 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Module Not Found (Python)

```bash
cd backend
pip3 install -r requirements.txt --upgrade
```

### Frontend Build Errors

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📂 Project Organization

This repository follows an enterprise-grade structure:

- **Clean Root Directory**: Only essential utilities and config files in root
- **Organized Documentation**: All docs in `docs/` with subdirectories by type
- **Structured Tests**: Tests organized by type (integration, e2e, unit) with results
- **Centralized Scripts**: All generators and utilities in `scripts/`
- **Sample Archives**: Generated PDFs organized by visa type in `samples/`
- **Comprehensive READMEs**: Each directory has a README explaining its contents

For details on the directory structure and file organization, see the "Repository Structure" section above.

## 🤝 Contributing

1. Read `WARP.md` for development guidelines
2. Follow the established code style (see `WARP.md` Code Style section)
3. Write tests for new features
4. Update documentation as needed
5. Test with all 8 visa types before committing
6. Keep the organized directory structure - don't add files to root without reason

## 📝 License

[Add your license information here]

## 🔗 Links

- **Production**: https://formfiller-26.preview.emergentagent.com
- **API Docs**: http://localhost:8001/docs
- **Admin Panel**: http://localhost:3000/admin

## 📞 Support

For support and questions, check the documentation in `docs/` directory or review the quick reference guide at `docs/guides/COMANDOS_RAPIDOS.md`.

---

**Built with ❤️ using FastAPI, React, and AI**
