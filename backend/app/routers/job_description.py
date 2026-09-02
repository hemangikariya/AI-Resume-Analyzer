from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.middlewares.auth import get_current_user
from app.services.jd_service import JDService
from app.schemas.schemas import JDCreate

router = APIRouter(prefix="/job-descriptions", tags=["Job Descriptions"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_jd(
    payload: JDCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits a Job Description, parses required skills, and saves to DB.
    """
    try:
        jd = JDService.create_job_description(db, current_user, payload.title, payload.jd_text)
        return {
            "success": True,
            "message": "Job Description created successfully",
            "data": {
                "jd": {
                    "id": jd.id,
                    "title": jd.title,
                    "jd_text": jd.jd_text,
                    "extracted_skills": jd.extracted_skills,
                    "created_at": jd.created_at
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "CREATION_FAILED",
                    "message": f"Failed to save Job Description: {str(e)}"
                }
            }
        )

@router.get("")
async def list_jds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all job descriptions for the authenticated user.
    """
    jds = JDService.get_user_jds(db, current_user.id)
    serialized = []
    for jd in jds:
        serialized.append({
            "id": jd.id,
            "title": jd.title,
            "jd_text": jd.jd_text,
            "extracted_skills": jd.extracted_skills,
            "created_at": jd.created_at
        })
        
    return {
        "success": True,
        "message": "Job Descriptions retrieved successfully",
        "data": {
            "job_descriptions": serialized
        }
    }

@router.get("/{jd_id}")
async def get_jd(
    jd_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves details of a specific job description.
    """
    jd = JDService.get_jd_by_id(db, jd_id, current_user.id)
    if not jd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "JD_NOT_FOUND",
                    "message": "Job Description record not found or access denied."
                }
            }
        )
        
    return {
        "success": True,
        "message": "Job Description details retrieved successfully",
        "data": {
            "jd": {
                "id": jd.id,
                "title": jd.title,
                "jd_text": jd.jd_text,
                "extracted_skills": jd.extracted_skills,
                "created_at": jd.created_at
            }
        }
    }

@router.delete("/{jd_id}")
async def delete_jd(
    jd_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific job description.
    """
    success = JDService.delete_jd(db, jd_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "JD_NOT_FOUND",
                    "message": "Job Description record not found or access denied."
                }
            }
        )
        
    return {
        "success": True,
        "message": "Job Description deleted successfully",
        "data": {}
    }
