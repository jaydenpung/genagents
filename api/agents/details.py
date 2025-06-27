"""
Agent details endpoint
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db, Agent as DBAgent

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