"""
Agent chat endpoints
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import time

from database import get_db, Agent as DBAgent
from genagents.genagents import GenerativeAgent
from api.models import ChatRequest, ChatResponse

# Import shared state
from api.shared_state import loaded_agents, conversation_histories

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

async def clear_conversation_history(agent_id: str):
    """
    Clear the conversation history for an agent
    """
    if agent_id in conversation_histories:
        del conversation_histories[agent_id]
    return {"message": "Conversation history cleared"}