# Backend Scripts

Utility scripts for backend operations and migrations.

## Prompt Migration Scripts

Automated scripts for migrating prompts to Portkey.

### Quick Start

```bash
# Test Portkey connection
python test_portkey_connection.py

# Run full migration
python portkey_prompt_migrator.py --full

# Extract prompts only
python portkey_prompt_migrator.py --extract

# Create in Portkey only
python portkey_prompt_migrator.py --create-prompts

# Generate patches only
python portkey_prompt_migrator.py --generate-patches

# Dry run (no changes)
python portkey_prompt_migrator.py --dry-run
```

### Scripts

- **`test_portkey_connection.py`** - Test Portkey API connectivity
- **`portkey_api_client.py`** - Portkey REST API wrapper
- **`prompt_extractor.py`** - Extract prompts from codebase
- **`portkey_prompt_migrator.py`** - Main orchestrator

### Requirements

```bash
pip install httpx python-dotenv
```

### Environment

Ensure `backend/.env` contains:

```bash
LLM_PORTKEY_API_KEY=your_api_key_here
LLM_ENABLE_PORTKEY=true
```

## Other Scripts

- **`create_admin_user.py`** - Create admin user
- **`create_superadmin.py`** - Create superadmin
- **`create_test_admin.py`** - Create test admin
- **`create_stripe_coupon.py`** - Create Stripe coupon
- **`fix_indexes.py`** - Fix MongoDB indexes
- **`mongodb_backup.py`** - Backup MongoDB database
