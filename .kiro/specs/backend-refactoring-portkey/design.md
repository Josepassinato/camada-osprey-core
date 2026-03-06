# Design Document

## Overview

This design document outlines the technical approach for refactoring the Osprey backend codebase into a well-organized, maintainable Python package structure while modernizing the LLM infrastructure with Portkey.ai integration.

### Goals

1. Transform flat backend structure into logical Python packages
2. Replace legacy OpenAI v1 and custom "Emergent" integrations with Portkey.ai
3. Establish observability, cost control, and multi-provider routing for all LLM calls
4. Update dependencies to latest stable versions (OpenAI v2, etc.)
5. Maintain backward compatibility and zero downtime during migration

### Non-Goals

- Rewriting business logic or changing API contracts
- Adding new features beyond the refactoring scope
- Migrating to a different web framework
- Changing database schema or data models

## Architecture

### Current State Analysis

The backend currently has:
- **70+ Python files** in flat structure at `backend/` root
- **Multiple LLM patterns**: Direct OpenAI v1, AsyncOpenAI, emergentintegrations, LiteLLM
- **Inconsistent imports**: Mix of absolute and relative imports
- **Scattered configuration**: API keys and settings throughout codebase
- **No LLM observability**: No centralized logging, cost tracking, or analytics
- **Legacy dependencies**: OpenAI v1, outdated packages

### Target State Architecture

