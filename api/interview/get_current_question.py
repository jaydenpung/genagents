from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_db, InterviewSession as DBInterviewSession
from api.models import QuestionResponse

router = APIRouter(prefix="/interview", tags=["interview"])

@router.get("/{session_id}/question", response_model=QuestionResponse)
async def get_current_question(session_id: str, db: Session = Depends(get_db)):
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