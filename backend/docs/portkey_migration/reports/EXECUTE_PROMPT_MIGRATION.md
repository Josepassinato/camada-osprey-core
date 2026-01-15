# Execute Prompt Migration - Quick Guide

**Status**: ✅ Ready to Execute
**Estimated Time**: 3-4 minutes
**Approach**: Fully Automated

---

## Prerequisites Check

Before running, verify:

```bash
# 1. Check Portkey API key is set
grep LLM_PORTKEY_API_KEY backend/.env

# 2. Check Python dependencies
pip list | grep -E "httpx|python-dotenv"

# 3. Verify you're in the correct directory
pwd  # Should be in camada-osprey-core/
```

---

## Step-by-Step Execution

### Step 1: Test Connection (30 seconds)

```bash
cd backend
python scripts/test_portkey_connection.py
```

**Expected Output**:
```
🔍 Testing Portkey API Connection...

1️⃣  Initializing Portkey client...
   ✅ Client initialized

2️⃣  Testing API connection...
   ✅ Connection successful!

3️⃣  Listing existing prompts...
   ✅ Found X prompts

✅ All tests passed!
🚀 Ready to run prompt migration!
```

**If it fails**: Check troubleshooting section below.

---

### Step 2: Run Full Migration (3-4 minutes)

```bash
python scripts/portkey_prompt_migrator.py --full
```

**What happens**:
1. **Phase 1**: Tests Portkey connection
2. **Phase 2**: Extracts all prompts from codebase (~30 seconds)
3. **Phase 3**: Creates prompts in Portkey (~2-3 minutes)
4. **Phase 4**: Generates migration patches (~10 seconds)

**Expected Output**:
```
🚀 Starting full prompt migration...

============================================================
PHASE 1: Testing Portkey Connection
============================================================
✅ Portkey API connection successful
📋 Found X existing prompts in Portkey

============================================================
PHASE 2: Extracting Prompts from Codebase
============================================================
🔍 Scanning backend for prompts...
📁 Found 150 Python files to scan
✅ Extracted 85 prompts

📊 Extraction Summary:
  HIGH: 15 prompts
  MEDIUM: 30 prompts
  LOW: 40 prompts

💾 Saved catalog to backend/prompts_catalog.json
📄 Generated report: backend/PROMPT_EXTRACTION_REPORT.md

============================================================
PHASE 3: Creating Prompts in Portkey
============================================================
📊 Creating prompts by priority:
  HIGH: 15
  MEDIUM: 30
  LOW: 40

🔥 Creating HIGH priority prompts...
  [1/15] Creating: Maria Agent System Prompt
  ✅ Created prompt: Maria Agent System Prompt (ID: pp-...)
  [2/15] Creating: Dra. Paula Immigration Expert
  ...

✅ Created 85/85 prompts successfully

============================================================
PHASE 4: Generating Code Migration Patches
============================================================
📝 Generating migration patches for 85 prompts
✅ Generated 85 migration patches
📄 Saved migration patches document

✅ Full migration complete!

============================================================
MIGRATION SUMMARY
============================================================
Total Prompts: 85
Created in Portkey: 85
Success Rate: 100.0%

📁 Generated Files:
  - backend/prompts_catalog.json
  - backend/PROMPT_EXTRACTION_REPORT.md
  - backend/PORTKEY_CREATION_REPORT.md
  - backend/PROMPT_MIGRATION_PATCHES.md

✅ Migration complete!
```

---

### Step 3: Review Results (2 minutes)

```bash
# View extraction report
cat backend/PROMPT_EXTRACTION_REPORT.md

# View creation report
cat backend/PORTKEY_CREATION_REPORT.md

# View migration patches
cat backend/PROMPT_MIGRATION_PATCHES.md

# Check catalog
cat backend/prompts_catalog.json | jq '.metadata'
```

---

### Step 4: Verify in Portkey Dashboard (1 minute)

1. Open https://app.portkey.ai
2. Navigate to **Prompt Library**
3. Filter by tag: `automated-migration`
4. Verify prompts are created
5. Test a few prompts with sample inputs

