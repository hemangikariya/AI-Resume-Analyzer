import re
from typing import List, Dict, Any
from app.core.cache import get_spacy_model

# Constants for education detection
DEGREE_KEYWORDS = [
    r"b\.?s\.?c?", r"m\.?s\.?c?", r"ph\.?d", r"b\.?tech", r"m\.?tech", r"b\.?e\.?", r"m\.?e\.?",
    r"b\.?a\.?", r"m\.?a\.?", r"mba", r"bachelor", r"master", r"doctorate", r"diploma"
]

INSTITUTION_KEYWORDS = [
    r"university", r"college", r"institute", r"school", r"academy", r"technology", r"iit", r"nit", r"iiit", r"bits"
]

YEAR_REGEX = re.compile(r"\b(19|20)\d{2}\b")
YEAR_RANGE_REGEX = re.compile(r"\b(19|20)\d{2}\s*[-–—]\s*(20\d{2}|present)\b", re.IGNORECASE)

def extract_education(section_text: str) -> List[Dict[str, Any]]:
    """
    Parses education text to extract institution name, degree, and graduation dates/years.
    """
    if not section_text:
        return []
        
    lines = [line.strip() for line in section_text.split("\n") if line.strip()]
    education_entries = []
    
    nlp = get_spacy_model()
    
    current_entry = {}
    
    for line in lines:
        line_lower = line.lower()
        
        # 1. Search for degree
        detected_degree = None
        for pattern in DEGREE_KEYWORDS:
            match = re.search(rf"\b{pattern}\b", line_lower)
            if match:
                # Capture the matching phrase from original line
                start_idx = match.start()
                # Extract some context around the match
                words = line.split()
                # Find matching word index
                detected_degree = line
                break
                
        # 2. Search for institution
        detected_institution = None
        for pattern in INSTITUTION_KEYWORDS:
            if re.search(rf"\b{pattern}\b", line_lower):
                detected_institution = line
                break
                
        # 3. Search for years
        year_match = YEAR_RANGE_REGEX.search(line)
        single_year_match = YEAR_REGEX.findall(line)
        
        detected_year = None
        if year_match:
            detected_year = year_match.group(0)
        elif single_year_match:
            detected_year = " - ".join(single_year_match)

        # Build entries based on discovered cues
        if detected_institution or detected_degree:
            # If we already have something in current_entry and find new cues, save the old one
            if current_entry:
                education_entries.append(current_entry)
                current_entry = {}
                
            current_entry = {
                "institution": detected_institution or "Unknown Institution",
                "degree": detected_degree or "Degree / Coursework",
                "year": detected_year or "Date details not found"
            }
        elif detected_year and current_entry:
            # If we just find a year, update current entry
            current_entry["year"] = detected_year
            
    # Append the last entry
    if current_entry:
        education_entries.append(current_entry)
        
    # Clean duplicates or resolve empty entries
    cleaned_entries = []
    for entry in education_entries:
        # Simplify display
        inst = entry.get("institution", "")
        deg = entry.get("degree", "")
        
        # Clean line structures (remove long text)
        if len(inst) > 100:
            inst = inst[:100] + "..."
        if len(deg) > 100:
            deg = deg[:100] + "..."
            
        cleaned_entries.append({
            "institution": inst,
            "degree": deg,
            "year": entry.get("year", "Not specified")
        })
        
    return cleaned_entries
