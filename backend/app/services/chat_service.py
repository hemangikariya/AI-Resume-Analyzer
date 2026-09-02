from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.ai.engines.chat_engine import run_resume_chat
from app.core.logger import logger

class ChatService:
    @staticmethod
    def process_chat_message(
        db: Session,
        resume_id: int,
        user_id: int,
        message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Orchestrates resume chat sessions. Loads resume contexts, verifies ownership,
        and fires the LLM query engines.
        """
        logger.info(f"Processing chat message for Resume ID: {resume_id}...")
        
        # Load resume and verify access
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume record not found or access denied.")
            
        # Call Chat Engine
        reply = run_resume_chat(
            parsed_data=resume.parsed_data,
            message=message,
            history=history
        )
        
        return reply
