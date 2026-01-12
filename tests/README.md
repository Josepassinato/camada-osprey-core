# Tests

This directory contains all test files organized by test type.

## Structure

### integration/
Integration tests that verify the interaction between multiple components.

**Examples:**
- `test_agent_integration.py` - Multi-agent system integration
- `test_all_agents.py` - All 8 visa specialist agents
- `backend_test.py` - Backend API integration
- `test_google_credentials.py` - Google Cloud API integration

**Run integration tests:**
```bash
python3 tests/integration/test_agent_integration.py
python3 -m pytest tests/integration/
```

### e2e/
End-to-end tests that validate complete user flows from start to finish.

**Examples:**
- `comprehensive_visa_test.py` - Complete visa application flow
- `visa_types_e2e_test.py` - All 8 visa types end-to-end
- `friendly_forms_e2e_test.py` - Friendly form submission flow

**Run e2e tests:**
```bash
python3 tests/e2e/comprehensive_visa_test.py
python3 -m pytest tests/e2e/
```

### unit/
Unit tests that verify individual functions, methods, and components in isolation.

**Examples:**
- `test_visa_api_simple.py` - Visa API unit tests
- `friendly_form_test.py` - Form validation tests
- `test_official_form_structure.py` - USCIS form structure tests

**Run unit tests:**
```bash
python3 tests/unit/test_visa_api_simple.py
python3 -m pytest tests/unit/
```

### results/
Test execution results stored as JSON files and reports.

**Contents:**
- `*_test_results.json` - Test execution results
- `*_results.json` - Various test outputs
- `test_result.md` - Formatted test reports

## Running Tests

All tests should be run from the repository root:

```bash
# Run specific test
python3 tests/integration/test_agent_integration.py

# Run all tests in a category with pytest
python3 -m pytest tests/integration/
python3 -m pytest tests/e2e/
python3 -m pytest tests/unit/

# Run all tests
python3 -m pytest tests/
```

## Test Database

Tests use MongoDB database `test_database` on `localhost:27017`.
