# Prompt Migration to Portkey - Automated Workplan

## Overview

This document tracks the automated migration of all hardcoded prompts in the Osprey backend to Portkey's Prompt Management system. This workplan is designed to be tracked and executed by AI agents (Kiro, Claude Code) using Portkey's API.

**Status**: 🚧 In Progress
**Approach**: Fully Automated via Portkey API
**Last Updated**: 2026-01-14

---

## Migration Strategy

### Phase 1: Infrastructure Setup ✅ Completed
**Goal**: Create automation tools for prompt extraction and migration

#### Tasks
- [x] 1.1 Create `backend/scripts/portkey_api_client.py` ✅
  - Wrapper for Portkey REST API
  - Methods: create_prompt, update_prompt, list_prompts, delete_prompt
  - Error handling and retry logic
  - Uses `LLM_PORTKEY_API_KEY` from .env

- [x] 1.2 Create `backend/scripts/prompt_extractor.py` ✅
  - AST-based Python code parser
  - Extract system prompts from `get_system_prompt()` methods
  - Extract inline prompts from LLM calls
  - Detect variables using f-strings and .format()
  - Output structured JSON catalog

- [x] 1.3 Create `backend/scripts/portkey_prompt_migrator.py` ✅
  - Main orchestrator script
  - Coordinates extraction → creation → patching
  - Progress tracking and reporting
  - Rollback capabilities

- [x] 1.4 Create `backend/scripts/test_portkey_connection.py` ✅
  - Verify Portkey API connectivity
  - Test authentication
  - Validate permissions

**Success Criteria**:
- ✅ All scripts created and executable
- ✅ Portkey API connection verified
- ✅ Test prompt created and retrieved successfully

---

### Phase 2: Prompt Extraction ⚠️ Incomplete
**Goal**: Automatically extract all prompts from codebase

#### Tasks
- [x] 2.1 Scan all Python files in backend/ ✅
  - Recursively find all .py files
  - Exclude: __pycache__, .venv, tests, migrations
  - Generate file list for processing

- [x] 2.2 Extract system prompts ✅
  - Find all `get_system_prompt()` method definitions
  - Extract prompt text (handle multi-line strings)
  - Identify agent/class name
  - Detect embedded variables

- [ ] 2.3 Extract inline prompts ⚠️
  - Find `messages=[...]` patterns in LLM calls
  - Extract system, user, assistant messages
  - Identify prompt context (function name, module)
  - Detect f-string variables
  - **Status**: Only found 14 inline prompts, many more likely exist

- [ ] 2.4 Analyze prompt configurations ⚠️
  - Extract temperature, max_tokens from LLM calls
  - Identify model selection logic
  - Detect response format requirements (JSON, text)
  - **Status**: Partial - only for extracted prompts

- [x] 2.5 Generate catalog ✅
  - Create `backend/prompts_catalog.json`
  - Structure: prompt_id, location, text, variables, config
  - Include metadata: agent, purpose, priority

**Output Files**:
- `backend/prompts_catalog.json` - Structured prompt data (48KB) ✅
- `backend/PROMPT_EXTRACTION_REPORT.md` - Human-readable summary (11KB) ✅
- `backend/prompts_for_portkey_import.csv` - Spreadsheet (28KB) ✅
- `backend/prompts_for_portkey_import.json` - Import format (38KB) ✅

**Success Criteria**:
- [x] Infrastructure working
- [x] Variables correctly identified
- [x] Configurations captured
- [ ] **ALL prompts extracted** (currently 22/85 = 26%) ❌

**Issues**:
- Only 26% extraction coverage
- Need manual code review to find remaining ~63 prompts
- AST parser limited to obvious patterns

---

### Phase 3: Portkey Prompt Creation ❌ Blocked
**Goal**: Create all prompts in Portkey

**CRITICAL BLOCKER**: Portkey API does not support prompt creation yet. Documentation states "CRUD: coming soon 🚀"

#### Tasks
- [ ] 3.1 Manual creation in Portkey UI ⏳
  - Open Portkey dashboard at https://portkey.ai
  - Create each prompt manually following guide
  - Use `prompts_for_portkey_import.csv` as reference
  - Record Portkey IDs in tracking sheet

- [ ] 3.2 Update catalog with Portkey IDs ⏳
  - Run `python3 scripts/update_catalog_with_portkey_ids.py`
  - Enter Portkey ID for each prompt
  - Verify catalog updated correctly

- [ ] 3.3 Verify prompt retrieval ⏳
  - Test each prompt via `/prompts/{id}/render` endpoint
  - Verify variables work correctly
  - Confirm model configurations match

