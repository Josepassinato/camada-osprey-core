# Implementation Plan

This implementation plan breaks down the backend refactoring and Portkey integration into discrete, manageable coding tasks. Each task builds incrementally on previous work and includes specific requirements references.

## Phase 1: Foundation & Package Structure

- [x] 1. Create new package directory structure

  - Create all new package directories under `backend/`
  - Create `__init__.py` files for each package
  - Add package-level docstrings explaining purpose
  - _Requirements: 1.1, 1.10, 1.11_

- [x] 2. Set up configuration management

  - [x] 2.1 Create `backend/config/` package

    - Create `backend/config/__init__.py`
    - Create `backend/config/settings.py` with Pydantic BaseSettings
    - Create `backend/config/llm_config.py` with LLM configuration models
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

  - [x] 2.2 Update environment configuration
    - Update `.env.example` with Portkey configuration variables
    - Add validation for required environment variables at startup
    - Document all configuration options
    - _Requirements: 9.8, 9.9, 9.10_

- [x] 3. Create LLM abstraction layer

  - [x] 3.1 Create `backend/llm/` package structure

    - Create `backend/llm/__init__.py`
    - Create `backend/llm/types.py` with LLM data models (MessageRole, ChatMessage, LLMRequest, LLMResponse, PromptMetadata)
    - Create `backend/llm/exceptions.py` with LLM-specific exceptions
    - _Requirements: 8.1, 8.2, 8.6_

  - [x] 3.2 Implement Portkey client wrapper

    - Create `backend/llm/portkey_client.py` with LLMClient class
    - Implement `chat_completion()` method with error handling
    - Implement `stream_completion()` method for streaming responses
    - Implement `completion_with_prompt()` for Portkey prompt templates
    - Add retry logic with exponential backoff
    - Add circuit breaker for failing providers
    - _Requirements: 2.1, 2.8, 8.3, 8.4, 8.7, 8.8, 8.11_

  - [x] 3.3 Add LLM client configuration and helpers
    - Implement provider routing logic
    - Implement fallback model chains
    - Add caching support
    - Add logging and metrics collection
    - _Requirements: 2.10, 8.9, 8.12_

- [x] 4. Create base agent class
  - Create `backend/agents/base.py` with BaseAgent abstract class
  - Implement `_call_llm()` helper method with error handling
  - Add agent-level logging and metrics
  - _Requirements: 8.3, 8.4_

## Phase 2: Document Processing Migration

- [x] 5. Migrate document processing modules

  - [x] 5.1 Create documents package structure

    - Create `backend/documents/__init__.py` with public API exports
    - Create `backend/documents/validators/` sub-package
    - _Requirements: 1.2, 1.10_

  - [x] 5.2 Move and refactor document analyzer

    - Move `document_analyzer_agent.py` to `backend/documents/analyzer.py`
    - Update class to inherit from BaseAgent
    - Replace direct LLM calls with LLMClient
    - Update all imports within the file
    - _Requirements: 1.2, 2.1, 5.1_

  - [x] 5.3 Move and refactor document classifier

    - Move `document_classifier.py` to `backend/documents/classifier.py`
    - Update LLM calls to use LLMClient
    - Update imports
    - _Requirements: 1.2, 2.1, 5.1_

  - [x] 5.4 Move remaining document modules

    - Move `document_catalog.py` to `backend/documents/catalog.py`
    - Move `document_data_extractor.py` to `backend/documents/data_extractor.py`
    - Move `document_quality_checker.py` to `backend/documents/quality_checker.py`
    - Move `document_validation_database.py` to `backend/documents/validation_database.py`
    - Move `enhanced_document_recognition.py` to `backend/documents/recognition.py`
    - Move `cross_document_consistency.py` to `backend/documents/consistency.py`
    - Move `document_analysis_metrics.py` to `backend/documents/metrics.py`
    - Update all imports in moved files
    - _Requirements: 1.2, 5.1_

  - [x] 5.5 Move specialized document validators
    - Move `specialized_document_validators.py` to `backend/documents/validators/specialized.py`
    - Update imports
    - _Requirements: 1.2, 5.1_

