import re
from typing import Dict, Optional
from app.core.cache import get_spacy_model

# Regular expressions for contact info
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LINKEDIN_REGEX = re.compile(r"linkedin\.com/in/[a-zA-Z0-9_-]+")
GITHUB_REGEX = re.compile(r"github\.com/[a-zA-Z0-9_-]+")

LABEL_PATTERNS = re.compile(r"\b(email|phone|mobile|tel|linkedin|github|address|contact|resume|cv|portfolio|profile|summary|education|experience|projects|skills|certifications)\b.*$", re.IGNORECASE)
DELIMITER_PATTERNS = re.compile(r"[\t|•·–—:]")
NON_NAME_WORDS = {"education", "experience", "projects", "skills", "certifications", "achievements", "summary", "profile", "resume", "curriculum", "vitae", "university", "college", "school", "secondary"}

def clean_candidate_name(raw_name: str) -> str:
    """Strips contact labels, delimiters, and non-name characters from a name candidate."""
    if not raw_name:
        return ""
    # Strip after any delimiter
    cleaned = DELIMITER_PATTERNS.split(raw_name)[0]
    # Strip label patterns
    cleaned = LABEL_PATTERNS.sub("", cleaned)
    # Strip non-alpha characters except space, dot, hyphen, apostrophe
    cleaned = re.sub(r"[^\w\s\.\-']", "", cleaned)
    # Normalize whitespace
    cleaned = " ".join(cleaned.split()).strip()
    return cleaned

def extract_name_from_text(text: str) -> Optional[str]:
    """
    Extracts the candidate name generically without contact/section label contamination.
    1. Evaluates top lines for candidate person names.
    2. Applies spaCy NER and structural capital letter checks.
    3. Strips trailing contact label words (Email, Phone, etc.).
    """
    nlp = get_spacy_model()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    if not lines:
        return "Unknown Candidate"
        
    cleaned_lines = []
    for l in lines[:5]:
        cl = clean_candidate_name(l)
        words = [w for w in cl.split() if w.lower() not in NON_NAME_WORDS]
        if 2 <= len(words) <= 4 and not any(c.isdigit() for c in cl):
            cleaned_lines.append(" ".join(words))
            
    # Check spaCy NER on cleaned candidates
    for candidate in cleaned_lines:
        doc = nlp(candidate)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                cleaned_ent = clean_candidate_name(ent.text)
                if len(cleaned_ent.split()) >= 2:
                    return cleaned_ent
                    
        # Capitalization heuristic (e.g. 'Alex Mercer')
        words = candidate.split()
        if len(words) in (2, 3) and all(w[0].isupper() for w in words if w):
            return candidate
            
    return cleaned_lines[0] if cleaned_lines else "Unknown Candidate"

def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts name, email, phone, linkedin, and github URL endpoints from raw text.
    """
    email_match = EMAIL_REGEX.search(text)
    phone_match = PHONE_REGEX.search(text)
    linkedin_match = LINKEDIN_REGEX.search(text)
    github_match = GITHUB_REGEX.search(text)
    
    name = extract_name_from_text(text)
    
    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
        "linkedin": f"https://{linkedin_match.group(0)}" if linkedin_match else None,
        "github": f"https://{github_match.group(0)}" if github_match else None
    }
