import json
from typing import Dict, Any, List
from app.core.logger import logger

def validate_json_schema(data: Any, expected_keys: List[str]) -> bool:
    """
    Validates that the given object is a dictionary containing all expected keys.
    """
    if not isinstance(data, dict):
        logger.warning(f"Validation failed: Data is not a dictionary. Type: {type(data)}")
        return False
        
    for key in expected_keys:
        if key not in data:
            logger.warning(f"Validation failed: Expected key '{key}' was missing.")
            return False
            
    return True

def clean_and_parse_llm_json(raw_text: str, expected_keys: List[str], fallback: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses, cleans, and validates raw text output from an LLM. 
    Falls back to a safe default if parsing or validation fails.
    """
    try:
        # Basic sanitizing
        cleaned = raw_text.strip()
        # Find JSON boundaries
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        
        if start_idx != -1 and end_idx != -1:
            cleaned = cleaned[start_idx:end_idx + 1]
            
        data = json.loads(cleaned)
        
        if validate_json_schema(data, expected_keys):
            return data
            
        logger.warning("JSON parsed successfully but failed schema validation. Returning fallback.")
        return fallback
        
    except Exception as e:
        logger.error(f"Error parsing JSON from LLM text: {e}. Raw text preview: {raw_text[:200]}")
        return fallback
