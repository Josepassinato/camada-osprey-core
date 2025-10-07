# 📐 DECISÕES DE ARQUITETURA - SISTEMA DE IMIGRAÇÃO OSPREY

**Data de Criação:** 2025-01-07  
**Última Atualização:** 2025-01-07  
**Versão:** 1.0

---

## 🎯 PROPÓSITO DESTE DOCUMENTO

Este documento registra **TODAS** as decisões arquiteturais importantes para:
- ✅ Evitar reimplementação de funcionalidades existentes
- ✅ Manter consistência entre sessões de desenvolvimento
- ✅ Servir como fonte única de verdade
- ✅ Evitar perda de contexto

**⚠️ REGRA CRÍTICA:** Antes de implementar qualquer funcionalidade, SEMPRE verificar este documento!

---

## 🏗️ COMPONENTES PRINCIPAIS EXISTENTES

### **1. DOCUMENT CLASSIFIER** ✅ **JÁ IMPLEMENTADO**
**Arquivo:** `/app/backend/document_classifier.py`  
**Status:** ✅ Completamente funcional e treinado  
**Data Implementação:** Há 8 horas (sessão anterior)

**O que faz:**
- Classifica automaticamente 13+ tipos de documentos
- Usa 50+ padrões regex por tipo
- Sistema de scoring ponderado
- Suporta análise de filename
- Retorna confiança (0.0-1.0)

**Tipos Suportados:**
```
1. PASSPORT_ID_PAGE
2. BIRTH_CERTIFICATE
3. MARRIAGE_CERT
4. DEGREE_CERTIFICATE
5. EMPLOYMENT_OFFER_LETTER
6. I797_NOTICE
7. I94_RECORD
8. PAY_STUB
9. BANK_STATEMENT
10. TAX_RETURN
11. DRIVER_LICENSE
12. TRANSCRIPT
13. POLICE_CLEARANCE
```

**Como Usar:**
```python
from document_classifier import document_classifier

result = document_classifier.classify_document(
    text_content=extracted_text,
    filename=filename,
    file_size=file_size
)

# Retorna:
{
    'document_type': 'PASSPORT_ID_PAGE',
    'confidence': 0.92,
    'status': 'success',
    'candidates': [...]
}
```

**❌ NUNCA REIMPLEMENTAR ISSO! Use sempre `document_classifier.classify_document()`**

---

### **2. GOOGLE CLOUD VISION OCR** ✅ **JÁ INTEGRADO**
**Arquivo:** `/app/backend/pipeline/google_vision_ocr.py`  
**Status:** ✅ Funcional com API key configurada  
**API Key:** Configurada em `/app/backend/.env` como `GOOGLE_API_KEY`

**O que faz:**
- Extrai texto de imagens de documentos
- Suporta múltiplos idiomas (pt+en)
- Retorna confiança do OCR
- Modo 'document' para alta precisão

**Como Usar:**
```python
from pipeline.real_ocr_engine import real_ocr_engine

ocr_result = await real_ocr_engine.extract_text_from_image(
    image_data=file_content,
    mode='document',
    language='pt+en'
)

# ocr_result.text → texto extraído
# ocr_result.confidence → confiança (0-100)
# ocr_result.engine → 'google_vision'
```

**❌ NUNCA usar dados simulados/fake quando há OCR real disponível!**

---

### **3. DR. MIGUEL - VALIDADOR DE DOCUMENTOS** ✅ **INTEGRADO**
**Arquivo:** `/app/backend/specialized_agents.py`  
**Classe:** `DrMiguelValidator`  
**Status:** ✅ Usa OCR real + Document Classifier

**Fluxo Correto:**
```
1. Recebe imagem/PDF
2. Extrai texto com Google Vision OCR
3. Classifica tipo com DocumentClassifier
4. Compara tipo detectado vs esperado
5. Se diferente → REJEITA com mensagem clara
6. Se igual → Continua validação específica
```

**Métodos Principais:**
- `validate_document_enhanced()` - Validação completa
- `_detect_document_type_from_text()` - Usa DocumentClassifier
- `_translate_doc_type()` - Tradução PT/EN

**❌ NUNCA usar simulação em validate_document_enhanced!**

---

### **4. SPECIALIZED VALIDATORS** ✅ **JÁ IMPLEMENTADOS**
**Arquivo:** `/app/backend/specialized_document_validators.py`

