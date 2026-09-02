import re
from typing import List
from app.core.cache import get_spacy_model

def clean_text_basic(text: str) -> str:
    """
    Cleans raw text by removing extra whitespaces, double spacing, 
    weird unicode quotes, and trailing garbage.
    """
    if not text:
        return ""
    # Normalize spaces and newlines
    cleaned = re.sub(r"\r+", "\n", text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)
    return cleaned.strip()

def tokenize_and_remove_stopwords(text: str) -> List[str]:
    """
    Tokenizes text and filters out punctuation and stop words using spaCy.
    """
    nlp = get_spacy_model()
    doc = nlp(text.lower())
    tokens = []
    for token in doc:
        if not token.is_stop and not token.is_punct and not token.is_space:
            tokens.append(token.lemma_)
    return tokens
