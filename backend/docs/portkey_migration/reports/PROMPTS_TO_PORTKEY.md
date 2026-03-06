# Prompt Migration to Portkey - AUTOMATED APPROACH

## ⚠️ This Migration is Fully Automated

Instead of manually creating prompts in Portkey's UI, we use automated scripts that:

1. **Extract** all prompts from the codebase using AST parsing
2. **Create** prompts in Portkey via API automatically  
3. **Generate** code migration patches programmatically
4. **Track** progress in machine-readable format

## Quick Start

```bash
cd backend

# Test connection
python scripts/test_portkey_connection.py

# Run full migration
python scripts/portkey_prompt_migrator.py --full
```

## Documentation

- **[PROMPT_MIGRATION_WORKPLAN.md](./PROMPT_MIGRATION_WORKPLAN.md)** - Detailed execution plan
- **Generated Files**:
  - `prompts_catalog.json` - All extracted prompts
  - `PROMPT_EXTRACTION_REPORT.md` - Extraction summary
  - `PORTKEY_CREATION_REPORT.md` - Creation results
  - `PROMPT_MIGRATION_PATCHES.md` - Code patches

## Why Automated?

| Aspect | Manual | Automated |
|--------|--------|-----------|
| Time | Hours | Minutes |
| Errors | High | Low |
| Tracking | Manual | JSON catalog |
| Rollback | Difficult | Easy |

See [PROMPT_MIGRATION_WORKPLAN.md](./PROMPT_MIGRATION_WORKPLAN.md) for complete details.
