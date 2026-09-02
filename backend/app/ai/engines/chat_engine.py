from typing import Dict, Any, List
from app.ai.llm.gemini_gateway import gemini_gateway
from app.ai.llm.prompt_manager import prompt_manager
from app.core.logger import logger

def run_resume_chat(
    parsed_data: Dict[str, Any],
    message: str,
    history: List[Dict[str, str]]
) -> str:
    """
    Formulates a RAG context using only the parsed resume details,
    compiles it into the chat template, and calls the Gemini Gateway.
    """
    from app.services.retrieval_service import RetrievalService
    logger.info("Retrieving optimized context chunks for Resume Chat...")
    
    formatted_context = RetrievalService.retrieve_context(parsed_data, message)
    
    # Render prompt via prompt manager
    rendered_prompt = prompt_manager.render_prompt(
        "resume_chat.jinja",
        resume_context=formatted_context,
        query=message
    )
    
    # Prepend history as instructions or pass directly
    # For simplicity, we can inject history into the prompt text
    history_str = ""
    if history:
        history_str = "Conversation History:\n"
        for turn in history[-5:]:  # Keep last 5 turns to preserve tokens
            role = "User" if turn.get("role") == "user" else "Assistant"
            history_str += f"{role}: {turn.get('content')}\n"
        rendered_prompt = f"{history_str}\n=== CURRENT INQUIRY ===\n{rendered_prompt}"
        
    logger.info("Calling Gemini Gateway for Resume Chat response...")
    response = gemini_gateway.generate_text(rendered_prompt)
    
    return response
