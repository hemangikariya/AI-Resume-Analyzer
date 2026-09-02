from typing import Dict, Any, List
from app.ai.llm.gemini_gateway import gemini_gateway
from app.ai.llm.prompt_manager import prompt_manager
from app.core.logger import logger

def analyze_career_fit(parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates what job profiles (AI Intern, Full Stack, DevOps, etc.) match the candidate
    and details skills gaps for profiles that are not recommended yet.
    """
    logger.info("Analyzing candidate career role fit profiles...")
    
    # Format details
    resume_context = (
        f"Skills: {parsed_resume.get('sections', {}).get('skills') or parsed_resume.get('skills')}\n"
        f"Projects: {parsed_resume.get('projects')}\n"
        f"Experience: {parsed_resume.get('experience')}\n"
        f"Education: {parsed_resume.get('education')}\n"
    )
    
    rendered_prompt = prompt_manager.render_prompt(
        "career_fit.jinja",
        resume_data=resume_context
    )
    
    fallback = {
        "recommended": [
            {"role": "Python Developer", "reason": "Demonstrated coding skills and API knowledge."},
            {"role": "AI Intern", "reason": "Basic Python and academic project portfolio."}
        ],
        "not_recommended": [
            {"role": "DevOps Engineer", "gaps": ["Lacks containerization (Docker) and Cloud (AWS/GCP) deployment experience."]}
        ]
    }
    
    response_json = gemini_gateway.generate_json(rendered_prompt)
    
    if "recommended" not in response_json or "not_recommended" not in response_json:
        logger.warning("Gemini failed career fit schema check. Using fallback.")
        return fallback
        
    return response_json
