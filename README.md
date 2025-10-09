# 🇺🇸 OSPREY Immigration Platform

> **Plataforma completa para automação de processos de imigração americana com IA integrada**

[![CI/CD Pipeline](https://github.com/osprey/osprey-platform/workflows/OSPREY%20CI/CD%20Pipeline/badge.svg)](https://github.com/osprey/osprey-platform/actions)
[![Security Scan](https://github.com/osprey/osprey-platform/workflows/Security%20Scan/badge.svg)](https://github.com/osprey/osprey-platform/actions)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](CHANGELOG.md)

## 🎯 Visão Geral

A **OSPREY Immigration Platform** é uma solução completa que automatiza todo o processo de aplicação para imigração americana, desde o upload de documentos até a montagem final do pacote para submissão ao USCIS.

## ✨ Principais Funcionalidades

### 📄 Sistema de Documentos
- ✅ Upload com validação automática via IA
- ✅ OCR inteligente e extração de dados  
- ✅ Validação específica por tipo de visto
- ✅ Sistema de disclaimer por etapa

### 📋 Formulários USCIS Inteligentes
- ✅ **Formulário Amigável**: Interface em português
- ✅ **Preenchimento Automático**: Baseado em documentos validados
- ✅ **Dra. Ana**: IA especializada em validação
- ✅ **Conversão Automática**: Português → Inglês oficial USCIS

### ✉️ Geração de Cartas
- ✅ **Dr. Paula**: IA especializada em cartas de imigração
- ✅ **Roteiros Personalizados**: Por tipo de visto (H-1B, L1A, O1, F1)
- ✅ **Revisão Automática**: Análise de completude e sugestões

### 📦 Montagem Final
- ✅ **Auditoria Avançada**: Verificação de completude por cenário
- ✅ **Preview Interativo**: Visualização do pacote
- ✅ **Geração de PDFs**: Organização automática

## 🏗️ Arquitetura

```
Frontend (React) ←→ Backend (FastAPI) ←→ Database (MongoDB)
                           ↓
                    AI Services (OpenAI, Emergent LLM)
```

## 🚀 Início Rápido

### Pré-requisitos
- Docker 20.10+ e Docker Compose 2.0+
- Node.js 18+ e Yarn
- Python 3.11+

### Instalação Automática
```bash
git clone https://github.com/osprey/osprey-platform.git
cd osprey-platform
./scripts/setup.sh
./scripts/deploy.sh development
```

### Acesso
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
├── backend/          # FastAPI + IA
├── frontend/         # React + TypeScript
├── docs/            # Documentação
├── k8s/             # Kubernetes
└── scripts/         # Deploy automation
```

### Comandos Úteis
```bash
./scripts/setup.sh              # Setup inicial
./scripts/deploy.sh development # Deploy local
docker-compose logs -f          # Ver logs
```

## 🚀 Produção

### Deploy com Docker
```bash
./scripts/deploy.sh production
```

### Deploy com Kubernetes
```bash
kubectl apply -f k8s/
```

## 📖 Documentação da API

- **Swagger UI**: https://api.osprey.com/docs
- **ReDoc**: https://api.osprey.com/redoc
- **Postman Collection**: [Download](docs/OSPREY_API_Postman_Collection.json)

## 📞 Suporte

- **Email**: support@osprey.com
- **Documentação**: https://docs.osprey.com
- **Issues**: [GitHub Issues](https://github.com/osprey/osprey-platform/issues)

---

**Desenvolvido com ❤️ pela equipe OSPREY**
