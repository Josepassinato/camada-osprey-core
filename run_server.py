#!/usr/bin/env python3
"""
Osprey Server Launcher

Run this from the project root directory:
    python3 run_server.py

This ensures proper Python path setup for the backend package.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the server
from backend.server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        reload_dirs=[str(project_root / "backend")]
    )
