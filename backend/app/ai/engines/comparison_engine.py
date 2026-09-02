from typing import Dict, Any, List
from app.core.logger import logger

def compare_resume_versions(
    ats_res_1: Dict[str, Any],
    ats_res_2: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compares two parsed resume versions (V1 vs V2) and details:
    - Score delta (e.g., V1: 72 -> V2: 89, Diff: +17)
    - Side-by-side section health comparison
    - Added skills and structural check improvements
    """
    logger.info("Comparing two resume versions...")
    
    score1 = ats_res_1["ats_score"]
    score2 = ats_res_2["ats_score"]
    diff = score2 - score1
    
    # Extract checklists
    chk1 = ats_res_1["checklist"]
    chk2 = ats_res_2["checklist"]
    
    # Extract matched skills (need to extract from list)
    skills1 = set(s.lower() for s in ats_res_1.get("matched_skills", []))
    skills2 = set(s.lower() for s in ats_res_2.get("matched_skills", []))
    
    added_skills = list(skills2 - skills1)
    
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
        
    # Check score breakdowns
    bd1 = ats_res_1["score_breakdown"]
    bd2 = ats_res_2["score_breakdown"]
    
    for section in ["experience_score", "projects_score", "semantic_score"]:
        sec_name = section.replace("_score", "").capitalize()
        if bd2[section] > bd1[section]:
            improved_sections.append(sec_name.lower())
            why_improvement.append(f"Improved {sec_name} quality (+{bd2[section] - bd1[section]} points)")
            
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
        "added_skills": added_skills,
        "improved_sections": list(set(improved_sections)),
        "why_improvement": why_improvement,
        "health_1": ats_res_1["resume_health"],
        "health_2": ats_res_2["resume_health"]
    }
