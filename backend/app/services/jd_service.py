from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.jd import JobDescription
from app.models.user import User
from app.ai.engines.skill_engine import extract_skills_from_text
from app.core.logger import logger

class JDService:
    @staticmethod
    def create_job_description(
        db: Session,
        user: User,
        title: str,
        jd_text: str
    ) -> JobDescription:
        """
        Cleans the pasted Job Description text, extracts relevant skill keywords,
        and saves it to the database.
        """
        logger.info(f"User {user.email} submitted new Job Description: {title}")
        
        # 1. Clean up spacing
        cleaned_text = jd_text.strip()
        if not cleaned_text:
            raise ValueError("Job Description content cannot be empty.")
            
        # 2. Identify required skills
        skills_res = extract_skills_from_text(cleaned_text)
        extracted_skills = skills_res["all_skills"]
        
        # 3. Save to DB
        jd = JobDescription(
            user_id=user.id,
            title=title,
            jd_text=cleaned_text,
            extracted_skills=extracted_skills
        )
        
        db.add(jd)
        db.commit()
        db.refresh(jd)
        
        logger.info(f"Job Description ID {jd.id} saved successfully with {len(extracted_skills)} skill keywords.")
        return jd

    @staticmethod
    def get_user_jds(db: Session, user_id: int) -> List[JobDescription]:
        """Fetches all JD records uploaded by a user."""
        return db.query(JobDescription).filter(JobDescription.user_id == user_id).order_by(JobDescription.created_at.desc()).all()

    @staticmethod
    def get_jd_by_id(db: Session, jd_id: int, user_id: int) -> Optional[JobDescription]:
        """Fetches a specific JD by ID and verifies owner access."""
        return db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == user_id).first()

    @staticmethod
    def delete_jd(db: Session, jd_id: int, user_id: int) -> bool:
        """Deletes a job description record."""
        jd = JDService.get_jd_by_id(db, jd_id, user_id)
        if not jd:
            return False
            
        try:
            db.delete(jd)
            db.commit()
            logger.info(f"Successfully deleted Job Description ID {jd_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Job Description ID {jd_id}: {e}")
            db.rollback()
            raise e
