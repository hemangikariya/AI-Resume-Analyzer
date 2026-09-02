import re
from typing import Dict, List, Set, Any
from app.core.constants import TECHNICAL_SKILLS
from app.core.logger import logger

def extract_skills_from_text(text: str) -> Dict[str, Any]:
    """
    Scans text for skills from the predefined taxonomy and categorizes them.
    Ensures safe boundary matching (e.g. 'c' or 'r' matches only if isolated).
    """
    if not text:
        return {
            "programming_languages": [],
            "databases": [],
            "frameworks": [],
            "cloud_tools": [],
            "ai_tools": [],
            "soft_skills": [],
            "all_skills": []
        }
        
    text_lower = text.lower()
    extracted: Dict[str, List[str]] = {}
    all_extracted_set: Set[str] = set()
    
    for category, skill_set in TECHNICAL_SKILLS.items():
        extracted[category] = []
        for skill in skill_set:
            # Match word boundary. Special handling for skills like C++, C#, .NET
            escaped_skill = re.escape(skill)
            # C++, C#, .NET need custom word boundaries because '+' and '#' are non-word chars in regex \b
            if skill in ["c++", "c#", ".net"]:
                pattern = rf"(?:^|(?<=\s)){escaped_skill}(?=\s|$|,|\.)"
            elif len(skill) <= 2:
                # Very short skill names (like R, Go) need strict boundaries
                pattern = rf"\b{escaped_skill}\b"
            else:
                pattern = rf"\b{escaped_skill}\b"
                
            if re.search(pattern, text_lower):
                extracted[category].append(skill)
                all_extracted_set.add(skill)
                
    # Sort for deterministic outputs
    for category in extracted:
        extracted[category].sort()
        
    extracted["all_skills"] = sorted(list(all_extracted_set))
    
    logger.info(f"Extracted {len(extracted['all_skills'])} unique skills from text.")
    return extracted
