# Prompt Migration to Portkey Guide

## Introduction

This document provides a comprehensive guide for migrating all hardcoded prompts in the Osprey backend to Portkey's Prompt Engineering Studio. Portkey enables centralized prompt management, versioning, A/B testing, and observability across all LLM calls.

### Why Migrate to Portkey?

- **Centralized Management**: All prompts in one place, versioned and auditable
- **A/B Testing**: Test prompt variations without code changes
- **Observability**: Track prompt performance, costs, and usage
- **Multi-Provider**: Switch between OpenAI, Anthropic, Gemini without code changes
- **Collaboration**: Non-technical team members can iterate on prompts
- **Rollback**: Instantly revert to previous prompt versions

### Migration Process Overview

1. **Audit**: Identify all hardcoded prompts in the codebase
2. **Document**: Specify model, parameters, and variables for each prompt
3. **Create**: Build prompts in Portkey Prompt Engineering Studio
4. **Test**: Validate prompts with sample inputs
5. **Migrate**: Update code to use Portkey prompt IDs
6. **Validate**: Ensure outputs match original behavior

## Portkey Documentation Links

- [Portkey Documentation](https://portkey.ai/docs)
- [Prompt Engineering Studio Guide](https://portkey.ai/docs/product/prompt-library)
- [Prompt Templates](https://portkey.ai/docs/product/prompt-library/prompt-templates)
- [Python SDK Reference](https://portkey.ai/docs/api-reference/portkey-sdk-client)
- [OpenAI Integration](https://portkey.ai/docs/integrations/llms/openai)
- [Gemini Integration](https://portkey.ai/docs/integrations/llms/gemini-vertex-ai)

## Document Structure

This document is organized into the following sections:

1. **Prompt Inventory**: Complete list of all prompts in the codebase
2. **Prompt Specifications**: Detailed specifications for each prompt
3. **Migration Instructions**: Step-by-step guide for creating prompts in Portkey
4. **Code Patterns**: Before/after examples for common patterns
5. **Testing Guide**: How to validate migrated prompts
6. **Troubleshooting**: Common issues and solutions

---

## Prompt Inventory

Below is a comprehensive inventory of all prompts found in the Osprey backend codebase. Each prompt is documented with:

- **Prompt ID**: Unique identifier for tracking
- **Location**: File path and line number
- **Purpose**: What the prompt does
- **Agent/Module**: Which agent or module uses it
- **Status**: Migration status (⏳ Not Started, 🚧 In Progress, ✅ Completed)

### Summary Statistics

- **Total Prompts Identified**: 50+
- **System Prompts**: 15
- **User Prompts**: 35+
- **Complex Multi-Turn Prompts**: 5
- **Prompts Migrated**: 0

### Prompt Categories

1. **Agent System Prompts** (15 prompts)
   - Maria Agent
   - Dra. Paula (Immigration Expert)
   - Specialized Agents (Document Validator, Form Validator, etc.)
   - Owl Agent
   - QA Agents

2. **Document Processing Prompts** (10 prompts)
   - Document identification
   - Data extraction
   - Quality analysis
   - Relevance checking

3. **Form Processing Prompts** (8 prompts)
   - Form validation
   - Translation
   - Field extraction

4. **Education & Interview Prompts** (4 prompts)
   - Question generation
   - Answer evaluation
   - Educational content

5. **Server Endpoint Prompts** (10+ prompts)
   - Document analysis
   - Translation
   - Recommendations
   - Letter generation

6. **Visa Processing Prompts** (3 prompts)
   - Auto-updater
   - Document mapping
   - Extraction

### Detailed Prompt Inventory

#### 1. Agent System Prompts

| ID | Agent | Location | Purpose | Status |
|----|-------|----------|---------|--------|
| PROMPT_001 | Maria | `backend/maria_agent.py:146` | Main system prompt for Maria assistant | ⏳ Not Started |
| PROMPT_002 | Maria (Migrated) | `backend/agents/maria/agent.py:213` | Main system prompt for Maria assistant (new location) | ⏳ Not Started |
| PROMPT_003 | Dra. Paula | `backend/immigration_expert.py:37` | Immigration expert system prompt | ⏳ Not Started |
| PROMPT_004 | Dra. Paula (Migrated) | `backend/agents/immigration_expert.py:50` | Immigration expert system prompt (new location) | ⏳ Not Started |
| PROMPT_005 | Dr. Miguel | `backend/specialized_agents.py:156` | Document validator system prompt | ⏳ Not Started |
| PROMPT_006 | Dr. Miguel (Migrated) | `backend/agents/specialized/document_validator.py:120` | Document validator system prompt (new location) | ⏳ Not Started |
| PROMPT_007 | Dra. Ana | `backend/specialized_agents.py:786` | Form validator system prompt | ⏳ Not Started |
| PROMPT_008 | Dra. Ana (Migrated) | `backend/agents/specialized/form_validator.py:88` | Form validator system prompt (new location) | ⏳ Not Started |
| PROMPT_009 | Dr. Carlos | `backend/specialized_agents.py:832` | Eligibility analyst system prompt | ⏳ Not Started |
| PROMPT_010 | Dr. Carlos (Migrated) | `backend/agents/specialized/eligibility_analyst.py:66` | Eligibility analyst system prompt (new location) | ⏳ Not Started |
| PROMPT_011 | Dra. Patricia | `backend/specialized_agents.py:878` | Compliance checker system prompt | ⏳ Not Started |
| PROMPT_012 | Dra. Patricia (Migrated) | `backend/agents/specialized/compliance_checker.py:66` | Compliance checker system prompt (new location) | ⏳ Not Started |
| PROMPT_013 | Dr. Ricardo | `backend/specialized_agents.py:923` | Letter writer system prompt | ⏳ Not Started |
| PROMPT_014 | Dr. Ricardo (Migrated) | `backend/agents/specialized/letter_writer.py:68` | Letter writer system prompt (new location) | ⏳ Not Started |
| PROMPT_015 | Dr. Fernando | `backend/specialized_agents.py:998` | Translator system prompt | ⏳ Not Started |
| PROMPT_016 | Dr. Fernando (Migrated) | `backend/agents/specialized/translator.py:66` | Translator system prompt (new location) | ⏳ Not Started |
| PROMPT_017 | Dr. Roberto | `backend/specialized_agents.py:1112` | Triage agent system prompt | ⏳ Not Started |
| PROMPT_018 | Dr. Roberto (Migrated) | `backend/agents/specialized/triage.py:63` | Triage agent system prompt (new location) | ⏳ Not Started |
| PROMPT_019 | Owl Agent | `backend/intelligent_owl_agent.py` | Intelligent guidance system prompt | ⏳ Not Started |
| PROMPT_020 | Owl Agent (Migrated) | `backend/agents/owl/agent.py` | Intelligent guidance system prompt (new location) | ⏳ Not Started |
| PROMPT_021 | Dra. Paula Gemini | `backend/agents/dra_paula/gemini_agent.py:121` | Gemini-specific Dra. Paula prompt | ⏳ Not Started |
| PROMPT_022 | Dra. Paula Hybrid | `backend/agents/dra_paula/hybrid_agent.py:180` | Hybrid agent Dra. Paula prompt | ⏳ Not Started |
| PROMPT_023 | Conversational Assistant | `backend/agents/conversational_assistant.py:299` | Brief Q&A system prompt | ⏳ Not Started |

#### 2. Document Processing Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_024 | Visual document identification | `backend/documents/recognition.py:112` | ⏳ Not Started |
| PROMPT_025 | Visual document identification (old) | `backend/enhanced_document_recognition.py:112` | ⏳ Not Started |
| PROMPT_026 | Intelligent data extraction | `backend/documents/recognition.py:208` | ⏳ Not Started |
| PROMPT_027 | Intelligent data extraction (old) | `backend/enhanced_document_recognition.py:208` | ⏳ Not Started |
| PROMPT_028 | Technical quality analysis | `backend/documents/recognition.py:313` | ⏳ Not Started |
| PROMPT_029 | Technical quality analysis (old) | `backend/enhanced_document_recognition.py:313` | ⏳ Not Started |
| PROMPT_030 | Visa relevance analysis | `backend/documents/recognition.py:387` | ⏳ Not Started |
| PROMPT_031 | Visa relevance analysis (old) | `backend/enhanced_document_recognition.py:387` | ⏳ Not Started |
| PROMPT_032 | Document validation (Dr. Miguel) | `backend/specialized_agents.py:759` | ⏳ Not Started |
| PROMPT_033 | Document validation (Dr. Miguel migrated) | `backend/agents/specialized/document_validator.py` | ⏳ Not Started |
| PROMPT_034 | Completeness quality analysis | `backend/case/completeness_analyzer.py:189` | ⏳ Not Started |

#### 3. Form Processing Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_035 | Form validation (Dra. Ana) | `backend/api/specialized_agents.py:70` | ⏳ Not Started |
| PROMPT_036 | Form validation (Dra. Ana migrated) | `backend/agents/specialized/form_validator.py:167` | ⏳ Not Started |
| PROMPT_037 | USCIS form translation | `backend/api/auto_application_ai.py:181` | ⏳ Not Started |
| PROMPT_038 | Form translation (Dr. Fernando) | `backend/api/specialized_agents.py:242` | ⏳ Not Started |
| PROMPT_039 | Form translation (Dr. Fernando migrated) | `backend/agents/specialized/translator.py:149` | ⏳ Not Started |
| PROMPT_040 | Translation service | `backend/utils/translation/service.py:226` | ⏳ Not Started |
| PROMPT_041 | Translation service (alternative) | `backend/utils/translation/service.py:239` | ⏳ Not Started |
| PROMPT_042 | Dra. Paula form validation | `backend/immigration_expert.py:159` | ⏳ Not Started |
| PROMPT_043 | Dra. Paula form validation (migrated) | `backend/agents/immigration_expert.py:177` | ⏳ Not Started |

#### 4. Education & Interview Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_044 | Interview question generation | `backend/services/education.py:28` | ⏳ Not Started |
| PROMPT_045 | Interview answer evaluation | `backend/services/education.py:103` | ⏳ Not Started |
| PROMPT_046 | Educational tips | `backend/services/education.py:260` | ⏳ Not Started |
| PROMPT_047 | Knowledge base Q&A | `backend/services/education.py` | ⏳ Not Started |

#### 5. Server Endpoint Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_048 | Maria chat (server) | `backend/server.py:1842` | ⏳ Not Started |
| PROMPT_049 | Document analysis | `backend/server.py:1942` | ⏳ Not Started |
| PROMPT_050 | Language detection | `backend/server.py:1984` | ⏳ Not Started |
| PROMPT_051 | Translation | `backend/server.py:2002` | ⏳ Not Started |
| PROMPT_052 | Visa recommendation | `backend/server.py:2049` | ⏳ Not Started |
| PROMPT_053 | Directive generation | `backend/server.py:902` | ⏳ Not Started |
| PROMPT_054 | Letter review | `backend/server.py:959` | ⏳ Not Started |
| PROMPT_055 | Letter improvement | `backend/server.py:1145` | ⏳ Not Started |
| PROMPT_056 | Letter generation | `backend/server.py:1259` | ⏳ Not Started |
| PROMPT_057 | Gap notification | `backend/server.py:1358` | ⏳ Not Started |
| PROMPT_058 | Document validation (server) | `backend/server.py:2698` | ⏳ Not Started |
| PROMPT_059 | Consistency check | `backend/server.py:2770` | ⏳ Not Started |
| PROMPT_060 | Translation (server) | `backend/server.py:2842` | ⏳ Not Started |
| PROMPT_061 | Content generation | `backend/server.py:2919` | ⏳ Not Started |
| PROMPT_062 | Review (server) | `backend/server.py:3007` | ⏳ Not Started |

#### 6. Visa Processing Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_063 | Visa change analysis | `backend/visa/auto_updater.py:378` | ⏳ Not Started |
| PROMPT_064 | Document extraction | `backend/visa/document_mapping.py:343` | ⏳ Not Started |

#### 7. Specialized Agent Task Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_065 | Eligibility analysis | `backend/api/specialized_agents.py:110` | ⏳ Not Started |
| PROMPT_066 | Eligibility analysis (migrated) | `backend/agents/specialized/eligibility_analyst.py:99` | ⏳ Not Started |
| PROMPT_067 | Compliance review | `backend/api/specialized_agents.py:150` | ⏳ Not Started |
| PROMPT_068 | Compliance review (migrated) | `backend/agents/specialized/compliance_checker.py:107` | ⏳ Not Started |
| PROMPT_069 | Letter writing | `backend/api/specialized_agents.py:191` | ⏳ Not Started |
| PROMPT_070 | Letter writing (migrated) | `backend/agents/specialized/letter_writer.py:126` | ⏳ Not Started |
| PROMPT_071 | Triage routing | `backend/agents/specialized/triage.py:101` | ⏳ Not Started |

#### 8. Owl Agent Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_072 | Contextual guidance | `backend/intelligent_owl_agent.py:597` | ⏳ Not Started |
| PROMPT_073 | Contextual guidance (migrated) | `backend/agents/owl/agent.py:622` | ⏳ Not Started |
| PROMPT_074 | Input validation | `backend/intelligent_owl_agent.py:877` | ⏳ Not Started |
| PROMPT_075 | Input validation (migrated) | `backend/agents/owl/agent.py:899` | ⏳ Not Started |

#### 9. Voice & Compliance Prompts

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_076 | Voice compliance check | `backend/voice/agent.py:484` | ⏳ Not Started |
| PROMPT_077 | Voice compliance check (old) | `backend/voice_agent.py:484` | ⏳ Not Started |

#### 10. Document Analysis Prompts (Dra. Paula)

| ID | Purpose | Location | Status |
|----|---------|----------|--------|
| PROMPT_078 | Document rigorous analysis | `backend/immigration_expert.py:248` | ⏳ Not Started |
| PROMPT_079 | Document rigorous analysis (migrated) | `backend/agents/immigration_expert.py:279` | ⏳ Not Started |
| PROMPT_080 | General consultation | `backend/immigration_expert.py:356` | ⏳ Not Started |
| PROMPT_081 | General consultation (migrated) | `backend/agents/immigration_expert.py:399` | ⏳ Not Started |

---

## Prompt Specifications

This section provides detailed specifications for each prompt identified in the inventory. Use these specifications to recreate prompts in Portkey's Prompt Engineering Studio.

### PROMPT_001: Maria Agent System Prompt

**Prompt ID**: `PROMPT_001`
**Portkey ID**: `pp-maria-system-v1` (to be assigned)
**Location**: `backend/maria_agent.py:146`
**Agent**: Maria (Virtual Assistant)
**Status**: ⏳ Not Started

#### Purpose
Main system prompt for Maria, the Osprey virtual assistant. Defines her personality, capabilities, communication style, and guardrails for customer interactions.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`
- Alternative: `gemini-1.5-pro`

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "[Full Maria system prompt - see below]"
    },
    {
        "role": "user",
        "content": "{{user_message}}"
    }
]
```

#### Variables
- `{{user_name}}`: User's name (optional, defaults to "amigo(a)")
- `{{visa_type}}`: Type of visa application (optional)
- `{{progress}}`: Application progress percentage (optional)
- `{{case_status}}`: Current case status (optional)

#### Configuration
```python
{
    "temperature": 0.8,  # Higher for more natural, empathetic responses
    "max_tokens": 1500,
    "top_p": 0.95,
    "frequency_penalty": 0.3,  # Reduce repetition
    "presence_penalty": 0.2
}
```

#### Expected Response Format
Natural language text in Portuguese with:
- Emojis (moderate use)
- Bullet points for lists
- Empathetic tone
- Disclaimers when needed

#### Full Prompt Text
See `backend/maria_agent.py:146-217` for complete prompt. Key sections:
- Identity (name, age, nationality, tone)
- Mission (customer service, emotional support, education, sales)
- Capabilities (what she can/cannot do)
- Communication style (informal, warm, emoji usage)
- Positive psychology techniques
- Osprey benefits
- Important rules (never use "advogado" or "lawyer")
- Disclaimers

#### Migration Notes
- This is a critical prompt - test thoroughly
- Preserve Portuguese language and cultural nuances
- Maintain empathetic tone
- Ensure disclaimers are always included
- Test with various emotional states (anxiety, frustration, celebration)

---

### PROMPT_003: Dra. Paula Immigration Expert System Prompt

**Prompt ID**: `PROMPT_003`
**Portkey ID**: `pp-dra-paula-system-v1` (to be assigned)
**Location**: `backend/immigration_expert.py:37`
**Agent**: Dra. Paula (Immigration Expert)
**Status**: ⏳ Not Started

#### Purpose
System prompt for Dra. Paula, the immigration expert agent. Provides specialized knowledge about US immigration law, USCIS processes, and visa requirements.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`
- Alternative: `gemini-1.5-pro`

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "[Dra. Paula system prompt]"
    },
    {
        "role": "user",
        "content": "{{user_query}}"
    }
]
```

#### Variables
- `{{user_query}}`: User's question or request
- `{{context}}`: Additional context about the case (optional)
- `{{visa_type}}`: Specific visa type being discussed

#### Configuration
```python
{
    "temperature": 0.7,  # Balanced for accuracy and natural language
    "max_tokens": 2500,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

#### Expected Response Format
Structured Portuguese text with:
- Professional but accessible tone
- Legal accuracy
- Citations to USCIS sources when applicable
- Clear disclaimers about not providing legal advice

#### Full Prompt Text
See `backend/immigration_expert.py:37-100` for complete prompt. Key sections:
- Identity as Brazilian immigration expert
- Extensive knowledge of US immigration law
- B2C focus (self-application)
- Capabilities and limitations
- Communication style
- Disclaimers

#### Migration Notes
- Critical for legal accuracy
- Must maintain professional tone
- Test with complex immigration scenarios
- Ensure disclaimers are preserved
- Validate against USCIS guidelines

---

### PROMPT_005: Dr. Miguel Document Validator System Prompt

**Prompt ID**: `PROMPT_005`
**Portkey ID**: `pp-dr-miguel-system-v1` (to be assigned)
**Location**: `backend/specialized_agents.py:156`
**Agent**: Dr. Miguel (Document Validator)
**Status**: ⏳ Not Started

#### Purpose
System prompt for Dr. Miguel, specialized in document validation for immigration applications. Validates document authenticity, completeness, and compliance with USCIS requirements.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "[Dr. Miguel system prompt with knowledge base context]"
    },
    {
        "role": "user",
        "content": "{{validation_request}}"
    }
]
```

#### Variables
- `{{document_type}}`: Type of document being validated
- `{{visa_type}}`: Visa type for context
- `{{document_data}}`: Extracted document data
- `{{case_context}}`: Additional case information
- `{{kb_context}}`: Knowledge base context from Dra. Paula

#### Configuration
```python
{
    "temperature": 0.3,  # Lower for more consistent validation
    "max_tokens": 2000,
    "top_p": 0.85,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

#### Expected Response Format
JSON with validation results:
```json
{
    "valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["list", "of", "issues"],
    "recommendations": ["list", "of", "recommendations"],
    "missing_fields": ["list", "of", "missing"],
    "quality_score": 0-100
}
```

#### Full Prompt Text
See `backend/specialized_agents.py:156-180` for complete prompt. Key sections:
- Identity as document validation specialist
- Exclusive focus on document validation
- Validation criteria
- Output format requirements

#### Migration Notes
- Requires consistent JSON output
- Test with various document types
- Validate against USCIS document requirements
- Ensure knowledge base context is properly injected

---

### PROMPT_024: Visual Document Identification

**Prompt ID**: `PROMPT_024`
**Portkey ID**: `pp-doc-visual-id-v1` (to be assigned)
**Location**: `backend/documents/recognition.py:112`
**Module**: Document Recognition
**Status**: ⏳ Not Started

#### Purpose
Analyzes document images to identify document type using visual features. Uses GPT-4 Vision capabilities.

#### Recommended Model
- Primary: `gpt-4o` (with vision)
- Fallback: `gpt-4-turbo` (with vision)

#### Message Structure
```python
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "{{identification_prompt}}"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": "data:image/{{file_extension}};base64,{{file_base64}}"
                }
            }
        ]
    }
]
```

#### Variables
- `{{file_extension}}`: Image file extension (jpg, png, pdf)
- `{{file_base64}}`: Base64-encoded image data
- `{{filename}}`: Original filename for context

#### Configuration
```python
{
    "temperature": 0.2,  # Very low for consistent identification
    "max_tokens": 1000,
    "top_p": 0.8
}
```

#### Expected Response Format
JSON with identification results:
```json
{
    "document_type": "passport",
    "confidence": 0.95,
    "country": "Brazil",
    "visual_features": ["photo", "stamps", "MRZ"],
    "quality": "high"
}
```

#### Full Prompt Text
See `backend/documents/recognition.py:112-180` for complete prompt. Includes:
- Visual analysis instructions
- Document type taxonomy
- Feature identification guidelines
- Quality assessment criteria

#### Migration Notes
- Requires vision-capable model
- Test with various image qualities
- Validate with different document types
- Ensure base64 encoding is correct

---

### PROMPT_037: USCIS Form Translation

**Prompt ID**: `PROMPT_037`
**Portkey ID**: `pp-form-translation-v1` (to be assigned)
**Location**: `backend/api/auto_application_ai.py:181`
**Module**: Auto Application AI
**Status**: ⏳ Not Started

#### Purpose
Translates user responses from Portuguese to English for USCIS forms, maintaining formal tone and accuracy.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`
- Alternative: `gpt-3.5-turbo` (for cost optimization)

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "Você é um especialista em formulários do USCIS. Converta respostas em português para inglês formal adequado para formulários oficiais."
    },
    {
        "role": "user",
        "content": "{{translation_request}}"
    }
]
```

#### Variables
- `{{source_text}}`: Portuguese text to translate
- `{{field_name}}`: Form field name for context
- `{{form_type}}`: USCIS form type (I-129, I-539, etc.)

#### Configuration
```python
{
    "temperature": 0.3,  # Low for consistent translation
    "max_tokens": 500,
    "top_p": 0.85
}
```

#### Expected Response Format
Plain text with formal English translation, suitable for USCIS forms.

#### Migration Notes
- Critical for form accuracy
- Test with various Portuguese inputs
- Validate formal English output
- Ensure cultural context is preserved

---

### PROMPT_044: Interview Question Generation

**Prompt ID**: `PROMPT_044`
**Portkey ID**: `pp-interview-questions-v1` (to be assigned)
**Location**: `backend/services/education.py:28`
**Module**: Education Service
**Status**: ⏳ Not Started

#### Purpose
Generates realistic immigration interview questions for practice, tailored to visa type and user profile.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "Você é um especialista em entrevistas de imigração. Responda APENAS em JSON válido."
    },
    {
        "role": "user",
        "content": "{{question_generation_request}}"
    }
]
```

