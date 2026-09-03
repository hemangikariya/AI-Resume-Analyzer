import threading
from app.core.logger import logger

# In-memory thread-safe global cache holders
_spacy_model = None
_spacy_lock = threading.Lock()

_sentence_transformer_model = None
_sentence_transformer_lock = threading.Lock()

def get_spacy_model():
    """
    Thread-safe lazy loader for spaCy English model.
    Only imports and loads spaCy when resume parsing or entity extraction is first executed.
    """
    global _spacy_model
    if _spacy_model is None:
        with _spacy_lock:
            if _spacy_model is None:
                import spacy
                import spacy.cli
                model_name = "en_core_web_sm"
                try:
                    logger.info(f"spaCy model loading lazily: {model_name}")
                    _spacy_model = spacy.load(model_name)
                    logger.info("spaCy model loaded lazily")
                except OSError:
                    logger.warning(f"{model_name} not found locally. Downloading lazily...")
                    try:
                        spacy.cli.download(model_name)
                        _spacy_model = spacy.load(model_name)
                        logger.info("spaCy model loaded lazily")
                    except Exception as e:
                        logger.error(f"Failed to download spaCy model {model_name}: {e}")
                        logger.info("Falling back to blank English spaCy model")
                        _spacy_model = spacy.blank("en")
    return _spacy_model

def get_sentence_transformer():
    """
    Thread-safe lazy loader for SentenceTransformer model.
    Only imports and loads SentenceTransformer when semantic embedding or RAG search is first requested.
    """
    global _sentence_transformer_model
    if _sentence_transformer_model is None:
        with _sentence_transformer_lock:
            if _sentence_transformer_model is None:
                from sentence_transformers import SentenceTransformer
                model_name = "all-MiniLM-L6-v2"
                try:
                    logger.info(f"SentenceTransformer loading lazily: {model_name}")
                    _sentence_transformer_model = SentenceTransformer(model_name)
                    logger.info("SentenceTransformer loaded lazily")
                except Exception as e:
                    logger.error(f"Failed to load SentenceTransformer model {model_name}: {e}")
                    raise e
    return _sentence_transformer_model

