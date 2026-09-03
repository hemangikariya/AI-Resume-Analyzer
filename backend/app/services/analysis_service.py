from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.models.ats_result import ATSResult
from app.models.resume import Resume
from app.models.jd import JobDescription

# Import AI Engines
from app.ai.engines.ats_engine import run_ats_calculation
from app.ai.engines.explainability_engine import generate_explainability_report
from app.ai.engines.summary import generate_resume_summary
from app.ai.engines.career_engine import analyze_career_fit
from app.ai.engines.roadmap import generate_roadmap_details
from app.ai.engines.cover_letter import generate_cover_letter_details
from app.ai.engines.comparison_engine import compare_resume_versions

from app.core.logger import logger

class AnalysisService:
    @staticmethod
    def run_resume_analysis(
        db: Session,
        resume_id: int,
        jd_id: Optional[int] = None,
        user_id: int = None
    ) -> Analysis:
        """
        Runs the full analysis pipeline for a resume against an optional Job Description.
        Implements intelligent caching: returns existing analysis if already computed.
        """
        logger.info(f"Initiating analysis pipeline for resume {resume_id} and JD {jd_id}...")
        
        # 1. Check for cached analysis
        existing_analysis = db.query(Analysis).filter(
            Analysis.resume_id == resume_id,
            Analysis.jd_id == jd_id
        ).first()
        
        if existing_analysis:
            logger.info(f"Retrieved cached Analysis ID {existing_analysis.id} from database.")
            return existing_analysis
            
        # Retrieve documents from DB
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found or access denied.")
            
        jd = None
        jd_text = None
        jd_skills = []
        
        if jd_id:
            jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == user_id).first()
            if not jd:
                raise ValueError("Job Description not found or access denied.")
            jd_text = jd.jd_text
            jd_skills = jd.extracted_skills or []
            
        # 2. Run Deterministic Python ATS Scoring Engine
        ats_results = run_ats_calculation(
            parsed_resume=resume.parsed_data,
            resume_skills=resume.parsed_data.get("skills", []),
            jd_text=jd_text,
            jd_skills=jd_skills
        )
        
        # 3. Run Explainability AI Engine
        xai_report = generate_explainability_report(ats_results)
        
        # 4. Trigger Gemini Services (Summary, Career Fit, Roadmap, Cover Letter)
        # Handle exceptions gracefully - fall back to deterministic if LLM fails
        try:
            summary = generate_resume_summary(resume.parsed_data)
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            summary = "Summary generation failed. Check API key."
            
        try:
            career_fit = analyze_career_fit(resume.parsed_data)
        except Exception as e:
            logger.error(f"Failed to generate career fit: {e}")
            career_fit = {
                "recommended": [{"role": "Software Developer", "reason": "Demonstrated technical skills."}],
                "not_recommended": []
            }
            
        try:
            missing_skills = [item["skill"] for item in xai_report["missing_skills"]]
            roadmap = generate_roadmap_details(missing_skills, resume.parsed_data, jd_text or "")
        except Exception as e:
            logger.error(f"Failed to generate roadmap: {e}")
            roadmap = []
            
        cover_letter = None
        if jd_text:
            try:
                cover_letter = generate_cover_letter_details(resume.parsed_data, jd_text, company=None, role=jd.title)
            except Exception as e:
                logger.error(f"Failed to generate cover letter: {e}")
                cover_letter = "Cover letter generation failed."

        # 5. Persist Analysis and ATS Results in DB
        analysis = Analysis(
            resume_id=resume.id,
            jd_id=jd.id if jd else None,
            summary=summary,
            suggestions=xai_report["why_explanation"], # Using explainable modifiers list as suggestions
            roadmap=roadmap,
            career_fit=career_fit,
            cover_letter=cover_letter
        )
        
        db.add(analysis)
        db.commit() # Commit to generate analysis.id
        db.refresh(analysis)
        
        # Create corresponding ATSResult entry
        ats_result = ATSResult(
            analysis_id=analysis.id,
            ats_score=ats_results["ats_score"],
            score_breakdown=ats_results["score_breakdown"],
            why_explanation=xai_report["why_explanation"],
            resume_health=xai_report["resume_health"],
            checklist=ats_results["checklist"],
            missing_skills=xai_report["missing_skills"]
        )
        
        db.add(ats_result)
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Analysis pipeline completed and saved successfully. ID: {analysis.id}")
        return analysis

    @staticmethod
    def get_analysis_by_id(db: Session, analysis_id: int, user_id: int) -> Optional[Analysis]:
        """Retrieves a specific Analysis by ID and verifies owner access."""
        # Find analysis and join with resume to confirm ownership
        return db.query(Analysis).join(Resume).filter(
            Analysis.id == analysis_id,
            Resume.user_id == user_id
        ).first()

    @staticmethod
    def get_user_analyses_history(db: Session, user_id: int) -> List[Analysis]:
        """Fetches all past analysis records for a user."""
        return db.query(Analysis).join(Resume).filter(
            Resume.user_id == user_id
        ).order_by(Analysis.created_at.desc()).all()

    @staticmethod
    def delete_analysis(db: Session, analysis_id: int, user_id: int) -> bool:
        """Deletes a specific analysis record."""
        analysis = AnalysisService.get_analysis_by_id(db, analysis_id, user_id)
        if not analysis:
            return False
            
        try:
            db.delete(analysis)
            db.commit()
            logger.info(f"Successfully deleted Analysis ID {analysis_id}.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Analysis ID {analysis_id}: {e}")
            db.rollback()
            raise e

    @staticmethod
    def _get_resume_ats_metrics(
        db: Session,
        resume_id: int,
        jd_id: Optional[int],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Retrieves cached ATS metrics or computes deterministic score/skills on the fly without heavy LLM calls.
        """
        # Check if cached analysis exists
        existing_analysis = db.query(Analysis).filter(
            Analysis.resume_id == resume_id,
            Analysis.jd_id == jd_id
        ).first()
        
        if existing_analysis and existing_analysis.ats_result:
            resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
            if not resume:
                raise ValueError("Resume not found or access denied.")
            return {
                "ats_score": existing_analysis.ats_result.ats_score,
                "score_breakdown": existing_analysis.ats_result.score_breakdown,
                "checklist": existing_analysis.ats_result.checklist,
                "resume_health": existing_analysis.ats_result.resume_health,
                "matched_skills": resume.parsed_data.get("skills", [])
            }
            
        # Retrieve resume & JD
        resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
        if not resume:
            raise ValueError("Resume not found or access denied.")
            
        jd_text = None
        jd_skills = []
        if jd_id:
            jd = db.query(JobDescription).filter(JobDescription.id == jd_id, JobDescription.user_id == user_id).first()
            if not jd:
                raise ValueError("Job Description not found or access denied.")
            jd_text = jd.jd_text
            jd_skills = jd.extracted_skills or []
            
        # Run deterministic ATS calculation (0.40 Skills + 0.25 Semantic + 0.15 Experience + 0.10 Projects + 0.10 Formatting)
        ats_results = run_ats_calculation(
            parsed_resume=resume.parsed_data,
            resume_skills=resume.parsed_data.get("skills", []),
            jd_text=jd_text,
            jd_skills=jd_skills
        )
        
        xai_report = generate_explainability_report(ats_results)
        
        return {
            "ats_score": ats_results["ats_score"],
            "score_breakdown": ats_results["score_breakdown"],
            "checklist": ats_results["checklist"],
            "resume_health": xai_report["resume_health"],
            "matched_skills": resume.parsed_data.get("skills", [])
        }

    @staticmethod
    def compare_resumes(
        db: Session,
        resume_id_1: int,
        resume_id_2: int,
        jd_id: Optional[int],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Orchestrates side-by-side version comparison analysis.
        Retrieves or deterministically calculates ATS metrics for both versions without Render timeout.
        """
        logger.info(f"Comparing resume versions: {resume_id_1} vs {resume_id_2}")
        
        # 1. Retrieve/Calculate ATS metrics for both versions
        ats_1 = AnalysisService._get_resume_ats_metrics(db, resume_id_1, jd_id, user_id)
        ats_2 = AnalysisService._get_resume_ats_metrics(db, resume_id_2, jd_id, user_id)
        
        # 2. Call Comparison Engine
        comparison_data = compare_resume_versions(ats_1, ats_2)
        
        return comparison_data