#### Variables
- `{{visa_type}}`: Type of visa (F-1, H-1B, etc.)
- `{{user_profile}}`: User background information
- `{{difficulty}}`: Question difficulty level (easy, medium, hard)
- `{{count}}`: Number of questions to generate (default: 10)

#### Configuration
```python
{
    "temperature": 0.8,  # Higher for variety in questions
    "max_tokens": 2000,
    "response_format": {"type": "json_object"}
}
```

#### Expected Response Format
```json
{
    "questions": [
        {
            "id": 1,
            "question": "Why do you want to study in the United States?",
            "category": "intent",
            "difficulty": "medium",
            "tips": "Be specific about your academic goals"
        }
    ]
}
```

#### Migration Notes
- Ensure JSON output is valid
- Test with different visa types
- Validate question relevance
- Check for cultural appropriateness

---

### PROMPT_053: Directive Generation

**Prompt ID**: `PROMPT_053`
**Portkey ID**: `pp-directive-generation-v1` (to be assigned)
**Location**: `backend/server.py:902`
**Module**: Server Endpoints
**Status**: ⏳ Not Started

#### Purpose
Generates informative guidance scripts based on USCIS requirements for specific visa types.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "{{system_prompt}}"
    },
    {
        "role": "user",
        "content": "{{directive_request}}"
    }
]
```

#### Variables
- `{{visa_type}}`: Visa type for directive
- `{{user_context}}`: User's specific situation
- `{{requirements}}`: USCIS requirements for visa type

#### Configuration
```python
{
    "temperature": 0.7,
    "max_tokens": 3000,
    "top_p": 0.9
}
```

#### Expected Response Format
Structured Portuguese text with:
- Introduction
- Step-by-step requirements
- Document checklist
- Timeline information
- Important notes and disclaimers

#### Full Prompt Text
See `backend/server.py:902-950` for complete prompt.

#### Migration Notes
- Must be accurate to USCIS requirements
- Test with all supported visa types
- Validate against official USCIS documentation
- Ensure disclaimers are included

---

### PROMPT_063: Visa Change Analysis

**Prompt ID**: `PROMPT_063`
**Portkey ID**: `pp-visa-change-analysis-v1` (to be assigned)
**Location**: `backend/visa/auto_updater.py:378`
**Module**: Visa Auto-Updater
**Status**: ⏳ Not Started

#### Purpose
Analyzes changes in visa information to determine if updates are significant enough to warrant user notification.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`

