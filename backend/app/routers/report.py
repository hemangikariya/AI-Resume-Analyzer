from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.database import get_db
from app.models.user import User
from app.middlewares.auth import get_current_user
from app.services.report_service import ReportService
from app.core.logger import logger

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{analysis_id}/download")
async def download_report(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assembles a ReportLab PDF matching candidate analysis results and returns it
    as an octet-stream downloadable file.
    """
    try:
        pdf_path = ReportService.get_or_generate_report(db, analysis_id, current_user.id)
        if not pdf_path.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "success": False,
                    "error": {
                        "code": "FILE_COMPILATION_ERROR",
                        "message": "The PDF report file could not be compiled on disk."
                    }
                }
            )
            
        return FileResponse(
            path=str(pdf_path),
            filename=pdf_path.name,
            media_type="application/pdf"
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
        logger.error(f"Download report endpoint exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "REPORT_GENERATION_FAILED",
                    "message": f"Failed to compile PDF report: {str(e)}"
                }
            }
        )
