# Compliance Package Migration Notes

## Overview
This document tracks the migration of compliance-related modules into the `backend/compliance/` package as part of the backend refactoring initiative.

## Migrated Files

### 1. Immigration Compliance Reviewer
- **Old Path**: `backend/immigration_compliance_reviewer.py`
- **New Path**: `backend/compliance/reviewer.py`
- **Class**: `ImmigrationComplianceReviewer`
- **Description**: Comprehensive compliance reviewer for immigration applications

### 2. Advanced Immigration Reviewer
- **Old Path**: `backend/advanced_immigration_reviewer.py`
- **New Path**: `backend/compliance/advanced_reviewer.py`
- **Class**: `AdvancedImmigrationReviewerAgent`
- **Description**: Advanced reviewer agent acting as immigration attorney specialist

### 3. Immigration Legal Rules
- **Old Path**: `backend/immigration_legal_rules.py`
- **New Path**: `backend/compliance/legal_rules.py`
- **Class**: `ImmigrationLegalRules`
- **Functions**: `apply_legal_rules()`
- **Description**: Legal rules and validation for immigration processes

### 4. Inadmissibility Screening
- **Old Path**: `backend/inadmissibility_screening.py`
- **New Path**: `backend/compliance/inadmissibility.py`
- **Class**: `InadmissibilityScreening`
- **Functions**: `perform_screening()`
- **Global Instance**: `screening`
- **Description**: Inadmissibility screening system based on INA §212

### 5. Policy Engine
- **Old Path**: `backend/policy_engine.py`
- **New Path**: `backend/compliance/policy_engine.py`
- **Class**: `PolicyEngine`
- **Description**: YAML-based policy engine for document validation

## Updated Import Locations

### Backend Files Updated
1. `backend/iterative_learning_system.py`
   - Updated: `from backend.compliance.reviewer import ImmigrationComplianceReviewer`

2. `backend/api/friendly_form.py`
   - Updated: `from backend.compliance.legal_rules import apply_legal_rules`

3. `backend/server.py` (2 locations)
   - Updated: `from backend.compliance.policy_engine import policy_engine`
   - Updated: `from backend.compliance.inadmissibility import screening, perform_screening`

### Archive Files (Not Updated)
The following files in the `archive/` directory still reference old paths but are not actively used:
- `archive/debug_scripts/run_complete_simulation.py`
- `archive/debug_scripts/compare_packages.py`
- `archive/old_tests/run_final_complete_test.py`

## Package Structure

```
backend/compliance/
├── __init__.py                 # Package exports
├── reviewer.py                 # ImmigrationComplianceReviewer
├── advanced_reviewer.py        # AdvancedImmigrationReviewerAgent
├── legal_rules.py              # ImmigrationLegalRules
├── inadmissibility.py          # InadmissibilityScreening
├── policy_engine.py            # PolicyEngine
└── MIGRATION_NOTES.md          # This file
```

## Public API

The package exports the following classes through `__init__.py`:

```python
from backend.compliance import (
    ImmigrationComplianceReviewer,
    AdvancedImmigrationReviewerAgent,
    ImmigrationLegalRules,
    InadmissibilityScreening,
    PolicyEngine,
)
```

## Dependencies

### Internal Dependencies
- `backend.documents.*` - Document processing modules
- `backend.forms.*` - Form processing modules
- `backend.utils.translation.*` - Translation utilities

### External Dependencies
- `pdfplumber` - PDF text extraction (optional)
- `yaml` - YAML policy file parsing
- Standard library: `logging`, `os`, `re`, `typing`, `datetime`, `hashlib`, `pathlib`

## Migration Date
January 14, 2026

## Requirements Satisfied
- Requirement 1.11: Organize compliance modules into dedicated package
- Requirement 5.1: Update all import statements to reflect new location