- [x] 6. Update document-related imports across codebase
  - Search for all imports of document modules
  - Update to new package paths (e.g., `from backend.documents.analyzer import DocumentAnalyzer`)
  - Test that all imports resolve correctly
  - _Requirements: 5.1, 5.2, 5.4, 5.8_

## Phase 3: Agent Migration

- [x] 7. Migrate Maria agent

  - [x] 7.1 Create Maria package structure

    - Create `backend/agents/maria/` package
    - Create `backend/agents/maria/__init__.py`
    - _Requirements: 1.3, 1.10_

  - [x] 7.2 Move Maria modules

    - Move `maria_agent.py` to `backend/agents/maria/agent.py`
    - Move `maria_api.py` to `backend/agents/maria/api.py`
    - Move `maria_voice.py` to `backend/agents/maria/voice.py`
    - Move `maria_whatsapp.py` to `backend/agents/maria/whatsapp.py`
    - Move `maria_gemini_chat.py` to `backend/agents/maria/gemini_chat.py`
    - Update all imports in moved files
    - _Requirements: 1.3, 5.1_

  - [x] 7.3 Refactor Maria agent to use LLMClient
    - Update MariaAgent to inherit from BaseAgent
    - Replace all direct OpenAI/Gemini calls with LLMClient
    - Remove emergentintegrations imports
    - Update error handling
    - _Requirements: 2.1, 2.5, 2.6, 8.9_

- [x] 8. Migrate Dra. Paula agents

  - [x] 8.1 Create Dra. Paula package

    - Create `backend/agents/dra_paula/` package
    - Create `backend/agents/dra_paula/__init__.py`
    - _Requirements: 1.3, 1.10_

  - [x] 8.2 Move Dra. Paula modules

    - Move `gemini_dra_paula_agent.py` to `backend/agents/dra_paula/gemini_agent.py`
    - Move `hybrid_dra_paula_agent.py` to `backend/agents/dra_paula/hybrid_agent.py`
    - Move `dra_paula_knowledge_base.py` to `backend/agents/dra_paula/knowledge_base.py`
    - Update imports
    - _Requirements: 1.3, 5.1_

  - [x] 8.3 Refactor Dra. Paula agents to use LLMClient
    - Update all agents to inherit from BaseAgent
    - Replace direct LLM calls with LLMClient
    - Remove emergentintegrations imports
    - _Requirements: 2.1, 2.5, 2.6, 8.9_

- [x] 9. Migrate Owl agent

  - [x] 9.1 Create Owl package

    - Create `backend/agents/owl/` package
    - Create `backend/agents/owl/__init__.py`
    - _Requirements: 1.3, 1.10_

  - [x] 9.2 Move and refactor Owl agent
    - Move `intelligent_owl_agent.py` to `backend/agents/owl/agent.py`
    - Update to inherit from BaseAgent
    - Replace emergentintegrations with LLMClient
    - Remove EMERGENT_LLM_KEY references
    - Update imports
    - _Requirements: 1.3, 2.1, 2.5, 2.6, 5.1_

- [x] 10. Migrate specialized agents

  - [x] 10.1 Create specialized agents package

    - Create `backend/agents/specialized/` package
    - Create `backend/agents/specialized/__init__.py`
    - _Requirements: 1.3, 1.10_

  - [x] 10.2 Refactor specialized_agents.py
    - Move `specialized_agents.py` to `backend/agents/specialized/coordinator.py`
    - Extract individual agents into separate files:
      - `document_validator.py`
      - `form_validator.py`
      - `eligibility_analyst.py`
      - `compliance_checker.py`
      - `letter_writer.py`
      - `translator.py`
      - `triage.py`
    - Update all agents to use LLMClient
    - Remove emergentintegrations imports
    - _Requirements: 1.3, 2.1, 2.5, 2.6, 5.1_

- [x] 11. Migrate QA agents

  - [x] 11.1 Create QA package

    - Create `backend/agents/qa/` package
    - Create `backend/agents/qa/__init__.py`
    - _Requirements: 1.3, 1.10_

  - [x] 11.2 Move QA modules
    - Move `professional_qa_agent.py` to `backend/agents/qa/professional_qa.py`
    - Move `qa_feedback_orchestrator.py` to `backend/agents/qa/feedback_orchestrator.py`
    - Update to use LLMClient
    - Update imports
    - _Requirements: 1.3, 2.1, 5.1_

