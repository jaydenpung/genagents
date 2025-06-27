from .start_interview import router as start_interview_router
from .get_current_question import router as get_current_question_router
from .submit_response import router as submit_response_router
from .finalize_agent import router as finalize_agent_router
from .get_interview import router as get_interview_router
from .list_sessions import router as list_sessions_router
from .delete_interview import router as delete_interview_router

from fastapi import APIRouter

router = APIRouter()
router.include_router(start_interview_router)
router.include_router(get_current_question_router)
router.include_router(submit_response_router)
router.include_router(finalize_agent_router)
router.include_router(get_interview_router)
router.include_router(list_sessions_router)
router.include_router(delete_interview_router) 