import spacy
import spacy.cli
from sentence_transformers import SentenceTransformer
from app.core.logger import logger

# In-memory global cache holders
_spacy_model = None
_sentence_transformer_model = None

def get_spacy_model():
    """
    Retrieves the spaCy English model. Programmatically downloads it
    if it is not already installed.
    """
    global _spacy_model
    if _spacy_model is None:
        model_name = "en_core_web_sm"
        try:
            logger.info(f"Loading spaCy model: {model_name}")
            _spacy_model = spacy.load(model_name)
        except OSError:
            logger.warning(f"{model_name} not found. Attempting to download it programmatically...")
            try:
                spacy.cli.download(model_name)
                _spacy_model = spacy.load(model_name)
                logger.info(f"Successfully downloaded and loaded {model_name}")
            except Exception as e:
                logger.error(f"Failed to download spaCy model {model_name}: {e}")
                # Fallback to a blank model if all else fails
                logger.info("Falling back to blank English spaCy model")
                _spacy_model = spacy.blank("en")
    return _spacy_model

def get_sentence_transformer():
    """
    Retrieves the SentenceTransformer model. Lazy loads the model and caches it.
    """
    global _sentence_transformer_model
    if _sentence_transformer_model is None:
        model_name = "all-MiniLM-L6-v2"
        try:
            logger.info(f"Loading SentenceTransformer model: {model_name}")
            _sentence_transformer_model = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded SentenceTransformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model {model_name}: {e}")
            raise e
    return _sentence_transformer_model

def prewarm_models():
    """
    Pre-warms NLP models on startup.
    """
    logger.info("Initializing pre-warming of AI/NLP models...")
    try:
        get_spacy_model()
        get_sentence_transformer()
        logger.info("AI/NLP models successfully pre-warmed and cached.")
    except Exception as e:
        logger.error(f"Error during pre-warming AI/NLP models: {e}")
