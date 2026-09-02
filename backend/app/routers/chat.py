from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.middlewares.auth import get_current_user
from app.services.chat_service import ChatService
from app.schemas.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Resume Chat"])

@router.post("", response_model=ChatResponse)
async def chat_with_resume(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Answers conversational queries regarding a user's resume using RAG search boundaries.
    """
    try:
        reply = ChatService.process_chat_message(
            db=db,
            resume_id=payload.resume_id,
            user_id=current_user.id,
            message=payload.message,
            history=payload.history
        )
        return ChatResponse(reply=reply)
        
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "RESUME_NOT_FOUND",
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
                    "code": "CHAT_FAILED",
                    "message": f"Resume chat helper failed: {str(e)}"
                }
            }
        )
