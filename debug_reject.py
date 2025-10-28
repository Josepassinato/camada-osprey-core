#!/usr/bin/env python3
"""
Debug the reject endpoint
"""

import requests
import json

# Get backend URL
API_BASE = "https://agente-coruja.preview.emergentagent.com/api"

# Get a pending update ID
response = requests.get(f"{API_BASE}/admin/visa-updates/pending")
if response.status_code == 200:
    data = response.json()
    updates = data.get('updates', [])
    if updates:
        update_id = updates[0]['id']
        print(f"Testing reject with update ID: {update_id}")
        
        # Test reject
        rejection_data = {
            "admin_notes": "debug test rejection",
            "admin_user": "debug_admin"
        }
        
        reject_response = requests.post(
            f"{API_BASE}/admin/visa-updates/{update_id}/reject",
            json=rejection_data
        )
        
        print(f"Reject response status: {reject_response.status_code}")
        print(f"Reject response: {reject_response.text}")
        
        # Check if it was rejected by getting pending again
        check_response = requests.get(f"{API_BASE}/admin/visa-updates/pending")
        if check_response.status_code == 200:
            check_data = check_response.json()
            remaining_updates = len(check_data.get('updates', []))
            print(f"Remaining pending updates: {remaining_updates}")
    else:
        print("No pending updates found")
else:
    print(f"Failed to get pending updates: {response.status_code}")