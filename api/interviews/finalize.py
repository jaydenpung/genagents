"""
Interview finalization endpoint
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import uuid

from database import get_db, InterviewSession as DBInterviewSession, Agent as DBAgent
from genagents.genagents import GenerativeAgent
from api.models import AgentCreationResponse
from api.shared_state import loaded_agents
from api.utils import safe_len

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
        # Get agent from memory (it should always be there after interview)
        if session_id not in loaded_agents:
            print(f"Agent not in memory for session {session_id}, creating new one...")
            # If agent is not in memory, create a new one with interview responses
            agent = GenerativeAgent()
            print(f"Created agent, has memory_stream: {hasattr(agent, 'memory_stream')}")
            
            # Set up basic information
            participant = session.participant_data
            agent.update_scratch({
                "first_name": participant["first_name"],
                "last_name": participant["last_name"],
                "age": participant["age"],
                **{k: v for k, v in participant.items() if k not in ["first_name", "last_name", "age"]}
            })
            
            # Add interview responses as memories
            responses = session.responses_data if session.responses_data is not None else []
            print(f"Adding {len(responses)} responses as memories...")
            for i, response in enumerate(responses):
                if response.get("response") and response["response"].strip():
                    agent.remember(response["response"].strip(), time_step=i)
            
            loaded_agents[session_id] = agent
        
        agent = loaded_agents[session_id]
        print(f"Using agent, has memory_stream: {hasattr(agent, 'memory_stream')}")
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