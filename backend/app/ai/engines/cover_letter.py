from typing import Dict, Any, Optional
from app.ai.llm.gemini_gateway import gemini_gateway
from app.ai.llm.prompt_manager import prompt_manager
from app.core.logger import logger

def generate_cover_letter_details(
    parsed_resume: Dict[str, Any],
    jd_text: str,
    company: Optional[str] = None,
    role: Optional[str] = None
) -> str:
    """
    Creates a customized cover letter using candidate resume details and target job description.
    """
    logger.info("Generating customized cover letter details...")
    
    # Format resume profile context
    contact = parsed_resume.get("contact", {})
    resume_context = (
        f"Candidate Name: {contact.get('name', 'Applicant')}\n"
        f"Skills: {parsed_resume.get('sections', {}).get('skills')}\n"
        f"Projects: {parsed_resume.get('projects')}\n"
        f"Experience: {parsed_resume.get('experience')}\n"
    )
    
    rendered_prompt = prompt_manager.render_prompt(
        "cover_letter.jinja",
        resume_data=resume_context,
        jd_text=jd_text,
        company=company or "the Company",
        role=role or "Engineering Position"
    )
    
    # Call Gemini Gateway
    response = gemini_gateway.generate_text(rendered_prompt)
    return response
