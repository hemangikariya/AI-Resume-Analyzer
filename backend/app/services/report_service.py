from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from app.models.report import Report
from app.models.analysis import Analysis
from app.models.resume import Resume
from app.ai.engines.report_engine import generate_pdf_report
from app.core.settings import settings
from app.core.logger import logger

class ReportService:
    @staticmethod
    def get_or_generate_report(
        db: Session,
        analysis_id: int,
        user_id: int
    ) -> Path:
        """
        Retrieves an existing PDF report path, or triggers ReportLab to build it.
        Persists report asset mapping in the DB.
        """
        logger.info(f"Retrieving or generating PDF report for Analysis ID {analysis_id}...")
        
        # 1. Check if analysis exists and belongs to the user
        analysis = db.query(Analysis).join(Resume).filter(
            Analysis.id == analysis_id,
            Resume.user_id == user_id
        ).first()
        
        if not analysis:
            raise ValueError("Analysis record not found or access denied.")
            
        # 2. Check if a report file is already registered in DB
        existing_report = db.query(Report).filter(Report.analysis_id == analysis_id).first()
        if existing_report:
            report_path = Path(existing_report.file_path)
            if report_path.exists():
                logger.info(f"Cached report file found: {report_path}")
                return report_path
            else:
                # File missing on disk, delete record to regenerate
                logger.warning(f"Report record existed in DB but file was missing from disk: {report_path}. Regenerating.")
                db.delete(existing_report)
                db.commit()
                
        # 3. Define output path
        filename = f"Resume_Analysis_Report_{analysis_id}.pdf"
        output_path = settings.reports_dir / filename
        
        # Gather inputs
        resume = analysis.resume
        contact = resume.parsed_data.get("contact", {})
        candidate_name = contact.get("name") or resume.filename
        
        ats = analysis.ats_result
        
        # Compile suggestions (combining why explanation labels)
        sugs_list = [item["label"] for item in ats.why_explanation]
        
        # Retrieve matched skills
        matched_skills = resume.parsed_data.get("skills", [])
        
        # Generate the PDF
        generate_pdf_report(
            output_path=output_path,
            candidate_name=candidate_name,
            ats_score=ats.ats_score,
            breakdown=ats.score_breakdown,
            health=ats.resume_health,
            summary=analysis.summary or "Summary not available.",
            matched_skills=matched_skills,
            missing_skills=ats.missing_skills or [],
            suggestions=sugs_list,
            roadmap=analysis.roadmap or []
        )
        
        # 4. Save to DB
        report = Report(
            analysis_id=analysis_id,
            file_path=str(output_path)
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"PDF report mapping successfully registered in database. ID: {report.id}")
        return output_path
