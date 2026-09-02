from typing import Dict, Any, List
from app.ai.llm.gemini_gateway import gemini_gateway
from app.ai.llm.prompt_manager import prompt_manager
from app.core.constants import SKILL_RESOURCES
from app.core.logger import logger

def generate_roadmap_details(
    missing_skills: List[str],
    parsed_resume: Dict[str, Any],
    jd_text: str
) -> List[Dict[str, Any]]:
    """
    Generates a structured learning roadmap for missing skills.
    Utilizes Gemini JSON generation with hardcoded dictionary fallbacks for offline support.
    """
    logger.info(f"Generating learning roadmap details for skills: {missing_skills}...")
    
    if not missing_skills:
        return []
        
    # Render prompt via prompt manager
    resume_context = f"Skills present: {parsed_resume.get('sections', {}).get('skills')}"
    rendered_prompt = prompt_manager.render_prompt(
        "roadmap.jinja",
        missing_skills=missing_skills,
        resume_data=resume_context,
        jd_data=jd_text
    )
    
    # Try calling Gemini JSON interface
    try:
        response_json = gemini_gateway.generate_json(rendered_prompt)
        # Check if list format is correct
        if isinstance(response_json, list) and len(response_json) > 0:
            logger.info("Successfully generated learning roadmap from Gemini API.")
            return response_json
    except Exception as e:
        logger.error(f"Gemini roadmap generation failed: {e}. Reverting to static constant mapping.")
        
    # Fallback compilation
    logger.info("Compiling learning roadmap details from static constants fallbacks...")
    roadmap_result = []
    for skill in missing_skills:
        skill_lower = skill.lower()
        if skill_lower in SKILL_RESOURCES:
            res_details = SKILL_RESOURCES[skill_lower]
            roadmap_result.append({
                "skill": skill,
                "resource": res_details["resource"],
                "time": res_details["time"],
                "project": res_details["project"],
                "certification": res_details["certification"]
            })
        else:
            # General fallback template
            roadmap_result.append({
                "skill": skill,
                "resource": f"Complete {skill} Developer Course (Udemy / Coursera / YouTube)",
                "time": "10-15 hours",
                "project": f"Build a lightweight project integrating {skill} functionalities.",
                "certification": f"Professional {skill} Certification"
            })
            
    return roadmap_result
