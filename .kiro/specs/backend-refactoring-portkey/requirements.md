# Requirements Document

## Introduction

This specification outlines the comprehensive refactoring and modernization of the Osprey backend codebase. The project addresses three critical areas:

1. **Code Organization**: Restructure the flat backend directory into a proper Python package hierarchy with logical module groupings
2. **LLM Infrastructure Modernization**: Replace legacy OpenAI v1 API calls and raw prompts with Portkey.ai for observability, cost control, and multi-provider routing
3. **Dependency Management**: Update to OpenAI v2 API, remove unused dependencies, and ensure all packages are current

The current backend has ~70 Python files in a flat structure with inconsistent patterns, making maintenance difficult. Multiple LLM integrations (OpenAI, Gemini, custom "Emergent" wrappers) lack observability and cost controls. This refactoring will establish a maintainable, observable, and cost-effective foundation for future development.

## Requirements

### Requirement 1: Backend Code Reorganization

**User Story:** As a backend developer, I want the codebase organized into logical Python packages and modules, so that I can easily locate, maintain, and extend functionality.

#### Acceptance Criteria

1. WHEN examining the backend directory THEN all Python files SHALL be organized into domain-specific packages under `backend/`
2. WHEN looking for document-related code THEN all `document_*.py` files SHALL be consolidated into `backend/documents/` package
3. WHEN looking for agent code THEN all agent files (maria_*, *_agent.py, specialized_agents.py, etc.) SHALL be organized into `backend/agents/` with sub-packages per agent type
4. WHEN looking for visa-related code THEN all visa_*.py files SHALL be consolidated into `backend/visa/` package
5. WHEN looking for form-related code THEN all form and USCIS files SHALL be organized into `backend/forms/` package
6. WHEN looking for admin functionality THEN all admin_*.py files SHALL be consolidated into `backend/admin/` package
7. WHEN looking for utility code THEN all utility files (validators, sanitizers, rate limiters, etc.) SHALL be organized into `backend/utils/` package
8. WHEN looking for integration code THEN all third-party integrations SHALL be organized into `backend/integrations/` package
9. WHEN a module is moved THEN all import statements across the codebase SHALL be updated to reflect the new location
10. WHEN a package is created THEN it SHALL include a proper `__init__.py` file with appropriate exports
11. WHEN examining any package THEN it SHALL follow Python package best practices (flat is better than nested, clear naming, single responsibility)
12. WHEN examining the root backend directory THEN it SHALL only contain `server.py`, configuration files, and package directories

### Requirement 2: Portkey.ai Integration

**User Story:** As a platform operator, I want all LLM calls routed through Portkey.ai, so that I have observability, cost control, prompt versioning, and multi-provider routing capabilities.

#### Acceptance Criteria

1. WHEN making any LLM API call THEN it SHALL be routed through Portkey.ai gateway
2. WHEN using OpenAI models THEN the code SHALL use OpenAI v2 API specification through Portkey
3. WHEN using Gemini models THEN the code SHALL be routed through Portkey's unified interface
4. WHEN a prompt is used THEN it SHALL be managed in Portkey's Prompt Engineering Studio (not hardcoded)
5. WHEN examining LLM code THEN there SHALL be NO direct OpenAI v1 API calls (openai.ChatCompletion.create, etc.)
6. WHEN examining LLM code THEN there SHALL be NO "emergentintegrations" or "emergentllm" imports
7. WHEN examining LLM code THEN all prompts SHALL reference Portkey prompt IDs or use Portkey's prompt API
8. WHEN a Portkey call fails THEN it SHALL include proper error handling and fallback logic
9. WHEN examining the codebase THEN there SHALL be a thin abstraction layer (`backend/llm/portkey_client.py`) wrapping Portkey for future flexibility
10. WHEN switching LLM providers THEN it SHALL be configurable through Portkey routing without code changes
11. WHEN examining logs THEN all LLM calls SHALL be traceable through Portkey's observability dashboard
12. WHEN examining costs THEN all LLM usage SHALL be tracked and reportable through Portkey analytics

### Requirement 3: Prompt Migration Documentation

**User Story:** As a developer migrating prompts, I want clear documentation on how to recreate each prompt in Portkey, so that I can accurately migrate all system prompts without losing functionality.

#### Acceptance Criteria

