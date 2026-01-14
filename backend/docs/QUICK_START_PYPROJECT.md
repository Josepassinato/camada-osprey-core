# Quick Start: Using pyproject.toml

## What Changed?

We've added a modern `pyproject.toml` configuration file to the backend. This is the new Python standard for project configuration (PEP 517/518/621).

---

## Installation

### Option 1: Using pyproject.toml (Recommended)

```bash
cd backend

# Install production dependencies
pip install -e .

# Install with development tools (pytest, black, mypy, etc.)
pip install -e .[dev]
```

### Option 2: Using requirements.txt (Still Works)

```bash
cd backend
pip install -r requirements.txt
```

**Note:** Both methods install the same dependencies. Use whichever you prefer!

---

## Development Tools

### Code Formatting with Black

```bash
# Format all Python files
black backend/

# Check formatting without changing files
black --check backend/

# Format specific file
black backend/api/cases.py
```

**Configuration:** Line length = 100, Python 3.11+

### Import Sorting with isort

```bash
# Sort imports in all files
isort backend/

# Check without changing
isort --check backend/

# Sort specific file
isort backend/api/cases.py
```

**Configuration:** Compatible with Black

### Type Checking with MyPy

```bash
# Check types in all files
mypy backend/

# Check specific file
mypy backend/api/cases.py

# Check with verbose output
mypy --verbose backend/
```

**Configuration:** Python 3.11, ignore missing imports for third-party libs

### Linting with Flake8

```bash
# Lint all files
flake8 backend/

# Lint specific file
flake8 backend/api/cases.py

# Show statistics
flake8 --statistics backend/
```

**Configuration:** Max line length = 100, max complexity = 10

### Testing with Pytest

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_cases.py

# Run tests matching pattern
pytest -k "test_create"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

---

## Common Workflows

### Before Committing Code

```bash
# 1. Format code
black backend/
isort backend/

# 2. Check types
mypy backend/

# 3. Lint
flake8 backend/

# 4. Run tests
pytest
```

### Setting Up New Environment

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -e .[dev]

# 3. Verify installation
python -c "import fastapi; print('✓ FastAPI installed')"
pytest --version
black --version
```

### Updating Dependencies

```bash
# Update a specific package
pip install --upgrade fastapi

# Update all packages (careful!)
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip-audit
```

---

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

1. Go to **Settings → Tools → Black**
2. Enable "Run Black on save"
3. Go to **Settings → Tools → External Tools**
4. Add MyPy and Flake8 as external tools

---

## Makefile (Optional)

Create a `Makefile` in backend/:

```makefile
.PHONY: install format lint typecheck test clean

install:
	pip install -e .[dev]

format:
	black backend/
	isort backend/

lint:
	flake8 backend/

typecheck:
	mypy backend/

test:
	pytest

coverage:
	pytest --cov=backend --cov-report=html
	open htmlcov/index.html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage

all: format lint typecheck test
```

Usage:
```bash
make install    # Install dependencies
make format     # Format code
make lint       # Run linter
make typecheck  # Check types
make test       # Run tests
make all        # Run everything
```

---

## Pre-commit Hooks (Optional)

Install pre-commit to automatically run checks before commits:

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 25.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 7.0.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.19.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

# Install the hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

Now checks run automatically before each commit!

---

## Troubleshooting

### "Module not found" errors

```bash
# Make sure you're in the backend directory
cd backend

# Reinstall in editable mode
pip install -e .
```

### Black/MyPy not found

```bash
# Install dev dependencies
pip install -e .[dev]

# Or install individually
pip install black mypy flake8 isort pytest
```

### Import errors after cleanup

The following imports have changed:

```python
# Old (will fail)
from validate_endpoint import form_validator
from scheduler_visa_updates import get_visa_update_scheduler

# New (correct)
from backend.utils.form_validator import form_validator
from backend.utils.scheduler import get_visa_update_scheduler
```

---

## Benefits of pyproject.toml

1. **Single Source of Truth**: All project metadata in one place
2. **Modern Standard**: PEP 517/518/621 compliant
3. **Better IDE Support**: IDEs read pyproject.toml automatically
4. **Easier Dependency Management**: `pip install -e .[dev]`
5. **Consistent Tooling**: All team members use same settings
6. **Future-Proof**: Python's recommended approach

---

## Questions?

- Check `backend/pyproject.toml` for full configuration
- See `backend/docs/CLEANUP_SUMMARY_2026-01-14.md` for details
- Ask in #backend-dev channel

---

**Last Updated:** January 14, 2026  
**Python Version:** 3.11+  
**Status:** ✅ Production Ready
