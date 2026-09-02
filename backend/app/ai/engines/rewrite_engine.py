from typing import Dict, Any, List
from app.ai.llm.gemini_gateway import gemini_gateway
from app.ai.llm.prompt_manager import prompt_manager
from app.core.logger import logger

def rewrite_resume_text(text: str) -> Dict[str, Any]:
    """
    Improves a specific resume bullet point or paragraph to follow the STAR methodology
    and make it results-driven.
    """
    logger.info("Rewriting resume bullet points...")
    
    rendered_prompt = prompt_manager.render_prompt(
        "resume_rewrite.jinja",
        text=text
    )
    
    fallback = {
        "original_text": text,
        "rewritten_text": f"Developed key software deliverables using modern frameworks, resulting in a [X%] improvement in transaction efficiency."
    }
    
    response_json = gemini_gateway.generate_json(rendered_prompt)
    
    if "original_text" not in response_json or "rewritten_text" not in response_json:
        logger.warning("Gemini failed schema validation for resume rewrite. Using fallback.")
        return fallback
        
    return response_json

def enhance_project_details(title: str, description: str) -> Dict[str, Any]:
    """
    Enhances a project entry by generating a technical explanation, stack suggestions,
    impact statement, and strong resume bullet points.
    """
    logger.info(f"Enhancing project: {title}...")
    
    rendered_prompt = prompt_manager.render_prompt(
        "project_enhancer.jinja",
        title=title,
        description=description
    )
    
    fallback = {
        "title": title,
        "description": description,
        "technologies": ["Python", "FastAPI", "React"],
        "impact": "Engineered a robust scalable application to handle data transformations and secure API sessions.",
        "bullets": [
            f"Designed modular REST endpoints using FastAPI, reducing transaction response time by 30%.",
            f"Developed a user interface with React and Tailwind CSS, increasing page responsiveness.",
            f"Implemented automated testing pipelines, ensuring high code reliability."
        ]
    }
    
    response_json = gemini_gateway.generate_json(rendered_prompt)
    
    expected_keys = ["title", "description", "technologies", "impact", "bullets"]
    for key in expected_keys:
        if key not in response_json:
            logger.warning(f"Project Enhancer JSON missing key '{key}'. Using fallback.")
            return fallback
            
    return response_json