- [x] 12. Migrate Oracle consultant

  - Create `backend/agents/oracle/` package
  - Move `oracle_consultant.py` to `backend/agents/oracle/consultant.py`
  - Update to use LLMClient
  - Update imports
  - _Requirements: 1.3, 2.1, 5.1_

- [x] 13. Migrate immigration expert

  - Move `immigration_expert.py` to `backend/agents/immigration_expert.py`
  - Update to use LLMClient
  - Remove emergentintegrations imports
  - Update imports
  - _Requirements: 1.3, 2.1, 2.5, 2.6, 5.1_

- [x] 14. Update agent-related imports across codebase
  - Search for all imports of agent modules
  - Update to new package paths
  - Test that all imports resolve correctly
  - _Requirements: 5.1, 5.2, 5.4, 5.8_

## Phase 4: Visa Processing Migration

- [x] 15. Migrate visa modules

  - [x] 15.1 Create visa package

    - Create `backend/visa/` package
    - Create `backend/visa/__init__.py`
    - _Requirements: 1.4, 1.10_

  - [x] 15.2 Move visa modules

    - Move `visa_specifications.py` to `backend/visa/specifications.py`
    - Move `visa_document_mapping.py` to `backend/visa/document_mapping.py`
    - Move `visa_information_detailed.py` to `backend/visa/information.py`
    - Move `visa_api.py` to `backend/visa/api.py`
    - Move `visa_directive_guides_informative.yaml` to `backend/visa/directives.yaml`
    - Update imports
    - _Requirements: 1.4, 5.1_

  - [x] 15.3 Refactor visa auto-updater
    - Move `visa_auto_updater.py` to `backend/visa/auto_updater.py`
    - Update to use LLMClient
    - Remove emergentintegrations imports
    - Update imports
    - _Requirements: 1.4, 2.1, 2.6, 5.1_

- [x] 16. Update visa-related imports across codebase
  - Search for all imports of visa modules ✅
  - Update to new package paths ✅
  - Test that all imports resolve correctly ✅
  - _Requirements: 5.1, 5.2, 5.4, 5.8_
  - **Completed**: Updated `backend/enhanced_document_recognition.py`, verified all 10 files using visa imports have correct `backend.visa.*` paths, confirmed no old-style imports remain

## Phase 5: Forms & USCIS Migration

- [x] 17. Migrate form modules

  - [x] 17.1 Create forms package

    - Create `backend/forms/` package
    - Create `backend/forms/__init__.py`
    - Create `backend/forms/debug/` sub-package
    - _Requirements: 1.5, 1.10_

  - [x] 17.2 Move form modules

    - Move `uscis_form_filler.py` to `backend/forms/filler.py`
    - Move `form_filler_agent.py` code into `backend/forms/filler.py` (merge if duplicate)
    - Move `friendly_form_structures.py` to `backend/forms/structures.py`
    - Move `field_extraction_engine.py` to `backend/forms/field_extraction.py`
    - Move `i129_overlay_filler.py` to `backend/forms/i129_overlay.py`
    - Update imports
    - _Requirements: 1.5, 5.1_

  - [x] 17.3 Move form debug utilities
    - Move `debug_i129_fields.py` to `backend/forms/debug/i129_fields.py`
    - Move `debug_i539_fields.py` to `backend/forms/debug/i539_fields.py`
    - Move `debug_pymupdf_fields.py` to `backend/forms/debug/pymupdf_fields.py`
    - Update imports
    - _Requirements: 1.5, 5.1_

- [x] 18. Update form-related imports across codebase
  - Search for all imports of form modules
  - Update to new package paths
  - Test that all imports resolve correctly
  - _Requirements: 5.1, 5.2, 5.4, 5.8_

## Phase 6: Remaining Modules Migration

- [x] 19. Migrate admin modules

  - Create `backend/admin/` package
  - Move `admin_security.py` to `backend/admin/security.py`
  - Move `admin_knowledge_base.py` to `backend/admin/knowledge_base.py`
  - Move `admin_products.py` to `backend/admin/products.py`
  - Update imports
  - _Requirements: 1.6, 5.1_

