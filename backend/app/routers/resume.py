from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.user import User
from app.middlewares.auth import get_current_user
from app.services.resume_service import ResumeService
from app.ai.engines.rewrite_engine import rewrite_resume_text, enhance_project_details
from app.schemas.schemas import RewriteRequest, ProjectEnhanceRequest

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a resume file (PDF or DOCX), parses it, extracts skills, and saves to DB.
    """
    try:
        resume = ResumeService.upload_and_parse_resume(db, current_user, file)
        return {
            "success": True,
            "message": "Resume uploaded and parsed successfully",
            "data": {
                "resume": {
                    "id": resume.id,
                    "filename": resume.filename,
                    "version": resume.version,
                    "created_at": resume.created_at,
                    "parsed_data": resume.parsed_data
                }
            }
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
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
                    "code": "PARSING_FAILED",
                    "message": f"Resume processing failed: {str(e)}"
                }
            }
        )

@router.get("")
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lists all uploaded resumes for the current authenticated user.
    """
    resumes = ResumeService.get_user_resumes(db, current_user.id)
    serialized = []
    for r in resumes:
        serialized.append({
            "id": r.id,
            "filename": r.filename,
            "version": r.version,
            "created_at": r.created_at,
            "parsed_data": r.parsed_data
        })
        
    return {
        "success": True,
        "message": "Resumes retrieved successfully",
        "data": {
            "resumes": serialized
        }
    }

@router.get("/{resume_id}")
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gets details of a specific resume file.
    """
    resume = ResumeService.get_resume_by_id(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "RESUME_NOT_FOUND",
                    "message": "Resume record not found or access denied."
                }
            }
        )
        
    return {
        "success": True,
        "message": "Resume details retrieved successfully",
        "data": {
            "resume": {
                "id": resume.id,
                "filename": resume.filename,
                "version": resume.version,
                "created_at": resume.created_at,
                "parsed_data": resume.parsed_data
            }
        }
    }

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific resume file.
    """
    success = ResumeService.delete_resume(db, resume_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "RESUME_NOT_FOUND",
                    "message": "Resume record not found or access denied."
                }
            }
        )
        
    return {
        "success": True,
        "message": "Resume deleted successfully",
        "data": {}
    }

@router.post("/rewrite")
async def rewrite_point(
    payload: RewriteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Rewrites a single resume bullet point or sentence to follow results-oriented formats.
    """
    try:
        rewritten = rewrite_resume_text(payload.text)
        return {
            "success": True,
            "message": "Text rewritten successfully",
            "data": rewritten
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "REWRITE_FAILED",
                    "message": f"AI rewrite operation failed: {str(e)}"
                }
            }
        )

@router.post("/enhance-project")
async def enhance_project(
    payload: ProjectEnhanceRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Improves a project description with technologies, bullet points, and impact.
    """
    try:
        enhanced = enhance_project_details(payload.title, payload.description)
        return {
            "success": True,
            "message": "Project enhanced successfully",
            "data": enhanced
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "ENHANCEMENT_FAILED",
                    "message": f"AI project enhancement failed: {str(e)}"
                }
            }
        )
