import logging
import sys
from pathlib import Path
from app.core.settings import settings

def setup_logger() -> logging.Logger:
    # Ensure logs folder exists
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(settings.PROJECT_NAME)
    logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    try:
        file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to set up file logging: {e}")
        
    return logger

logger = setup_logger()