#### Message Structure
```python
messages = [
    {
        "role": "user",
        "content": "{{change_analysis_request}}"
    }
]
```

#### Variables
- `{{form_code}}`: USCIS form code (I-129, I-539, etc.)
- `{{data_type}}`: Type of data changed (requirements, fees, etc.)
- `{{old_data}}`: Previous version of data
- `{{new_data}}`: New version of data

#### Configuration
```python
{
    "temperature": 0.3,  # Low for consistent analysis
    "max_tokens": 1000,
    "response_format": {"type": "json_object"}
}
```

#### Expected Response Format
```json
{
    "significant": true/false,
    "severity": "low|medium|high",
    "summary": "Brief description of changes",
    "impact": "How this affects users",
    "action_required": true/false
}
```

#### Migration Notes
- Critical for keeping users informed
- Test with various change scenarios
- Validate severity classification
- Ensure JSON output is consistent

---

### PROMPT_072: Owl Contextual Guidance

**Prompt ID**: `PROMPT_072`
**Portkey ID**: `pp-owl-guidance-v1` (to be assigned)
**Location**: `backend/intelligent_owl_agent.py:597`
**Agent**: Owl (Intelligent Assistant)
**Status**: ⏳ Not Started

#### Purpose
Provides AI-powered contextual guidance for users filling out immigration forms, offering smart suggestions and validation.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`

#### Message Structure
```python
messages = [
    {
        "role": "user",
        "content": "{{guidance_request}}"
    }
]
```

#### Variables
- `{{visa_type}}`: Type of visa application
- `{{current_step}}`: Current form step
- `{{user_input}}`: User's current input
- `{{context}}`: Additional context about the application

#### Configuration
```python
{
    "temperature": 0.6,
    "max_tokens": 1500,
    "top_p": 0.9
}
```

#### Expected Response Format
JSON with guidance information:
```json
{
    "suggestion": "Helpful suggestion text",
    "validation": "valid|warning|error",
    "explanation": "Why this matters",
    "examples": ["example1", "example2"],
    "next_steps": ["step1", "step2"]
}
```

#### Full Prompt Text
See `backend/intelligent_owl_agent.py:597-650` for complete prompt.

#### Migration Notes
- Test with various form steps
- Validate suggestions are helpful
- Ensure guidance is accurate
- Check for edge cases

---

### PROMPT_076: Voice Compliance Check

**Prompt ID**: `PROMPT_076`
**Portkey ID**: `pp-voice-compliance-v1` (to be assigned)
**Location**: `backend/voice/agent.py:484`
**Module**: Voice Agent
**Status**: ⏳ Not Started

#### Purpose
Validates voice input for compliance with immigration application requirements, checking for inappropriate content or legal advice requests.

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "Você é um assistente de conformidade do sistema Osprey para aplicações de imigração."
    },
    {
        "role": "user",
        "content": "{{compliance_check_request}}"
    }
]
```

