# Prompt Migration Patches

**Generated**: 2026-01-14 23:46:32 UTC
**Total Patches**: 22

This document contains code migration patches for all prompts migrated to Portkey.

---

## Patch 1: unknown_function Prompt

**Prompt ID**: `PROMPT_001`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `server.py:2048`

### Before

```python
# server.py:2048

messages = [
    {
        "role": "system",
        "content": "Você é um assistente de análise de documentos para auto-aplicação em imigração. Forneça análises úte..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# server.py:2048
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 2: unknown_function Prompt

**Prompt ID**: `PROMPT_002`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `server.py:2114`

### Before

```python
# server.py:2114

messages = [
    {
        "role": "system",
        "content": "Você é um tradutor profissional especializado em documentos de imigração. Traduza o texto a seguir p..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# server.py:2114
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={"target_lang_name": target_lang_name}
)

```

---

## Patch 3: unknown_function Prompt

**Prompt ID**: `PROMPT_003`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `server.py:2180`

### Before

```python
# server.py:2180

messages = [
    {
        "role": "system",
        "content": "Você é um assistente para auto-aplicação em imigração. Forneça recomendações precisas mas sempre men..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# server.py:2180
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 4: unknown_function Prompt

**Prompt ID**: `PROMPT_004`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `voice/agent.py:514`

### Before

```python
# voice/agent.py:514

messages = [
    {
        "role": "system",
        "content": "Você é um assistente de conformidade que ajuda com preenchimento de formulários, mas nunca dá aconse..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# voice/agent.py:514
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 5: unknown_function Prompt

**Prompt ID**: `PROMPT_005`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `api/auto_application_ai.py:188`

### Before

```python
# api/auto_application_ai.py:188

messages = [
    {
        "role": "system",
        "content": "Você é um especialista em formulários do USCIS. Converta respostas em português para formato oficial..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# api/auto_application_ai.py:188
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 6: unknown_function Prompt

**Prompt ID**: `PROMPT_006`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `case/completeness_analyzer.py:204`

### Before

```python
# case/completeness_analyzer.py:204

messages = [
    {
        "role": "system",
        "content": "Você é um assistente educativo sobre requisitos do USCIS. Forneça feedback baseado em informações pú..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# case/completeness_analyzer.py:204
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 7: unknown_function Prompt

**Prompt ID**: `PROMPT_007`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `documents/recognition.py:164`

### Before

```python
# documents/recognition.py:164

messages = [
    {
        "role": "system",
        "content": "You are a document analysis expert. Analyze documents and return structured JSON...."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# documents/recognition.py:164
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 8: unknown_function Prompt

**Prompt ID**: `PROMPT_008`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `documents/recognition.py:283`

### Before

```python
# documents/recognition.py:283

messages = [
    {
        "role": "system",
        "content": "You are a document data extraction expert. Extract structured data from documents...."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# documents/recognition.py:283
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 9: unknown_function Prompt

**Prompt ID**: `PROMPT_009`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `documents/recognition.py:461`

### Before

```python
# documents/recognition.py:461

messages = [
    {
        "role": "system",
        "content": "You are a USCIS document relevance expert. Assess document relevance for visa applications...."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# documents/recognition.py:461
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 10: unknown_function Prompt

**Prompt ID**: `PROMPT_010`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `services/education.py:65`

### Before

```python
# services/education.py:65

messages = [
    {
        "role": "system",
        "content": "Você é um especialista em entrevistas de imigração. Responda APENAS em JSON válido...."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# services/education.py:65
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 11: unknown_function Prompt

**Prompt ID**: `PROMPT_011`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `services/education.py:128`

### Before

```python
# services/education.py:128

messages = [
    {
        "role": "system",
        "content": "Você é um especialista em avaliação de entrevistas de imigração. Responda APENAS em JSON...."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# services/education.py:128
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 12: unknown_function Prompt

**Prompt ID**: `PROMPT_012`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `services/education.py:214`

### Before

```python
# services/education.py:214

messages = [
    {
        "role": "system",
        "content": "Você é um consultor educativo de imigração. Forneça dicas práticas em português. Sempre mencione que..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# services/education.py:214
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 13: unknown_function Prompt

**Prompt ID**: `PROMPT_013`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `services/education.py:292`

### Before

```python
# services/education.py:292

messages = [
    {
        "role": "system",
        "content": "Você é uma base de conhecimento educativa sobre imigração americana. Forneça informações precisas em..."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# services/education.py:292
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 14: unknown_function Prompt

**Prompt ID**: `PROMPT_014`
**Portkey ID**: `pp-local-unknown_function-prompt`
**Location**: `utils/translation/service.py:64`

### Before

```python
# utils/translation/service.py:64

messages = [
    {
        "role": "system",
        "content": "You are a professional translator for USCIS immigration forms. Translate accurately and formally...."
    }
]
response = await client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)

```

### After

```python
# utils/translation/service.py:64
# Migrated to Portkey: pp-local-unknown_function-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-unknown_function-prompt",
    variables={}
)

```

---

## Patch 15: FormValidationAgent System Prompt

**Prompt ID**: `PROMPT_015`
**Portkey ID**: `pp-local-formvalidationagent-system-prompt`
**Location**: `agents/specialized/form_validator.py:82`

### Before

```python
# agents/specialized/form_validator.py:82

def get_system_prompt(self) -> str:
    return f"""

        Você é a Dra. Ana, especialista EXCLUSIVA em validação de formulários USCIS.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({{self.dra_paula_assistant_id}}).

        EXPERTISE ESPECÍFICA...
"""

```

### After

```python
# agents/specialized/form_validator.py:82
# Migrated to Portkey: pp-local-formvalidationagent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-formvalidationagent-system-prompt",
    variables={}
)

```

---

## Patch 16: DocumentValidationAgent System Prompt

**Prompt ID**: `PROMPT_016`
**Portkey ID**: `pp-local-documentvalidationagent-system-prompt`
**Location**: `agents/specialized/document_validator.py:106`

### Before

```python
# agents/specialized/document_validator.py:106

def get_system_prompt(self) -> str:
    return f"""

        Você é o Dr. Miguel, especialista FORENSE em validação de documentos de imigração com 15+ anos de experiência.
        INTEGRADO COMPLETAMENTE COM A BASE DE CONHECIMENTO DA DRA. PAULA B2C.

 ...
"""

```

### After

```python
# agents/specialized/document_validator.py:106
# Migrated to Portkey: pp-local-documentvalidationagent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-documentvalidationagent-system-prompt",
    variables={"var": var, "enhanced_prompt": enhanced_prompt}
)

```

---

## Patch 17: ComplianceCheckAgent System Prompt

**Prompt ID**: `PROMPT_017`
**Portkey ID**: `pp-local-compliancecheckagent-system-prompt`
**Location**: `agents/specialized/compliance_checker.py:60`

### Before

```python
# agents/specialized/compliance_checker.py:60

def get_system_prompt(self) -> str:
    return f"""

        Você é a Dra. Patricia, especialista EXCLUSIVA em compliance USCIS e revisão final.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({{self.dra_paula_assistant_id}}).

        EXPERTISE ESP...
"""

```

### After

```python
# agents/specialized/compliance_checker.py:60
# Migrated to Portkey: pp-local-compliancecheckagent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-compliancecheckagent-system-prompt",
    variables={}
)

```

---

## Patch 18: UrgencyTriageAgent System Prompt

**Prompt ID**: `PROMPT_018`
**Portkey ID**: `pp-local-urgencytriageagent-system-prompt`
**Location**: `agents/specialized/triage.py:56`

### Before

```python
# agents/specialized/triage.py:56

def get_system_prompt(self) -> str:
    return f"""

        Você é o Dr. Roberto, especialista em triagem e roteamento de questões de imigração.

        FUNÇÃO PRINCIPAL:
        - Classificar urgência e tipo de problema
        - Rotear para o espec...
"""

```

### After

```python
# agents/specialized/triage.py:56
# Migrated to Portkey: pp-local-urgencytriageagent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-urgencytriageagent-system-prompt",
    variables={}
)

```

---

## Patch 19: EligibilityAnalysisAgent System Prompt

**Prompt ID**: `PROMPT_019`
**Portkey ID**: `pp-local-eligibilityanalysisagent-system-prompt`
**Location**: `agents/specialized/eligibility_analyst.py:60`

### Before

```python
# agents/specialized/eligibility_analyst.py:60

def get_system_prompt(self) -> str:
    return f"""

        Você é o Dr. Carlos, especialista EXCLUSIVO em análise de elegibilidade para vistos americanos.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({{self.dra_paula_assistant_id}}).

        E...
"""

```

### After

```python
# agents/specialized/eligibility_analyst.py:60
# Migrated to Portkey: pp-local-eligibilityanalysisagent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-eligibilityanalysisagent-system-prompt",
    variables={}
)

```

---

## Patch 20: ImmigrationLetterWriterAgent System Prompt

**Prompt ID**: `PROMPT_020`
**Portkey ID**: `pp-local-immigrationletterwriteragent-system-prompt`
**Location**: `agents/specialized/letter_writer.py:63`

### Before

```python
# agents/specialized/letter_writer.py:63

def get_system_prompt(self) -> str:
    return f"""

        Você é o Dr. Ricardo, especialista EXCLUSIVO em redação de cartas de imigração.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({{self.dra_paula_assistant_id}}).

        REGRA FUNDAMENTAL...
"""

```

### After

```python
# agents/specialized/letter_writer.py:63
# Migrated to Portkey: pp-local-immigrationletterwriteragent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-immigrationletterwriteragent-system-prompt",
    variables={}
)

```

---

## Patch 21: USCISFormTranslatorAgent System Prompt

**Prompt ID**: `PROMPT_021`
**Portkey ID**: `pp-local-uscisformtranslatoragent-system-prompt`
**Location**: `agents/specialized/translator.py:62`

### Before

```python
# agents/specialized/translator.py:62

def get_system_prompt(self) -> str:
    return f"""

        Você é o Dr. Fernando, especialista EXCLUSIVO em validação e tradução de formulários USCIS.
        USANDO O BANCO DE DADOS DA DRA. PAULA B2C ({{self.dra_paula_assistant_id}}).

        FUNÇÃ...
"""

```

### After

```python
# agents/specialized/translator.py:62
# Migrated to Portkey: pp-local-uscisformtranslatoragent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-uscisformtranslatoragent-system-prompt",
    variables={}
)

```

---

## Patch 22: MariaAgent System Prompt

**Prompt ID**: `PROMPT_022`
**Portkey ID**: `pp-local-mariaagent-system-prompt`
**Location**: `agents/maria/agent.py:209`

### Before

```python
# agents/maria/agent.py:209

def get_system_prompt(self) -> str:
    return f"""
Você é a Maria, a assistente virtual da Osprey - uma plataforma de imigração americana.

## SUA IDENTIDADE
Nome: {{var}}
Idade: {{var}}
Nacionalidade: {{var}}
Tom: {{var}}

## SUA MISSÃO
1. **Atendime...
"""

```

### After

```python
# agents/maria/agent.py:209
# Migrated to Portkey: pp-local-mariaagent-system-prompt

from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

response = await llm_client.completion_with_prompt(
    prompt_id="pp-local-mariaagent-system-prompt",
    variables={"var": var}
)

```

---