**Output Files**:
- `backend/prompts_catalog.json` (updated with real Portkey IDs) ⏳
- `backend/PORTKEY_CREATION_REPORT.md` (manual creation log) ⏳
- `backend/PORTKEY_MANUAL_CREATION_GUIDE.md` (instructions) ✅

**Success Criteria**:
- [ ] All prompts created in Portkey UI (0/22 = 0%)
- [ ] All Portkey IDs recorded in catalog
- [ ] All prompts retrievable via API
- [ ] Variables and configs verified

**Estimated Time**: 2-4 hours for 22 prompts + more for additional prompts

**Instructions**: See `PORTKEY_MANUAL_CREATION_GUIDE.md`

---

### Phase 4: Code Migration ⏳ Pending
**Goal**: Generate and apply code patches to use Portkey prompts

**BLOCKED BY**: Phase 3 completion (need real Portkey IDs)

#### Tasks
- [x] 4.1 Analyze prompt usage patterns ✅
  - Identify all locations where prompts are used
  - Determine migration pattern (direct replacement, refactor)
  - Check for dependencies

- [ ] 4.2 Regenerate migration patches ⏳
  - Update patches with real Portkey IDs (not placeholder IDs)
  - Verify import statements correct
  - Check variable mappings

- [ ] 4.3 Update migration document ⏳
  - Regenerate `backend/PROMPT_MIGRATION_PATCHES.md`
  - Include all code changes with real IDs
  - Provide testing instructions
  - Document rollback procedures

- [ ] 4.4 Generate test cases ⏳
  - Create unit tests for migrated functions
  - Comparison tests (old vs new)
  - Integration tests

**Output Files**:
- `backend/PROMPT_MIGRATION_PATCHES.md` - Code changes (needs regeneration) ⚠️
- Test suite (pending implementation) ⏳

**Success Criteria**:
- [x] All usage locations identified (22 locations)
- [ ] Migration patches with real Portkey IDs
- [ ] Test cases created
- [ ] Documentation complete

**Note**: Current patches use placeholder IDs (`pp-local-*`) and must be regenerated after Phase 3

---

## Prompt Catalog Structure

```json
{
  "prompts": [
    {
      "id": "PROMPT_001",
      "portkey_id": "pp-maria-system-v1",
      "name": "Maria Agent System Prompt",
      "agent": "Maria",
      "location": {
        "file": "backend/maria_agent.py",
        "line": 146,
        "function": "get_system_prompt"
      },
      "type": "system",
      "text": "Você é a Maria, a assistente virtual da Osprey...",
      "variables": [
        {"name": "user_name", "type": "str", "required": false, "default": "amigo(a)"},
        {"name": "visa_type", "type": "str", "required": false},
        {"name": "progress", "type": "int", "required": false}
      ],
      "config": {
        "model": "gpt-4o",
        "temperature": 0.8,
        "max_tokens": 1500,
        "top_p": 0.95
      },
      "priority": "HIGH",
      "status": "not_started",
      "created_at": null,
      "migrated_at": null
    }
  ]
}
```

---

## Progress Tracking

### Overall Progress
- **Total Prompts**: ~85 estimated (only 22 extracted so far)
- **Extracted**: 22 (26% coverage) ⚠️
- **Created in Portkey**: 0 (manual creation required) ❌
- **Code Migrated**: 0 patches applied ❌
- **Tests Passing**: Pending

### Phase Status
| Phase | Status | Progress | Completion Date |
|-------|--------|----------|-----------------|
| 1. Infrastructure | ✅ Completed | 6/6 | 2026-01-14 |
| 2. Extraction | ⚠️ Incomplete | 2/5 | 2026-01-14 |
| 3. Portkey Creation | ❌ Blocked | 0/7 | - |
| 4. Code Migration | ⏳ Pending | 0/4 | - |

### Prompt Categories Progress
| Category | Estimated | Extracted | Created | Migrated |
|----------|-----------|-----------|---------|----------|
| Agent System Prompts | ~15 | 8 | 0 | 0 |
| Document Processing | ~10 | 3 | 0 | 0 |
| Form Processing | ~8 | 1 | 0 | 0 |
| Server Endpoints | ~10 | 3 | 0 | 0 |
| Education & Interview | ~4 | 4 | 0 | 0 |
| Visa Processing | ~3 | 0 | 0 | 0 |
| Specialized Tasks | ~10 | 0 | 0 | 0 |
| Voice & Compliance | ~2 | 1 | 0 | 0 |
| Translation | ~2 | 1 | 0 | 0 |
| Other | ~20 | 1 | 0 | 0 |
| **TOTAL** | **~85** | **22** | **0** | **0** |

