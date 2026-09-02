from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.middlewares.auth import get_current_user
from app.services.interview_service import InterviewService
from app.schemas.schemas import InterviewStartRequest, InterviewStartResponse

router = APIRouter(prefix="/interviews", tags=["Mock Interview"])

@router.post("/start", response_model=InterviewStartResponse)
async def start_interview_session(
    payload: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initializes a new interview session and returns the first question.
    """
    try:
        session_data = InterviewService.start_interview(
            db=db,
            resume_id=payload.resume_id,
            jd_id=payload.jd_id,
            difficulty=payload.difficulty,
            user_id=current_user.id
        )
        return InterviewStartResponse(
            session_id=session_data["session_id"],
            question=session_data["question"],
            category=session_data["category"]
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": str(ve)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERVIEW_START_FAILED",
                    "message": f"Failed to initialize mock interview: {str(e)}"
                }
            }
        )

@router.post("/submit")
async def submit_interview_answer(
    session_id: str,
    answer: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluates the candidate's answer and either returns the next question or compiles final stats.
    """
    try:
        eval_result = InterviewService.submit_answer(
            db=db,
            session_id=session_id,
            answer=answer,
            user_id=current_user.id
        )
        return {
            "success": True,
            "message": "Answer evaluated successfully",
            "data": eval_result
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_SESSION",
                    "message": str(ve)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "SUBMISSION_FAILED",
                    "message": f"Failed to process answer evaluation: {str(e)}"
                }
            }
        )
