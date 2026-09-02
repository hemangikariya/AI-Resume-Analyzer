from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMGateway(ABC):
    """
    Abstract interface for LLM operations. Any provider (Gemini, OpenAI, Claude)
    must implement these methods to be plugged into the application services.
    """
    
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """
        Sends a text prompt to the LLM and returns the response as string.
        """
        pass
        
    @abstractmethod
    def generate_json(self, prompt: str) -> Dict[str, Any]:
        """
        Sends a prompt expecting a JSON response. Decodes and returns a python dictionary.
        """
        pass