#### Variables
- `{{voice_input}}`: Transcribed voice input
- `{{context}}`: Application context

#### Configuration
```python
{
    "temperature": 0.2,  # Very low for consistent compliance checking
    "max_tokens": 500,
    "response_format": {"type": "json_object"}
}
```

#### Expected Response Format
```json
{
    "compliant": true/false,
    "issues": ["list", "of", "issues"],
    "severity": "low|medium|high",
    "recommendation": "What to do next"
}
```

#### Migration Notes
- Critical for legal compliance
- Test with various voice inputs
- Validate issue detection
- Ensure false positives are minimized

---

For each prompt, we document:

1. **Recommended Model**: GPT-4o, GPT-4-turbo, Gemini 1.5 Pro, etc.
2. **Message Types**: System, user, assistant, developer
3. **Variables/Parameters**: Dynamic values injected into the prompt
4. **Configuration**: Temperature, max_tokens, top_p, etc.
5. **Expected Response Format**: JSON, text, structured output
6. **Example Input/Output**: Sample data for testing

### Specification Template

```markdown
### Prompt: [Prompt Name]

**Prompt ID**: `PROMPT_XXX`
**Portkey ID**: `pp-[to-be-assigned]`
**Location**: `backend/path/to/file.py:123`
**Status**: ⏳ Not Started

#### Purpose
[Brief description of what this prompt does]

#### Recommended Model
- Primary: `gpt-4o`
- Fallback: `gpt-4-turbo`
- Alternative: `gemini-1.5-pro`

#### Message Structure
```python
messages = [
    {
        "role": "system",
        "content": "[System prompt text]"
    },
    {
        "role": "user",
        "content": "[User prompt with {{variables}}]"
    }
]
```

#### Variables
- `{{variable_name}}`: Description of variable
- `{{another_var}}`: Description of another variable

#### Configuration
```python
{
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}
```

#### Expected Response Format
```json
{
    "field1": "value",
    "field2": ["array", "of", "values"]
}
```

#### Example Input
```python
variables = {
    "variable_name": "example value",
    "another_var": "another example"
}
```

#### Example Output
```
[Expected output text or JSON]
```

#### Migration Notes
- [Any special considerations for migration]
- [Dependencies on other prompts]
- [Testing requirements]
```

