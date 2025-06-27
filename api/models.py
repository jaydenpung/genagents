"""
Pydantic models for the API
"""

from pydantic import BaseModel
from typing import Optional, Dict, List

class StartInterviewRequest(BaseModel):
    first_name: str
    last_name: str
    age: str
    additional_info: Optional[Dict[str, str]] = None

class SubmitResponseRequest(BaseModel):
    session_id: str
    response: str

class InterviewSession(BaseModel):
    session_id: str
    participant: Dict[str, str]
    current_question_index: int
    total_questions: int
    responses: List[Dict]
    created_at: str
    status: str  # "active", "completed", "error"

class QuestionResponse(BaseModel):
    session_id: str
    question_number: int
    total_questions: int
    question: str
    time_limit: int
    is_introduction: bool = False
    is_conclusion: bool = False

class AgentCreationResponse(BaseModel):
    session_id: str
    agent_path: str
    total_responses: int
    memory_nodes: int
    message: str

class ChatRequest(BaseModel):
    agent_id: str
    message: str

class ChatResponse(BaseModel):
    agent_id: str
    agent_name: str
    response: str
    timestamp: str 