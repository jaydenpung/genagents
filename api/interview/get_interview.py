from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_db, InterviewSession as DBInterviewSession
from api.models import InterviewSession as InterviewSessionModel

router = APIRouter(prefix="/interview", tags=["interview"])

@router.get("/{session_id}", response_model=InterviewSessionModel)
async def get_interview_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return InterviewSessionModel(
        session_id=session_id,
        participant=session.participant_data,  # type: ignore
        current_question_index=session.current_question_index,  # type: ignore
        total_questions=len(session.questions_data) - 2,  # type: ignore
        responses=session.responses_data if session.responses_data is not None else [],  # type: ignore
        created_at=session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        status=session.status  # type: ignore
    ) 