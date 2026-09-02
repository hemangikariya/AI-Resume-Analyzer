import re
from typing import List, Dict, Any
from app.core.cache import get_spacy_model

# Constants for experience detection
COMMON_JOB_TITLES = [
    r"engineer", r"developer", r"analyst", r"manager", r"intern", r"lead", r"architect",
    r"programmer", r"specialist", r"consultant", r"designer", r"scientist", r"administrator", r"officer"
]

DATE_RANGE_PATTERN = re.compile(
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{2,4}\s*[-–—]\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{2,4}|present|current)\b",
    re.IGNORECASE
)

def extract_experience(section_text: str) -> List[Dict[str, Any]]:
    """
    Parses experience text blocks into list of job records.
    """
    if not section_text:
        return []
        
    lines = [line.strip() for line in section_text.split("\n") if line.strip()]
    experience_entries = []
    
    current_entry = {}
    current_description = []
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if line looks like a job title
        is_title = False
        for title in COMMON_JOB_TITLES:
            if re.search(rf"\b{title}\b", line_lower):
                is_title = True
                break
                
        # Check if date range is present
        date_match = DATE_RANGE_PATTERN.search(line)
        
        if is_title or date_match:
            # Save previous entry if exists
            if current_entry:
                current_entry["description"] = "\n".join(current_description).strip()
                experience_entries.append(current_entry)
                current_entry = {}
                current_description = []
                
            detected_date = date_match.group(0) if date_match else "Not specified"
            
            # Estimate company name using basic split or ORGs
            # Usually line format: Job Title | Company Name | Date
            # Or Job Title - Company Name
            company_candidate = "Unknown Company"
            parts = re.split(r"[-|•–—,]", line)
            
            if len(parts) > 1:
                # Remove title and date from candidates
                clean_parts = []
                for p in parts:
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    # Skip if it is the date
                    if DATE_RANGE_PATTERN.search(p_clean):
                        continue
                    # Skip if it matches a job title keyword exactly
                    if any(t in p_clean.lower() for t in COMMON_JOB_TITLES) and len(clean_parts) == 0:
                        job_title_candidate = p_clean
                        continue
                    clean_parts.append(p_clean)
                    
                if clean_parts:
                    company_candidate = clean_parts[0]
            else:
                job_title_candidate = line
                
            # If no splits occurred
            if 'job_title_candidate' not in locals():
                job_title_candidate = line
                
            # Strip date from title if date was on the same line
            if date_match:
                job_title_candidate = job_title_candidate.replace(detected_date, "").strip()
                
            current_entry = {
                "title": job_title_candidate[:100].strip(),
                "company": company_candidate[:100].strip(),
                "duration": detected_date,
                "description": ""
            }
        else:
            # It's description bullet points
            if current_entry:
                current_description.append(line)
                
    # Save the last item
    if current_entry:
        current_entry["description"] = "\n".join(current_description).strip()
        experience_entries.append(current_entry)
        
    return experience_entries