1. WHEN migrating prompts THEN there SHALL be a `PROMPTS_TO_PORTKEY.md` document in the backend root
2. WHEN examining the migration document THEN it SHALL list every prompt currently in the codebase with its location
3. WHEN examining each prompt entry THEN it SHALL specify the recommended model (GPT-4o, GPT-4-turbo, Gemini 1.5 Pro, etc.)
4. WHEN examining each prompt entry THEN it SHALL specify the message types (system, user, assistant, developer)
5. WHEN examining each prompt entry THEN it SHALL include the full prompt text or reference to source file
6. WHEN examining each prompt entry THEN it SHALL specify any variables/parameters used in the prompt
7. WHEN examining each prompt entry THEN it SHALL include configuration settings (temperature, max_tokens, etc.)
8. WHEN examining each prompt entry THEN it SHALL specify the expected response format (JSON, text, structured output)
9. WHEN examining each prompt entry THEN it SHALL include step-by-step instructions for creating it in Portkey UI
10. WHEN examining each prompt entry THEN it SHALL include the Portkey prompt ID once created (for tracking)
11. WHEN examining the migration document THEN it SHALL include links to relevant Portkey documentation
12. WHEN examining the migration document THEN it SHALL include examples of before/after code for common patterns

### Requirement 4: Dependency Management

**User Story:** As a backend developer, I want clean, up-to-date dependencies with no unused packages, so that the application is secure, maintainable, and has minimal attack surface.

#### Acceptance Criteria

1. WHEN examining requirements.txt THEN it SHALL use OpenAI v2 API (openai>=2.0.0)
2. WHEN examining requirements.txt THEN it SHALL include portkey-ai package
3. WHEN examining requirements.txt THEN it SHALL NOT include emergentintegrations or emergentllm
4. WHEN examining requirements.txt THEN all packages SHALL be at their latest stable versions (as of January 2026)
5. WHEN examining requirements.txt THEN unused packages SHALL be removed
6. WHEN examining requirements.txt THEN each package SHALL have a comment explaining its purpose
7. WHEN examining requirements.txt THEN packages SHALL be organized into logical sections
8. WHEN running pip-audit THEN there SHALL be NO known security vulnerabilities
9. WHEN examining package versions THEN they SHALL be compatible with each other (no dependency conflicts)
10. WHEN examining the codebase THEN all imports SHALL correspond to packages in requirements.txt

### Requirement 5: Import Path Updates

**User Story:** As a developer, I want all import statements updated to reflect the new package structure, so that the application runs without import errors after refactoring.

#### Acceptance Criteria

1. WHEN a module is moved THEN all absolute imports SHALL be updated (e.g., `from backend.documents.analyzer import DocumentAnalyzer`)
2. WHEN a module is moved THEN all relative imports SHALL be updated appropriately
3. WHEN examining any Python file THEN it SHALL NOT have broken imports
4. WHEN running the application THEN there SHALL be NO ImportError exceptions
5. WHEN running tests THEN all imports SHALL resolve correctly
6. WHEN examining imports THEN they SHALL follow Python best practices (absolute imports preferred)
7. WHEN examining imports THEN circular dependencies SHALL be avoided
8. WHEN examining imports THEN unused imports SHALL be removed
9. WHEN examining `__init__.py` files THEN they SHALL export the appropriate public API
10. WHEN examining imports THEN they SHALL be organized (stdlib, third-party, local) per PEP 8

### Requirement 6: Documentation Updates

**User Story:** As a developer, I want updated documentation reflecting the new structure, so that I can understand the codebase organization and find what I need.

#### Acceptance Criteria

1. WHEN examining the backend THEN there SHALL be a `REFACTORING_GUIDE.md` documenting the new structure
2. WHEN examining the refactoring guide THEN it SHALL include a directory tree showing the new organization
3. WHEN examining the refactoring guide THEN it SHALL explain the purpose of each package
4. WHEN examining the refactoring guide THEN it SHALL include migration notes for developers
5. WHEN examining each package THEN it SHALL have a README.md explaining its contents
6. WHEN examining backend/README.md THEN it SHALL be updated to reflect the new structure
7. WHEN examining module docstrings THEN they SHALL be updated if the module's purpose changed
8. WHEN examining the documentation THEN it SHALL include examples of the new import paths
9. WHEN examining the documentation THEN it SHALL include Portkey integration examples
10. WHEN examining the documentation THEN it SHALL reference the PROMPTS_TO_PORTKEY.md guide

