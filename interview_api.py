"""
Web API for conducting interviews to create generative agents
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import time
import os
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genagents.genagents import GenerativeAgent

app = FastAPI(title="Generative Agent Interview API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ChatRequest(BaseModel):
    agent_id: str
    message: str

class ChatResponse(BaseModel):
    agent_id: str
    agent_name: str
    response: str
    timestamp: str

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
    
    try:
        # Create the agent immediately
        agent = GenerativeAgent()
        
        # Set up basic information
        participant = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "age": request.age,
            **(request.additional_info or {})
        }
        
        agent.update_scratch({
            "first_name": participant["first_name"],
            "last_name": participant["last_name"],
            "age": participant["age"],
            **{k: v for k, v in participant.items() if k not in ["first_name", "last_name", "age"]}
        })
        
        # Create agent directory
        timestamp = int(time.time())
        save_dir = f"agent_bank/interview_agents/interview_{participant['first_name'].lower()}_{participant['last_name'].lower()}_{timestamp}"
        os.makedirs(save_dir, exist_ok=True)
        
        # Save initial agent
        agent.save(save_dir)
        
        # Create session with agent info
        session = {
            "session_id": session_id,
            "participant": participant,
            "questions": interview_data,
            "current_question_index": 0,
            "responses": [],
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active",
            "agent_path": save_dir,
            "agent": agent
        }
        
        interview_sessions[session_id] = session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")
    
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
        
        # Update the agent with the new response
        try:
            agent = session["agent"]
            response_text = request.response.strip()
            # Handle empty responses by using a placeholder
            if not response_text:
                response_text = "N/A"
            
            # Add the response as a memory
            agent.remember(response_text, time_step=len(session["responses"]))
            
            # Save the updated agent
            agent.save(session["agent_path"])
            
            # Save the updated interview data
            interview_file = os.path.join(session["agent_path"], "interview_data.json")
            with open(interview_file, 'w') as f:
                json.dump({
                    "session_id": request.session_id,
                    "participant": session["participant"],
                    "interview_date": session["created_at"],
                    "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "responses": session["responses"],
                    "status": session["status"]
                }, f, indent=2)
                
        except Exception as e:
            # Log the error but don't fail the response submission
            print(f"Warning: Failed to update agent: {str(e)}")
    
    # Move to next question
    session["current_question_index"] += 1
    
    # Check if interview is complete
    if session["current_question_index"] >= len(questions):
        session["status"] = "completed"
        
        # Save final interview data
        try:
            interview_file = os.path.join(session["agent_path"], "interview_data.json")
            with open(interview_file, 'w') as f:
                json.dump({
                    "session_id": request.session_id,
                    "participant": session["participant"],
                    "interview_date": session["created_at"],
                    "completion_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "responses": session["responses"],
                    "status": "completed"
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save final interview data: {str(e)}")
            
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
    Finalize the agent creation (agent is already created and updated during interview)
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    session = interview_sessions[session_id]
    
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Interview must be completed before finalizing agent")
    
    try:
        # Agent is already created and updated, just finalize
        agent = session["agent"]
        agent_path = session["agent_path"]
        
        # Update session status
        session["status"] = "agent_created"
        
        # Save final agent state
        agent.save(agent_path)
        
        return AgentCreationResponse(
            session_id=session_id,
            agent_path=agent_path,
            total_responses=len(session["responses"]),
            memory_nodes=len(agent.memory_stream.seq_nodes),
            message="Agent successfully finalized from interview responses"
        )
        
    except Exception as e:
        session["status"] = "error"
        raise HTTPException(status_code=500, detail=f"Error finalizing agent: {str(e)}")

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

@app.get("/agents")
async def list_created_agents():
    """
    List all created agents from the agent_bank
    """
    agents = []
    agent_bank_path = "agent_bank/interview_agents"
    
    if not os.path.exists(agent_bank_path):
        return {"agents": []}
    
    try:
        for agent_dir in os.listdir(agent_bank_path):
            agent_path = os.path.join(agent_bank_path, agent_dir)
            if os.path.isdir(agent_path):
                # Try to read the interview data
                interview_data_path = os.path.join(agent_path, "interview_data.json")
                if os.path.exists(interview_data_path):
                    try:
                        with open(interview_data_path, 'r') as f:
                            interview_data = json.load(f)
                        
                        # Get agent metadata
                        meta_path = os.path.join(agent_path, "meta.json")
                        agent_meta = {}
                        if os.path.exists(meta_path):
                            with open(meta_path, 'r') as f:
                                agent_meta = json.load(f)
                        
                        agents.append({
                            "agent_id": agent_dir,
                            "name": f"{interview_data['participant']['first_name']} {interview_data['participant']['last_name']}",
                            "age": interview_data['participant'].get('age', 'Unknown'),
                            "created_date": interview_data.get('completion_date', interview_data.get('interview_date', 'Unknown')),
                            "total_responses": len(interview_data.get('responses', [])),
                            "agent_path": agent_path,
                            "session_id": interview_data.get('session_id', 'Unknown')
                        })
                    except (json.JSONDecodeError, KeyError) as e:
                        # If we can't read the data, create a basic entry
                        agents.append({
                            "agent_id": agent_dir,
                            "name": agent_dir.replace('_', ' ').title(),
                            "age": "Unknown",
                            "created_date": "Unknown",
                            "total_responses": 0,
                            "agent_path": agent_path,
                            "session_id": "Unknown"
                        })
        
        # Sort by creation date (newest first)
        agents.sort(key=lambda x: x['created_date'], reverse=True)
        return {"agents": agents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading agents: {str(e)}")

@app.delete("/interview/{session_id}")
async def delete_interview_session(session_id: str):
    """
    Delete an interview session
    """
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    del interview_sessions[session_id]
    return {"message": "Interview session deleted successfully"}

# In-memory storage for loaded agents and conversation histories
loaded_agents: Dict[str, GenerativeAgent] = {}
conversation_histories: Dict[str, List[List[str]]] = {}

@app.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str):
    """
    Get details about a specific agent
    """
    agent_path = f"agent_bank/interview_agents/{agent_id}"
    
    if not os.path.exists(agent_path):
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Try to read the interview data
        interview_data_path = os.path.join(agent_path, "interview_data.json")
        if os.path.exists(interview_data_path):
            with open(interview_data_path, 'r') as f:
                interview_data = json.load(f)
            
            return {
                "agent_id": agent_id,
                "name": f"{interview_data['participant']['first_name']} {interview_data['participant']['last_name']}",
                "age": interview_data['participant'].get('age', 'Unknown'),
                "created_date": interview_data.get('completion_date', interview_data.get('interview_date', 'Unknown')),
                "total_responses": len(interview_data.get('responses', [])),
                "agent_path": agent_path,
                "session_id": interview_data.get('session_id', 'Unknown'),
                "participant": interview_data.get('participant', {}),
                "status": interview_data.get('status', 'Unknown')
            }
        else:
            raise HTTPException(status_code=404, detail="Agent data not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading agent: {str(e)}")

@app.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(agent_id: str, request: ChatRequest):
    """
    Send a message to an agent and get a response
    """
    agent_path = f"agent_bank/interview_agents/{agent_id}"
    
    if not os.path.exists(agent_path):
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Load or get the agent
        if agent_id not in loaded_agents:
            # Load the agent from disk by passing the folder path to constructor
            agent = GenerativeAgent(agent_path)
            loaded_agents[agent_id] = agent
        else:
            agent = loaded_agents[agent_id]
        
        # Get agent name
        interview_data_path = os.path.join(agent_path, "interview_data.json")
        agent_name = "Agent"
        if os.path.exists(interview_data_path):
            with open(interview_data_path, 'r') as f:
                interview_data = json.load(f)
                agent_name = f"{interview_data['participant']['first_name']} {interview_data['participant']['last_name']}"
        
        # Get or initialize conversation history for this agent
        if agent_id not in conversation_histories:
            conversation_histories[agent_id] = []
        
        # Add user message to conversation history
        conversation_histories[agent_id].append(["User", request.message])
        
        # Generate response from agent using the full conversation history
        try:
            if hasattr(agent, 'utterance') and callable(getattr(agent, 'utterance')):
                # Use the conversation history as done in main.py
                response = agent.utterance(conversation_histories[agent_id])
                
                # Add agent's response to conversation history
                conversation_histories[agent_id].append([agent.get_fullname(), response])
            else:
                # Fallback: create a simple response based on agent's memories
                response = f"As {agent_name}, I remember my experiences from the interview. You said: '{request.message}'. Based on what I shared during my interview, I think..."
                conversation_histories[agent_id].append([agent_name, response])
        except Exception as e:
            print(f"Error generating utterance: {str(e)}")
            # Another fallback
            response = f"I understand you said: '{request.message}'. Let me think about that based on my experiences..."
            conversation_histories[agent_id].append([agent_name, response])
        
        return ChatResponse(
            agent_id=agent_id,
            agent_name=agent_name,
            response=response,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error chatting with agent: {str(e)}")

@app.delete("/agents/{agent_id}/chat")
async def clear_conversation_history(agent_id: str):
    """
    Clear the conversation history for an agent
    """
    if agent_id in conversation_histories:
        del conversation_histories[agent_id]
    return {"message": "Conversation history cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)