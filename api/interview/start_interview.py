from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import time
import os
import uuid
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genagents.genagents import GenerativeAgent
from database import get_db, InterviewSession as DBInterviewSession
from api.models import StartInterviewRequest, QuestionResponse

router = APIRouter(prefix="/interview", tags=["interview"])

# In-memory storage for loaded agents
loaded_agents = {}

@router.post("/start", response_model=QuestionResponse)
async def start_interview(request: StartInterviewRequest, db: Session = Depends(get_db)):
    """
    Start a new interview session
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Load interview questions
    try:
        with open('interview_questions.json', 'r') as f:
            interview_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Interview questions file not found")
    
    try:
        # Create the agent immediately
        agent = GenerativeAgent()
        
        # Set up basic information
        participant = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "age": request.age,
            **(request.additional_info or {})
        }
        
        agent.update_scratch({
            "first_name": participant["first_name"],
            "last_name": participant["last_name"],
            "age": participant["age"],
            **{k: v for k, v in participant.items() if k not in ["first_name", "last_name", "age"]}
        })
        
        # Create agent directory
        timestamp = int(time.time())
        save_dir = f"agent_bank/interview_agents/interview_{participant['first_name'].lower()}_{participant['last_name'].lower()}_{timestamp}"
        os.makedirs(save_dir, exist_ok=True)
        
        # Create database session record
        db_session = DBInterviewSession(
            session_id=session_id,
            participant_data=participant,
            questions_data=interview_data,
            responses_data=[],
            current_question_index=0,
            status="active",
            agent_path=save_dir
        )
        
        db.add(db_session)
        db.commit()
        
        # Keep agent in memory for current session
        loaded_agents[session_id] = agent
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")
    
    # Return first question (introduction)
    first_question = interview_data[0]
    question_text = first_question['question'].replace("<participant's name>", request.first_name)
    
    return QuestionResponse(
        session_id=session_id,
        question_number=0,
        total_questions=len(interview_data) - 2,  # Exclude intro and outro
        question=question_text,
        time_limit=first_question['timeLimit'],
        is_introduction=True
    ) 