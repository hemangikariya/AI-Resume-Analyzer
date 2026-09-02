import shutil
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.user import User
from app.ai.engines.parser.parser import parse_resume_document
from app.ai.engines.skill_engine import extract_skills_from_text
from app.core.settings import settings
from app.core.logger import logger

def get_next_resume_version(db: Session, user_id: int) -> int:
    """Calculates the incremented version count for a user's resume uploads."""
    latest = db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.version.desc()).first()
    if latest:
        return latest.version + 1
    return 1

def save_uploaded_file(upload_file: UploadFile, destination_dir: Path) -> Path:
    """Saves a FastAPI upload stream to local storage directories."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to prevent collisions
    filename = upload_file.filename
    clean_filename = f"{Path(filename).stem}_{int(time.time())}{Path(filename).suffix}"
    dest_path = destination_dir / clean_filename
    
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return dest_path
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise e

class ResumeService:
    @staticmethod
    def upload_and_parse_resume(
        db: Session,
        user: User,
        file: UploadFile
    ) -> Resume:
        """
        Orchestrates saving the upload, running the text parser, 
        running skill extraction, and persisting details to DB.
        """
        logger.info(f"User {user.email} initiated resume upload: {file.filename}")
        
        # Verify file extensions
        ext = Path(file.filename).suffix.lower()
        if ext not in [".pdf", ".docx"]:
            logger.error(f"Upload rejected. Unsupported file type: {ext}")
            raise ValueError("Unsupported file type. Please upload a PDF or DOCX document.")
            
        # 1. Save file to storage/resumes/
        dest_path = save_uploaded_file(file, settings.resumes_dir)
        
        try:
            # 2. Run Parser Pipeline
            parsed_data = parse_resume_document(dest_path)
            
            # 3. Extract skills from parsed layout text & sections
            extracted_skills = extract_skills_from_text(parsed_data["raw_text"])
            
            # Combine skills back into parsed JSON
            parsed_data["skills"] = extracted_skills["all_skills"]
            parsed_data["skills_categorized"] = extracted_skills
            
            # 4. Save to DB
            version = get_next_resume_version(db, user.id)
            
            resume = Resume(
                user_id=user.id,
                filename=file.filename,
                file_path=str(dest_path),
                extracted_text=parsed_data["raw_text"],
                parsed_data=parsed_data,
                version=version
            )
            
            db.add(resume)
            db.commit()
            db.refresh(resume)
            
            logger.info(f"Resume {resume.id} version {resume.version} saved successfully in DB.")
            return resume
            
        except Exception as e:
            # Clean up saved file if parsing failed
            if dest_path.exists():
                dest_path.unlink()
            logger.error(f"Error parsing or storing resume: {e}")
            raise e

    @staticmethod
    def get_user_resumes(db: Session, user_id: int) -> List[Resume]:
        """Fetches all uploaded resume records for a specific user."""
        return db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).all()

    @staticmethod
    def get_resume_by_id(db: Session, resume_id: int, user_id: int) -> Optional[Resume]:
        """Fetches a specific resume by ID and verifies owner access."""
        return db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()

    @staticmethod
    def delete_resume(db: Session, resume_id: int, user_id: int) -> bool:
        """Deletes a resume record and its local stored file."""
        resume = ResumeService.get_resume_by_id(db, resume_id, user_id)
        if not resume:
            return False
            
        try:
            # Remove local file
            file_path = Path(resume.file_path)
            if file_path.exists():
                file_path.unlink()
                
            db.delete(resume)
            db.commit()
            logger.info(f"Successfully deleted resume ID {resume_id} and its storage asset.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete resume ID {resume_id}: {e}")
            db.rollback()
            raise e
