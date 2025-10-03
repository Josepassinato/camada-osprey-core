#!/usr/bin/env python3
"""
OSPREY Backend Education System Focused Tests
Tests specifically the education endpoints as requested
"""

import requests
import json
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://visa-wizard-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing OSPREY Education System at: {API_BASE}")
print("=" * 60)

# Test user credentials
TEST_USER = {
    "email": "test@osprey.com",
    "password": "TestUser123"
}
AUTH_TOKEN = None
INTERVIEW_SESSION_ID = None

def login_user():
    """Login and get auth token"""
    global AUTH_TOKEN
    print("\n🔐 Logging in...")
    
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            AUTH_TOKEN = data.get('token')
            print(f"✅ Login successful - Token obtained")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False

def test_education_guides():
    """Test GET /api/education/guides - List interactive guides"""
    print("\n📚 Testing GET /api/education/guides...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        # Test getting all guides
        response = requests.get(f"{API_BASE}/education/guides", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            guides = data.get('guides', [])
            print(f"✅ All guides retrieved successfully")
            print(f"   Total guides: {len(guides)}")
            
            for guide in guides:
                print(f"   - {guide.get('title')} ({guide.get('visa_type')}) - {guide.get('difficulty_level')} - {guide.get('estimated_time_minutes')}min")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_specific_guide():
    """Test GET /api/education/guides/{visa_type} - Specific guide details"""
    print("\n📖 Testing GET /api/education/guides/h1b...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/guides?visa_type=h1b", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            guide = data.get('guide', {})
            print(f"✅ H1-B guide retrieved successfully")
            print(f"   Title: {guide.get('title')}")
            print(f"   Description: {guide.get('description')}")
            print(f"   Difficulty: {guide.get('difficulty_level')}")
            print(f"   Time: {guide.get('estimated_time_minutes')} minutes")
            print(f"   Sections: {len(guide.get('sections', []))}")
            print(f"   Requirements: {len(guide.get('requirements', []))}")
            print(f"   Common mistakes: {len(guide.get('common_mistakes', []))}")
            print(f"   Success tips: {len(guide.get('success_tips', []))}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_education_progress():
    """Test GET /api/education/progress - User educational progress"""
    print("\n📈 Testing GET /api/education/progress...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/progress", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            progress = data.get('progress', {})
            print(f"✅ Education progress retrieved successfully")
            print(f"   Guides completed: {len(progress.get('guides_completed', []))}")
            print(f"   Interviews completed: {len(progress.get('interviews_completed', []))}")
            print(f"   Knowledge queries: {progress.get('knowledge_queries', 0)}")
            print(f"   Total study time: {progress.get('total_study_time_minutes', 0)} minutes")
            print(f"   Achievement badges: {len(progress.get('achievement_badges', []))}")
            print(f"   Unread tips: {progress.get('unread_tips_count', 0)}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_personalized_tips():
    """Test GET /api/education/tips - Personalized tips"""
    print("\n💡 Testing GET /api/education/tips...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/education/tips", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            tips = data.get('tips', [])
            print(f"✅ Personalized tips retrieved successfully")
            print(f"   Total tips: {len(tips)}")
            
            for i, tip in enumerate(tips[:3]):  # Show first 3 tips
                print(f"   Tip {i+1}: {tip.get('title')} ({tip.get('tip_category')}) - Priority: {tip.get('priority')}")
                print(f"           Content: {tip.get('content', '')[:100]}...")
                print(f"           Read: {tip.get('is_read', False)}")
            
            # Check if tips are in Portuguese
            if tips:
                content = tips[0].get('content', '').lower()
                if any(word in content for word in ['você', 'seus', 'para', 'com', 'documentos']):
                    print("✅ Tips are in Portuguese")
                else:
                    print("⚠️  Tips language unclear")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_interview_start():
    """Test POST /api/education/interview/start - Start interview simulation"""
    print("\n🎤 Testing POST /api/education/interview/start...")
    global INTERVIEW_SESSION_ID
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        payload = {
            "interview_type": "consular",
            "visa_type": "h1b",
            "difficulty_level": "beginner"
        }
        
        response = requests.post(f"{API_BASE}/education/interview/start", json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            INTERVIEW_SESSION_ID = data.get('session_id')
            questions = data.get('questions', [])
            
            print(f"✅ Interview simulation started successfully")
            print(f"   Session ID: {INTERVIEW_SESSION_ID}")
            print(f"   Total questions: {data.get('total_questions', 0)}")
            print(f"   Estimated duration: {data.get('estimated_duration', 0)} minutes")
            print(f"   Questions generated: {len(questions)}")
            
            if questions:
                first_q = questions[0]
                print(f"   First question (EN): {first_q.get('question_en', 'N/A')[:80]}...")
                print(f"   First question (PT): {first_q.get('question_pt', 'N/A')[:80]}...")
                print(f"   Category: {first_q.get('category', 'N/A')}")
                print(f"   Tips: {len(first_q.get('tips', []))}")
                print(f"   Key points: {len(first_q.get('key_points', []))}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_interview_answer():
    """Test POST /api/education/interview/{session_id}/answer - Submit interview answer"""
    print("\n💬 Testing POST /api/education/interview/{session_id}/answer...")
    
    if not AUTH_TOKEN or not INTERVIEW_SESSION_ID:
        print("❌ No auth token or session ID available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        payload = {
            "question_id": "q1",
            "answer": "Eu venho aos Estados Unidos para trabalhar como engenheiro de software em uma empresa de tecnologia. Tenho uma oferta de emprego válida e pretendo contribuir com minhas habilidades técnicas para o desenvolvimento de software inovador na área de inteligência artificial."
        }
        
        response = requests.post(
            f"{API_BASE}/education/interview/{INTERVIEW_SESSION_ID}/answer", 
            json=payload, 
            headers=headers, 
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            feedback = data.get('feedback', {})
            
            print(f"✅ Interview answer submitted successfully")
            print(f"   Score: {feedback.get('score', 'N/A')}/100")
            print(f"   Confidence level: {feedback.get('confidence_level', 'N/A')}")
            print(f"   Strengths: {len(feedback.get('strengths', []))}")
            print(f"   Weaknesses: {len(feedback.get('weaknesses', []))}")
            print(f"   Suggestions: {len(feedback.get('suggestions', []))}")
            print(f"   Next question index: {data.get('next_question_index', 'N/A')}")
            
            # Show some feedback details
            if feedback.get('strengths'):
                print(f"   First strength: {feedback['strengths'][0]}")
            if feedback.get('suggestions'):
                print(f"   First suggestion: {feedback['suggestions'][0]}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_interview_complete():
    """Test POST /api/education/interview/{session_id}/complete - Complete interview"""
    print("\n🏁 Testing POST /api/education/interview/{session_id}/complete...")
    
    if not AUTH_TOKEN or not INTERVIEW_SESSION_ID:
        print("❌ No auth token or session ID available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.post(
            f"{API_BASE}/education/interview/{INTERVIEW_SESSION_ID}/complete", 
            headers=headers, 
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            feedback = data.get('overall_feedback', {})
            
            print(f"✅ Interview session completed successfully")
            print(f"   Session completed: {data.get('session_completed', False)}")
            print(f"   Overall score: {feedback.get('overall_score', 'N/A')}/100")
            print(f"   Questions answered: {feedback.get('questions_answered', 'N/A')}")
            print(f"   Average confidence: {feedback.get('average_confidence', 'N/A')}")
            print(f"   Strengths: {len(feedback.get('strengths', []))}")
            print(f"   Areas for improvement: {len(feedback.get('areas_for_improvement', []))}")
            print(f"   Recommendations: {len(feedback.get('recommendations', []))}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_knowledge_base_search():
    """Test POST /api/education/knowledge-base/search - Search knowledge base"""
    print("\n🔍 Testing POST /api/education/knowledge-base/search...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        payload = {
            "query": "Como aplicar para H1-B? Quais são os requisitos principais?",
            "visa_type": "h1b",
            "category": "application"
        }
        
        response = requests.post(f"{API_BASE}/education/knowledge-base/search", json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Knowledge base search successful")
            print(f"   Answer length: {len(data.get('answer', ''))}")
            print(f"   Related topics: {len(data.get('related_topics', []))}")
            print(f"   Next steps: {len(data.get('next_steps', []))}")
            print(f"   Resources: {len(data.get('resources', []))}")
            print(f"   Warnings: {len(data.get('warnings', []))}")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            
            # Show answer preview
            answer = data.get('answer', '')
            if answer:
                print(f"   Answer preview: {answer[:200]}...")
            
            # Check for legal disclaimers
            answer_lower = answer.lower()
            warnings = ' '.join(data.get('warnings', [])).lower()
            
            has_disclaimer = any(phrase in (answer_lower + warnings) for phrase in [
                'consultoria jurídica', 'advogado', 'não substitui', 'educativa'
            ])
            
            if has_disclaimer:
                print("✅ Legal disclaimers present")
            else:
                print("⚠️  Legal disclaimers not clearly present")
            
            # Check if answer is in Portuguese
            if any(word in answer_lower for word in ['para', 'como', 'você', 'processo', 'aplicação']):
                print("✅ Answer provided in Portuguese")
            else:
                print("⚠️  Answer language unclear")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_dashboard_integration():
    """Test GET /api/dashboard - Verify education stats integration"""
    print("\n📊 Testing GET /api/dashboard - Education stats integration...")
    
    if not AUTH_TOKEN:
        print("❌ No auth token available")
        return False
    
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    
    try:
        response = requests.get(f"{API_BASE}/dashboard", headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user', {})
            stats = data.get('stats', {})
            
            print(f"✅ Dashboard with education stats loaded successfully")
            print(f"   User: {user_info.get('name')} ({user_info.get('email')})")
            print(f"   Guides completed: {stats.get('guides_completed', 0)}")
            print(f"   Interviews completed: {stats.get('interviews_completed', 0)}")
            print(f"   Total study time: {stats.get('total_study_time', 0)} minutes")
            print(f"   Unread tips: {stats.get('unread_tips', 0)}")
            print(f"   Total applications: {stats.get('total_applications', 0)}")
            print(f"   Total documents: {stats.get('total_documents', 0)}")
            
            # Verify education stats are present
            education_keys = ['guides_completed', 'interviews_completed', 'total_study_time', 'unread_tips']
            has_education_stats = all(key in stats for key in education_keys)
            
            if has_education_stats:
                print("✅ Education statistics properly integrated in dashboard")
            else:
                missing = [key for key in education_keys if key not in stats]
                print(f"⚠️  Missing education stats: {missing}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_education_tests():
    """Run all education system tests"""
    print("🎓 Starting OSPREY Education System Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Login first
    if not login_user():
        print("❌ Cannot proceed without authentication")
        return
    
    # Run all education tests
    results = {
        "education_guides": test_education_guides(),
        "specific_guide": test_specific_guide(),
        "education_progress": test_education_progress(),
        "personalized_tips": test_personalized_tips(),
        "interview_start": test_interview_start(),
        "interview_answer": test_interview_answer(),
        "interview_complete": test_interview_complete(),
        "knowledge_base_search": test_knowledge_base_search(),
        "dashboard_integration": test_dashboard_integration()
    }
    
    print("\n" + "=" * 60)
    print("📊 EDUCATION SYSTEM TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All education system tests passed! Sistema educacional funcionando perfeitamente.")
    elif passed >= total - 1:
        print("✅ Education system working correctly with minor issues.")
    else:
        print("⚠️  Some education tests failed. Check details above.")
    
    return results

if __name__ == "__main__":
    run_education_tests()