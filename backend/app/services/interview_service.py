import time
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.models.jd import JobDescription
from app.ai.engines.interview_engine import generate_interview_question, evaluate_interview_answer
from app.core.logger import logger

# In-memory interview session cache with timestamp tracking
# session_id -> {resume_id, jd_id, difficulty, question_index, created_at, updated_at, history: [...]}
INTERVIEW_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Simple category alternator
CATEGORY_FLOW = ["HR", "Technical", "Project", "Coding"]
SESSION_TTL_SECONDS = 3600  # 1 hour active timeout

class InterviewService:
    @staticmethod
    def _cleanup_expired_sessions():
        """Cleans up stale in-memory interview sessions older than TTL."""
        now = time.time()
        expired = [sid for sid, s in INTERVIEW_SESSIONS.items() if now - s.get("updated_at", now) > SESSION_TTL_SECONDS]
        for sid in expired:
            INTERVIEW_SESSIONS.pop(sid, None)

    @staticmethod
    def start_interview(
        db: Session,
        resume_id: int,
        jd_id: Optional[int],
        difficulty: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Starts a new interview simulation session. Generates the first question.
        """
        InterviewService._cleanup_expired_sessions()
        logger.info(f"Starting interview session for resume {resume_id}...")
        
        # Verify access
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume record not found or access denied.")
            
        jd_text = None
        if jd_id:
            jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == user_id).first()
            if jd:
                jd_text = jd.jd_text
                
        # 1. Generate First Question (Category: HR)
        first_category = CATEGORY_FLOW[0]
        question_data = generate_interview_question(
            parsed_resume=resume.parsed_data,
            jd_text=jd_text,
            difficulty=difficulty,
            category=first_category
        )
        
        session_id = str(uuid.uuid4())
        now = time.time()
        
        # 2. Store session details
        INTERVIEW_SESSIONS[session_id] = {
            "resume_id": resume_id,
            "jd_id": jd_id,
            "difficulty": difficulty,
            "question_index": 0,
            "current_question": question_data.get("question", "Tell me about your technical background."),
            "current_category": first_category,
            "created_at": now,
            "updated_at": now,
            "history": []
        }
        
        logger.info(f"Mock Interview session {session_id} initialized successfully.")
        
        return {
            "session_id": session_id,
            "question": question_data.get("question", "Tell me about your technical background."),
            "category": first_category
        }

    @staticmethod
    def submit_answer(
        db: Session,
        session_id: str,
        answer: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Evaluates the user's answer, logs details in session history,
        and generates the next category question or wraps up.
        """
        logger.info(f"Submitting answer for Interview Session: {session_id}...")
        
        if session_id not in INTERVIEW_SESSIONS:
            raise ValueError("Invalid or expired interview session ID.")
            
        session = INTERVIEW_SESSIONS[session_id]
        resume_id = session.get("resume_id")
        jd_id = session.get("jd_id")
        difficulty = session.get("difficulty", "medium")
        q_idx = session.get("question_index", 0)
        current_question = session.get("current_question", "")
        current_category = session.get("current_category", "Technical")
        
        # Verify ownership
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Unauthorized session access.")
            
        jd_text = None
        if jd_id:
            jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == user_id).first()
            if jd:
                jd_text = jd.jd_text
                
        # 1. Evaluate candidate answer
        evaluation = evaluate_interview_answer(
            question=current_question,
            answer=answer,
            parsed_resume=resume.parsed_data,
            jd_text=jd_text
        )
        
        # Save to history
        session["history"].append({
            "question": current_question,
            "category": current_category,
            "answer": answer,
            "score": evaluation.get("score", 7),
            "feedback": evaluation.get("feedback", "Good response."),
            "strengths": evaluation.get("strengths", "Clear explanation."),
            "weaknesses": evaluation.get("weaknesses", "Could include additional metrics.")
        })
        session["updated_at"] = time.time()
        
        # 2. Check if interview is complete (e.g., 4 questions limit)
        q_idx += 1
        max_questions = 4
        
        if q_idx >= max_questions:
            session["question_index"] = q_idx
            logger.info(f"Mock Interview session {session_id} completed.")
            
            final_report = {
                "score": evaluation.get("score", 7),
                "feedback": evaluation.get("feedback", "Interview completed."),
                "strengths": evaluation.get("strengths", "Completed full round."),
                "weaknesses": evaluation.get("weaknesses", "Review key topics before live interviews."),
                "next_question": None,
                "next_category": None,
                "is_complete": True,
                "history": session["history"]
            }
            INTERVIEW_SESSIONS.pop(session_id, None)
            return final_report
            
        # 3. Else, generate next category question
        next_category = CATEGORY_FLOW[q_idx % len(CATEGORY_FLOW)]
        next_q_data = generate_interview_question(
            parsed_resume=resume.parsed_data,
            jd_text=jd_text,
            difficulty=difficulty,
            category=next_category
        )
        
        session["question_index"] = q_idx
        session["current_question"] = next_q_data.get("question", "Describe your experience with software architecture.")
        session["current_category"] = next_category
        
        return {
            "score": evaluation.get("score", 7),
            "feedback": evaluation.get("feedback", "Response recorded."),
            "strengths": evaluation.get("strengths", "Good points."),
            "weaknesses": evaluation.get("weaknesses", "Continue elaboration."),
            "next_question": next_q_data.get("question", "Describe your experience with software architecture."),
            "next_category": next_category,
            "is_complete": False
        }
