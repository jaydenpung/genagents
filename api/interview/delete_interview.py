from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import get_db, InterviewSession as DBInterviewSession

router = APIRouter(prefix="/interview", tags=["interview"])

@router.delete("/{session_id}")
async def delete_interview_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(DBInterviewSession).filter(DBInterviewSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    db.delete(session)
    db.commit()
    return {"message": "Interview session deleted successfully"} 