- [x] 20. Migrate integration modules

  - [x] 20.1 Create integrations package structure

    - Create `backend/integrations/` package
    - Create `backend/integrations/google/` sub-package
    - Create `backend/integrations/stripe/` sub-package
    - _Requirements: 1.8, 1.10_

  - [x] 20.2 Move integration modules
    - Move `google_document_ai_integration.py` to `backend/integrations/google/document_ai.py`
    - Move `stripe_integration.py` to `backend/integrations/stripe/integration.py`
    - Update imports
    - _Requirements: 1.8, 5.1_

- [x] 21. Migrate utility modules

  - [x] 21.1 Create utils package structure

    - Create `backend/utils/` package
    - Create `backend/utils/translation/` sub-package
    - _Requirements: 1.7, 1.10_

  - [x] 21.2 Move utility modules
    - Move `validators.py` to `backend/utils/validators.py`
    - Move `input_sanitizer.py` to `backend/utils/sanitizer.py`
    - Move `rate_limiter.py` to `backend/utils/rate_limiter.py`
    - Move `translation_agent.py` to `backend/utils/translation/agent.py`
    - Move `translation_gate.py` to `backend/utils/translation/gate.py`
    - Move `translation_service.py` to `backend/utils/translation/service.py`
    - Update imports
    - _Requirements: 1.7, 5.1_

- [x] 22. Migrate case management modules

  - Create `backend/case/` package
  - Move `case_finalizer.py` to `backend/case/finalizer.py`
  - Move `case_finalizer_complete.py` to `backend/case/finalizer_complete.py`
  - Update imports
  - _Requirements: 1.11, 5.1_

- [x] 23. Migrate compliance modules

  - Create `backend/compliance/` package
  - Move `immigration_compliance_reviewer.py` to `backend/compliance/reviewer.py`
  - Move `advanced_immigration_reviewer.py` to `backend/compliance/advanced_reviewer.py`
  - Move `immigration_legal_rules.py` to `backend/compliance/legal_rules.py`
  - Move `inadmissibility_screening.py` to `backend/compliance/inadmissibility.py`
  - Move `policy_engine.py` to `backend/compliance/policy_engine.py`
  - Update imports
  - _Requirements: 1.11, 5.1_

- [x] 24. Migrate knowledge management modules

  - Create `backend/knowledge/` package
  - Move `knowledge_base_manager.py` to `backend/knowledge/manager.py`
  - Move `agent_knowledge_helper.py` to `backend/knowledge/helper.py`
  - Move `extract_openai_assistant_knowledge.py` to `backend/knowledge/extraction.py`
  - Update imports
  - _Requirements: 1.11, 5.1_

- [x] 25. Migrate learning system modules

  - Create `backend/learning/` package
  - Move `agent_learning_system.py` to `backend/learning/agent_learning.py`
  - Move `iterative_learning_system.py` to `backend/learning/iterative_learning.py`
  - Move `feedback_system.py` to `backend/learning/feedback.py`
  - Update imports
  - _Requirements: 1.11, 5.1_

- [x] 26. Migrate package generation modules

  - Create `backend/packages/` package
  - Move `package_generator.py` to `backend/packages/generator.py`
  - Move `payment_packages.py` to `backend/packages/payment_packages.py`
  - Update imports
  - _Requirements: 1.11, 5.1_

- [x] 27. Migrate voice processing modules

  - Create `backend/voice/` package
  - Move `voice_agent.py` to `backend/voice/agent.py`
  - Move `voice_websocket.py` to `backend/voice/websocket.py`
  - Update imports
  - _Requirements: 1.11, 5.1_

- [x] 28. Migrate utility scripts

  - Create `backend/scripts/` package
  - Move `create_admin_user.py` to `backend/scripts/create_admin_user.py`
  - Move `create_superadmin.py` to `backend/scripts/create_superadmin.py`
  - Move `create_test_admin.py` to `backend/scripts/create_test_admin.py`
  - Move `create_stripe_coupon.py` to `backend/scripts/create_stripe_coupon.py`
  - Move `fix_indexes.py` to `backend/scripts/fix_indexes.py`
  - Move `mongodb_backup.py` to `backend/scripts/mongodb_backup.py`
  - Update imports
  - _Requirements: 1.11, 5.1_

