"""
Main API router that combines all endpoints
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import init_database, get_db

# Import endpoint functions
from api.interviews.start import start_interview
from api.interviews.questions import get_current_question
from api.interviews.responses import submit_response
from api.interviews.finalize import finalize_agent_creation
from api.interviews.sessions import list_interview_sessions, get_interview_session, delete_interview_session
from api.agents.list import list_created_agents
from api.agents.details import get_agent_details
from api.agents.chat import chat_with_agent, clear_conversation_history

# Import models for request/response types
from api.models import (
    StartInterviewRequest, SubmitResponseRequest, ChatRequest,
    QuestionResponse, AgentCreationResponse, InterviewSession, ChatResponse
)

app = FastAPI(title="Generative Agent Interview API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://genagents.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_database()

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

# Interview endpoints
@app.post("/interview/start", response_model=QuestionResponse)
async def start_interview_endpoint(request: StartInterviewRequest, db: Session = Depends(get_db)):
    return await start_interview(request, db)

@app.get("/interview/{session_id}/question", response_model=QuestionResponse)
async def get_current_question_endpoint(session_id: str, db: Session = Depends(get_db)):
    return await get_current_question(session_id, db)

@app.post("/interview/response")
async def submit_response_endpoint(request: SubmitResponseRequest, db: Session = Depends(get_db)):
    return await submit_response(request, db)

@app.post("/interview/{session_id}/finalize", response_model=AgentCreationResponse)
async def finalize_agent_creation_endpoint(session_id: str, db: Session = Depends(get_db)):
    return await finalize_agent_creation(session_id, db)

@app.get("/interview/sessions")
async def list_interview_sessions_endpoint(db: Session = Depends(get_db)):
    return await list_interview_sessions(db)

@app.get("/interview/{session_id}", response_model=InterviewSession)
async def get_interview_session_endpoint(session_id: str, db: Session = Depends(get_db)):
    return await get_interview_session(session_id, db)

@app.delete("/interview/{session_id}")
async def delete_interview_session_endpoint(session_id: str, db: Session = Depends(get_db)):
    return await delete_interview_session(session_id, db)

# Agent endpoints
@app.get("/agents")
async def list_created_agents_endpoint(db: Session = Depends(get_db)):
    return await list_created_agents(db)

@app.get("/agents/{agent_id}")
async def get_agent_details_endpoint(agent_id: str, db: Session = Depends(get_db)):
    return await get_agent_details(agent_id, db)

@app.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent_endpoint(agent_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    return await chat_with_agent(agent_id, request, db)

@app.delete("/agents/{agent_id}/chat")
async def clear_conversation_history_endpoint(agent_id: str):
    return await clear_conversation_history(agent_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)