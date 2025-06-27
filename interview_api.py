"""
Web API for conducting interviews to create generative agents
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
import json
import time
import os
import uuid
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genagents.genagents import GenerativeAgent
from database import init_database, get_db, InterviewSession as DBInterviewSession, Agent as DBAgent, get_db_session

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

# In-memory storage for loaded agents and conversation histories (keep these)
loaded_agents: Dict[str, GenerativeAgent] = {}
conversation_histories: Dict[str, List[List[str]]] = {}

# Helper function to safely handle SQLAlchemy column values
def safe_len(value: Any) -> int:
    """Safely get length of a value that might be None"""
    return len(value) if value is not None else 0

# Helper function to get actual values from SQLAlchemy objects
def get_session_value(session_obj: Any, attr_name: str) -> Any:
    """Get the actual value from a SQLAlchemy session object"""
    return getattr(session_obj, attr_name)

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
async def start_interview(request: StartInterviewRequest, db: Session = Depends(get_db)):
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
        
        # Agent will be saved to database when finalized
        
        # Create database session record
        db_session = DBInterviewSession(
            session_id=session_id,
            participant_data=participant,
            questions_data=interview_data,
            responses_data=[],
            current_question_index=0,
            status="active",
            agent_path=save_dir
        )
        
        db.add(db_session)
        db.commit()
        
        # Keep agent in memory for current session
        loaded_agents[session_id] = agent
        
    except Exception as e:
        db.rollback()
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
async def get_current_question(session_id: str, db: Session = Depends(get_db)):
    """
    Get the current question for an interview session
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status != "active":  # type: ignore
        raise HTTPException(status_code=400, detail=f"Interview session is {session.status}")
    
    current_index = session.current_question_index
    questions = session.questions_data
    
    if current_index >= len(questions):  # type: ignore
        raise HTTPException(status_code=400, detail="Interview already completed")
    
    question_data = questions[current_index]
    question_text = question_data['question'].replace("<participant's name>", session.participant_data["first_name"])
    
    # Check if this is introduction or conclusion
    is_introduction = current_index == 0  # type: ignore
    is_conclusion = current_index == len(questions) - 1  # type: ignore
    
    return QuestionResponse(
        session_id=session_id,
        question_number=current_index,  # type: ignore
        total_questions=len(questions) - 2,  # type: ignore
        question=question_text,
        time_limit=question_data['timeLimit'],  # type: ignore
        is_introduction=is_introduction,  # type: ignore
        is_conclusion=is_conclusion  # type: ignore
    )

@app.post("/interview/response")
async def submit_response(request: SubmitResponseRequest, db: Session = Depends(get_db)):
    """
    Submit a response to the current question and advance to next question
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == request.session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status != "active":  # type: ignore
        raise HTTPException(status_code=400, detail=f"Interview session is {session.status}")
    
    current_index = session.current_question_index
    questions = session.questions_data
    
    if current_index >= len(questions):  # type: ignore
        raise HTTPException(status_code=400, detail="Interview already completed")
    
    # Save the response (skip for introduction)
    if current_index > 0:  # type: ignore
        question_data = questions[current_index]
        question_text = question_data['question'].replace("<participant's name>", session.participant_data["first_name"])
        
        response_record = {
            "question_number": current_index,
            "question": question_text,
            "response": request.response,
            "timestamp": time.time()
        }
        
        # Update responses in database
        responses = session.responses_data if session.responses_data is not None else []
        responses.append(response_record)
        session.responses_data = responses  # type: ignore
        
        # Update the agent with the new response
        try:
            # Get agent from memory or load from disk
            agent = None
            if request.session_id in loaded_agents:
                agent = loaded_agents[request.session_id]
            else:
                # Load agent from disk
                agent = GenerativeAgent(session.agent_path)
                loaded_agents[request.session_id] = agent
            
            response_text = request.response.strip()
            # Handle empty responses by using a placeholder
            if not response_text:
                response_text = "N/A"
            
            # Add the response as a memory
            agent.remember(response_text, time_step=len(responses))  # type: ignore
            
            # Agent updates are stored in memory until finalization
                
        except Exception as e:
            # Log the error but don't fail the response submission
            print(f"Warning: Failed to update agent: {str(e)}")
    
    # Move to next question
    session.current_question_index += 1  # type: ignore
    
    # Check if interview is complete
    if session.current_question_index >= len(questions):  # type: ignore
        session.status = "completed"  # type: ignore
        
        # All interview data is now stored in the database
    
    # Save changes to database
    db.commit()
    
    if session.status == "completed":  # type: ignore
        return {
            "message": "Interview completed",
            "session_id": request.session_id,
            "total_responses": safe_len(session.responses_data),
            "ready_for_agent_creation": True
        }
    
    # Return next question
    return await get_current_question(request.session_id, db)

@app.post("/interview/{session_id}/finalize", response_model=AgentCreationResponse)
async def finalize_agent_creation(session_id: str, db: Session = Depends(get_db)):
    """
    Finalize the agent creation (agent is already created and updated during interview)
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status != "completed":  # type: ignore
        raise HTTPException(status_code=400, detail="Interview must be completed before finalizing agent")
    
    try:
        # Load or get agent from memory
        agent = None
        if session_id in loaded_agents:
            agent = loaded_agents[session_id]
        else:
            agent = GenerativeAgent(session.agent_path)
        
        agent_path = session.agent_path
        
        # Create agent in database
        agent_id = str(uuid.uuid4())
        db_agent = DBAgent(
            agent_id=agent_id,
            name=f"{session.participant_data['first_name']} {session.participant_data['last_name']}",
            age=session.participant_data.get('age', 'Unknown'),
            participant_data=session.participant_data,
            memory_stream={
                "embeddings": agent.memory_stream.embeddings,
                "nodes": [node.package() for node in agent.memory_stream.seq_nodes]
            },
            scratch_data=agent.scratch
        )
        
        db.add(db_agent)
        
        # Update session status
        session.status = "agent_created"  # type: ignore
        db.commit()
        
        # Agent is now stored in database only
        
        return AgentCreationResponse(
            session_id=session_id,
            agent_path=agent_path,  # type: ignore
            total_responses=safe_len(session.responses_data),
            memory_nodes=len(agent.memory_stream.seq_nodes),
            message="Agent successfully finalized from interview responses"
        )
        
    except Exception as e:
        session.status = "error"  # type: ignore
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error finalizing agent: {str(e)}")