- [x] 29. Migrate remaining standalone modules
  - Move `completeness_analyzer.py` to appropriate package (likely `backend/case/`)
  - Move `conversational_assistant.py` to appropriate package (likely `backend/agents/`)
  - Move `adaptive_texts.py` to `backend/utils/`
  - Move `ai_guardrails.py` to `backend/llm/`
  - Move `proactive_alerts.py` to `backend/utils/`
  - Move `social_proof_system.py` to `backend/utils/`
  - Move `voucher_system.py` to `backend/utils/`
  - Update imports
  - _Requirements: 1.11, 5.1_

## Phase 7: Prompt Migration to Portkey

- [x] 30. Audit and document all prompts

  - [x] 30.1 Create prompt migration document

    - Create `backend/PROMPTS_TO_PORTKEY.md`
    - Add document structure and introduction
    - Add links to Portkey documentation
    - _Requirements: 3.1, 3.11_

  - [x] 30.2 Identify all prompts in codebase

    - Search for all hardcoded prompts in Python files
    - Search for system messages in LLM calls
    - Document each prompt with location, purpose, and parameters
    - _Requirements: 3.2, 3.3_

  - [x] 30.3 Document prompt specifications

    - For each prompt, document:
      - Recommended model (GPT-4o, Gemini, etc.)
      - Message types (system, user, assistant)
      - Variables/parameters
      - Configuration (temperature, max_tokens)
      - Expected response format
    - _Requirements: 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [x] 30.4 Create Portkey migration instructions
    - Write step-by-step instructions for creating prompts in Portkey UI
    - Include screenshots or examples
    - Document before/after code patterns
    - _Requirements: 3.9, 3.12_

- [ ] 31. Migrate prompts to Portkey

  - [ ] 31.1 Create prompts in Portkey UI

    - Create each documented prompt in Portkey Prompt Engineering Studio
    - Test each prompt with sample inputs
    - Record Portkey prompt IDs
    - _Requirements: 2.4, 3.10_

  - [ ] 31.2 Update code to use Portkey prompts

    - Replace hardcoded prompts with Portkey prompt IDs
    - Use `completion_with_prompt()` method
    - Update variable passing
    - _Requirements: 2.4, 2.7_

  - [ ] 31.3 Test prompt migrations
    - Test each migrated prompt with real data
    - Compare outputs with original prompts
    - Adjust prompts in Portkey if needed
    - _Requirements: 2.4, 7.2_

## Phase 8: Dependency Management

- [x] 32. Update requirements.txt

  - [x] 32.1 Add new dependencies

    - Add `portkey-ai>=1.0.0`
    - Update `openai>=2.0.0`
    - _Requirements: 4.2, 4.1_

  - [x] 32.2 Remove unused dependencies

    - Remove emergentintegrations references
    - Remove emergentllm references
    - Identify and remove other unused packages
    - _Requirements: 4.3, 4.5_

  - [x] 32.3 Update existing dependencies

    - Update all packages to latest stable versions
    - Ensure compatibility between packages
    - Run pip-audit to check for vulnerabilities
    - _Requirements: 4.4, 4.8, 4.9_

  - [x] 32.4 Document dependencies
    - Add/update comments explaining each package's purpose
    - Organize into logical sections
    - _Requirements: 4.6, 4.7_

- [x] 33. Update OpenAI v2 API usage
  - Search for OpenAI v1 API patterns (openai.ChatCompletion.create, etc.)
  - Update to OpenAI v2 patterns (client.chat.completions.create)
  - Test all updated code
  - _Requirements: 2.2, 2.5_

## Phase 9: Testing & Validation

- [ ] 34. Create unit tests for new components

  - [ ] 34.1 Test LLM client

    - Write tests for `portkey_client.py`
    - Test chat completion, streaming, prompt-based completion
    - Test error handling and retries
    - Test fallback logic
    - _Requirements: 7.2, 8.3, 8.4_

  - [ ] 34.2 Test base agent

    - Write tests for `BaseAgent` class
    - Test LLM call helper methods
    - Test error handling
    - _Requirements: 7.2_

  - [ ] 34.3 Test configuration
    - Write tests for `llm_config.py`
    - Test environment variable loading
    - Test validation
    - _Requirements: 7.2, 9.10_

