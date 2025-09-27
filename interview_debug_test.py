#!/usr/bin/env python3
"""
Debug test for interview answer submission
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visawiz.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Login first
login_payload = {
    "email": "test@osprey.com",
    "password": "TestUser123"
}

print("🔐 Logging in...")
login_response = requests.post(f"{API_BASE}/auth/login", json=login_payload, timeout=10)
if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    exit(1)

auth_token = login_response.json().get('token')
headers = {"Authorization": f"Bearer {auth_token}"}
print("✅ Login successful")

# Start interview
print("\n🎤 Starting interview...")
interview_payload = {
    "interview_type": "consular",
    "visa_type": "h1b",
    "difficulty_level": "beginner"
}

interview_response = requests.post(f"{API_BASE}/education/interview/start", json=interview_payload, headers=headers, timeout=60)
if interview_response.status_code != 200:
    print(f"❌ Interview start failed: {interview_response.status_code}")
    print(interview_response.text)
    exit(1)

session_data = interview_response.json()
session_id = session_data.get('session_id')
questions = session_data.get('questions', [])
print(f"✅ Interview started - Session: {session_id}")
print(f"   Questions: {len(questions)}")

if questions:
    first_question = questions[0]
    print(f"   First question ID: {first_question.get('id')}")
    print(f"   Question (PT): {first_question.get('question_pt', 'N/A')}")

# Try to submit answer with shorter timeout and simpler answer
print("\n💬 Submitting answer...")
answer_payload = {
    "question_id": first_question.get('id', 'q1'),
    "answer": "Eu venho trabalhar como engenheiro de software."
}

try:
    answer_response = requests.post(
        f"{API_BASE}/education/interview/{session_id}/answer", 
        json=answer_payload, 
        headers=headers, 
        timeout=30
    )
    
    print(f"Response status: {answer_response.status_code}")
    print(f"Response headers: {dict(answer_response.headers)}")
    print(f"Response text: {answer_response.text}")
    
    if answer_response.status_code == 200:
        print("✅ Answer submitted successfully")
        data = answer_response.json()
        feedback = data.get('feedback', {})
        print(f"   Score: {feedback.get('score', 'N/A')}")
        print(f"   Confidence: {feedback.get('confidence_level', 'N/A')}")
    else:
        print(f"❌ Answer submission failed: {answer_response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except Exception as e:
    print(f"❌ Error: {str(e)}")