```
backend/
├── server.py                    # Main FastAPI app (routes only)
├── config/                      # Configuration management
│   ├── __init__.py
│   ├── settings.py             # Pydantic settings
│   └── llm_config.py           # LLM provider configuration
├── core/                        # Existing core infrastructure
│   ├── auth.py
│   ├── database.py
│   ├── logging.py
│   ├── serialization.py
│   └── sentry.py
├── api/                         # Existing API routers (unchanged)
├── models/                      # Existing Pydantic models (unchanged)
├── llm/                         # NEW: LLM abstraction layer
│   ├── __init__.py
│   ├── portkey_client.py       # Portkey wrapper
│   ├── types.py                # LLM types and enums
│   └── exceptions.py           # LLM-specific exceptions
├── agents/                      # NEW: All AI agents
│   ├── __init__.py
│   ├── base.py                 # Base agent class
│   ├── maria/                  # Maria assistant
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── api.py
│   │   ├── voice.py
│   │   ├── whatsapp.py
│   │   └── gemini_chat.py
│   ├── dra_paula/              # Dra. Paula specialist
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── gemini_agent.py
│   │   ├── hybrid_agent.py
│   │   └── knowledge_base.py
│   ├── owl/                    # Owl intelligent agent
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── specialized/            # Specialized agents
│   │   ├── __init__.py
│   │   ├── coordinator.py
│   │   ├── document_validator.py
│   │   ├── form_validator.py
│   │   ├── eligibility_analyst.py
│   │   ├── compliance_checker.py
│   │   ├── letter_writer.py
│   │   ├── translator.py
│   │   └── triage.py
│   ├── qa/                     # QA agents
│   │   ├── __init__.py
│   │   ├── professional_qa.py
│   │   └── feedback_orchestrator.py
│   └── oracle/                 # Oracle consultant
│       ├── __init__.py
│       └── consultant.py
├── documents/                   # NEW: Document processing
│   ├── __init__.py
│   ├── analyzer.py             # document_analyzer_agent.py
│   ├── classifier.py           # document_classifier.py
│   ├── catalog.py              # document_catalog.py
│   ├── data_extractor.py       # document_data_extractor.py
│   ├── quality_checker.py      # document_quality_checker.py
│   ├── validation_database.py  # document_validation_database.py
│   ├── recognition.py          # enhanced_document_recognition.py
│   ├── consistency.py          # cross_document_consistency.py
│   ├── metrics.py              # document_analysis_metrics.py
│   └── validators/             # Specialized validators
│       ├── __init__.py
│       └── specialized.py      # specialized_document_validators.py
├── visa/                        # NEW: Visa processing
│   ├── __init__.py
│   ├── specifications.py       # visa_specifications.py
│   ├── document_mapping.py     # visa_document_mapping.py
│   ├── information.py          # visa_information_detailed.py
│   ├── auto_updater.py         # visa_auto_updater.py
│   ├── api.py                  # visa_api.py
│   └── directives.yaml         # visa_directive_guides_informative.yaml
├── forms/                       # NEW: USCIS forms
│   ├── __init__.py
│   ├── filler.py               # uscis_form_filler.py, form_filler_agent.py
│   ├── structures.py           # friendly_form_structures.py
│   ├── field_extraction.py     # field_extraction_engine.py
│   ├── i129_overlay.py         # i129_overlay_filler.py
│   └── debug/                  # Debug utilities
│       ├── __init__.py
│       ├── i129_fields.py
│       ├── i539_fields.py
│       └── pymupdf_fields.py
├── admin/                       # NEW: Admin functionality
│   ├── __init__.py
│   ├── security.py             # admin_security.py
│   ├── knowledge_base.py       # admin_knowledge_base.py
│   └── products.py             # admin_products.py
├── integrations/                # NEW: Third-party integrations
│   ├── __init__.py
│   ├── google/
│   │   ├── __init__.py
│   │   ├── document_ai.py      # google_document_ai_integration.py
│   │   └── vision.py           # (if exists)
│   ├── stripe/
│   │   ├── __init__.py
│   │   └── integration.py      # stripe_integration.py
│   └── resend/
│       ├── __init__.py
│       └── email.py            # (if exists)
├── utils/                       # NEW: Utilities
│   ├── __init__.py
│   ├── validators.py           # validators.py
│   ├── sanitizer.py            # input_sanitizer.py
│   ├── rate_limiter.py         # rate_limiter.py
│   └── translation/
│       ├── __init__.py
│       ├── agent.py            # translation_agent.py
│       ├── gate.py             # translation_gate.py
│       └── service.py          # translation_service.py
├── case/                        # NEW: Case management
│   ├── __init__.py
│   ├── finalizer.py            # case_finalizer.py
│   └── finalizer_complete.py   # case_finalizer_complete.py
├── compliance/                  # NEW: Compliance & legal
│   ├── __init__.py
│   ├── reviewer.py             # immigration_compliance_reviewer.py
│   ├── advanced_reviewer.py    # advanced_immigration_reviewer.py
│   ├── legal_rules.py          # immigration_legal_rules.py
│   ├── inadmissibility.py      # inadmissibility_screening.py
│   └── policy_engine.py        # policy_engine.py
├── knowledge/                   # NEW: Knowledge management
│   ├── __init__.py
│   ├── manager.py              # knowledge_base_manager.py
│   ├── helper.py               # agent_knowledge_helper.py
│   └── extraction.py           # extract_openai_assistant_knowledge.py
├── learning/                    # NEW: Learning systems
│   ├── __init__.py
│   ├── agent_learning.py       # agent_learning_system.py
│   ├── iterative_learning.py   # iterative_learning_system.py
│   └── feedback.py             # feedback_system.py
├── packages/                    # NEW: Package generation
│   ├── __init__.py
│   ├── generator.py            # package_generator.py
│   └── payment_packages.py     # payment_packages.py
├── voice/                       # NEW: Voice processing
│   ├── __init__.py
│   ├── agent.py                # voice_agent.py
│   └── websocket.py            # voice_websocket.py
├── services/                    # Existing services (unchanged)
├── scripts/                     # NEW: Utility scripts
│   ├── __init__.py
│   ├── create_admin_user.py
│   ├── create_superadmin.py
│   ├── create_test_admin.py
│   ├── create_stripe_coupon.py
│   ├── fix_indexes.py
│   └── mongodb_backup.py
└── policies/                    # Existing YAML policies (unchanged)
```

### Key Architectural Decisions

#### 1. Package Organization Strategy

**Decision**: Organize by domain/feature rather than by technical layer

**Rationale**:
- Improves discoverability (all document code in `documents/`)
- Reduces coupling between unrelated modules
- Aligns with Domain-Driven Design principles
- Makes testing easier (test documents together)

**Trade-offs**:
- Some cross-cutting concerns (like LLM calls) span multiple domains
- Need clear interfaces between packages
- Migration requires careful dependency analysis

#### 2. LLM Abstraction Layer

**Decision**: Create thin wrapper (`backend/llm/portkey_client.py`) over Portkey SDK

