"""
Agent listing endpoint
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db, Agent as DBAgent

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