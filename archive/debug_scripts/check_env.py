#!/usr/bin/env python3
"""
Check environment variables for Google Vision API
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent / 'backend'
env_path = ROOT_DIR / '.env'

print(f"Looking for .env file at: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path)
    print("Loaded .env file")
else:
    print("No .env file found, checking system environment")

# Check Google Vision API environment variables
google_api_key = os.environ.get('GOOGLE_API_KEY')
google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
google_project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')

print("\n=== GOOGLE VISION API ENVIRONMENT VARIABLES ===")
print(f"GOOGLE_API_KEY: {'SET' if google_api_key else 'NOT SET'}")
if google_api_key:
    print(f"  Value: {google_api_key[:20]}...")
    print(f"  Length: {len(google_api_key)} characters")

print(f"GOOGLE_CLIENT_ID: {'SET' if google_client_id else 'NOT SET'}")
if google_client_id:
    print(f"  Value: {google_client_id[:30]}...")
    print(f"  Length: {len(google_client_id)} characters")

print(f"GOOGLE_CLOUD_PROJECT_ID: {'SET' if google_project_id else 'NOT SET'}")
if google_project_id:
    print(f"  Value: {google_project_id}")

# Check if credentials are configured
has_credentials = bool(google_api_key or google_client_id)
print(f"\nCredentials configured: {has_credentials}")

if has_credentials:
    auth_method = "api_key" if google_api_key else "oauth2" if google_client_id else "mock"
    print(f"Authentication method: {auth_method}")
    print("✅ Google Vision API should be in REAL mode")
else:
    print("❌ Google Vision API will be in MOCK mode")

# Check other relevant environment variables
print("\n=== OTHER ENVIRONMENT VARIABLES ===")
openai_key = os.environ.get('OPENAI_API_KEY')
emergent_key = os.environ.get('EMERGENT_LLM_KEY')
mongo_url = os.environ.get('MONGO_URL')

print(f"OPENAI_API_KEY: {'SET' if openai_key else 'NOT SET'}")
print(f"EMERGENT_LLM_KEY: {'SET' if emergent_key else 'NOT SET'}")
print(f"MONGO_URL: {'SET' if mongo_url else 'NOT SET'}")