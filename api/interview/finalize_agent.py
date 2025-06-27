from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genagents.genagents import GenerativeAgent
from database import get_db, InterviewSession as DBInterviewSession, Agent as DBAgent
from api.models import AgentCreationResponse
from api.utils import safe_len

router = APIRouter(prefix="/interview", tags=["interview"])

# In-memory storage for loaded agents
loaded_agents = {}

@router.post("/{session_id}/finalize", response_model=AgentCreationResponse)
async def finalize_agent_creation(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.status != "completed":  # type: ignore
        raise HTTPException(status_code=400, detail="Interview must be completed before finalizing agent")
    try:
        agent = None
        if session_id in loaded_agents:
            agent = loaded_agents[session_id]
        else:
            agent = GenerativeAgent(session.agent_path)
        agent_path = session.agent_path
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
        session.status = "agent_created"  # type: ignore
        db.commit()
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