**Rationale**:
- Allows future provider switching (Helicone, OpenRouter)
- Centralizes LLM configuration and error handling
- Provides consistent interface across codebase
- Enables testing with mock LLM responses

**Trade-offs**:
- Additional abstraction layer adds complexity
- Must keep wrapper thin to avoid over-engineering
- Need to expose Portkey-specific features when needed

#### 3. Portkey Integration Approach

**Decision**: Use Portkey's OpenAI-compatible SDK with prompt management

**Rationale**:
- Minimal code changes (drop-in replacement for OpenAI client)
- Centralized prompt versioning and A/B testing
- Built-in observability and cost tracking
- Multi-provider routing without code changes

**Trade-offs**:
- Dependency on Portkey service availability
- Learning curve for prompt management UI
- Need fallback strategy if Portkey is down

## Components and Interfaces

### 1. LLM Client Abstraction (`backend/llm/portkey_client.py`)

```python
from typing import Optional, Dict, Any, List, AsyncIterator
from enum import Enum
import os
from portkey_ai import Portkey, PORTKEY_GATEWAY_URL

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "google"
    
class LLMClient:
    """Unified LLM client with Portkey integration"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        virtual_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.portkey = Portkey(
            api_key=api_key or os.getenv("PORTKEY_API_KEY"),
            virtual_key=virtual_key,
            config=config
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        prompt_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute chat completion with Portkey routing"""
        pass
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion responses"""
        pass
    
    async def completion_with_prompt(
        self,
        prompt_id: str,
        variables: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Execute completion using Portkey prompt template"""
        pass
```

### 2. Configuration Management (`backend/config/llm_config.py`)

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import os

class ModelConfig(BaseModel):
    name: str
    provider: str
    max_tokens: int = 4096
    temperature: float = 0.7
    fallback_models: List[str] = []
    cost_per_1k_tokens: float = 0.0

class LLMConfig(BaseModel):
    portkey_api_key: str = Field(default_factory=lambda: os.getenv("PORTKEY_API_KEY"))
    portkey_virtual_keys: Dict[str, str] = {}
    default_model: str = "gpt-4o"
    models: Dict[str, ModelConfig] = {}
    rate_limits: Dict[str, int] = {}
    cost_budget_daily: float = 100.0
    enable_caching: bool = True
    enable_fallbacks: bool = True
    
    class Config:
        env_prefix = "LLM_"

