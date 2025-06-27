"""
Database models and connection for interview sessions and agents
"""

from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from simulation_engine.settings import DATABASE_URL

Base = declarative_base()

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    session_id = Column(String, primary_key=True)
    participant_data = Column(JSON)  # Store participant info as JSON
    questions_data = Column(JSON)    # Store questions as JSON
    responses_data = Column(JSON)    # Store responses as JSON
    current_question_index = Column(Integer, default=0)
    status = Column(String, default="active")  # active, completed, error, agent_created
    agent_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to agent
    agent = relationship("Agent", back_populates="interview_session", uselist=False)

class Agent(Base):
    __tablename__ = "agents"
    
    agent_id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey('interview_sessions.session_id'), unique=True)
    name = Column(String, nullable=False)
    age = Column(String)
    participant_data = Column(JSON)  # Full participant info
    memory_stream = Column(JSON)     # Agent's memory stream data
    scratch_data = Column(JSON)      # Agent's scratch/state data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to interview session
    interview_session = relationship("InterviewSession", back_populates="agent")

# Database connection
engine = None
SessionLocal = None

def init_database():
    """Initialize database connection"""
    global engine, SessionLocal
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get database session for direct use"""
    if SessionLocal is None:
        init_database()
    
    return SessionLocal()