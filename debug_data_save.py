#!/usr/bin/env python3
"""
Debug script to check what's happening with data saving
"""

import requests
import json

BACKEND_URL = "https://smart-visa-helper-1.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

def test_data_save():
    # Create a new case
    print("Creating new case...")
    response = requests.post(
        f"{API_BASE}/auto-application/start",
        json={"visa_type": "I-539", "form_code": "I-539"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code not in [200, 201]:
        print(f"Failed to create case: {response.status_code}")
        return
    
    case_data = response.json()
    case_id = case_data.get("case", {}).get("case_id")
    print(f"Created case: {case_id}")
    
    # Check initial state
    print("\nChecking initial case state...")
    response = requests.get(f"{API_BASE}/auto-application/case/{case_id}")
    if response.status_code == 200:
        case_info = response.json().get("case", {})
        print(f"Initial simplified_form_responses: {case_info.get('simplified_form_responses', 'NOT FOUND')}")
    
    # Submit minimal data
    print("\nSubmitting minimal data...")
    test_data = {
        "nome_completo": "Test User Debug",
        "email": "debug@test.com",
        "pais_nascimento": "Brazil"
    }
    
    response = requests.post(
        f"{API_BASE}/case/{case_id}/friendly-form",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"Submit response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Submit success: {result.get('success')}")
        print(f"Validation status: {result.get('validation_status')}")
    else:
        print(f"Submit error: {response.text}")
    
    # Check final state
    print("\nChecking final case state...")
    response = requests.get(f"{API_BASE}/auto-application/case/{case_id}")
    if response.status_code == 200:
        case_info = response.json().get("case", {})
        print(f"Final simplified_form_responses: {case_info.get('simplified_form_responses', 'NOT FOUND')}")
        print(f"Basic data: {case_info.get('basic_data', 'NOT FOUND')}")
        print(f"Friendly form validation: {case_info.get('friendly_form_validation', 'NOT FOUND')}")
    else:
        print(f"Failed to get final case: {response.status_code}")

if __name__ == "__main__":
    test_data_save()