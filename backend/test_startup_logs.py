#!/usr/bin/env python3
"""Test startup logs to verify Google Document AI initialization messages"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['LOG_FORMAT'] = 'plain'
os.environ['LOG_PRETTY'] = 'true'

# Setup logging first
from backend.core.logging import setup_logging

logger = setup_logging()

print("\n" + "="*60)
print("Testing Google Document AI Initialization")
print("="*60 + "\n")

# Import and initialize Google Document AI
from backend.integrations.google.document_ai import (
    GoogleDocumentAIProcessor,
    HybridDocumentValidator,
)

print("\n--- Initializing GoogleDocumentAIProcessor ---")
processor = GoogleDocumentAIProcessor()

print("\n--- Initializing HybridDocumentValidator ---")
validator = HybridDocumentValidator()

print("\n--- Accessing google_processor property (singleton) ---")
_ = validator.google_processor

print("\n--- Accessing google_processor property again (should reuse) ---")
_ = validator.google_processor

print("\n" + "="*60)
print("✅ Initialization test completed!")
print("="*60 + "\n")