**Validadores Específicos:**
- `PassportValidator` - Validação completa de passaportes
- `I797Validator` - Formulários I-797 do USCIS
- `TranslationCertificateValidator` - Certificados de tradução

**Pipeline Validators:**
- `/app/backend/pipeline/birth_certificate_validator.py`
- `/app/backend/pipeline/i765_validator.py`
- `/app/backend/pipeline/driver_license_validator.py`
- `/app/backend/pipeline/marriage_certificate_validator.py`
- `/app/backend/pipeline/tax_documents_validator.py`
- `/app/backend/pipeline/medical_records_validator.py`
- `/app/backend/pipeline/utility_bills_validator.py`

**❌ NUNCA reimplementar validadores! Use os existentes.**

---

### **5. FLUXOS DE APLICAÇÃO** ✅ **DOIS FLUXOS DIFERENTES**

**IMPORTANTE:** Sistema tem fluxos diferentes para diferentes tipos de visto!

**Fluxo A - Vistos de Trabalho (H-1B, L-1, O-1, F-1):**
```
1. basic-data
2. friendly-form (questionário amigável)
3. ai-review
4. uscis-form
5. documents (upload)
6. story (narrativa)
7. review
8. payment
```

**Fluxo B - Casos Humanitários (I-589 Asilo, I-130 Família):**
```
1. basic-data
2. cover-letter (carta PRIMEIRO) ⭐
3. documents (upload)
4. friendly-form
5. ai-review
6. review
7. payment
```

**Por quê?** Casos humanitários precisam da narrativa pessoal ANTES.

**❌ NUNCA assumir que todos os vistos seguem o mesmo fluxo!**

---

### **6. FORMULÁRIOS USCIS** ✅ **NUNCA SÃO ENVIADOS PELO USUÁRIO**

**Decisão Importante:** Formulários USCIS são GERADOS pela IA, não enviados!

**Tipos Removidos do Upload:**
- ❌ form_i130
- ❌ form_ds160
- ❌ form_i129
- ❌ form_i485

**Tipo Especial para IA:**
- ✅ `uscis_form` - Apenas para documentos gerados pela IA

**Fluxo Correto:**
```
1. Usuário preenche questionário amigável (PT)
2. Dr. Fernando valida e traduz (EN)
3. IA gera formulário USCIS oficial
4. Usuário revisa e autoriza
5. Sistema SALVA AUTOMATICAMENTE (tipo: uscis_form)
```

**Endpoint:** `POST /api/auto-application/case/{case_id}/authorize-uscis-form`

**❌ NUNCA adicionar formulários USCIS na lista de upload manual!**

---

### **7. SISTEMA DE SALVAMENTO** ✅ **FUNCIONANDO**

**Auto-Save:** A cada 30 segundos  
**Endpoint:** `PATCH /api/auto-application/case/{case_id}`

**Salvar e Continuar Depois:**
- Modal: `/app/frontend/src/components/SaveAndContinueModal.tsx`
- Endpoint signup: `/api/auth/signup` (NÃO `/api/auth/register`!)
- Endpoint associação: `/api/auto-application/case/{case_id}/associate-user`

**Campos do Signup:**
```json
{
  "first_name": string,
  "last_name": string,
  "email": string,
  "password": string,
  "phone": string (opcional)
}
```

**❌ NUNCA usar `/api/auth/register` - endpoint correto é `/api/auth/signup`!**

---

### **8. ANALYTICS SYSTEM** ✅ **JÁ IMPLEMENTADO**

**Diretório:** `/app/backend/analytics/`

**Componentes:**
- `models.py` - Modelos de dados
- `collector.py` - Coleta de métricas
- `analyzer.py` - Processamento
- `endpoints.py` - API endpoints

**Frontend Dashboards:**
- `/app/frontend/src/pages/AdvancedAnalytics.tsx`
- `/app/frontend/src/pages/analytics/DocumentProcessingDashboard.tsx`
- `/app/frontend/src/pages/analytics/UserJourneyDashboard.tsx`
- `/app/frontend/src/pages/analytics/AIPerformanceDashboard.tsx`
- `/app/frontend/src/pages/analytics/BusinessIntelligenceDashboard.tsx`
- `/app/frontend/src/pages/analytics/SystemHealthDashboard.tsx`

