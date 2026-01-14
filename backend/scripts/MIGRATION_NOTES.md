# Scripts Package Migration Notes

## Migration Summary

All utility scripts have been successfully migrated from `backend/` root to `backend/scripts/` package.

## Migrated Files

1. ✅ `create_admin_user.py` - Interactive script to create admin users
2. ✅ `create_superadmin.py` - Automated script to create superadmin user
3. ✅ `create_test_admin.py` - Automated script to create test admin user
4. ✅ `create_stripe_coupon.py` - Script to create Stripe discount coupons
5. ✅ `fix_indexes.py` - Database index maintenance script
6. ✅ `mongodb_backup.py` - MongoDB backup and restore utility

## Updated Imports

### backend/core/database.py
- Updated import: `from backend.scripts.mongodb_backup import mongodb_backup`
- Used in: `_start_backup_scheduler()` function

### backend/server.py
- Updated 3 imports: `from backend.scripts.mongodb_backup import mongodb_backup`
- Used in:
  - `/admin/backup/create` endpoint
  - `/admin/backup/list` endpoint
  - `/admin/backup/restore/{backup_name}` endpoint

## Running Scripts

All scripts can still be run directly from the command line:

```bash
# From project root
python3 backend/scripts/create_admin_user.py
python3 backend/scripts/create_superadmin.py
python3 backend/scripts/create_test_admin.py
python3 backend/scripts/create_stripe_coupon.py
python3 backend/scripts/fix_indexes.py

# Or using Python module syntax
python3 -m backend.scripts.create_admin_user
python3 -m backend.scripts.create_superadmin
# etc.
```

## Import Usage

To import from these scripts in other modules:

```python
from backend.scripts.mongodb_backup import mongodb_backup, MongoDBBackup
```

## Verification

All imports have been verified to work correctly:
- ✅ No old-style imports remain in codebase
- ✅ All new imports use `backend.scripts.*` path
- ✅ Scripts can be imported as modules
- ✅ Scripts can be run directly from command line

## Requirements Satisfied

- ✅ Requirement 1.11: Organized utility scripts into proper package
- ✅ Requirement 5.1: Updated all imports to reflect new location
