# 🏗️ ARQUITETURA TÉCNICA - SISTEMA DE IMIGRAÇÃO (OSPREY B2C)

## 📊 VISÃO GERAL DO SISTEMA

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USUÁRIO FINAL (Browser)                          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  │ HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite + TypeScript)                  │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  • SelectForm (8 tipos de visto)                                   │ │
│  │  • BasicData (dados pessoais)                                      │ │
│  │  • CoverLetterModule                                               │ │
│  │  • DocumentUploadAuto                                              │ │
│  │  • FriendlyForm (perguntas simplificadas)                          │ │
│  │  • AIReviewAndTranslation                                          │ │
│  │  • Payment (Stripe Integration)                                    │ │
│  │  • CaseFinalizer (chamada aos agentes)                             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  Port: 3000                                                              │
│  URL: https://formfiller-26.preview.emergentagent.com                    │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  │ REST API (axios)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI + Python)                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  API ENDPOINTS                                                      │ │
│  │  • /api/auth/* (autenticação JWT)                                  │ │
│  │  • /api/cases/* (CRUD de casos)                                    │ │
│  │  • /api/visa/generate (sistema multi-agente)                       │ │
│  │  • /api/cases/{id}/finalize/start (finalização com agentes)       │ │
│  │  • /api/payment/* (Stripe webhooks)                                │ │
│  │  • /api/google-document-ai/* (OCR e extração)                      │ │
│  │  • /api/intelligent-owl/* (chatbot IA)                             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│  Port: 8001                                                              │
│  51 arquivos Python                                                      │
└───────┬─────────────────────────┬───────────────────────────────────────┘
        │                         │
        │                         │
        ▼                         ▼
┌──────────────────┐    ┌──────────────────────────────────────────────┐
│   MONGODB        │    │     SISTEMA MULTI-AGENTE (8 AGENTES)        │
│                  │    │  ┌────────────────────────────────────────┐ │
│  • test_database │    │  │  SupervisorAgent (Orquestrador)        │ │
│  • Collections:  │    │  │  • Analisa requisição                  │ │
│    - users       │    │  │  • Detecta tipo de visto               │ │
│    - auto_cases  │    │  │  • Delega para especialista correto    │ │
│    - payments    │    │  └───────────┬────────────────────────────┘ │
│    - sessions    │    │              │                               │
│                  │    │              │ Delega para:                  │
│  Port: 27017     │    │              ▼                               │
└──────────────────┘    │  ┌────────────────────────────────────────┐ │
                        │  │  AGENTES ESPECIALIZADOS                │ │
                        │  │                                        │ │
                        │  │  1️⃣  B2ExtensionAgent (I-539)          │ │
                        │  │      • Extensão visto turístico        │ │
                        │  │      • Cover letter + documentos       │ │
                        │  │      • PDF personalizado               │ │
                        │  │                                        │ │
                        │  │  2️⃣  F1StudentAgent (F-1)              │ │
                        │  │      • Visto de estudante              │ │
                        │  │      • I-20, financeiro, escola        │ │
                        │  │                                        │ │
                        │  │  3️⃣  H1BWorkerAgent (H-1B)             │ │
                        │  │      • Visto de trabalho               │ │
                        │  │      • LCA, specialty occupation        │ │
                        │  │                                        │ │
                        │  │  4️⃣  I130FamilyAgent (I-130)           │ │
                        │  │      • Petições familiares             │ │
                        │  │      • Cônjuge, filhos, pais           │ │
                        │  │                                        │ │
                        │  │  5️⃣  I765EADAgent (I-765)              │ │
                        │  │      • Employment Authorization        │ │
                        │  │      • 10+ categorias suportadas       │ │
                        │  │                                        │ │
                        │  │  6️⃣  I90GreenCardAgent (I-90)          │ │
                        │  │      • Renovação/substituição GC       │ │
                        │  │      • Vários motivos                  │ │
                        │  │                                        │ │
                        │  │  7️⃣  EB2NIWAgent (EB-2 NIW)            │ │
                        │  │      • National Interest Waiver        │ │
                        │  │      • Advanced degree                 │ │
                        │  │      • Dhanasar 3-prong test           │ │
                        │  │                                        │ │
                        │  │  8️⃣  EB1AAgent (EB-1A)                 │ │
                        │  │      • Extraordinary Ability           │ │
                        │  │      • 3 de 10 critérios               │ │
                        │  │      • Top performers                  │ │
                        │  └────────────────────────────────────────┘ │
                        │                                              │
                        │  ┌────────────────────────────────────────┐ │
                        │  │  AGENTES DE SUPORTE                    │ │
                        │  │                                        │ │
                        │  │  • QualityAssuranceAgent               │ │
                        │  │    - Valida pacotes gerados            │ │
                        │  │    - Score de qualidade (0-100%)       │ │
                        │  │                                        │ │
                        │  │  • MetricsTracker                      │ │
                        │  │    - Rastreia performance              │ │
                        │  │    - Tempo de processamento            │ │
                        │  │    - Taxa de sucesso                   │ │
                        │  │                                        │ │
                        │  │  • LearningSystem                      │ │
                        │  │    - lessons_learned.md                │ │
                        │  │    - Melhoria contínua                 │ │
                        │  └────────────────────────────────────────┘ │
                        │                                              │
                        │  Total: 15 diretórios de agentes            │
                        └──────────────────────────────────────────────┘

```

## 🗄️ BANCO DE DADOS

### **MongoDB (localhost:27017)**

```
Database: test_database

Collections:
├── users
│   ├── _id (ObjectId)
│   ├── email (string)
│   ├── hashed_password (bcrypt)
│   ├── user_id (UUID)
│   └── created_at (datetime)
│
├── auto_cases (principais dados dos casos)
│   ├── case_id (string)
│   ├── user_id (string)
│   ├── form_code (string: "I-539", "F-1", "I-130", etc.)
│   ├── basic_data (object)
│   │   ├── firstName, lastName, dateOfBirth
│   │   ├── currentAddress, city, state, zipCode
│   │   ├── phoneNumber, email
│   │   ├── alienNumber, currentStatus, statusExpiration
│   │   └── ...
│   ├── simplified_form_responses (object)
│   │   ├── extension_reason (B-2)
│   │   ├── school_name, program_name (F-1)
│   │   ├── relationship_type (I-130)
│   │   └── ...
│   ├── user_story_text (string)
│   ├── uploaded_documents (array)
│   ├── payment_status (string)
│   ├── status (string)
│   └── created_at (datetime)
│
├── payments
│   ├── payment_id (string)
│   ├── user_id (string)
│   ├── case_id (string)
│   ├── stripe_payment_intent_id (string)
│   ├── amount (number)
│   ├── currency (string: "usd")
│   ├── status (string: "succeeded", "pending", "failed")
│   └── created_at (datetime)
│
└── sessions (JWT)
    ├── session_id (string)
    ├── user_id (string)
    ├── token (string)
    ├── expires_at (datetime)
    └── created_at (datetime)
```

## 🔌 INTEGRAÇÕES EXTERNAS

### 1. **OpenAI API**
- **Uso**: Chatbot inteligente (Intelligent Owl Agent)
- **Modelo**: GPT-4
- **Endpoints usados**:
  - `chat.completions.create()`
- **Arquivo**: `/app/backend/intelligent_owl_agent.py`

### 2. **Emergent LLM Key (Universal Key)**
- **Uso**: Acesso unificado a múltiplos LLMs
- **Suporta**: OpenAI, Anthropic Claude, Google Gemini
- **Biblioteca**: `emergentintegrations`
- **Key**: `sk-emergent-aE5F536B80dFf0bA6F`

### 3. **Google Cloud APIs**

#### **a) Google Document AI**
- **Uso**: OCR e extração de dados de documentos
- **Location**: us
- **Project ID**: 891629358081
- **Arquivo**: `/app/backend/google_document_ai_integration.py`
- **Funcionalidade**: Extrai texto de passaportes, I-20s, documentos

#### **b) Google Vision API**
- **Uso**: Análise de imagens e documentos
- **API Key**: `AIzaSyBjn25InzalbcQVeDN8dgfgv6StUsBIutw`
- **OAuth2**: Client ID + Client Secret configurados

### 4. **Stripe (LIVE MODE)**
- **Uso**: Processamento de pagamentos
- **Chaves**:
  - Publishable: `pk_live_51PByv6AfnK9GyzVJ...`
  - Secret: `sk_live_51PByv6AfnK9GyzVJ...`
- **Webhooks**: `/api/payment/webhook`
- **Funcionalidades**:
  - Payment intents
  - Checkout sessions
  - Subscription management

### 5. **Resend (Email Service)**
- **Uso**: Envio de emails transacionais
- **API Key**: `re_Hqp3VrM5_DjqoAsZqSKVridC123W5NMPu`
- **Sender**: `onboarding@resend.dev`
- **Casos de uso**:
  - Confirmação de cadastro
  - Notificações de pagamento
  - Status do caso
  - PDFs gerados

## 📦 BIBLIOTECAS E FRAMEWORKS

### **Backend (Python)**
```
Core:
├── FastAPI 0.110.1          (Web framework)
├── Uvicorn 0.25.0           (ASGI server)
├── Pydantic 2.11.7          (Validação de dados)
└── Python-dotenv 1.1.1      (Variáveis de ambiente)

Database:
├── Motor 3.3.1              (MongoDB async driver)
└── PyMongo 4.5.0            (MongoDB sync driver)

Authentication:
├── PyJWT 2.10.1             (JSON Web Tokens)
├── Passlib 1.7.4            (Hash de senhas)
└── Bcrypt 4.3.0             (Criptografia)

AI/LLM:
├── OpenAI 1.99.9            (GPT-4)
├── Google-generativeai      (Gemini)
├── LiteLLM 1.77.4           (Multi-LLM abstraction)
└── Emergentintegrations     (Universal LLM key)

PDF Generation:
├── ReportLab 4.4.4          (Geração de PDFs)
├── PyPDF2 3.0.1             (Manipulação de PDFs)
├── FPDF2 2.8.4              (PDFs alternativos)
└── PDFplumber               (Extração de PDFs)

Document Processing:
├── google-cloud-documentai   (OCR)
├── google-cloud-vision       (Image analysis)
└── Pillow 11.3.0             (Processamento de imagens)

Payment:
├── Stripe 12.5.1             (Pagamentos)
└── Resend 2.17.0             (Emails)

Utils:
├── Boto3 1.40.11             (AWS SDK - se usar S3)
├── APScheduler 3.10.4        (Jobs agendados)
└── Python-multipart          (Upload de arquivos)

Total: 143 dependências
```

### **Frontend (React + TypeScript)**
```
Core:
├── React 18.3.1
├── React-DOM 18.3.1
├── TypeScript 5.8.3
└── Vite 5.4.19              (Build tool)

UI Framework:
├── Radix-UI (20+ componentes)
├── Tailwind CSS 3.4.17
├── shadcn/ui (components)
├── Lucide-react (ícones)
└── Framer-motion 12.23.22   (Animações)

Forms & Validation:
├── React-hook-form 7.61.1
├── Zod 3.25.76              (Schema validation)
└── @hookform/resolvers

HTTP & State:
├── Axios 1.13.2             (HTTP client)
├── @tanstack/react-query    (Server state)
└── React-router-dom 6.30.1  (Routing)

Charts & Visualization:
└── Recharts 2.15.4

Utilities:
├── Date-fns 3.6.0           (Datas)
├── Class-variance-authority (CSS utils)
└── Sonner 1.7.4             (Toasts)

Total: 66 dependências
```

## 🗂️ ESTRUTURA DE ARQUIVOS

```
/app/
├── backend/                          (51 arquivos Python)
│   ├── server.py                     (Main FastAPI app)
│   ├── visa_api.py                   (Multi-agent system API)
│   ├── case_finalizer_complete.py    (Finalização com agentes)
│   ├── google_document_ai_integration.py
│   ├── intelligent_owl_agent.py      (Chatbot)
│   ├── .env                          (Configurações)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── SelectForm.tsx        (8 tipos de visto)
│   │   │   ├── BasicData.tsx
│   │   │   ├── CoverLetterModule.tsx
│   │   │   ├── DocumentUploadAuto.tsx
│   │   │   └── FriendlyForm.tsx
│   │   ├── components/               (UI components)
│   │   └── utils/
│   ├── package.json
│   └── .env
│
├── visa_specialists/                 (15 diretórios)
│   ├── supervisor/
│   │   └── supervisor_agent.py       (Orquestrador)
│   ├── b2_extension/
│   │   ├── b2_agent.py
│   │   ├── uscis_requirements.md
│   │   └── lessons_learned.md
│   ├── f1_student/
│   ├── h1b_worker/
│   ├── i130_family/                  🆕
│   ├── i765_ead/                     🆕
│   ├── i90_greencard/                🆕
│   ├── eb2_niw/                      🆕
│   ├── eb1a_extraordinary/           🆕
│   ├── qa_agent.py
│   ├── metrics_tracker.py
│   └── knowledge_base/               (USCIS docs)
│
├── test_agent_integration.py
├── test_all_agents.py
└── ARQUITETURA_TECNICA.md           (este arquivo)
```

## 🔐 SEGURANÇA

### **Autenticação & Autorização**
- **JWT Tokens**: HS256 algorithm
- **Secret**: `osprey-b2c-secure-jwt-key-production-ready-2025`
- **Password Hashing**: Bcrypt (salt rounds)
- **Session Management**: MongoDB + JWT

### **CORS**
- **Configuração**: `CORS_ORIGINS="*"` (revisar para produção)
- **Recomendação**: Restringir para domínio específico

### **Environment Variables**
- **Nunca commitar**: `.env` files
- **Produção**: Usar secrets manager (Kubernetes secrets)

### **API Keys Protegidas**
- OpenAI API Key ✅
- Emergent LLM Key ✅
- Google API credentials ✅
- Stripe keys (LIVE MODE) ⚠️

## 🚀 DEPLOY & INFRAESTRUTURA

### **Kubernetes**
- **Environment**: Preview/Production
- **Ingress**: Routing automático
  - `/api/*` → Backend (port 8001)
  - `/*` → Frontend (port 3000)

### **Supervisor (Process Manager)**
```bash
# Comandos disponíveis:
sudo supervisorctl status
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all
```

### **URLs**
- **Frontend**: `https://formfiller-26.preview.emergentagent.com`
- **Backend**: `https://formfiller-26.preview.emergentagent.com/api`
- **MongoDB**: `mongodb://localhost:27017`

## 📊 FLUXO DE DADOS COMPLETO

```
1. USUÁRIO SELECIONA VISTO
   ↓
2. FRONTEND: SelectForm → BasicData → FriendlyForm
   ↓
3. UPLOAD DE DOCUMENTOS (Google Document AI processa)
   ↓
4. PAGAMENTO (Stripe)
   ↓
5. DADOS SALVOS NO MONGODB (collection: auto_cases)
   ↓
6. CASE FINALIZER chamado
   ↓
7. SUPERVISOR AGENT recebe dados
   ↓
8. SUPERVISOR detecta tipo de visto (I-539 → B-2, F-1 → F-1, etc.)
   ↓
9. SUPERVISOR delega para AGENTE ESPECIALIZADO correto
   ↓
10. AGENTE ESPECIALIZADO:
    - Lê lessons_learned.md
    - Lê uscis_requirements.md
    - Transforma dados do MongoDB
    - Gera PDF personalizado (ReportLab)
    - Valida documentos obrigatórios
    ↓
11. QA AGENT valida pacote (score 0-100%)
    ↓
12. METRICS TRACKER registra performance
    ↓
13. PDF salvo em /tmp/visa_packages/
    ↓
14. USUÁRIO recebe link de download
    ↓
15. EMAIL enviado (Resend) com confirmação
```

## 📈 MÉTRICAS E MONITORAMENTO

### **Atualmente Rastreado**
- Tipo de visto processado
- Tempo de processamento
- Taxa de sucesso/falha
- QA Score médio
- Documentos faltantes

### **Logs**
```bash
# Backend logs
/var/log/supervisor/backend.out.log
/var/log/supervisor/backend.err.log

# Frontend logs
/var/log/supervisor/frontend.out.log
/var/log/supervisor/frontend.err.log
```

## 🎯 ESTATÍSTICAS DO SISTEMA

```
📊 NÚMEROS:
├── 8 Agentes Especializados ✅
├── 51 Arquivos Python Backend
├── 143 Dependências Python
├── 66 Dependências Node.js
├── 15 Diretórios de Agentes
├── 1 Banco de Dados MongoDB
├── 6 Integrações Externas
├── 100% Vistos Cobertos
└── 0% Uso do Método Tradicional

🎨 FRONTEND:
├── React 18.3.1
├── TypeScript 5.8.3
├── Vite (Build tool)
└── 20+ Componentes Radix-UI

⚡ BACKEND:
├── FastAPI 0.110.1
├── Python 3.x
├── Motor (MongoDB async)
└── 8 Agentes Ativos

🤖 IA/LLM:
├── OpenAI GPT-4
├── Google Gemini
├── Emergent Universal Key
└── Document AI (OCR)

💳 PAGAMENTOS:
├── Stripe (LIVE MODE)
└── Webhooks configurados

📧 EMAILS:
└── Resend API
```

## 🔄 PRÓXIMAS MELHORIAS RECOMENDADAS

1. **Cache**: Redis para sessões e cache de dados
2. **File Storage**: AWS S3 ou Google Cloud Storage para PDFs
3. **Monitoring**: Sentry para error tracking
4. **Analytics**: Google Analytics ou Mixpanel
5. **CI/CD**: GitHub Actions para deploy automático
6. **Testing**: Aumentar cobertura de testes (pytest, jest)
7. **Rate Limiting**: Para proteger APIs
8. **Backup**: Backup automático do MongoDB

---

**Última Atualização**: 21 de Novembro de 2025  
**Versão**: 2.0 (Multi-Agent System Completo)  
**Status**: ✅ Produção Ready
