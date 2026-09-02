from typing import Dict, Any
from app.ai.llm.gemini_gateway import gemini_gateway
from app.ai.llm.prompt_manager import prompt_manager
from app.core.logger import logger

def generate_resume_summary(parsed_resume: Dict[str, Any]) -> str:
    """
    Generates a professional resume summary from parsed resume structural data.
    """
    logger.info("Generating professional summary...")
    
    # Format experience and projects text
    experience_text = ""
    for exp in parsed_resume.get("experience", []):
        experience_text += f"- {exp.get('title')} at {exp.get('company')} ({exp.get('duration')}): {exp.get('description')}\n"
        
    projects_text = ""
    for proj in parsed_resume.get("projects", []):
        projects_text += f"- {proj.get('title')}: {proj.get('description')}\n"
        
    resume_context = (
        f"Education: {parsed_resume.get('education')}\n"
        f"Skills: {parsed_resume.get('sections', {}).get('skills')}\n"
        f"Experience details:\n{experience_text}\n"
        f"Projects details:\n{projects_text}\n"
    )
    
    rendered_prompt = prompt_manager.render_prompt(
        "resume_summary.jinja",
        resume_data=resume_context
    )
    
    # Call Gemini Gateway
    response = gemini_gateway.generate_text(rendered_prompt)
    return response.strip()