# Global config instance
llm_config = LLMConfig()
```

### 3. Agent Base Class (`backend/agents/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.llm.portkey_client import LLMClient

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        agent_name: str = "base_agent"
    ):
        self.llm_client = llm_client or LLMClient()
        self.agent_name = agent_name
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return result"""
        pass
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Helper method for LLM calls with error handling"""
        try:
            response = await self.llm_client.chat_completion(
                messages=messages,
                **kwargs
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LLM call failed in {self.agent_name}: {e}")
            raise
```

### 4. Document Processing Interface

```python
# backend/documents/__init__.py
from .analyzer import DocumentAnalyzer
from .classifier import DocumentClassifier
from .data_extractor import DocumentDataExtractor

__all__ = [
    "DocumentAnalyzer",
    "DocumentClassifier", 
    "DocumentDataExtractor"
]
```

### 5. Migration Compatibility Layer

To ensure zero downtime, we'll provide temporary compatibility imports:

```python
# backend/_compat.py (temporary during migration)
import warnings

def _deprecated_import(old_path: str, new_path: str):
    warnings.warn(
        f"{old_path} is deprecated. Use {new_path} instead.",
        DeprecationWarning,
        stacklevel=2
    )

# Example usage in old location
# backend/document_analyzer_agent.py (kept temporarily)
from backend.documents.analyzer import DocumentAnalyzer
from backend._compat import _deprecated_import

_deprecated_import(
    "backend.document_analyzer_agent",
    "backend.documents.analyzer"
)

# Re-export for backward compatibility
__all__ = ["DocumentAnalyzer"]
```

## Data Models

### LLM Request/Response Models

```python
# backend/llm/types.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    name: Optional[str] = None

class LLMRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    prompt_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    metadata: Dict[str, Any] = {}
```

### Prompt Metadata Model

```python
# backend/llm/types.py (continued)
class PromptMetadata(BaseModel):
    """Metadata for prompts migrated to Portkey"""
    prompt_id: str
    portkey_id: Optional[str] = None
    name: str
    description: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    variables: List[str] = []
    source_file: str
    source_line: int
    migrated: bool = False
    migration_date: Optional[str] = None
```

## Error Handling

### LLM-Specific Exceptions

```python
# backend/llm/exceptions.py
class LLMException(Exception):
    """Base exception for LLM operations"""
    pass

class LLMProviderError(LLMException):
    """Provider-specific error (OpenAI, Anthropic, etc.)"""
    pass

class LLMRateLimitError(LLMException):
    """Rate limit exceeded"""
    pass

class LLMCostLimitError(LLMException):
    """Cost budget exceeded"""
    pass

class LLMTimeoutError(LLMException):
    """Request timeout"""
    pass

class PromptNotFoundError(LLMException):
    """Portkey prompt ID not found"""
    pass
```

### Error Handling Strategy

1. **Retry Logic**: Automatic retries with exponential backoff for transient errors
2. **Fallback Models**: Automatic fallback to cheaper/faster models on failure
3. **Circuit Breaker**: Temporarily disable failing providers
4. **Graceful Degradation**: Return cached/default responses when LLM unavailable
5. **Detailed Logging**: Log all errors to Sentry with context

## Testing Strategy

### Unit Tests

```python
# tests/unit/llm/test_portkey_client.py
import pytest
from unittest.mock import AsyncMock, patch
from backend.llm.portkey_client import LLMClient

@pytest.mark.asyncio
async def test_chat_completion_success():
    client = LLMClient()
    with patch.object(client.portkey, 'chat_completion', new_callable=AsyncMock) as mock:
        mock.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        
        result = await client.chat_completion(
            messages=[{"role": "user", "content": "Test"}]
        )
        
        assert result["choices"][0]["message"]["content"] == "Test response"

@pytest.mark.asyncio
async def test_chat_completion_with_prompt_id():
    client = LLMClient()
    result = await client.completion_with_prompt(
        prompt_id="pp-test-123",
        variables={"name": "John"}
    )
    assert result is not None
```

### Integration Tests

```python
# tests/integration/test_agent_migration.py
import pytest
from backend.agents.maria.agent import MariaAgent
from backend.llm.portkey_client import LLMClient

@pytest.mark.asyncio
async def test_maria_agent_with_portkey():
    """Test Maria agent works with Portkey integration"""
    llm_client = LLMClient()
    maria = MariaAgent(llm_client=llm_client)
    
    result = await maria.process({
        "message": "What documents do I need for H1B?",
        "user_id": "test_user"
    })
    
    assert result["success"] is True
    assert "documents" in result["response"].lower()
```

### Migration Validation Tests

```python
# tests/migration/test_import_compatibility.py
def test_old_imports_still_work():
    """Ensure old import paths work during migration"""
    # Old import should work with deprecation warning
    with pytest.warns(DeprecationWarning):
        from backend.document_analyzer_agent import DocumentAnalyzer
    
    # New import should work without warning
    from backend.documents.analyzer import DocumentAnalyzer as NewAnalyzer
    
    # Both should be the same class
    assert DocumentAnalyzer is NewAnalyzer
```

## Migration Strategy

### Phase 1: Code Reorganization (Week 1-2)

**Objective**: Restructure codebase without changing functionality

**Steps**:
1. Create new package structure
2. Move files to new locations
3. Update all imports
4. Add compatibility shims
5. Run full test suite
6. Deploy to staging

**Success Criteria**:
- All tests pass
- No import errors
- API responses unchanged
- Performance metrics stable

### Phase 2: Portkey Integration (Week 3-4)

**Objective**: Replace LLM calls with Portkey

**Steps**:
1. Install Portkey SDK
2. Create LLM abstraction layer
3. Migrate one agent as proof-of-concept
4. Document prompt migration process
5. Migrate remaining agents incrementally
6. Remove emergent integrations
7. Update to OpenAI v2

**Success Criteria**:
- All LLM calls route through Portkey
- Observability dashboard shows all calls
- Cost tracking functional
- No emergent imports remain

### Phase 3: Testing & Validation (Week 5)

**Objective**: Comprehensive testing and documentation

**Steps**:
1. Run full regression test suite
2. Performance testing
3. Load testing
4. Security audit
5. Update all documentation
6. Create migration guide

**Success Criteria**:
- 100% test pass rate
- Performance within 5% of baseline
- No security vulnerabilities
- Documentation complete

### Phase 4: Production Deployment (Week 6)

**Objective**: Deploy to production with monitoring

**Steps**:
1. Deploy to staging
2. Smoke tests
3. Gradual rollout (10% → 50% → 100%)
4. Monitor metrics
5. Remove compatibility shims
6. Final cleanup

**Success Criteria**:
- Zero downtime
- No increase in error rates
- Cost tracking shows expected usage
- Team trained on new structure

## Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**: Revert to previous deployment (< 5 minutes)
2. **Partial Rollback**: Keep new structure, revert Portkey integration
3. **Compatibility Mode**: Re-enable compatibility shims
4. **Gradual Rollback**: Roll back one package at a time

## Monitoring & Observability

### Metrics to Track

1. **LLM Metrics** (via Portkey):
   - Request count by model
   - Average latency
   - Token usage
   - Cost per request
   - Error rates by provider
   - Cache hit rates

2. **Application Metrics**:
   - API response times
   - Error rates
   - Import resolution time
   - Memory usage

3. **Business Metrics**:
   - Daily LLM cost
   - Cost per user interaction
   - Model usage distribution

### Alerting

- LLM cost exceeds daily budget
- Error rate > 1%
- Latency > 5s (p95)
- Provider downtime
- Import errors

## Security Considerations

1. **API Key Management**:
   - Store Portkey API key in environment variables
   - Use Portkey virtual keys for different environments
   - Rotate keys quarterly

2. **Prompt Security**:
   - Review all prompts for injection vulnerabilities
   - Sanitize user inputs before LLM calls
   - Implement rate limiting per user

3. **Data Privacy**:
   - Ensure PII is not logged in Portkey
   - Configure data retention policies
   - Use Portkey's data residency options if needed

4. **Access Control**:
   - Restrict Portkey dashboard access
   - Audit prompt changes
   - Version control all prompts

## Performance Considerations

1. **Caching Strategy**:
   - Enable Portkey semantic caching
   - Cache common queries at application level
   - Set appropriate TTLs

2. **Async Operations**:
   - All LLM calls must be async
   - Use connection pooling
   - Implement request batching where possible

3. **Optimization**:
   - Use cheaper models for simple tasks
   - Implement streaming for long responses
   - Compress prompts to reduce token usage

## Documentation Updates Required

1. **REFACTORING_GUIDE.md**: Complete guide to new structure
2. **PROMPTS_TO_PORTKEY.md**: Prompt migration instructions
3. **backend/README.md**: Updated architecture documentation
4. **API_MIGRATION.md**: API changes (if any)
5. **DEPLOYMENT.md**: Updated deployment procedures
6. **Package READMEs**: One per new package explaining contents

## Dependencies

### New Dependencies

```txt
# Portkey AI SDK
portkey-ai>=1.0.0

# OpenAI v2 (updated)
openai>=2.0.0
```

### Removed Dependencies

```txt
# Remove emergent integrations
# emergentintegrations==0.1.0  # REMOVED
# emergentllm  # REMOVED (if exists)
```

### Updated Dependencies

All dependencies will be updated to latest stable versions as documented in requirements.txt with security patches applied.

## Success Metrics

1. **Code Quality**:
   - Reduced cyclomatic complexity
   - Improved test coverage (target: 80%+)
   - Zero linting errors

2. **Maintainability**:
   - Average time to locate code: < 30 seconds
   - New developer onboarding time: < 2 hours
   - Code review time: -30%

3. **Observability**:
   - 100% LLM calls visible in Portkey
   - Cost attribution by feature
   - Real-time error tracking

4. **Performance**:
   - API latency unchanged (±5%)
   - LLM response time: -10% (via caching)
   - Memory usage: -15% (better imports)

5. **Cost**:
   - LLM cost visibility: 100%
   - Cost optimization opportunities identified
   - Budget alerts functional
