"""
Interview session management endpoints
"""

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db, InterviewSession as DBInterviewSession
from api.models import InterviewSession
from api.utils import safe_len

async def list_interview_sessions(db: Session = Depends(get_db)):
    """
    List all interview sessions
    """
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

async def get_interview_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get details about an interview session
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    return InterviewSession(
        session_id=session_id,
        participant=session.participant_data,  # type: ignore
        current_question_index=session.current_question_index,  # type: ignore
        total_questions=len(session.questions_data) - 2,  # type: ignore
        responses=session.responses_data if session.responses_data is not None else [],  # type: ignore
        created_at=session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        status=session.status  # type: ignore
    )

async def delete_interview_session(session_id: str, db: Session = Depends(get_db)):
    """
    Delete an interview session
    """
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    db.delete(session)
    db.commit()
    return {"message": "Interview session deleted successfully"}