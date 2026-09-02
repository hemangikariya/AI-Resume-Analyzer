from typing import Dict, Any, List, Optional
import uuid
from app.ai.llm.gemini_gateway import gemini_gateway
from app.ai.llm.prompt_manager import prompt_manager
from app.ai.evaluation.validators import clean_and_parse_llm_json
from app.core.logger import logger

def generate_interview_question(
    parsed_resume: Dict[str, Any],
    jd_text: Optional[str] = None,
    difficulty: str = "medium",
    category: str = "Technical"
) -> Dict[str, Any]:
    """
    Generates a single interview question of specific difficulty and category,
    tailored to the resume and target job requirements.
    """
    logger.info(f"Generating interview question category: {category}, difficulty: {difficulty}...")
    
    # Format basic profile context
    resume_context = (
        f"Skills: {parsed_resume.get('sections', {}).get('skills')}\n"
        f"Projects: {parsed_resume.get('projects')}\n"
        f"Experience: {parsed_resume.get('experience')}\n"
    )
    
    rendered_prompt = prompt_manager.render_prompt(
        "interview.jinja",
        mode="generate",
        resume_data=resume_context,
        jd_data=jd_text or "General software development position",
        difficulty=difficulty,
        category=category
    )
    
    fallback = {
        "question": f"Based on your projects, can you explain the technical challenges and architecture of one system you built?",
        "category": category
    }
    
    response_json = gemini_gateway.generate_json(rendered_prompt)
    
    # Validate keys
    if "question" not in response_json or "category" not in response_json:
        logger.warning("Gemini did not return correct JSON schema for interview question. Using fallback.")
        return fallback
        
    return response_json

def evaluate_interview_answer(
    question: str,
    answer: str,
    parsed_resume: Dict[str, Any],
    jd_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates the candidate's response to an interview question.
    Returns score out of 10 and constructive feedback.
    """
    logger.info("Evaluating candidate interview response...")
    
    resume_context = (
        f"Skills: {parsed_resume.get('sections', {}).get('skills')}\n"
        f"Projects: {parsed_resume.get('projects')}\n"
        f"Experience: {parsed_resume.get('experience')}\n"
    )
    
    rendered_prompt = prompt_manager.render_prompt(
        "interview.jinja",
        mode="evaluate",
        resume_data=resume_context,
        jd_data=jd_text or "General software development position",
        question=question,
        answer=answer
    )
    
    fallback = {
        "score": 6,
        "feedback": "Answer recorded successfully. Make sure to detail your implementation methodologies, describe tools, and list metrics next time.",
        "strengths": "Answer addressed the core theme.",
        "weaknesses": "Lacked specific engineering details and technical metrics."
    }
    
    response_json = gemini_gateway.generate_json(rendered_prompt)
    
    # Validate keys
    expected_keys = ["score", "feedback", "strengths", "weaknesses"]
    for key in expected_keys:
        if key not in response_json:
            logger.warning(f"Gemini did not return '{key}' in evaluation JSON. Using fallback.")
            return fallback
            
    # Clean score type
    try:
        response_json["score"] = int(response_json["score"])
    except:
        response_json["score"] = 6
        
    return response_json
