"""
Web API for conducting interviews to create generative agents
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import time
import os
import uuid
from genagents.genagents import GenerativeAgent

app = FastAPI(title="Generative Agent Interview API", version="1.0.0")

# In-memory storage for interview sessions
interview_sessions: Dict[str, dict] = {}

class StartInterviewRequest(BaseModel):
    first_name: str
    last_name: str
    age: str
    additional_info: Optional[Dict[str, str]] = None

class SubmitResponseRequest(BaseModel):
    session_id: str
    response: str

class InterviewSession(BaseModel):
    session_id: str
    participant: Dict[str, str]
    current_question_index: int
    total_questions: int
    responses: List[Dict]
    created_at: str
    status: str  # "active", "completed", "error"

class QuestionResponse(BaseModel):
    session_id: str
    question_number: int
    total_questions: int
    question: str
    time_limit: int
    is_introduction: bool = False
    is_conclusion: bool = False

class AgentCreationResponse(BaseModel):
    session_id: str
    agent_path: str
    total_responses: int
    memory_nodes: int
    message: str

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Generative Agent Interview API",
        "version": "1.0.0",
        "endpoints": {
            "start_interview": "POST /interview/start",
            "get_question": "GET /interview/{session_id}/question",
            "submit_response": "POST /interview/response",
            "finalize_agent": "POST /interview/{session_id}/finalize",
            "get_session": "GET /interview/{session_id}",
            "list_sessions": "GET /interview/sessions"
        }
    }

@app.post("/interview/start", response_model=QuestionResponse)
async def start_interview(request: StartInterviewRequest):
    """
    Start a new interview session
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Load interview questions
    try:
        with open('interview_questions.json', 'r') as f:
            interview_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Interview questions file not found")
    
    # Create session
    session = {
        "session_id": session_id,
        "participant": {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "age": request.age,
            **(request.additional_info or {})
        },
        "questions": interview_data,
        "current_question_index": 0,
        "responses": [],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    
    interview_sessions[session_id] = session
    
    # Return first question (introduction)
    first_question = interview_data[0]
    question_text = first_question['question'].replace("<participant's name>", request.first_name)
    
    return QuestionResponse(
        session_id=session_id,
        question_number=0,
        total_questions=len(interview_data) - 2,  # Exclude intro and outro
        question=question_text,
        time_limit=first_question['timeLimit'],
        is_introduction=True
    )

@app.get("/interview/{session_id}/question", response_model=QuestionResponse)
async def get_current_question(session_id: str):
    """
    Get the current question for an interview session
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = interview_sessions[session_id]
    
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail=f"Interview session is {session['status']}")
    
    current_index = session["current_question_index"]
    questions = session["questions"]
    
    if current_index >= len(questions):
        raise HTTPException(status_code=400, detail="Interview already completed")
    
    question_data = questions[current_index]
    question_text = question_data['question'].replace("<participant's name>", session["participant"]["first_name"])
    
    # Check if this is introduction or conclusion
    is_introduction = current_index == 0
    is_conclusion = current_index == len(questions) - 1
    
    return QuestionResponse(
        session_id=session_id,
        question_number=current_index,
        total_questions=len(questions) - 2,
        question=question_text,
        time_limit=question_data['timeLimit'],
        is_introduction=is_introduction,
        is_conclusion=is_conclusion
    )

@app.post("/interview/response")
async def submit_response(request: SubmitResponseRequest):
    """
    Submit a response to the current question and advance to next question
    """
    if request.session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = interview_sessions[request.session_id]
    
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail=f"Interview session is {session['status']}")
    
    current_index = session["current_question_index"]
    questions = session["questions"]
    
    if current_index >= len(questions):
        raise HTTPException(status_code=400, detail="Interview already completed")
    
    # Save the response (skip for introduction)
    if current_index > 0:
        question_data = questions[current_index]
        question_text = question_data['question'].replace("<participant's name>", session["participant"]["first_name"])
        
        response_record = {
            "question_number": current_index,
            "question": question_text,
            "response": request.response,
            "timestamp": time.time()
        }
        session["responses"].append(response_record)
    
    # Move to next question
    session["current_question_index"] += 1
    
    # Check if interview is complete
    if session["current_question_index"] >= len(questions):
        session["status"] = "completed"
        return {
            "message": "Interview completed",
            "session_id": request.session_id,
            "total_responses": len(session["responses"]),
            "ready_for_agent_creation": True
        }
    
    # Return next question
    return await get_current_question(request.session_id)

@app.post("/interview/{session_id}/finalize", response_model=AgentCreationResponse)
async def finalize_agent_creation(session_id: str):
    """
    Create the generative agent from interview responses
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = interview_sessions[session_id]
    
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Interview must be completed before creating agent")
    
    try:
        # Create the agent
        agent = GenerativeAgent()
        
        # Set up basic information
        participant = session["participant"]
        agent.update_scratch({
            "first_name": participant["first_name"],
            "last_name": participant["last_name"],
            "age": participant["age"],
            **{k: v for k, v in participant.items() if k not in ["first_name", "last_name", "age"]}
        })
        
        # Add all responses as memories
        for i, response_data in enumerate(session["responses"]):
            agent.remember(response_data["response"], time_step=i + 1)
        
        # Save the agent
        timestamp = int(time.time())
        save_dir = f"agent_bank/interview_agents/interview_{participant['first_name'].lower()}_{participant['last_name'].lower()}_{timestamp}"
        agent.save(save_dir)
        
        # Save the interview data
        interview_file = os.path.join(save_dir, "interview_data.json")
        with open(interview_file, 'w') as f:
            json.dump({
                "session_id": session_id,
                "participant": participant,
                "interview_date": session["created_at"],
                "completion_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "responses": session["responses"]
            }, f, indent=2)
        
        # Update session status
        session["status"] = "agent_created"
        session["agent_path"] = save_dir
        
        return AgentCreationResponse(
            session_id=session_id,
            agent_path=save_dir,
            total_responses=len(session["responses"]),
            memory_nodes=len(agent.memory_stream.seq_nodes),
            message="Agent successfully created from interview responses"
        )
        
    except Exception as e:
        session["status"] = "error"
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@app.get("/interview/{session_id}", response_model=InterviewSession)
async def get_interview_session(session_id: str):
    """
    Get details about an interview session
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = interview_sessions[session_id]
    
    return InterviewSession(
        session_id=session_id,
        participant=session["participant"],
        current_question_index=session["current_question_index"],
        total_questions=len(session["questions"]) - 2,
        responses=session["responses"],
        created_at=session["created_at"],
        status=session["status"]
    )

@app.get("/interview/sessions")
async def list_interview_sessions():
    """
    List all interview sessions
    """
    sessions_summary = []
    for session_id, session in interview_sessions.items():
        sessions_summary.append({
            "session_id": session_id,
            "participant_name": f"{session['participant']['first_name']} {session['participant']['last_name']}",
            "created_at": session["created_at"],
            "status": session["status"],
            "progress": f"{len(session['responses'])}/{len(session['questions']) - 2}"
        })
    
    return {"sessions": sessions_summary}

@app.delete("/interview/{session_id}")
async def delete_interview_session(session_id: str):
    """
    Delete an interview session
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    del interview_sessions[session_id]
    return {"message": "Interview session deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)