@app.get("/interview/sessions")
async def list_interview_sessions(db: Session = Depends(get_db)):
    """
    List all interview sessions
    """
    sessions = db.query(DBInterviewSession).all()
    
    sessions_summary = []
    for session in sessions:
        sessions_summary.append({
            "session_id": session.session_id,
            "participant_name": f"{session.participant_data['first_name']} {session.participant_data['last_name']}",
            "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": session.status,
            "progress": f"{safe_len(session.responses_data)}/{len(session.questions_data) - 2}"  # type: ignore
        })
    
    return {"sessions": sessions_summary}

@app.get("/interview/{session_id}", response_model=InterviewSession)
async def get_interview_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get details about an interview session
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    return InterviewSession(
        session_id=session_id,
        participant=session.participant_data,  # type: ignore
        current_question_index=session.current_question_index,  # type: ignore
        total_questions=len(session.questions_data) - 2,  # type: ignore
        responses=session.responses_data if session.responses_data is not None else [],  # type: ignore
        created_at=session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        status=session.status  # type: ignore
    )

@app.get("/agents")
async def list_created_agents(db: Session = Depends(get_db)):
    """
    List all created agents from the database
    """
    try:
        # Query agents from database
        db_agents = db.query(DBAgent).all()
        
        agents = []
        for agent in db_agents:
            agents.append({
                "agent_id": agent.agent_id,
                "name": agent.name,
                "age": agent.age,
                "created_date": agent.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "memory_nodes": len(agent.memory_stream.get('nodes', []))
            })
        
        # Sort by creation date (newest first)
        agents.sort(key=lambda x: x['created_date'], reverse=True)
        return {"agents": agents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading agents: {str(e)}")

@app.delete("/interview/{session_id}")
async def delete_interview_session(session_id: str, db: Session = Depends(get_db)):
    """
    Delete an interview session
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    db.delete(session)
    db.commit()
    return {"message": "Interview session deleted successfully"}

@app.get("/agents/{agent_id}")
async def get_agent_details(agent_id: str, db: Session = Depends(get_db)):
    """
    Get details about a specific agent from database
    """
    # Get agent from database
    db_agent = db.query(DBAgent).filter(DBAgent.agent_id == agent_id).first()
    
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        return {
            "agent_id": agent_id,
            "name": db_agent.name,
            "age": db_agent.age,
            "created_date": db_agent.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "participant": db_agent.participant_data,
            "memory_nodes": len(db_agent.memory_stream.get('nodes', [])),
            "scratch_data": db_agent.scratch_data
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading agent: {str(e)}")

@app.post("/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(agent_id: str, request: ChatRequest, db: Session = Depends(get_db)):
    """
    Send a message to an agent and get a response
    """
    # Get agent from database
    db_agent = db.query(DBAgent).filter(DBAgent.agent_id == agent_id).first()
    
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Load or reconstruct the agent
        if agent_id not in loaded_agents:
            # Reconstruct agent from database
            agent = GenerativeAgent()
            agent.scratch = db_agent.scratch_data
            
            # Reconstruct memory stream
            memory_data = db_agent.memory_stream
            if memory_data and 'nodes' in memory_data and 'embeddings' in memory_data:  # type: ignore
                # Import the proper ConceptNode class
                from genagents.modules.memory_stream import ConceptNode
                
                # Create proper ConceptNode objects from stored data
                nodes = []
                id_to_node = {}
                
                for node_data in memory_data['nodes']:
                    # Ensure all required fields exist with defaults
                    node_dict = {
                        "node_id": node_data.get("node_id", 0),
                        "node_type": node_data.get("node_type", "observation"),
                        "content": node_data.get("content", ""),
                        "importance": node_data.get("importance", 0),
                        "created": node_data.get("created", 0),
                        "last_retrieved": node_data.get("last_retrieved", 0),
                        "pointer_id": node_data.get("pointer_id", None)
                    }
                    node = ConceptNode(node_dict)
                    nodes.append(node)
                    # Build the id_to_node mapping
                    id_to_node[node.node_id] = node
                
                agent.memory_stream.seq_nodes = nodes
                agent.memory_stream.id_to_node = id_to_node
                agent.memory_stream.embeddings = memory_data['embeddings']
            
            loaded_agents[agent_id] = agent
        else:
            agent = loaded_agents[agent_id]
        
        # Get agent name
        agent_name = db_agent.name
        
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
                conversation_histories[agent_id].append([agent_name, response])  # type: ignore
        except Exception as e:
            print(f"Error generating utterance: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            # Another fallback
            response = f"I understand you said: '{request.message}'. Let me think about that based on my experiences..."
            conversation_histories[agent_id].append([agent_name, response])  # type: ignore
        
        return ChatResponse(
            agent_id=agent_id,
            agent_name=agent_name,  # type: ignore
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