# Running the Osprey Server

## Recommended Method (From Project Root)

The **recommended** way to run the server is from the project root directory:

```bash
# From project root (camada-osprey-core/)
python3 run_server.py
```

This ensures:
- ✅ Proper Python path setup
- ✅ All `backend.*` imports work correctly
- ✅ Consistent behavior across all modules
- ✅ Works with testing and type checking tools

## Legacy Method (From Backend Directory)

You can still run from the backend directory for backward compatibility:

```bash
# From backend/ directory
cd backend
python3 server.py
```

The server.py now automatically adds the project root to Python path, so both methods work identically.

## Why This Change?

The codebase has evolved to use absolute imports (`from backend.visa import ...`) which is the Python best practice. This requires the `backend` directory to be treated as a proper Python package.

### Before (Inconsistent)
- Some modules used relative imports: `from visa import ...`
- Some modules used absolute imports: `from backend.visa import ...`
- This caused "No module named 'backend'" errors

### After (Consistent)
- All modules use absolute imports: `from backend.visa import ...`
- Server can run from project root or backend directory
- No more import errors

## Development Workflow

```bash
# 1. Install dependencies
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 3. Run the server (from project root)
cd ..
python3 run_server.py

# Or with uvicorn directly
uvicorn backend.server:app --reload --port 8001
```

## Docker/Production

For Docker or production deployments, always run from project root:

```dockerfile
# Dockerfile
WORKDIR /app
COPY . .
CMD ["python3", "run_server.py"]
```

Or with uvicorn:

```bash
uvicorn backend.server:app --host 0.0.0.0 --port 8001
```

## Testing

Tests should also run from project root:

```bash
# From project root
pytest backend/tests/

# Or with coverage
pytest --cov=backend backend/tests/
```

## IDE Configuration

### VS Code
Add to `.vscode/settings.json`:
```json
{
  "python.analysis.extraPaths": ["${workspaceFolder}"],
  "python.autoComplete.extraPaths": ["${workspaceFolder}"]
}
```

### PyCharm
Mark the project root as "Sources Root" in Project Structure settings.

## Troubleshooting

### "No module named 'backend'" Error

**Solution**: Make sure you're running from the project root, or that `server.py` has the path setup code at the top.

### Import Errors After Update

**Solution**: Restart your Python interpreter/IDE to pick up the new path configuration.

### Environment Variables Not Loading

**Solution**: Make sure `.env` file exists in the `backend/` directory, not the project root.
