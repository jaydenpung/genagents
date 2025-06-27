"""
Main FastAPI application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import init_database
from .interview import router as interview_router

app = FastAPI(title="Generative Agent Interview API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://genagents.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(interview_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Generative Agent Interview API",
        "version": "1.0.0",
        "endpoints": {
            "start_interview": "POST /interview/start",
            "get_question": "GET /interview/{session_id}/question",
            "submit_response": "POST /interview/response",
            "finalize_agent": "POST /interview/{session_id}/finalize",
            "get_session": "GET /interview/{session_id}",
            "list_sessions": "GET /interview/sessions",
            "delete_session": "DELETE /interview/{session_id}"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 