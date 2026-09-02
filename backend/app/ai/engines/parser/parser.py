from pathlib import Path
from typing import Dict, Any
from app.ai.engines.parser.loader import load_document_text
from app.ai.engines.parser.cleaner import clean_text_basic
from app.ai.engines.parser.section_detector import detect_sections
from app.ai.engines.parser.contact_extractor import extract_contact_info
from app.ai.engines.parser.education_extractor import extract_education
from app.ai.engines.parser.experience_extractor import extract_experience
from app.ai.engines.parser.project_extractor import extract_projects
from app.core.logger import logger

def parse_resume_document(file_path: Path) -> Dict[str, Any]:
    """
    Orchestrates the entire document parsing pipeline.
    Returns structured data for storage and analysis.
    """
    logger.info(f"Parsing process started for file path: {file_path}")
    
    # 1. Load document text
    raw_text = load_document_text(file_path)
    if not raw_text:
        logger.error(f"No text extracted from document: {file_path.name}")
        raise ValueError("Could not extract any text from the document. Please verify the file is not corrupted.")
        
    # 2. Basic cleaning
    cleaned_text = clean_text_basic(raw_text)
    
    # 3. Detect sections
    sections = detect_sections(cleaned_text)
    
    # 4. Extract contact details from the whole text or contact section
    contact_text = sections.get("contact", "")
    # Fallback to sample the first 1000 characters if contact section is empty
    if not contact_text:
        contact_text = cleaned_text[:1500]
    contact_info = extract_contact_info(contact_text)
    
    # 5. Extract academic details
    education_text = sections.get("education", "")
    education_info = extract_education(education_text)
    
    # 6. Extract experience
    experience_text = sections.get("experience", "")
    experience_info = extract_experience(experience_text)
    
    # 7. Extract projects
    projects_text = sections.get("projects", "")
    projects_info = extract_projects(projects_text)
    
    # Assemble parsed layout
    parsed_layout = {
        "contact": contact_info,
        "education": education_info,
        "experience": experience_info,
        "projects": projects_info,
        "sections": {
            "skills": sections.get("skills", ""),
            "certifications": sections.get("certifications", ""),
            "languages": sections.get("languages", ""),
            "achievements": sections.get("achievements", "")
        },
        "raw_text": cleaned_text
    }
    
    logger.info(f"Parsing complete for {file_path.name}. Found name: {contact_info.get('name')}")
    return parsed_layout
