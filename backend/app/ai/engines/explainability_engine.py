from typing import Dict, Any, List
from app.core.logger import logger

def calculate_missing_skill_priority(skill: str) -> int:
    """
    Rates the priority/importance of a skill (1-5 stars).
    High demand tech gets 5 stars, helper packages get less.
    """
    skill_lower = skill.lower()
    
    # 5 Stars: Devops, Cloud Core, Backend core
    if any(s in skill_lower for s in ["docker", "kubernetes", "aws", "python", "fastapi", "react", "sql", "machine learning"]):
        return 5
    # 4 Stars: Frameworks, JS dialects, Big databases
    elif any(s in skill_lower for s in ["typescript", "pytorch", "tensorflow", "mongodb", "gcp", "postgres", "django"]):
        return 4
    # 3 Stars: Utilities, Small libraries, general tools
    elif any(s in skill_lower for s in ["git", "redis", "scikit", "numpy", "pandas", "spacy", "nltk", "tailwind"]):
        return 3
    # 2 Stars: general soft skills
    else:
        return 2

def generate_explainability_report(
    ats_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Formulates a list of positive and negative modifiers with quantitative impacts,
    evaluates resume health ratings per section, and priorities missing skills.
    """
    logger.info("Generating Explainable AI score reports...")
    
    breakdown = ats_results["score_breakdown"]
    checklist = ats_results["checklist"]
    matched_skills = ats_results["matched_skills"]
    missing_skills_list = ats_results["missing_skills_list"]
    
    why_explanation: List[Dict[str, Any]] = []
    
    # 1. Evaluate Skills Matches (40%)
    skills_score = breakdown["skills_score"]
    if skills_score >= 80:
        why_explanation.append({
            "type": "positive",
            "impact": int(skills_score * 0.4),
            "label": f"Excellent skill match ({len(matched_skills)} skills aligned with Job Description)"
        })
    elif skills_score >= 40:
        why_explanation.append({
            "type": "positive",
            "impact": int(skills_score * 0.4),
            "label": f"Moderate skill overlap (matched {len(matched_skills)} requirements)"
        })
        why_explanation.append({
            "type": "negative",
            "impact": -int((100 - skills_score) * 0.4),
            "label": f"Missing {len(missing_skills_list)} required skills specified in Job Description"
        })
    else:
        why_explanation.append({
            "type": "negative",
            "impact": -int((100 - skills_score) * 0.4),
            "label": f"Low skill alignment (missing {len(missing_skills_list)} core job requirements)"
        })
        
    # 2. Evaluate Semantic Matches (25%)
    semantic_score = breakdown["semantic_score"]
    if semantic_score >= 75:
        why_explanation.append({
            "type": "positive",
            "impact": int(semantic_score * 0.25),
            "label": "Strong semantic similarity and context match with the JD"
        })
    elif semantic_score < 50:
        why_explanation.append({
            "type": "negative",
            "impact": -int((100 - semantic_score) * 0.25),
            "label": "Weak contextual alignment; resume language does not match industry terms in JD"
        })
        
    # 3. Evaluate Experiences (15%)
    exp_score = breakdown["experience_score"]
    if exp_score >= 90:
        why_explanation.append({
            "type": "positive",
            "impact": int(exp_score * 0.15),
            "label": "Strong work experience section with high-impact action verbs"
        })
    elif exp_score == 0:
        why_explanation.append({
            "type": "negative",
            "impact": -15,
            "label": "No professional experience listed or parsed from the resume"
        })
    elif exp_score < 70:
        why_explanation.append({
            "type": "negative",
            "impact": -int((100 - exp_score) * 0.15),
            "label": "Work experience description lacks professional action verbs (e.g. 'Optimized', 'Led')"
        })
        
    # 4. Evaluate Projects (10%)
    proj_score = breakdown["projects_score"]
    if proj_score == 100:
        why_explanation.append({
            "type": "positive",
            "impact": 10,
            "label": "Strong project portfolio (detected 3 or more distinct projects)"
        })
    elif proj_score == 0:
        why_explanation.append({
            "type": "negative",
            "impact": -10,
            "label": "No projects listed to demonstrate hands-on application of skills"
        })
    else:
        why_explanation.append({
            "type": "negative",
            "impact": -int((100 - proj_score) * 0.1),
            "label": f"Limited project profile (only {proj_score // 40} project(s) detected)"
        })
        
    # 5. Evaluate Formatting / Checklist details (10%)
    form_score = breakdown["formatting_score"]
    if not checklist["github"]:
        why_explanation.append({
            "type": "negative",
            "impact": -2,
            "label": "Missing GitHub profile link (highly recommended for engineering roles)"
        })
    if not checklist["linkedin"]:
        why_explanation.append({
            "type": "negative",
            "impact": -2,
            "label": "Missing LinkedIn profile link"
        })
    if not checklist["certifications"]:
        why_explanation.append({
            "type": "negative",
            "impact": -2,
            "label": "No professional certifications listed to bolster profile validity"
        })

    # Generate Resume Health Grades
    resume_health = {}
    
    # Skills Health
    if skills_score >= 80:
        resume_health["skills"] = "Excellent"
    elif skills_score >= 50:
        resume_health["skills"] = "Good"
    elif skills_score > 0:
        resume_health["skills"] = "Improve"
    else:
        resume_health["skills"] = "Missing"
        
    # Projects Health
    if proj_score == 100:
        resume_health["projects"] = "Excellent"
    elif proj_score == 80:
        resume_health["projects"] = "Good"
    elif proj_score > 0:
        resume_health["projects"] = "Average"
    else:
        resume_health["projects"] = "Missing"
        
    # Experience Health
    if exp_score >= 85:
        resume_health["experience"] = "Excellent"
    elif exp_score >= 60:
        resume_health["experience"] = "Good"
    elif exp_score > 0:
        resume_health["experience"] = "Average"
    else:
        resume_health["experience"] = "Missing"
        
    # Formatting Health
    if form_score >= 90:
        resume_health["formatting"] = "Excellent"
    elif form_score >= 70:
        resume_health["formatting"] = "Good"
    else:
        resume_health["formatting"] = "Improve"
        
    # Certifications and Achievements
    resume_health["certifications"] = "Good" if checklist["certifications"] else "Improve"
    resume_health["achievements"] = "Good" if checklist["achievements"] else "Missing"
    
    # Build missing skills priorities
    missing_skills: List[Dict[str, Any]] = []
    for skill in missing_skills_list:
        missing_skills.append({
            "skill": skill,
            "priority": calculate_missing_skill_priority(skill)
        })
        
    # Sort missing skills by priority descending
    missing_skills.sort(key=lambda x: x["priority"], reverse=True)
    
    return {
        "why_explanation": why_explanation,
        "resume_health": resume_health,
        "missing_skills": missing_skills
    }
