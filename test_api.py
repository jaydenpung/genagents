"""
Test script for the Interview API
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_interview_api():
    """Test the complete interview flow"""
    
    print("Testing Interview API...")
    
    # 1. Start an interview
    print("\n1. Starting interview...")
    start_data = {
        "first_name": "Alice",
        "last_name": "Smith", 
        "age": "28",
        "additional_info": {
            "occupation": "Teacher",
            "location": "New York"
        }
    }
    
    response = requests.post(f"{BASE_URL}/interview/start", json=start_data)
    if response.status_code != 200:
        print(f"Error starting interview: {response.text}")
        return
    
    question_data = response.json()
    session_id = question_data["session_id"]
    print(f"Session ID: {session_id}")
    print(f"First question: {question_data['question'][:100]}...")
    
    # 2. Submit response to introduction (skip)
    print("\n2. Skipping introduction...")
    response = requests.post(f"{BASE_URL}/interview/response", json={
        "session_id": session_id,
        "response": "Ready to proceed"
    })
    
    # 3. Get a few questions and submit responses
    for i in range(3):
        print(f"\n3.{i+1}. Getting question {i+1}...")
        
        response = requests.get(f"{BASE_URL}/interview/{session_id}/question")
        if response.status_code != 200:
            print(f"Error getting question: {response.text}")
            break
            
        question_data = response.json()
        print(f"Question {question_data['question_number']}: {question_data['question'][:100]}...")
        
        # Submit a sample response
        sample_response = f"This is a sample response to question {i+1}. I'm providing meaningful content that would help create an accurate agent representation."
        
        response = requests.post(f"{BASE_URL}/interview/response", json={
            "session_id": session_id,
            "response": sample_response
        })
        
        if response.status_code != 200:
            print(f"Error submitting response: {response.text}")
            break
        
        print(f"Response submitted successfully")
    
    # 4. Get session status
    print(f"\n4. Getting session status...")
    response = requests.get(f"{BASE_URL}/interview/{session_id}")
    if response.status_code == 200:
        session_data = response.json()
        print(f"Session status: {session_data['status']}")
        print(f"Progress: {len(session_data['responses'])}/{session_data['total_questions']}")
    
    # 5. List all sessions
    print(f"\n5. Listing all sessions...")
    response = requests.get(f"{BASE_URL}/interview/sessions")
    if response.status_code == 200:
        sessions = response.json()
        print(f"Total sessions: {len(sessions['sessions'])}")
        for session in sessions['sessions']:
            print(f"  - {session['participant_name']}: {session['status']} ({session['progress']})")

if __name__ == "__main__":
    try:
        test_interview_api()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API. Make sure the server is running.")
        print("Start the server with: python interview_api.py")
    except Exception as e:
        print(f"Error: {e}")