import re
from typing import Dict, Any, List, Optional
from app.ai.engines.embedding_engine import calculate_semantic_similarity, match_skills_semantically
from app.ai.engines.skill_engine import extract_skills_from_text
from app.core.constants import (
    ATS_WEIGHT_SKILLS, ATS_WEIGHT_SEMANTIC, ATS_WEIGHT_EXPERIENCE, 
    ATS_WEIGHT_PROJECTS, ATS_WEIGHT_FORMATTING, ACTION_VERBS
)
from app.core.logger import logger

def calculate_formatting_score(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes a structural completeness checklist and score.
    Name (15), Email (15), Phone (15), LinkedIn (15), GitHub (10), Education (15), Skills (15).
    """
    contact = parsed_data.get("contact", {})
    education = parsed_data.get("education", [])
    projects = parsed_data.get("projects", [])
    sections = parsed_data.get("sections", {})
    
    checklist = {
        "name": bool(contact.get("name") and contact.get("name") != "Unknown Candidate"),
        "email": bool(contact.get("email")),
        "phone": bool(contact.get("phone")),
        "linkedin": bool(contact.get("linkedin")),
        "github": bool(contact.get("github")),
        "education": bool(education),
        "projects": bool(projects),
        "skills": bool(sections.get("skills") or parsed_data.get("skills")),
        "certifications": bool(sections.get("certifications")),
        "achievements": bool(sections.get("achievements"))
    }
    
    # Points mapping
    score = 0
    if checklist["name"]: score += 15
    if checklist["email"]: score += 15
    if checklist["phone"]: score += 15
    if checklist["linkedin"]: score += 15
    if checklist["github"]: score += 10
    if checklist["education"]: score += 15
    if checklist["skills"]: score += 15
    
    return {
        "score": score,
        "checklist": checklist
    }

def calculate_experience_score(parsed_data: Dict[str, Any]) -> int:
    """
    Evaluates experience quality based on:
    - Presence of listed experiences (50 points)
    - Use of professional action verbs (50 points)
    """
    experience = parsed_data.get("experience", [])
    raw_text = parsed_data.get("raw_text", "").lower()
    
    if not experience:
        return 0
        
    score = 50 # Base points for having experience listed
    
    # Count matching action verbs
    verb_count = 0
    for verb in ACTION_VERBS:
        if re.search(rf"\b{verb}\b", raw_text):
            verb_count += 1
            
    # Scale verb points up to 50 (e.g. 5+ verbs = full points)
    verb_score = min(50, verb_count * 10)
    score += verb_score
    
    return min(100, score)

def calculate_projects_score(parsed_data: Dict[str, Any]) -> int:
    """
    Scores projects: 1 project = 40 pts, 2 projects = 80 pts, 3+ projects = 100 pts.
    """
    projects = parsed_data.get("projects", [])
    count = len(projects)
    if count == 0:
        return 0
    elif count == 1:
        return 40
    elif count == 2:
        return 80
    else:
        return 100

def run_ats_calculation(
    parsed_resume: Dict[str, Any],
    resume_skills: List[str],
    jd_text: Optional[str] = None,
    jd_skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Calculates the detailed ATS score and breakdown metrics.
    """
    logger.info("Initializing ATS score calculation...")
    
    # 1. Skills Matching Score (40%)
    matched_skills = []
    missing_skills = []
    skills_score = 0
    
    if jd_skills and len(jd_skills) > 0:
        semantic_res = match_skills_semantically(resume_skills, jd_skills)
        matched_skills = semantic_res["matched_skills"]
        missing_skills = semantic_res["missing_skills"]
        
        # Percent overlap
        skills_score = int((len(matched_skills) / len(jd_skills)) * 100)
    else:
        # If no Job Description is provided, default skills score to 80 if resume has skills
        skills_score = 80 if len(resume_skills) > 0 else 0
        
    # 2. Semantic Match Score (25%)
    semantic_score = 0
    if jd_text:
        similarity = calculate_semantic_similarity(parsed_resume.get("raw_text", ""), jd_text)
        semantic_score = int(similarity * 100)
    else:
        semantic_score = 70  # Default baseline similarity
        
    # 3. Experience Match Score (15%)
    experience_score = calculate_experience_score(parsed_resume)
    
    # 4. Projects Match Score (10%)
    projects_score = calculate_projects_score(parsed_resume)
    
    # 5. Formatting & Completeness Score (10%)
    formatting_res = calculate_formatting_score(parsed_resume)
    formatting_score = formatting_res["score"]
    checklist = formatting_res["checklist"]
    
    # Calculate final weighted score
    weighted_score = (
        (skills_score * ATS_WEIGHT_SKILLS) +
        (semantic_score * ATS_WEIGHT_SEMANTIC) +
        (experience_score * ATS_WEIGHT_EXPERIENCE) +
        (projects_score * ATS_WEIGHT_PROJECTS) +
        (formatting_score * ATS_WEIGHT_FORMATTING)
    )
    
    final_score = int(round(weighted_score))
    
    breakdown = {
        "skills_score": skills_score,
        "semantic_score": semantic_score,
        "experience_score": experience_score,
        "projects_score": projects_score,
        "formatting_score": formatting_score
    }
    
    logger.info(f"ATS Score computed: {final_score}/100. Breakdown: {breakdown}")
    
    return {
        "ats_score": final_score,
        "score_breakdown": breakdown,
        "checklist": checklist,
        "matched_skills": matched_skills,
        "missing_skills_list": missing_skills
    }