- [ ] 35. Create integration tests

  - [ ] 35.1 Test agent migrations

    - Test Maria agent with Portkey
    - Test Dra. Paula agents with Portkey
    - Test Owl agent with Portkey
    - Test specialized agents with Portkey
    - _Requirements: 7.2, 7.5_

  - [ ] 35.2 Test end-to-end flows
    - Test document upload and analysis
    - Test form filling
    - Test visa application flow
    - _Requirements: 7.2, 7.5_

- [ ] 36. Create migration validation tests

  - [ ] 36.1 Test import compatibility

    - Test that old import paths work with deprecation warnings
    - Test that new import paths work without warnings
    - _Requirements: 7.3, 7.4_

  - [ ] 36.2 Test API compatibility
    - Test all API endpoints return expected responses
    - Test response schemas match existing contracts
    - _Requirements: 7.1, 7.5_

- [ ] 37. Run full test suite

  - Run all existing tests with new structure
  - Fix any failing tests
  - Ensure test coverage doesn't decrease
  - _Requirements: 7.2, 7.6_

- [ ] 38. Performance testing
  - Benchmark API response times
  - Compare with baseline metrics
  - Identify any performance regressions
  - _Requirements: 7.5_

## Phase 10: Documentation

- [ ] 39. Create refactoring guide

  - [ ] 39.1 Write REFACTORING_GUIDE.md

    - Document new directory structure
    - Explain purpose of each package
    - Include migration notes for developers
    - Add import path examples
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.8_

  - [ ] 39.2 Create package READMEs
    - Write README.md for each major package
    - Explain package contents and purpose
    - Include usage examples
    - _Requirements: 6.5_

- [ ] 40. Update existing documentation

  - [ ] 40.1 Update backend/README.md

    - Update architecture section
    - Update directory structure
    - Add Portkey integration section
    - _Requirements: 6.6_

  - [ ] 40.2 Update module docstrings

    - Update docstrings for moved modules
    - Add deprecation notices where needed
    - _Requirements: 6.7_

  - [ ] 40.3 Create Portkey integration guide
    - Document how to use LLMClient
    - Document how to create prompts in Portkey
    - Document monitoring and cost tracking
    - _Requirements: 6.9_

- [ ] 41. Create deployment documentation
  - Document deployment procedure
  - Document rollback procedure
  - Document monitoring setup
  - _Requirements: 7.8_

## Phase 11: Cleanup & Finalization

- [x] 42. Remove old files

  - Delete original files from backend root (after confirming all imports updated)
  - Remove backup files (\_.BACKUP\_\_)
  - Remove deprecated compatibility shims
  - _Requirements: 1.12, 7.10_

- [x] 43. Clean up imports

  - Remove unused imports across codebase
  - Organize imports per PEP 8 (stdlib, third-party, local)
  - Run isort to standardize import order
  - _Requirements: 5.6, 5.8, 5.9_

- [x] 44. Update .gitignore

  - Add any new directories that should be ignored
  - Remove references to old structure
  - _Requirements: 1.12_

- [ ] 45. Final code quality checks
  - Run black for code formatting
  - Run flake8 for linting
  - Run mypy for type checking
  - Fix all issues
  - _Requirements: 5.6_

## Phase 12: Deployment

- [ ] 46. Deploy to staging

  - Deploy refactored code to staging environment
  - Run smoke tests
  - Monitor for errors
  - _Requirements: 7.1, 7.4_

- [ ] 47. Gradual production rollout

  - Deploy to 10% of production traffic
  - Monitor metrics (latency, errors, costs)
  - Deploy to 50% of production traffic
  - Monitor metrics
  - Deploy to 100% of production traffic
  - _Requirements: 7.1, 7.5_

- [ ] 48. Post-deployment validation

  - Verify all API endpoints working
  - Verify Portkey dashboard showing all LLM calls
  - Verify cost tracking functional
  - Verify no increase in error rates
  - _Requirements: 7.1, 7.5, 2.11, 2.12_

- [ ] 49. Final cleanup

  - Remove compatibility shims
  - Remove deprecation warnings
  - Archive old code
  - _Requirements: 7.10_

- [ ] 50. Team training
  - Train team on new structure
  - Train team on Portkey usage
  - Train team on prompt management
  - Update onboarding documentation
  - _Requirements: 6.4, 6.9_
