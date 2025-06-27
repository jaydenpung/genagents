from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genagents.genagents import GenerativeAgent
from database import get_db, InterviewSession as DBInterviewSession
from api.models import SubmitResponseRequest
from api.utils import safe_len
from .get_current_question import get_current_question

router = APIRouter(prefix="/interview", tags=["interview"])

# In-memory storage for loaded agents
loaded_agents = {}

@router.post("/response")
async def submit_response(request: SubmitResponseRequest, db: Session = Depends(get_db)):
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    if session.status != "active":  # type: ignore
        raise HTTPException(status_code=400, detail=f"Interview session is {session.status}")
    current_index = session.current_question_index
    questions = session.questions_data
    if current_index >= len(questions):  # type: ignore
        raise HTTPException(status_code=400, detail="Interview already completed")
    if current_index > 0:  # type: ignore
        question_data = questions[current_index]
        question_text = question_data['question'].replace("<participant's name>", session.participant_data["first_name"])
        response_record = {
            "question_number": current_index,
            "question": question_text,
            "response": request.response,
            "timestamp": time.time()
        }
        responses = session.responses_data if session.responses_data is not None else []
        responses.append(response_record)
        session.responses_data = responses  # type: ignore
        try:
            agent = None
            if request.session_id in loaded_agents:
                agent = loaded_agents[request.session_id]
            else:
                agent = GenerativeAgent(session.agent_path)
                loaded_agents[request.session_id] = agent
            response_text = request.response.strip()
            if not response_text:
                response_text = "N/A"
            agent.remember(response_text, time_step=len(responses))  # type: ignore
        except Exception as e:
            print(f"Warning: Failed to update agent: {str(e)}")
    session.current_question_index += 1  # type: ignore
    if session.current_question_index >= len(questions):  # type: ignore
        session.status = "completed"  # type: ignore
    db.commit()
    if session.status == "completed":  # type: ignore
        return {
            "message": "Interview completed",
            "session_id": request.session_id,
            "total_responses": safe_len(session.responses_data),
            "ready_for_agent_creation": True
        }
    return await get_current_question(request.session_id, db) 