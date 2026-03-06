# Old SQL Migration Files

This directory contains legacy database migration files from a previous version of the Osprey B2C system that used **Supabase/PostgreSQL**.

## Contents

- **104 SQL migration files** (`.sql`)
- **1 Supabase Edge Function** (`supabase-edge-function-index.ts`)

## What These Files Are

### SQL Migration Files

PostgreSQL/Supabase database migration scripts dated between July-August 2025. These files created tables for:

**Authentication & Users:**
- `auth.users` - Supabase authentication users
- `platform_users` - Platform user profiles
- `clients` - Client management

**Immigration Forms & Processing:**
- `immigration_forms` - Form definitions (I-129, DS-160, I-140, I-485, I-130, I-751)
- `prompt_templates` - AI prompt version control
- `template_audit_logs` - Template change tracking

**AI & Document Processing:**
- `ai_agent_interactions` - AI chat history
- `document_analyses` - Document analysis results
- `visa_recommendations` - AI visa recommendations
- `api_usage_logs` - API tracking

**Case Management:**
- `cases` - Immigration case data
- `case_events` - Case event tracking
- `package_quality_reports` - QA reports
- `package_quality_overrides` - Admin overrides

**E-Filing Integration:**
- `efiling_accounts` - USCIS account management
- `efiling_logs` - E-filing automation logs

### Supabase Edge Function

`supabase-edge-function-index.ts` - A Deno-based serverless function that automated USCIS e-filing:
- Logged into USCIS accounts
- Filled forms automatically
- Uploaded documents
- Generated receipt numbers
- Tracked biometrics appointments

## Why These Files Are Archived

The Osprey B2C system **migrated from Supabase/PostgreSQL to MongoDB**:

**Old Architecture (Archived):**
- Supabase (PostgreSQL + Authentication + Edge Functions)
- Row Level Security (RLS) policies
- SQL-based data storage

**Current Architecture (Active):**
- MongoDB 7.0+ (NoSQL document database)
- Motor async driver
- FastAPI backend with custom authentication
- MongoDB collections: `users`, `auto_cases`, `documents`, `payments`, `chat_history`, `sessions`, `products`, `vouchers`

## Historical Value

These files are preserved for:
1. **Reference**: Understanding the previous data model
2. **Audit**: Tracking architectural decisions
3. **Migration**: Potential future data reconciliation needs
4. **Documentation**: Historical context for the project

## Do Not Use

⚠️ **These files are NOT compatible with the current system.** They reference:
- PostgreSQL-specific syntax (UUIDs, JSONB, Row Level Security)
- Supabase authentication (`auth.uid()`)
- Tables that don't exist in MongoDB

The current system uses MongoDB exclusively. These files are for **historical reference only**.

---

**Archived on**: January 12, 2026
**Original Location**: `frontend/` (root level)
**Migration Context**: Supabase/PostgreSQL → MongoDB migration