---

## Migration Instructions

### Overview

This section provides step-by-step instructions for migrating prompts from hardcoded strings in Python files to Portkey's Prompt Engineering Studio. Follow these steps for each prompt in the inventory.

### Prerequisites

Before starting migration:

1. **Portkey Account**: Ensure you have access to [Portkey Dashboard](https://app.portkey.ai)
2. **API Keys**: Configure Portkey API key in `.env` file
3. **Virtual Keys**: Set up virtual keys for OpenAI, Anthropic, Gemini
4. **Testing Environment**: Have a staging environment ready for testing
5. **Backup**: Ensure code is committed to version control

### Step 1: Access Portkey Prompt Engineering Studio

1. Log in to [Portkey Dashboard](https://app.portkey.ai)
2. Navigate to **Prompt Library** in the left sidebar
3. Click **Create New Prompt** button (top right)

**Screenshot Description**: You'll see a clean interface with:
- Left sidebar with navigation menu
- Main area showing existing prompts (if any)
- Blue "Create New Prompt" button in top right corner

### Step 2: Create Prompt in Portkey UI

#### 2.1 Basic Information

1. **Name**: Use descriptive name following convention
   - Format: `[Agent/Module] - [Purpose]`
   - Examples:
     - `Maria - System Prompt`
     - `Document Validator - Dr. Miguel`
     - `Form Translation - USCIS`

2. **Description**: Brief explanation (1-2 sentences)
   - Example: "Main system prompt for Maria virtual assistant. Defines personality, capabilities, and communication style."

3. **Tags**: Add relevant tags for organization
   - Suggested tags: `agent`, `system-prompt`, `maria`, `document`, `translation`, `validation`
   - Use tags to group related prompts

**Screenshot Description**: Form with fields:
- Name (text input)
- Description (textarea)
- Tags (multi-select dropdown)

#### 2.2 Configure Messages

Portkey supports multiple message types in a single prompt:

1. **Add System Message** (if applicable)
   - Click **Add Message** button
   - Select **Role**: `System`
   - Enter **Content**: Paste system prompt text
   - Use `{{variable_name}}` syntax for dynamic values

2. **Add User Message** (if applicable)
   - Click **Add Message** button
   - Select **Role**: `User`
   - Enter **Content**: Paste user prompt template
   - Use `{{variable_name}}` for variables

3. **Add Assistant Message** (for few-shot examples)
   - Click **Add Message** button
   - Select **Role**: `Assistant`
   - Enter **Content**: Example response

**Example: Maria System Prompt**
```
Message 1:
Role: System
Content: Você é a Maria, a assistente virtual da Osprey...
[Full system prompt with {{user_name}}, {{visa_type}} variables]

Message 2:
Role: User
Content: {{user_message}}
```

**Screenshot Description**: Message builder interface with:
- List of messages (can reorder by dragging)
- Each message shows role badge and content preview
- "Add Message" button at bottom
- Variable highlighting in content area

#### 2.3 Define Variables

For each `{{variable}}` in your prompt:

1. Click **Variables** tab
2. Click **Add Variable**
3. Enter variable details:
   - **Name**: Variable name (without braces)
   - **Type**: String, Number, Boolean, Array, Object
   - **Required**: Yes/No
   - **Default Value**: Optional default
   - **Description**: What this variable represents

**Example Variables for Maria:**
```
Name: user_message
Type: String
Required: Yes
Description: The user's message to Maria

Name: user_name
Type: String
Required: No
Default: "amigo(a)"
Description: User's name for personalization

Name: visa_type
Type: String
Required: No
Description: Type of visa application (I-539, H-1B, etc.)
```

**Screenshot Description**: Variables panel showing:
- Table of defined variables
- Columns: Name, Type, Required, Default, Description
- "Add Variable" button
- Edit/Delete icons for each variable

#### 2.4 Model Configuration

Configure the LLM model and parameters:

1. **Model Selection**
   - Click **Model** dropdown
   - Select primary model (e.g., `gpt-4o`, `gpt-4-turbo`, `gemini-1.5-pro`)
   - Portkey will route to this model by default

2. **Temperature** (0.0 - 2.0)
   - Lower (0.0-0.3): More deterministic, consistent
   - Medium (0.4-0.7): Balanced
   - Higher (0.8-2.0): More creative, varied
   - **Recommendations**:
     - Validation/Analysis: 0.2-0.3
     - Translation: 0.3-0.5
     - Conversation: 0.7-0.9
     - Creative Writing: 0.8-1.2

3. **Max Tokens**
   - Set maximum response length
   - Consider your use case:
     - Short responses: 500-1000
     - Medium responses: 1000-2000
     - Long responses: 2000-4000
   - Note: Affects cost and latency

4. **Advanced Settings** (click to expand)
   - **Top P** (0.0-1.0): Nucleus sampling (usually 0.9-1.0)
   - **Frequency Penalty** (0.0-2.0): Reduce repetition (0.0-0.5)
   - **Presence Penalty** (0.0-2.0): Encourage new topics (0.0-0.5)
   - **Stop Sequences**: Strings that stop generation
   - **Response Format**: `text` or `json_object`

**Example Configuration for Maria:**
```
Model: gpt-4o
Temperature: 0.8
Max Tokens: 1500
Top P: 0.95
Frequency Penalty: 0.3
Presence Penalty: 0.2
Response Format: text
```

**Example Configuration for Document Validator:**
```
Model: gpt-4o
Temperature: 0.3
Max Tokens: 2000
Top P: 0.85
Frequency Penalty: 0.0
Presence Penalty: 0.0
Response Format: json_object
```

**Screenshot Description**: Configuration panel with:
- Model dropdown (searchable)
- Sliders for temperature, max_tokens
- Expandable "Advanced Settings" section
- Response format toggle
- Real-time cost estimate

#### 2.5 Test Prompt

Before saving, test your prompt:

1. Click **Test** button (top right)
2. Enter sample values for variables
3. Click **Run Test**
4. Review output in right panel
5. Iterate on prompt if needed

**Testing Checklist**:
- [ ] Test with typical inputs
- [ ] Test with edge cases (empty, very long, special characters)
- [ ] Test with different variable combinations
- [ ] Verify output format matches expectations
- [ ] Check for any errors or warnings
- [ ] Validate response quality

**Example Test for Maria:**
```json
{
  "user_message": "Estou muito ansioso com minha aplicação de visto",
  "user_name": "João",
  "visa_type": "H-1B"
}
```

Expected output: Empathetic response in Portuguese with anxiety management tips.

**Screenshot Description**: Test panel showing:
- Left side: Variable input form (JSON or form fields)
- Right side: Response output
- Run button at top
- Response metadata (tokens used, latency, cost)
- Option to save test case

#### 2.6 Save and Deploy

1. Click **Save** button
2. Prompt is saved in draft state
3. Click **Publish** to make it available via API
4. Copy **Prompt ID** (format: `pp-xxxxxxxx`)
5. Document Prompt ID in this guide (update inventory table)

**Important**: Only published prompts are accessible via API!

**Screenshot Description**: Save dialog showing:
- Prompt name and ID
- Status: Draft or Published
- Publish button
- Copy ID button
- Version history link

### Step 3: Update Code to Use Portkey Prompt

Now update your Python code to use the Portkey prompt instead of hardcoded strings.

#### 3.1 Import LLM Client

```python
from backend.llm.portkey_client import LLMClient

# Initialize client (uses env vars for API keys)
llm_client = LLMClient()
```

#### 3.2 Replace Hardcoded Prompt

**Before (Hardcoded):**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def analyze_document(document_text: str):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a document analyzer. Classify the document type and extract key information."
            },
            {
                "role": "user",
                "content": f"Analyze this document:\n\n{document_text}"
            }
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content
```

**After (Portkey Prompt):**
```python
from backend.llm.portkey_client import LLMClient

llm_client = LLMClient()

async def analyze_document(document_text: str):
    # Use Portkey prompt by ID
    response = await llm_client.completion_with_prompt(
        prompt_id="pp-document-analyzer-v1",  # Portkey Prompt ID
        variables={
            "document_text": document_text
        }
    )
    return response["choices"][0]["message"]["content"]
```

#### 3.3 Handle Variables

Map your function parameters to Portkey variables:

```python
async def maria_chat(
    user_message: str,
    user_name: str = None,
    visa_type: str = None,
    progress: int = 0
):
    response = await llm_client.completion_with_prompt(
        prompt_id="pp-maria-system-v1",
        variables={
            "user_message": user_message,
            "user_name": user_name or "amigo(a)",
            "visa_type": visa_type or "não especificado",
            "progress": str(progress)
        }
    )
    return response["choices"][0]["message"]["content"]
```

#### 3.4 Override Model/Config (Optional)

You can override prompt configuration at runtime:

```python
response = await llm_client.completion_with_prompt(
    prompt_id="pp-maria-system-v1",
    variables={"user_message": message},
    # Override model for this call
    model="gpt-4-turbo",
    # Override temperature
    temperature=0.9,
    # Override max_tokens
    max_tokens=2000
)
```

#### 3.5 Handle Streaming (Optional)

For streaming responses:

```python
async def maria_chat_stream(user_message: str):
    async for chunk in llm_client.stream_completion_with_prompt(
        prompt_id="pp-maria-system-v1",
        variables={"user_message": user_message}
    ):
        yield chunk
```

#### 3.6 Error Handling

Always include error handling:

```python
from backend.llm.exceptions import (
    LLMException,
    PromptNotFoundError,
    LLMRateLimitError
)

async def analyze_document(document_text: str):
    try:
        response = await llm_client.completion_with_prompt(
            prompt_id="pp-document-analyzer-v1",
            variables={"document_text": document_text}
        )
        return response["choices"][0]["message"]["content"]
    
    except PromptNotFoundError:
        logger.error("Prompt ID not found in Portkey")
        # Fallback to default behavior
        return await fallback_analysis(document_text)
    
    except LLMRateLimitError:
        logger.warning("Rate limit exceeded, retrying...")
        # Retry logic handled by LLMClient
        raise
    
    except LLMException as e:
        logger.error(f"LLM error: {e}")
        raise
```

### Step 4: Test Migration

Comprehensive testing is critical for successful migration.

#### 4.1 Unit Tests

Create unit tests for the migrated function:

```python
import pytest
from backend.llm.portkey_client import LLMClient
from backend.documents.analyzer import DocumentAnalyzer

@pytest.mark.asyncio
async def test_document_analyzer_with_portkey():
    """Test document analyzer uses Portkey prompt correctly"""
    analyzer = DocumentAnalyzer()
    
    # Test with sample document
    sample_doc = "This is a passport document with MRZ..."
    
    result = await analyzer.analyze_document(sample_doc)
    
    # Verify result structure
    assert result is not None
    assert "document_type" in result
    assert result["document_type"] == "passport"
    assert result["confidence"] > 0.8

@pytest.mark.asyncio
async def test_document_analyzer_error_handling():
    """Test error handling when Portkey fails"""
    analyzer = DocumentAnalyzer()
    
    # Test with invalid input
    with pytest.raises(ValueError):
        await analyzer.analyze_document("")
```

#### 4.2 Integration Tests

Test end-to-end flows:

```python
@pytest.mark.asyncio
async def test_maria_conversation_flow():
    """Test complete Maria conversation with Portkey"""
    from backend.agents.maria.agent import MariaAgent
    
    maria = MariaAgent()
    
    # Test greeting
    response1 = await maria.chat(
        user_message="Olá, preciso de ajuda com meu visto",
        user_name="João"
    )
    assert "João" in response1["response"]
    assert "visto" in response1["response"].lower()
    
    # Test follow-up
    response2 = await maria.chat(
        user_message="Estou ansioso com o processo",
        user_name="João"
    )
    assert response2["emotion_detected"] == "anxiety"
    assert "respiração" in response2["response"].lower()
```

#### 4.3 Comparison Testing

Ensure migrated prompts produce equivalent results:

```python
@pytest.mark.asyncio
async def test_prompt_migration_equivalence():
    """Compare old vs new implementation"""
    
    test_input = "Sample document text..."
    
    # Old implementation (if still available)
    old_result = await old_analyze_document(test_input)
    
    # New implementation with Portkey
    new_result = await analyze_document(test_input)
    
    # Compare key fields (allow for minor variations in LLM output)
    assert old_result["document_type"] == new_result["document_type"]
    assert abs(old_result["confidence"] - new_result["confidence"]) < 0.1
```

#### 4.4 Load Testing

Test performance under load:

```python
import asyncio
import time

@pytest.mark.asyncio
async def test_portkey_performance():
    """Test Portkey performance with concurrent requests"""
    
    async def single_request():
        return await llm_client.completion_with_prompt(
            prompt_id="pp-maria-system-v1",
            variables={"user_message": "Test message"}
        )
    
    # Run 10 concurrent requests
    start = time.time()
    results = await asyncio.gather(*[single_request() for _ in range(10)])
    duration = time.time() - start
    
    # Verify all succeeded
    assert len(results) == 10
    assert all(r is not None for r in results)
    
    # Check average latency
    avg_latency = duration / 10
    assert avg_latency < 2.0  # Should be under 2 seconds per request
```

### Step 5: Update Documentation

After successful migration:

#### 5.1 Update This Document

1. Update prompt inventory table:
   - Change status from ⏳ to ✅
   - Add Portkey Prompt ID
   - Add migration date

2. Document any issues encountered

3. Add learnings for future migrations

#### 5.2 Update Code Comments

Add comments referencing Portkey prompt:

```python
async def analyze_document(document_text: str):
    """
    Analyze document using AI.
    
    Uses Portkey Prompt: pp-document-analyzer-v1
    See: backend/PROMPTS_TO_PORTKEY.md#PROMPT_024
    
    Args:
        document_text: Text content of document
    
    Returns:
        Analysis results with document type and confidence
    """
    response = await llm_client.completion_with_prompt(
        prompt_id="pp-document-analyzer-v1",
        variables={"document_text": document_text}
    )
    return response["choices"][0]["message"]["content"]
```

#### 5.3 Update API Documentation

If the function is exposed via API, update OpenAPI docs:

```python
@router.post("/analyze-document")
async def analyze_document_endpoint(
    document: UploadFile
) -> DocumentAnalysisResponse:
    """
    Analyze uploaded document.
    
    This endpoint uses AI (via Portkey) to identify document type
    and extract key information.
    
    Portkey Prompt: pp-document-analyzer-v1
    Model: gpt-4o
    """
    # Implementation
    pass
```

### Step 6: Monitor in Production

After deployment, monitor the migrated prompts:

#### 6.1 Portkey Dashboard

1. Navigate to **Analytics** in Portkey dashboard
2. Filter by Prompt ID
3. Monitor metrics:
   - Request count
   - Average latency
   - Token usage
   - Cost per request
   - Error rate
   - Cache hit rate

#### 6.2 Set Up Alerts

Configure alerts in Portkey:

1. Go to **Settings** > **Alerts**
2. Create alerts for:
   - Error rate > 5%
   - Latency > 5 seconds (p95)
   - Daily cost > budget
   - Rate limit approaching

#### 6.3 Review Logs

Regularly review logs for issues:

```python
# Application logs
logger.info(f"Portkey prompt called: pp-maria-system-v1")
logger.info(f"Response time: {latency}ms")
logger.info(f"Tokens used: {tokens}")
```

### Step 7: Iterate and Optimize

Continuously improve prompts based on real-world usage:

#### 7.1 A/B Testing

Use Portkey's A/B testing feature:

1. Create variant of prompt (e.g., `pp-maria-system-v2`)
2. Configure traffic split (50/50)
3. Monitor performance metrics
4. Choose winning variant

#### 7.2 Prompt Optimization

Based on analytics:

- Reduce token usage by shortening prompts
- Improve response quality by adding examples
- Adjust temperature for better consistency
- Add constraints to reduce errors

#### 7.3 Version Management

Maintain prompt versions:

- Use semantic versioning: `v1`, `v2`, `v3`
- Document changes in Portkey description
- Keep old versions for rollback
- Test new versions in staging first

---

## Code Patterns

### Pattern 1: Simple System + User Prompt

**Before:**
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f"Answer this: {question}"}
]
response = await openai_client.chat.completions.create(
    model="gpt-4o",
    messages=messages
)
```

**After:**
```python
response = await llm_client.completion_with_prompt(
    prompt_id="pp-helpful-assistant-001",
    variables={"question": question}
)
```

### Pattern 2: Multi-Turn Conversation

**Before:**
```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message_1},
    {"role": "assistant", "content": assistant_response_1},
    {"role": "user", "content": user_message_2}
]
```

**After:**
```python
# For multi-turn, use chat_completion with messages
response = await llm_client.chat_completion(
    messages=messages,
    model="gpt-4o"
)
# Note: Multi-turn conversations may need custom handling
```

### Pattern 3: JSON Response Format

**Before:**
```python
messages = [
    {
        "role": "system",
        "content": "You are a JSON generator. Always respond with valid JSON."
    },
    {
        "role": "user",
        "content": f"Generate JSON for: {data}"
    }
]
response = await openai_client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    response_format={"type": "json_object"}
)
```

**After:**
```python
response = await llm_client.completion_with_prompt(
    prompt_id="pp-json-generator-001",
    variables={"data": data},
    response_format={"type": "json_object"}
)
```

### Pattern 4: Streaming Responses

**Before:**
```python
stream = await openai_client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    stream=True
)
async for chunk in stream:
    yield chunk.choices[0].delta.content
```

**After:**
```python
# Streaming with Portkey prompts
async for chunk in llm_client.stream_completion_with_prompt(
    prompt_id="pp-streaming-001",
    variables={"input": user_input}
):
    yield chunk
```

### Pattern 5: Conditional Model Selection

**Before:**
```python
model = "gpt-4o" if complex_task else "gpt-3.5-turbo"
response = await openai_client.chat.completions.create(
    model=model,
    messages=messages
)
```

**After:**
```python
# Configure model in Portkey prompt or override at runtime
response = await llm_client.completion_with_prompt(
    prompt_id="pp-conditional-001",
    variables={"input": data},
    model="gpt-4o" if complex_task else "gpt-3.5-turbo"
)
```

---

## Testing Guide

### Unit Testing Migrated Prompts

```python
import pytest
from backend.llm.portkey_client import LLMClient

@pytest.mark.asyncio
async def test_document_analyzer_prompt():
    """Test document analyzer prompt migration"""
    llm_client = LLMClient()
    
    # Test with sample document
    sample_doc = "This is a passport document..."
    
    response = await llm_client.completion_with_prompt(
        prompt_id="pp-document-analyzer-123",
        variables={"document_text": sample_doc}
    )
    
    # Verify response structure
    assert response is not None
    assert "choices" in response
    assert len(response["choices"]) > 0
    
    # Verify content
    content = response["choices"][0]["message"]["content"]
    assert "passport" in content.lower()
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_end_to_end_document_flow():
    """Test complete document processing flow with Portkey"""
    from backend.documents.analyzer import DocumentAnalyzer
    
    analyzer = DocumentAnalyzer()
    result = await analyzer.analyze_document(
        document_path="test_passport.pdf"
    )
    
    assert result["document_type"] == "passport"
    assert result["confidence"] > 0.8
```

### Comparison Testing

```python
@pytest.mark.asyncio
async def test_prompt_migration_equivalence():
    """Ensure migrated prompt produces equivalent results"""
    
    # Original implementation
    original_result = await original_function(test_input)
    
    # Migrated implementation
    migrated_result = await migrated_function(test_input)
    
    # Compare outputs (may need fuzzy matching for LLM responses)
    assert original_result["type"] == migrated_result["type"]
    assert abs(original_result["score"] - migrated_result["score"]) < 0.1
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Prompt ID Not Found
**Error**: `PromptNotFoundError: Prompt ID 'pp-xxx' not found`

**Solution**:
- Verify Prompt ID is correct in Portkey dashboard
- Ensure prompt is published (not in draft state)
- Check API key has access to the prompt

#### Issue 2: Variable Not Replaced
**Error**: Variables like `{{variable_name}}` appear in output

**Solution**:
- Ensure variable names match exactly (case-sensitive)
- Pass all required variables in `variables` dict
- Check for typos in variable names

#### Issue 3: Different Output Format
**Error**: Migrated prompt returns different format than original

**Solution**:
- Review prompt text for formatting instructions
- Add explicit format instructions to prompt
- Use `response_format` parameter for JSON outputs
- Test with multiple examples to ensure consistency

#### Issue 4: Rate Limiting
**Error**: `LLMRateLimitError: Rate limit exceeded`

**Solution**:
- Configure rate limits in Portkey dashboard
- Implement exponential backoff in code
- Use caching for repeated queries
- Consider upgrading Portkey plan

#### Issue 5: Cost Overruns
**Error**: Unexpected high costs

**Solution**:
- Set cost budgets in Portkey dashboard
- Monitor token usage per prompt
- Optimize prompts to reduce token count
- Use cheaper models for simple tasks
- Enable semantic caching

---

## Migration Checklist

Use this checklist to track migration progress:

### Pre-Migration
- [ ] Read this entire guide
- [ ] Set up Portkey account and API keys
- [ ] Configure Portkey in `.env` file
- [ ] Test Portkey connection with sample prompt
- [ ] Review existing prompts in codebase

### During Migration
- [ ] Identify all prompts (see Prompt Inventory section)
- [ ] Document prompt specifications
- [ ] Create prompts in Portkey UI
- [ ] Test each prompt with sample inputs
- [ ] Update code to use Portkey prompt IDs
- [ ] Run unit tests for migrated code
- [ ] Compare outputs with original implementation

### Post-Migration
- [ ] Remove hardcoded prompts from code
- [ ] Update documentation
- [ ] Train team on Portkey usage
- [ ] Set up monitoring and alerts
- [ ] Configure cost budgets
- [ ] Archive old prompt code

---

## Next Steps

After completing this guide:

1. **Review Prompt Inventory**: Familiarize yourself with all prompts
2. **Prioritize Migration**: Start with high-traffic prompts
3. **Create Test Suite**: Ensure comprehensive testing
4. **Monitor Performance**: Track latency and costs in Portkey
5. **Iterate**: Optimize prompts based on real-world usage

---

## Appendix

### Portkey Prompt ID Naming Convention

Use consistent naming for Portkey Prompt IDs:

```
pp-[agent]-[function]-[version]

Examples:
- pp-maria-greeting-v1
- pp-document-analyzer-classification-v1
- pp-owl-eligibility-check-v2
```

### Environment Variables

Required environment variables for Portkey:

```bash
# Portkey Configuration
PORTKEY_API_KEY=your_portkey_api_key_here
PORTKEY_VIRTUAL_KEY_OPENAI=your_openai_virtual_key
PORTKEY_VIRTUAL_KEY_ANTHROPIC=your_anthropic_virtual_key
PORTKEY_VIRTUAL_KEY_GEMINI=your_gemini_virtual_key
```

### Useful Portkey CLI Commands

```bash
# Install Portkey CLI
pip install portkey-ai

# List all prompts
portkey prompts list

# Get prompt details
portkey prompts get pp-prompt-id-123

# Test prompt
portkey prompts test pp-prompt-id-123 --variables '{"var": "value"}'
```

---

**Document Version**: 1.0
**Last Updated**: January 2026
**Maintained By**: Backend Team
**Status**: 🚧 In Progress
