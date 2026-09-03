import json
from typing import Dict, Any, List
from app.core.logger import logger

def _ensure_dict(val: Any) -> Dict[str, Any]:
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return {}

def compare_resume_versions(
    ats_res_1: Dict[str, Any],
    ats_res_2: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compares two parsed resume versions (V1 vs V2) and details:
    - Score delta (e.g., V1: 72 -> V2: 89, Diff: +17)
    - 5-factor score changes breakdown
    - Side-by-side section health comparison
    - Added and removed skills
    - Structural check improvements
    """
    logger.info("Comparing two resume versions...")
    
    score1 = int(ats_res_1.get("ats_score", 0))
    score2 = int(ats_res_2.get("ats_score", 0))
    diff = score2 - score1
    
    # Extract checklists safely
    chk1 = _ensure_dict(ats_res_1.get("checklist"))
    chk2 = _ensure_dict(ats_res_2.get("checklist"))
    
    # Extract matched skills safely
    raw_skills1 = ats_res_1.get("matched_skills", []) or []
    raw_skills2 = ats_res_2.get("matched_skills", []) or []
    
    skills1 = set(str(s).lower() for s in raw_skills1 if s)
    skills2 = set(str(s).lower() for s in raw_skills2 if s)
    
    added_skills = sorted(list(skills2 - skills1))
    removed_skills = sorted(list(skills1 - skills2))
    
    # Check score breakdowns safely
    bd1 = _ensure_dict(ats_res_1.get("score_breakdown"))
    bd2 = _ensure_dict(ats_res_2.get("score_breakdown"))
    
    score_delta_breakdown = {
        "skills_score": {
            "v1": bd1.get("skills_score", 0),
            "v2": bd2.get("skills_score", 0),
            "delta": bd2.get("skills_score", 0) - bd1.get("skills_score", 0)
        },
        "semantic_score": {
            "v1": bd1.get("semantic_score", 0),
            "v2": bd2.get("semantic_score", 0),
            "delta": bd2.get("semantic_score", 0) - bd1.get("semantic_score", 0)
        },
        "experience_score": {
            "v1": bd1.get("experience_score", 0),
            "v2": bd2.get("experience_score", 0),
            "delta": bd2.get("experience_score", 0) - bd1.get("experience_score", 0)
        },
        "projects_score": {
            "v1": bd1.get("projects_score", 0),
            "v2": bd2.get("projects_score", 0),
            "delta": bd2.get("projects_score", 0) - bd1.get("projects_score", 0)
        },
        "formatting_score": {
            "v1": bd1.get("formatting_score", 0),
            "v2": bd2.get("formatting_score", 0),
            "delta": bd2.get("formatting_score", 0) - bd1.get("formatting_score", 0)
        }
    }
    
    # Formulate structural changes
    why_improvement = []
    improved_sections = []
    
    # Check checklist differences
    for key, val in chk2.items():
        if val and not chk1.get(key, False):
            improved_sections.append(key)
            why_improvement.append(f"Added {key.capitalize()} section or link (+{key} present)")
            
    # Check skills differences
    if len(added_skills) > 0:
        improved_sections.append("skills")
        why_improvement.append(f"Successfully integrated missing skills: {', '.join(added_skills)}")
        
    for section in ["experience_score", "projects_score", "semantic_score", "skills_score", "formatting_score"]:
        sec_name = section.replace("_score", "").capitalize()
        delta_val = bd2.get(section, 0) - bd1.get(section, 0)
        if delta_val > 0:
            improved_sections.append(sec_name.lower())
            why_improvement.append(f"Improved {sec_name} quality (+{delta_val} points)")
            
    if not why_improvement:
        if diff > 0:
            why_improvement.append("Generic improvement across text structures.")
        elif diff < 0:
            why_improvement.append("Subtle formatting modifications decreased structure points.")
        else:
            why_improvement.append("No notable difference detected between versions.")
            
    return {
        "score_1": score1,
        "score_2": score2,
        "difference": diff,
        "score_delta_breakdown": score_delta_breakdown,
        "added_skills": added_skills,
        "removed_skills": removed_skills,
        "improved_sections": sorted(list(set(improved_sections))),
        "why_improvement": why_improvement,
        "health_1": _ensure_dict(ats_res_1.get("resume_health")),
        "health_2": _ensure_dict(ats_res_2.get("resume_health"))
    }

