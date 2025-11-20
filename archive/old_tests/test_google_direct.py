#!/usr/bin/env python3
"""
Direct test of Google Vision API configuration
"""

import os
import sys
sys.path.append('/app/backend')

from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# Now import the Google Vision API integration
from google_document_ai_integration import GoogleVisionAPIProcessor, hybrid_validator

def test_google_vision_config():
    print("🔍 TESTING GOOGLE VISION API CONFIGURATION DIRECTLY...")
    print("=" * 60)
    
    # Test 1: Check environment variables
    print("📋 Test 1: Environment Variables")
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    
    print(f"GOOGLE_API_KEY: {'SET' if google_api_key else 'NOT SET'}")
    print(f"GOOGLE_CLIENT_ID: {'SET' if google_client_id else 'NOT SET'}")
    print(f"GOOGLE_CLOUD_PROJECT_ID: {'SET' if google_project_id else 'NOT SET'}")
    print()
    
    # Test 2: Create new Google Vision API processor
    print("📋 Test 2: Google Vision API Processor")
    processor = GoogleVisionAPIProcessor()
    
    print(f"API Key: {'SET' if processor.api_key else 'NOT SET'}")
    print(f"Client ID: {'SET' if processor.client_id else 'NOT SET'}")
    print(f"Project ID: {processor.project_id}")
    print(f"Is Mock Mode: {processor.is_mock_mode}")
    print(f"Auth Method: {processor.auth_method}")
    print()
    
    # Test 3: Check hybrid validator
    print("📋 Test 3: Hybrid Validator")
    print(f"Google Processor Mock Mode: {hybrid_validator.google_processor.is_mock_mode}")
    print(f"Google Processor Auth Method: {hybrid_validator.google_processor.auth_method}")
    print(f"Google Processor Project ID: {hybrid_validator.google_processor.project_id}")
    print()
    
    # Test 4: Expected configuration
    print("📋 Test 4: Expected vs Actual")
    expected_api_key = "AIzaSyBjn25InzalbcQVeDN8dgfgv6StUsBIutw"
    expected_client_id = "891629358081-pb11latlhnnp0dj68v03c0v2ocr6bhb8.apps.googleusercontent.com"
    expected_project_id = "891629358081"
    
    api_key_match = processor.api_key == expected_api_key if processor.api_key else False
    client_id_match = processor.client_id == expected_client_id if processor.client_id else False
    project_id_match = processor.project_id == expected_project_id
    
    print(f"API Key Match: {api_key_match}")
    print(f"Client ID Match: {client_id_match}")
    print(f"Project ID Match: {project_id_match}")
    print()
    
    # Summary
    print("📊 SUMMARY")
    print("=" * 60)
    if not processor.is_mock_mode:
        print("✅ Google Vision API is configured with REAL credentials")
        print(f"   - Authentication Method: {processor.auth_method}")
        print(f"   - Project ID: {processor.project_id}")
        print("   - Ready for API calls (may get 403 if service not enabled)")
    else:
        print("❌ Google Vision API is in MOCK mode")
        print("   - No credentials detected")
        print("   - Check environment variable loading")

if __name__ == "__main__":
    test_google_vision_config()