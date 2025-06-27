from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_db, InterviewSession as DBInterviewSession
from api.utils import safe_len

router = APIRouter(prefix="/interview", tags=["interview"])

@router.get("/sessions")
async def list_interview_sessions(db: Session = Depends(get_db)):
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