### Blockers
1. **Portkey API Limitation**: No prompt creation endpoint (manual UI creation required)
2. **Incomplete Extraction**: Only 26% of prompts found (need manual code review)
3. **Manual Creation Time**: Estimated 2-4 hours for 22 prompts + more for additional prompts

---

## Execution Commands

### Run Full Migration
```bash
cd backend
python scripts/portkey_prompt_migrator.py --full
```

### Run Individual Phases
```bash
# Phase 1: Setup (test connection)
python scripts/test_portkey_connection.py

# Phase 2: Extract prompts
python scripts/prompt_extractor.py --output prompts_catalog.json

# Phase 3: Create in Portkey
python scripts/portkey_prompt_migrator.py --create-prompts

# Phase 4: Generate patches
python scripts/portkey_prompt_migrator.py --generate-patches
```

### Dry Run (No Changes)
```bash
python scripts/portkey_prompt_migrator.py --dry-run
```

---

## API Reference

### Portkey API Endpoints

#### Create Prompt
```http
POST https://api.portkey.ai/v1/prompts
Authorization: Bearer {PORTKEY_API_KEY}
Content-Type: application/json

{
  "name": "Maria System Prompt",
  "description": "Main system prompt for Maria assistant",
  "messages": [
    {
      "role": "system",
      "content": "Você é a Maria..."
    }
  ],
  "variables": [
    {"name": "user_name", "type": "string", "default": "amigo(a)"}
  ],
  "model": "gpt-4o",
  "temperature": 0.8,
  "max_tokens": 1500
}
```

#### List Prompts
```http
GET https://api.portkey.ai/v1/prompts
Authorization: Bearer {PORTKEY_API_KEY}
```

#### Get Prompt
```http
GET https://api.portkey.ai/v1/prompts/{prompt_id}
Authorization: Bearer {PORTKEY_API_KEY}
```

---

## Error Handling

### Common Issues

#### Issue 1: API Authentication Failed
**Error**: `401 Unauthorized`
**Solution**: Verify `LLM_PORTKEY_API_KEY` in `.env` file

#### Issue 2: Prompt Already Exists
**Error**: `409 Conflict`
**Solution**: Use update endpoint or delete existing prompt

#### Issue 3: Invalid Variable Syntax
**Error**: `400 Bad Request - Invalid variable format`
**Solution**: Ensure variables use `{{variable_name}}` syntax

#### Issue 4: Rate Limit Exceeded
**Error**: `429 Too Many Requests`
**Solution**: Implement exponential backoff, batch requests

---

## Rollback Procedures

### If Migration Fails

1. **Restore Original Code**
   ```bash
   git checkout backend/
   ```

2. **Delete Created Prompts** (if needed)
   ```bash
   python scripts/portkey_prompt_migrator.py --rollback
   ```

3. **Review Logs**
   ```bash
   cat backend/prompt_migration.log
   ```

---

## Testing Strategy

### Unit Tests
- Test each extracted prompt individually
- Verify variable substitution
- Validate response format

### Integration Tests
- Test complete agent workflows
- Compare old vs new implementations
- Verify no regressions

### Performance Tests
- Measure latency with Portkey
- Compare token usage
- Monitor costs

---

## Success Metrics

### Technical Metrics
- ✅ 100% prompts extracted
- ✅ 100% prompts created in Portkey
- ✅ 0 API errors
- ✅ All tests passing
- ✅ No performance degradation

### Business Metrics
- ✅ Centralized prompt management
- ✅ Version control for prompts
- ✅ Cost tracking enabled
- ✅ A/B testing capability
- ✅ Observability dashboard active

---

## Next Steps After Completion

1. **Monitor Portkey Dashboard**
   - Track usage, costs, latency
   - Set up alerts

2. **Optimize Prompts**
   - A/B test variations
   - Reduce token usage
   - Improve response quality

3. **Train Team**
   - Document new workflow
   - Update onboarding materials
   - Share best practices

4. **Archive Old Code**
   - Move hardcoded prompts to archive
   - Update documentation
   - Clean up imports

---

## Notes for AI Agents

### For Kiro
- Use this document to track progress
- Update status after each phase
- Generate reports automatically
- Handle errors gracefully

### For Claude Code
- Follow the execution commands
- Review generated patches before applying
- Run tests after each migration
- Document any issues encountered

### Collaboration
- Both agents can work on different phases simultaneously
- Use this document as single source of truth
- Update progress in real-time
- Communicate blockers clearly

---

**Document Version**: 1.0
**Last Updated**: 2026-01-14
**Status**: 🚧 Ready for Execution