**❌ NUNCA reimplementar analytics! Sistema completo já existe.**

---

### **9. CASE FINALIZER** ✅ **JÁ IMPLEMENTADO**

**Arquivo:** `/app/backend/case_finalizer_complete.py`

**O que faz:**
- Consolida todos os documentos em Master Packet
- Gera checklist de verificação
- Cria instruções de envio
- Fornece informações de taxas
- Endereços USCIS específicos por tipo de visto

**Scenarios Suportados:**
- H-1B (basic, extension, change of status)
- F-1 (initial, reinstatement)
- I-485 (employment, family)
- I-130 (spouse)
- I-589 (asylum)
- N-400 (naturalization)

**Endpoints:**
- `POST /api/cases/{case_id}/finalize/start`
- `GET /api/cases/finalize/{job_id}/status`
- `GET /api/cases/{case_id}/finalize/capabilities`

**❌ NUNCA reimplementar finalização! Sistema completo existe.**

---

## 🚫 ERROS COMUNS A EVITAR

### **1. Reimplementar Funcionalidades Existentes**
❌ **ERRADO:** Criar novo classificador de documentos  
✅ **CERTO:** Usar `document_classifier.classify_document()`

### **2. Usar Dados Simulados quando OCR Existe**
❌ **ERRADO:** Retornar dados fake de passaporte  
✅ **CERTO:** Usar `real_ocr_engine.extract_text_from_image()`

### **3. Assumir Fluxo Único**
❌ **ERRADO:** Todos os vistos seguem mesmo fluxo  
✅ **CERTO:** Verificar tipo de visto para determinar fluxo

### **4. Adicionar Formulários USCIS no Upload**
❌ **ERRADO:** Usuário pode enviar I-129, I-130  
✅ **CERTO:** Formulários são gerados pela IA apenas

### **5. Usar Endpoint Errado**
❌ **ERRADO:** `/api/auth/register`  
✅ **CERTO:** `/api/auth/signup`

### **6. Modificar URLs/Ports no .env**
❌ **ERRADO:** Alterar `REACT_APP_BACKEND_URL` ou `MONGO_URL`  
✅ **CERTO:** NUNCA modificar essas variáveis

---

## ✅ CHECKLIST ANTES DE IMPLEMENTAR

Antes de implementar QUALQUER funcionalidade:

- [ ] Verificar se já existe em `/app/backend/`
- [ ] Consultar este arquivo (ARCHITECTURE_DECISIONS.md)
- [ ] Buscar no código por palavras-chave relacionadas
- [ ] Verificar `/app/backend/server.py` para endpoints
- [ ] Checar `/app/frontend/src/` para componentes
- [ ] Ler `/app/test_result.md` para testes anteriores
- [ ] Verificar git log para implementações recentes

---

## 📝 REGISTRO DE MUDANÇAS

### 2025-01-07
- ✅ Criado arquivo ARCHITECTURE_DECISIONS.md
- ✅ Documentado Document Classifier existente
- ✅ Documentado Google Cloud Vision OCR
- ✅ Documentado Dr. Miguel com integração correta
- ✅ Documentado dois fluxos diferentes (trabalho vs humanitário)
- ✅ Documentado regra de formulários USCIS
- ✅ Documentado sistema de salvamento
- ✅ Documentado analytics system
- ✅ Documentado case finalizer

---

## 🔄 COMO MANTER ESTE DOCUMENTO

**Quando adicionar nova funcionalidade:**
1. Documentar aqui IMEDIATAMENTE
2. Incluir: arquivo, status, o que faz, como usar
3. Adicionar na seção "Erros Comuns a Evitar"
4. Atualizar data em "Registro de Mudanças"

**Quando modificar funcionalidade existente:**
1. Atualizar seção correspondente
2. Marcar com data da modificação
3. Explicar por que foi modificada

**Este documento é a FONTE ÚNICA DE VERDADE!**

---

## 📞 DÚVIDAS?

Se não encontrar informação aqui:
1. Buscar em `/app/backend/` e `/app/frontend/src/`
2. Verificar `/app/test_result.md`
3. Consultar git log
4. **Perguntar ao usuário antes de reimplementar!**

---

**Última atualização:** 2025-01-07 23:00 UTC  
**Próxima revisão:** A cada nova funcionalidade importante
