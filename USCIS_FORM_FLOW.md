# 📋 Fluxo de Formulários USCIS - Documentação

## 🎯 Princípio Fundamental

**FORMULÁRIOS USCIS NUNCA SÃO ENVIADOS MANUALMENTE PELO USUÁRIO**

Os formulários oficiais do USCIS (I-129, I-130, I-485, I-765, I-131, etc.) são:
- ✅ Gerados automaticamente pela IA
- ✅ Preenchidos com base no questionário amigável
- ✅ Traduzidos do português para inglês
- ✅ Salvos automaticamente após autorização do usuário

---

## 📊 Fluxo Completo

### 1️⃣ **Questionário Amigável (Português)**
**Arquivo:** `/frontend/src/pages/USCISFormFilling.tsx`
**Endpoint:** `POST /api/auto-application/case/{case_id}/uscis-form`

```
Usuário preenche em português:
- Nome completo
- Data de nascimento
- Informações profissionais
- Informações familiares
- etc.
```

### 2️⃣ **Validação pela IA (Dr. Fernando)**
**Arquivo:** `/backend/specialized_agents.py`
**Endpoint:** `POST /api/specialized-agents/uscis-form-translation`

```
Sistema valida:
✅ Campos obrigatórios preenchidos
✅ Formatos corretos (datas, telefones, etc.)
✅ Consistência entre seções
❌ Retorna erros se houver problemas
```

### 3️⃣ **Tradução para Inglês**
**Agente:** Dr. Fernando - USCIS Form Translator

```
IA traduz:
- Português → Inglês
- Mantém terminologia técnica oficial
- Preserva formatação USCIS
- NÃO inventa informações
```

### 4️⃣ **Geração do Formulário USCIS Oficial**
**Endpoint:** `POST /api/auto-application/generate-forms`

```
Sistema gera:
- Formulário I-129 (H-1B, L-1, O-1)
- Formulário I-130 (Family-based)
- Formulário I-485 (Adjustment of Status)
- etc.
```

### 5️⃣ **Revisão e Autorização pelo Usuário**
**Arquivo:** `/frontend/src/pages/USCISFormFilling.tsx` (Review Mode)

```
Usuário:
1. Revisa formulário gerado
2. Verifica todas as informações
3. Clica "Autorizar Formulário"
```

### 6️⃣ **Salvamento Automático**
**Endpoint:** `POST /api/auto-application/case/{case_id}/authorize-uscis-form`
**Código:** Linhas 5277-5350 em `/backend/server.py`

```python
# Sistema salva automaticamente:
uscis_document = {
    "id": f"uscis_form_{case_id}",
    "document_type": "uscis_form",
    "name": f"Formulário USCIS {form_code}",
    "generated_by_ai": True,
    "authorized_by_user": True,
    "authorization_timestamp": datetime.utcnow(),
    "status": "ready_for_submission"
}
```

### 7️⃣ **Disponível no Dashboard**
**Arquivo:** `/frontend/src/pages/Dashboard.tsx`

```
Usuário vê:
- ✅ Formulário USCIS (Gerado por IA)
- ✅ Status: Ready for Submission
- ✅ Data de autorização
- ✅ Download disponível
```

---

## 🚫 O QUE FOI REMOVIDO

### Backend (`/backend/server.py`)
**Antes:**
```python
class DocumentType(str, Enum):
    ...
    form_i130 = "form_i130"  # ❌ REMOVIDO
    form_ds160 = "form_ds160"  # ❌ REMOVIDO
```

**Depois:**
```python
class DocumentType(str, Enum):
    ...
    uscis_form = "uscis_form"  # ✅ Apenas para IA
    # Note: USCIS forms are NOT uploaded manually
```

### Frontend Upload (`/frontend/src/pages/DocumentUpload.tsx`)
**Antes:**
```javascript
{ value: "form_i130", label: "Formulário I-130" },  // ❌ REMOVIDO
{ value: "form_ds160", label: "Formulário DS-160" },  // ❌ REMOVIDO
```

**Depois:**
```javascript
// Formulários USCIS não aparecem mais na lista de upload
```

---

## ✅ Documentos que DEVEM ser enviados manualmente

```
✅ Passaporte
✅ Certidão de Nascimento
✅ Certidão de Casamento
✅ Diploma de Educação
✅ Histórico Escolar
✅ Carta de Trabalho
✅ Extrato Bancário
✅ Declaração de IR
✅ Exame Médico
✅ Antecedentes Criminais
✅ Documentos do Sponsor
✅ Fotos

❌ Formulários USCIS (gerados pela IA)
```

---

## 🔒 Benefícios desta Abordagem

### 1. **Sem Erros de Digitação**
- IA preenche automaticamente
- Campos sempre consistentes
- Formatação oficial do USCIS

### 2. **Tradução Precisa**
- Terminologia técnica correta
- Sem ambiguidades
- Padronização oficial

### 3. **Rastreabilidade**
```
- Quem gerou: IA
- Quando: timestamp
- Autorizado por: user_id
- Versão: caso_id
```

### 4. **Auditoria Completa**
```json
{
  "generated_by_ai": true,
  "authorized_by_user": true,
  "authorization_timestamp": "2025-01-06T23:45:00Z",
  "form_data": { ... },
  "case_id": "OSP-ABC123"
}
```

---

## 🧪 Como Testar

### 1. Criar um caso H-1B
```bash
POST /api/auto-application/start
{
  "form_code": "H-1B"
}
```

### 2. Preencher questionário amigável
```bash
POST /api/auto-application/case/{case_id}/uscis-form
{
  "uscis_form_data": { ... }
}
```

### 3. Autorizar formulário gerado
```bash
POST /api/auto-application/case/{case_id}/authorize-uscis-form
{
  "form_reviewed": true,
  "form_authorized": true
}
```

### 4. Verificar salvamento automático
```bash
GET /api/auto-application/case/{case_id}

# Response deve incluir:
{
  "uscis_form_authorized": true,
  "documents": [
    {
      "document_type": "uscis_form",
      "generated_by_ai": true,
      "authorized_by_user": true
    }
  ]
}
```

---

## 📝 Notas Importantes

1. **Não há upload manual de formulários USCIS**
   - Opções removidas da UI
   - Tipos removidos do backend
   - Apenas IA pode gerar

2. **Salvamento é sempre automático**
   - Após autorização do usuário
   - Não precisa fazer upload
   - Já está na pasta do caso

3. **Formulário sempre está atualizado**
   - Baseado nos dados mais recentes
   - Regenerado se necessário
   - Versionamento automático

---

**Última atualização:** 2025-01-06
**Versão:** 1.0
