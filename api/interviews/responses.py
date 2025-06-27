"""
Interview response submission endpoint
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import time

from database import get_db, InterviewSession as DBInterviewSession
from genagents.genagents import GenerativeAgent
from api.models import SubmitResponseRequest
from api.interviews.questions import get_current_question
from api.shared_state import loaded_agents
from api.utils import safe_len

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