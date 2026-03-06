# Portkey Manual Prompt Creation Guide

**Status**: ⚠️ Required - Portkey API does not support prompt creation yet
**Last Updated**: 2026-01-14

---

## Critical Discovery

**Portkey's API currently only supports RETRIEVING prompts, not CREATING them.**

From Portkey documentation:
> "CRUD: coming soon 🚀"

This means all 22 extracted prompts must be created **manually** in the Portkey UI before they can be used via API.

---

## Files Available for Manual Creation

1. **`prompts_for_portkey_import.csv`** - Spreadsheet format for easy viewing
2. **`prompts_for_portkey_import.json`** - Structured format for potential future bulk import
3. **`prompts_catalog.json`** - Complete catalog with all metadata

---

## Step-by-Step Manual Creation Process

### Step 1: Access Portkey Prompt Library

1. Go to [https://portkey.ai](https://portkey.ai)
2. Log in with your account
3. Click **"Prompts"** in the left sidebar
4. Click **"Create"** button

### Step 2: Create Each Prompt

For each of the 22 prompts in `prompts_for_portkey_import.csv`:

#### A. Basic Information
- **Name**: Use the "Name" column from CSV (e.g., "MariaAgent System Prompt")
- **Description**: Use format: `Migrated from {File}:{Line}`

#### B. Configure Messages
- Click **"JSON View"** for easier editing
- Copy the "Full Prompt" text from CSV
- Set the role:
  - If "Type" = "system" → Use `{"role": "system", "content": "..."}`
  - If "Type" = "inline" → Use `{"role": "user", "content": "..."}`

#### C. Add Variables
If the "Variables" column has values:
- Click **"Add Variable"** for each variable
- Variable name: Use exact name from CSV
- Variable type: Select "string"
- Mark as required if needed

#### D. Configure Model Settings
- **Model**: Use value from "Model" column (e.g., "gpt-4o")
- **Temperature**: Use value from "Temperature" column (e.g., 0.8)
- **Max Tokens**: Use value from "Max Tokens" column (if present)

#### E. Add Tags
- Add tag for priority: "high", "medium", or "low"
- Add tag for type: "system" or "inline"

#### F. Save and Record ID
1. Click **"Save"** button
2. Copy the generated Portkey Prompt ID (format: `pp-xxxxx`)
3. Record it in the tracking sheet (see Step 3)

### Step 3: Track Created Prompts

Create a tracking spreadsheet with columns:
- Original ID (from CSV)
- Name
- Portkey ID (record after creation)
- Status (Created/Pending)
- Notes

### Step 4: Update Catalog with Portkey IDs

After creating all prompts, update `prompts_catalog.json`:

```python
# Run this script to update catalog with Portkey IDs
python3 scripts/update_catalog_with_portkey_ids.py
```

(Script will prompt you to enter Portkey IDs for each prompt)

---

## Priority Order for Creation

### HIGH Priority (Create First) - 1 prompt
1. **MariaAgent System Prompt** - Main customer-facing agent

### MEDIUM Priority (Create Next) - 21 prompts

**Agent System Prompts (7)**:
2. FormValidationAgent
3. DocumentValidationAgent
4. ComplianceCheckAgent
5. UrgencyTriageAgent
6. EligibilityAnalysisAgent
7. ImmigrationLetterWriterAgent
8. USCISFormTranslatorAgent

**Server Endpoints (3)**:
9. Document analysis assistant
10. Translation assistant
11. Recommendations assistant

**Document Processing (3)**:
12. Document analysis expert
13. Document data extraction
14. Document relevance assessment

**Education & Interview (4)**:
15. Interview question generator
16. Interview evaluation
17. Immigration tips provider
18. Knowledge base assistant

**Other (4)**:
19. Voice compliance assistant
20. Form translation expert
21. Completeness analyzer
22. Translation service

---

## Example: Creating MariaAgent System Prompt

### Input Data (from CSV)
- **Name**: MariaAgent System Prompt
- **Type**: system
- **Priority**: HIGH
- **Model**: gpt-4o
- **Temperature**: 0.8
- **Max Tokens**: 1500
- **Variables**: var
- **Full Prompt**: (See CSV for complete text)

### In Portkey UI

1. **Create New Prompt**
   - Click "Prompts" → "Create"

2. **Set Name and Description**
   ```
   Name: MariaAgent System Prompt
   Description: Migrated from backend/agents/maria/agent.py:209
   ```

3. **Configure Message (JSON View)**
   ```json
   [
     {
       "role": "system",
       "content": "Você é a Maria, a assistente virtual da Osprey...[full text from CSV]"
     }
   ]
   ```

4. **Add Variable**
   - Name: `var`
   - Type: string
   - Required: Yes

5. **Set Model Config**
   - Model: gpt-4o
   - Temperature: 0.8
   - Max Tokens: 1500

6. **Add Tags**
   - high
   - system
   - maria

7. **Save**
   - Click "Save"
   - Copy Portkey ID (e.g., `pp-maria-system-v1`)
   - Record in tracking sheet

---

## Verification Checklist

After creating all prompts:

- [ ] All 22 prompts created in Portkey UI
- [ ] All Portkey IDs recorded in tracking sheet
- [ ] `prompts_catalog.json` updated with Portkey IDs
- [ ] Test retrieval of at least 3 prompts via API
- [ ] Verify variables work correctly
- [ ] Confirm model configurations are correct

---

## Testing Prompt Retrieval

After creation, test that prompts can be retrieved:

```bash
# Test retrieving a prompt
curl -X POST "https://api.portkey.ai/v1/prompts/YOUR_PROMPT_ID/render" \
  -H "x-portkey-api-key: $LLM_PORTKEY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "variables": {
      "var": "test value"
    }
  }'
```

Expected response:
```json
{
  "success": true,
  "data": {
    "model": "gpt-4o",
    "temperature": 0.8,
    "messages": [...]
  }
}
```

---

## Common Issues

### Issue 1: Variable Not Recognized
**Problem**: Portkey doesn't recognize `{{variable}}` syntax
**Solution**: Ensure variable is added in the Variables section, not just in the prompt text

### Issue 2: Prompt Too Long
**Problem**: Prompt exceeds UI limits
**Solution**: Break into multiple messages or use continuation

### Issue 3: Special Characters
**Problem**: Prompt contains special characters that break JSON
**Solution**: Properly escape quotes and newlines in JSON view

---

## Time Estimate

- **Per Prompt**: ~5-10 minutes (including testing)
- **Total Time**: ~2-4 hours for all 22 prompts
- **Recommended**: Create in batches of 5-7 prompts with breaks

---

## Next Steps After Manual Creation

1. **Update Catalog**: Run script to add Portkey IDs to `prompts_catalog.json`
2. **Regenerate Patches**: Update migration patches with real Portkey IDs
3. **Begin Code Migration**: Start implementing Task 31 (actual code changes)
4. **Test Integration**: Verify prompts work via LLMClient

---

## Future: When Portkey Adds Creation API

When Portkey releases their prompt creation API:
1. The existing `portkey_prompt_migrator.py` script can be updated
2. Use `prompts_for_portkey_import.json` for bulk import
3. Automate the entire process

**Monitor**: Check Portkey changelog at https://portkey.ai/docs/changelog

---

## Support

If you encounter issues:
- Portkey Documentation: https://portkey.ai/docs
- Portkey Support: support@portkey.ai
- Internal: Check `prompts_catalog.json` for prompt details

---

**Document Version**: 1.0
**Status**: Active - Manual creation required
