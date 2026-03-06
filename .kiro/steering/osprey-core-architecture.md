---
inclusion: always
---

# Osprey Platform - Core Architecture

## Project Overview
Osprey is a production-ready, enterprise-grade B2C immigration platform that automates US visa application processing using multi-agent AI orchestration.

**Tech Stack:**
- Backend: Python 3.11+ | FastAPI 0.128.0 | MongoDB 6.0+ (Motor async)
- Frontend: TypeScript 5.8+ | React 18.3 | Vite 5.4 | Tailwind CSS 3.4
- AI: OpenAI GPT-4o | Google Gemini 1.5 Pro | Google Document AI

**Project Stats:**
- ~50,000+ lines of code (Backend: ~30K, Frontend: ~20K)
- 7,000+ lines of documentation
- Production-ready with active development

## Repository Structure
```
camada-osprey-core/
├── backend/                    # FastAPI async backend
│   ├── server.py              # Main app (DO NOT add routes here)
│   ├── core/                  # Infrastructure (auth, db, logging, sentry)
│   ├── api/                   # API routers (23 modules, domain-organized)
│   ├── models/                # Pydantic schemas
│   ├── services/              # Business logic layer
│   └── requirements.txt       # Python dependencies (462 lines)
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── pages/            # 25+ page components
│   │   ├── components/       # 35+ reusable UI components
│   │   ├── lib/              # API client, utilities
│   │   └── hooks/            # Custom React hooks
│   └── package.json          # npm dependencies
│
└── README.md                  # Root documentation (1014 lines + Mermaid diagrams)
```

## Key Documentation Files
- **README.md** - System architecture + Mermaid diagrams
- **backend/README.md** - Backend deep dive (1830 lines)
- **frontend/README.md** - Frontend deep dive (1080 lines)
- **SECURITY_AUDIT_2026-01-13.md** - Latest security audit
- **AI_AGENT_GUIDE.md** - Universal AI agent guide

## API Documentation
Interactive API docs available at: http://localhost:8001/docs
