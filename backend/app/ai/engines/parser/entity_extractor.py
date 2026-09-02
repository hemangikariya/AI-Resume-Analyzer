from typing import Dict, List
from app.core.cache import get_spacy_model

def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Applies spaCy NER to extract names, organizations, dates, and locations.
    """
    nlp = get_spacy_model()
    
    # Process text limit to prevent memory bloat on large documents
    doc = nlp(text[:50000])
    
    entities: Dict[str, List[str]] = {
        "PERSON": [],
        "ORG": [],
        "GPE": [],
        "DATE": []
    }
    
    for ent in doc.ents:
        if ent.label_ in entities:
            # Clean and add unique entities
            clean_text = ent.text.strip().replace("\n", " ")
            if clean_text and clean_text not in entities[ent.label_]:
                entities[ent.label_].append(clean_text)
                
    return entities