### Requirement 7: Backward Compatibility & Testing

**User Story:** As a platform operator, I want the refactoring to maintain backward compatibility where possible and include comprehensive testing, so that existing functionality is not broken.

#### Acceptance Criteria

1. WHEN the refactoring is complete THEN all existing API endpoints SHALL continue to work
2. WHEN the refactoring is complete THEN all existing tests SHALL pass (after import updates)
3. WHEN examining the codebase THEN deprecated import paths MAY have compatibility shims with deprecation warnings
4. WHEN running the application THEN it SHALL start without errors
5. WHEN making API calls THEN responses SHALL match the existing API contract
6. WHEN examining test coverage THEN it SHALL NOT decrease from the current baseline
7. WHEN examining the codebase THEN breaking changes SHALL be documented in CHANGELOG.md
8. WHEN deploying THEN there SHALL be a rollback plan documented
9. WHEN examining the migration THEN it SHALL be possible to do incrementally (not all-at-once)
10. WHEN examining the codebase THEN any breaking changes SHALL be clearly marked with TODO comments

### Requirement 8: Portkey Abstraction Layer

**User Story:** As a platform architect, I want a thin abstraction layer over Portkey, so that we can switch to alternative providers (Helicone, OpenRouter) in the future without rewriting all LLM code.

#### Acceptance Criteria

1. WHEN examining the codebase THEN there SHALL be a `backend/llm/` package
2. WHEN examining backend/llm/ THEN it SHALL contain `portkey_client.py` with a unified LLM client interface
3. WHEN examining the client interface THEN it SHALL abstract common operations (chat, completion, streaming, embeddings)
4. WHEN examining the client interface THEN it SHALL accept provider-agnostic parameters
5. WHEN examining the client interface THEN it SHALL handle Portkey-specific features (prompt IDs, routing, caching)
6. WHEN examining the client interface THEN it SHALL include proper type hints
7. WHEN examining the client interface THEN it SHALL include comprehensive error handling
8. WHEN examining the client interface THEN it SHALL support async operations
9. WHEN examining the codebase THEN all LLM calls SHALL go through this abstraction layer
10. WHEN switching providers THEN only the `portkey_client.py` implementation SHALL need changes
11. WHEN examining the abstraction THEN it SHALL include configuration management (API keys, base URLs, etc.)
12. WHEN examining the abstraction THEN it SHALL include logging and metrics collection

### Requirement 9: Configuration Management

**User Story:** As a DevOps engineer, I want LLM provider configuration centralized and environment-based, so that I can easily manage different configurations across environments.

#### Acceptance Criteria

1. WHEN examining configuration THEN Portkey API keys SHALL be in environment variables
2. WHEN examining configuration THEN there SHALL be a `backend/config/llm_config.py` for LLM settings
3. WHEN examining LLM config THEN it SHALL include provider routing rules
4. WHEN examining LLM config THEN it SHALL include model fallback chains
5. WHEN examining LLM config THEN it SHALL include rate limiting settings
6. WHEN examining LLM config THEN it SHALL include cost budgets per model
7. WHEN examining LLM config THEN it SHALL support environment-specific overrides (dev, staging, prod)
8. WHEN examining .env.example THEN it SHALL include all required Portkey configuration variables
9. WHEN examining the codebase THEN there SHALL be NO hardcoded API keys or configuration
10. WHEN examining configuration THEN it SHALL be validated at startup with clear error messages

### Requirement 10: Migration Execution Plan

**User Story:** As a project manager, I want a clear execution plan for the migration, so that we can track progress and minimize disruption.

#### Acceptance Criteria

1. WHEN examining the spec THEN there SHALL be a phased migration plan in the tasks document
2. WHEN examining the plan THEN Phase 1 SHALL focus on code reorganization
3. WHEN examining the plan THEN Phase 2 SHALL focus on Portkey integration
4. WHEN examining the plan THEN Phase 3 SHALL focus on testing and validation
5. WHEN examining the plan THEN each phase SHALL be independently deployable
6. WHEN examining the plan THEN there SHALL be rollback procedures for each phase
7. WHEN examining the plan THEN there SHALL be success criteria for each phase
8. WHEN examining the plan THEN there SHALL be estimated effort for each task
9. WHEN examining the plan THEN there SHALL be dependencies between tasks clearly marked
10. WHEN examining the plan THEN there SHALL be a final validation checklist before production deployment