---

## Alternative: Run Individual Phases

If you want more control:

```bash
# Extract only
python scripts/portkey_prompt_migrator.py --extract

# Review extraction report
cat backend/PROMPT_EXTRACTION_REPORT.md

# Create in Portkey only
python scripts/portkey_prompt_migrator.py --create-prompts

# Review creation report
cat backend/PORTKEY_CREATION_REPORT.md

# Generate patches only
python scripts/portkey_prompt_migrator.py --generate-patches

# Review patches
cat backend/PROMPT_MIGRATION_PATCHES.md
```

---

## Dry Run (No Changes)

To see what would happen without making changes:

```bash
python scripts/portkey_prompt_migrator.py --dry-run
```

---

## Troubleshooting

### Issue: Connection Test Fails

**Error**: `❌ Portkey API connection failed!`

**Solutions**:
1. Check API key in `.env`:
   ```bash
   grep LLM_PORTKEY_API_KEY backend/.env
   ```

2. Verify API key is valid at https://app.portkey.ai

3. Check internet connectivity:
   ```bash
   curl -I https://api.portkey.ai
   ```

---

### Issue: No Prompts Extracted

**Error**: `✅ Extracted 0 prompts`

**Solutions**:
1. Verify you're in the correct directory:
   ```bash
   ls backend/*.py  # Should show Python files
   ```

2. Check for syntax errors:
   ```bash
   python -m py_compile backend/maria_agent.py
   ```

---

### Issue: Some Prompts Failed to Create

**Error**: `❌ Failed to create X prompts`

**Solutions**:
1. Check creation report:
   ```bash
   cat backend/PORTKEY_CREATION_REPORT.md
   ```

2. Look for specific errors (401, 429, 409)

3. Re-run creation phase:
   ```bash
   python scripts/portkey_prompt_migrator.py --create-prompts
   ```

---

### Issue: Rate Limit Exceeded

**Error**: `429 Too Many Requests`

**Solution**: Script includes automatic rate limiting (0.5s delay). If still hitting limits, the script will retry automatically.

---

## After Migration

### 1. Review Generated Files

- **`prompts_catalog.json`**: Complete catalog with Portkey IDs
- **`PROMPT_EXTRACTION_REPORT.md`**: Human-readable summary
- **`PORTKEY_CREATION_REPORT.md`**: Creation results
- **`PROMPT_MIGRATION_PATCHES.md`**: Code migration guide

### 2. Test Prompts in Portkey

Visit https://app.portkey.ai and test prompts with sample inputs.

### 3. Apply Code Patches

Use the generated patches in `PROMPT_MIGRATION_PATCHES.md` to update your code.

### 4. Run Tests

```bash
pytest backend/tests/
```

### 5. Monitor Performance

Check Portkey dashboard for:
- Request counts
- Latency
- Token usage
- Costs

---

## Rollback

If you need to undo the migration:

```bash
# 1. Restore original code
git checkout backend/

# 2. Delete created prompts (optional)
# Use Portkey dashboard to delete prompts with tag "automated-migration"

# 3. Remove generated files
rm backend/prompts_catalog.json
rm backend/PROMPT_EXTRACTION_REPORT.md
rm backend/PORTKEY_CREATION_REPORT.md
rm backend/PROMPT_MIGRATION_PATCHES.md
```

---

## Success Checklist

- [ ] Connection test passed
- [ ] All prompts extracted (target: 80+)
- [ ] All prompts created in Portkey
- [ ] No API errors
- [ ] Reports generated
- [ ] Prompts visible in Portkey dashboard
- [ ] Prompts testable with sample inputs

---

## Need Help?

- **Documentation**: See `PROMPT_MIGRATION_WORKPLAN.md` for detailed info
- **Summary**: See `PROMPT_MIGRATION_SUMMARY.md` for overview
- **Scripts**: See `scripts/README.md` for script documentation

---

**Ready to execute?** Run:

```bash
cd backend
python scripts/test_portkey_connection.py && \
python scripts/portkey_prompt_migrator.py --full
```

Good luck! 🚀
