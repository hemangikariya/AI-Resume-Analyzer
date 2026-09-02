from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.middlewares.auth import get_current_user
from app.services.analysis_service import AnalysisService
from app.schemas.schemas import ResumeCompareRequest

router = APIRouter(prefix="/analysis", tags=["Resume Analysis"])

@router.post("")
async def run_analysis(
    resume_id: int,
    jd_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers the ATS matching & explainability pipeline.
    Utilizes SQL cache lookups before calling heavy AI generators.
    """
    try:
        analysis = AnalysisService.run_resume_analysis(db, resume_id, jd_id, current_user.id)
        
        # Serialize response payload
        ats = analysis.ats_result
        return {
            "success": True,
            "message": "Analysis completed successfully",
            "data": {
                "analysis": {
                    "id": analysis.id,
                    "resume_id": analysis.resume_id,
                    "jd_id": analysis.jd_id,
                    "summary": analysis.summary,
                    "suggestions": [item["label"] for item in ats.why_explanation], # compatibility formatting
                    "roadmap": analysis.roadmap,
                    "career_fit": analysis.career_fit,
                    "cover_letter": analysis.cover_letter,
                    "created_at": analysis.created_at,
                    "ats_result": {
                        "ats_score": ats.ats_score,
                        "score_breakdown": ats.score_breakdown,
                        "why_explanation": ats.why_explanation,
                        "resume_health": ats.resume_health,
                        "checklist": ats.checklist,
                        "missing_skills": ats.missing_skills
                    }
                }
            }
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "BAD_REQUEST",
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
                    "code": "ANALYSIS_FAILED",
                    "message": f"Resume analysis pipeline failed: {str(e)}"
                }
            }
        )

@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gets all past analyses conducted by this user.
    """
    analyses = AnalysisService.get_user_analyses_history(db, current_user.id)
    serialized = []
    
    for a in analyses:
        ats = a.ats_result
        serialized.append({
            "id": a.id,
            "resume_id": a.resume_id,
            "resume_filename": a.resume.filename,
            "resume_version": a.resume.version,
            "jd_id": a.jd_id,
            "jd_title": a.jd.title if a.jd else None,
            "ats_score": ats.ats_score if ats else None,
            "created_at": a.created_at
        })
        
    return {
        "success": True,
        "message": "Analysis history retrieved successfully",
        "data": {
            "history": serialized
        }
    }

@router.get("/analytics")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated dashboard statistics including ATS trends, skill distribution, and health averages.
    """
    from app.models.analysis import Analysis
    from app.models.resume import Resume
    from app.models.ats_result import ATSResult
    
    # 1. Fetch user's analyses with ATS scores
    records = db.query(Analysis).join(Resume).filter(Resume.user_id == current_user.id).order_by(Analysis.created_at.asc()).all()
    
    ats_trends = []
    health_aggregates = {"skills": [], "experience": [], "projects": [], "formatting": []}
    
    for r in records:
        ats = r.ats_result
        if ats:
            ats_trends.append({
                "date": r.created_at.strftime("%Y-%m-%d"),
                "score": ats.ats_score,
                "resume_version": f"V{r.resume.version}"
            })
            for key in ["skills", "experience", "projects", "formatting"]:
                val = ats.resume_health.get(key)
                if val:
                    health_aggregates[key].append(val)
                    
    # 2. Fetch user's resumes and build skill distribution frequency
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    skill_counts = {}
    for res in resumes:
        skills = res.parsed_data.get("skills", [])
        for s in skills:
            skill_counts[s] = skill_counts.get(s, 0) + 1
            
    # Format skill distribution
    skill_distribution = [{"skill": k, "count": v} for k, v in sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    # Format health averages
    health_summary = {}
    for key, vals in health_aggregates.items():
        total = len(vals)
        if total == 0:
            health_summary[key] = {"Excellent": 0, "Good": 0, "Average": 0, "Improve": 0, "Missing": 0}
            continue
        health_summary[key] = {
            "Excellent": vals.count("Excellent"),
            "Good": vals.count("Good"),
            "Average": vals.count("Average"),
            "Improve": vals.count("Improve"),
            "Missing": vals.count("Missing")
        }
        
    return {
        "success": True,
        "message": "Dashboard analytics compiled successfully",
        "data": {
            "ats_trends": ats_trends,
            "skill_distribution": skill_distribution,
            "health_summary": health_summary,
            "total_resumes": len(resumes),
            "total_analyses": len(records)
        }
    }

@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the detailed results of a specific analysis run.
    """
    analysis = AnalysisService.get_analysis_by_id(db, analysis_id, current_user.id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "ANALYSIS_NOT_FOUND",
                    "message": "Analysis record not found or access denied."
                }
            }
        )
        
    ats = analysis.ats_result
    return {
        "success": True,
        "message": "Analysis retrieved successfully",
        "data": {
            "analysis": {
                "id": analysis.id,
                "resume_id": analysis.resume_id,
                "jd_id": analysis.jd_id,
                "summary": analysis.summary,
                "suggestions": [item["label"] for item in ats.why_explanation] if ats else [],
                "roadmap": analysis.roadmap,
                "career_fit": analysis.career_fit,
                "cover_letter": analysis.cover_letter,
                "created_at": analysis.created_at,
                "ats_result": {
                    "ats_score": ats.ats_score,
                    "score_breakdown": ats.score_breakdown,
                    "why_explanation": ats.why_explanation,
                    "resume_health": ats.resume_health,
                    "checklist": ats.checklist,
                    "missing_skills": ats.missing_skills
                } if ats else None
            }
        }
    }

@router.post("/compare")
async def compare_resumes(
    payload: ResumeCompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Performs side-by-side comparison of two resume versions (V1 vs V2).
    """
    try:
        comparison = AnalysisService.compare_resumes(
            db=db,
            resume_id_1=payload.resume_id_1,
            resume_id_2=payload.resume_id_2,
            jd_id=payload.jd_id,
            user_id=current_user.id
        )
        return {
            "success": True,
            "message": "Resumes compared successfully",
            "data": {
                "comparison": comparison
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "COMPARISON_FAILED",
                    "message": f"Version comparison analysis failed: {str(e)}"
                }
            }
        )

@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific analysis record.
    """
    success = AnalysisService.delete_analysis(db, analysis_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "ANALYSIS_NOT_FOUND",
                    "message": "Analysis record not found or access denied."
                }
            }
        )
        
    return {
        "success": True,
        "message": "Analysis deleted successfully",
        "data": {}
    }
