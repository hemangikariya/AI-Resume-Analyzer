import re
from typing import Dict, List, Tuple
from app.core.logger import logger

# Constants for common section headings
SECTION_KEYWORDS = {
    "contact": [r"contact", r"info", r"personal details", r"about me"],
    "education": [r"education", r"academic", r"studies", r"qualification", r"degrees"],
    "experience": [r"experience", r"employment", r"work history", r"professional experience", r"career history", r"work record"],
    "skills": [r"skills", r"technical skills", r"technologies", r"competencies", r"expertise", r"core strengths"],
    "projects": [r"projects", r"academic projects", r"key projects", r"personal projects", r"selected projects"],
    "certifications": [r"certifications", r"licenses", r"credentials", r"courses"],
    "languages": [r"languages", r"linguistic", r"tongues"],
    "achievements": [r"achievements", r"awards", r"honors", r"accomplishments"]
}

def detect_sections(text: str) -> Dict[str, str]:
    """
    Scans raw text and splits it into discrete text blocks per section category
    by identifying section header markers.
    """
    lines = text.split("\n")
    sections_found: List[Tuple[str, int, str]] = [] # list of (category, line_idx, raw_header)
    
    # 1. Match headings in lines
    for idx, line in enumerate(lines):
        trimmed_line = line.strip().lower()
        if not trimmed_line or len(trimmed_line) > 50:
            continue
            
        # Check against heading regex
        for category, patterns in SECTION_KEYWORDS.items():
            for pattern in patterns:
                # Matches if line starts or matches exactly the pattern (word-boundary)
                if re.search(rf"\b{pattern}\b", trimmed_line):
                    # Guard to avoid duplicates of the same category close by
                    # (e.g. "Work Experience" and "Experience Summary")
                    if not any(s[0] == category for s in sections_found):
                        sections_found.append((category, idx, line))
                        break
    
    # Sort section markers by their line index
    sections_found.sort(key=lambda x: x[1])
    
    # 2. Extract texts between markers
    parsed_sections: Dict[str, str] = {}
    total_lines = len(lines)
    
    for i, (category, line_idx, raw_header) in enumerate(sections_found):
        start_line = line_idx + 1
        end_line = sections_found[i+1][1] if i + 1 < len(sections_found) else total_lines
        
        section_text = "\n".join(lines[start_line:end_line])
        parsed_sections[category] = section_text.strip()
        
    # If a section was not detected, assign empty string
    for category in SECTION_KEYWORDS.keys():
        if category not in parsed_sections:
            parsed_sections[category] = ""
            
    # As fallback, if everything parsed as empty (no headings detected), put entire text in general
    if not any(parsed_sections.values()):
        parsed_sections["general"] = text
        
    logger.info(f"Detected sections: {[k for k, v in parsed_sections.items() if v]}")
    return parsed_sections
