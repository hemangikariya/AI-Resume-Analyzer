import json
import re
import time
from typing import Dict, Any
import google.generativeai as genai
from app.ai.llm.llm_gateway import LLMGateway
from app.core.settings import settings
from app.core.logger import logger

def clean_json_response(text: str) -> str:
    """Removes markdown code blocks (e.g., ```json ... ```) from LLM output."""
    # Find anything between ```json and ```
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Strip any leading/trailing backticks
    cleaned = text.strip().lstrip("```json").rstrip("```").strip()
    return cleaned

class GeminiGateway(LLMGateway):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.MODEL_NAME
        self.initialized = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.initialized = True
                logger.info(f"Gemini API Gateway initialized successfully with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to configure Gemini SDK: {e}")
        else:
            logger.warning("GEMINI_API_KEY is not set. All LLM features will fall back to deterministic mocks.")

    def generate_text(self, prompt: str) -> str:
        if not self.initialized:
            logger.warning("Gemini API not configured. Triggering deterministic fallback text response.")
            return self._get_fallback_text(prompt)
            
        start_time = time.time()
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            latency = (time.time() - start_time) * 1000
            logger.info(f"Gemini API request succeeded in {latency:.2f}ms")
            return response.text
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"Gemini API call failed after {latency:.2f}ms: {e}. Executing fallback.")
            return self._get_fallback_text(prompt)

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        if not self.initialized:
            logger.warning("Gemini API not configured. Triggering deterministic fallback JSON response.")
            return self._get_fallback_json(prompt)
            
        start_time = time.time()
        try:
            model = genai.GenerativeModel(self.model_name)
            # Sometimes Gemini needs temperature setting to ensure strict formatting
            response = model.generate_content(prompt)
            latency = (time.time() - start_time) * 1000
            logger.info(f"Gemini API JSON request succeeded in {latency:.2f}ms")
            
            raw_text = response.text
            cleaned_text = clean_json_response(raw_text)
            
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError as jde:
                logger.error(f"Failed to parse cleaned JSON: {cleaned_text}. Error: {jde}")
                # Try raw text
                return json.loads(raw_text)
                
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"Gemini API JSON call failed after {latency:.2f}ms: {e}. Executing fallback.")
            return self._get_fallback_json(prompt)

    def _get_fallback_text(self, prompt: str) -> str:
        """Deterministic text fallbacks for various prompts in case of API failure."""
        prompt_lower = prompt.lower()
        if "cover letter" in prompt_lower:
            return (
                "Dear Hiring Manager,\n\n"
                "I am writing to express my strong interest in the open engineering position. "
                "Based on my resume, I have hands-on experience developing software applications, "
                "designing databases, and deploying services. I am confident that my technical skills "
                "align well with your requirements and that I can bring immediate value to your engineering team.\n\n"
                "Thank you for your time and consideration. I look forward to discussing my application with you.\n\n"
                "Sincerely,\nCandidate"
            )
        elif "summary" in prompt_lower or "summarize" in prompt_lower:
            return (
                "Result-driven Software Engineer with solid experience in building scalable backend services, "
                "designing web applications, and writing clean, modular code. Proficient in Python, database integrations, "
                "and full-stack software development with a passion for building AI-integrated workflows."
            )
        else:
            return "Unable to retrieve AI-generated content at this time. Please check your API key configuration."

    def _get_fallback_json(self, prompt: str) -> Dict[str, Any]:
        """Deterministic JSON fallbacks for various prompts in case of API failure."""
        prompt_lower = prompt.lower()
        if "interview" in prompt_lower:
            # Check if generate mode
            if "generate" in prompt_lower:
                return {
                    "question": "Describe a challenging technical project you worked on. What was your stack, and how did you resolve technical bottlenecks?",
                    "category": "Project"
                }
            else:
                return {
                    "score": 7,
                    "feedback": "Answer was received. You can improve by adding concrete metrics, quantitative impacts, and outlining specific design decisions.",
                    "strengths": "Demonstrated core technical understanding.",
                    "weaknesses": "Lacked specific metrics and architectural rationale."
                }
        elif "roadmap" in prompt_lower:
            return [
                {
                    "skill": "Docker",
                    "resource": "Docker Tutorial for Beginners (YouTube - Programming with Mosh)",
                    "time": "4-6 hours",
                    "project": "Dockerize a local API service and launch it using container environments.",
                    "certification": "Docker Certified Associate"
                }
            ]
        elif "career" in prompt_lower or "fit" in prompt_lower:
            return {
                "recommended": [
                    {"role": "Python Developer", "reason": "Proficient in Python core coding and API building."},
                    {"role": "AI Intern", "reason": "Familiar with basic machine learning models and NLP concepts."}
                ],
                "not_recommended": [
                    {"role": "DevOps Engineer", "gaps": ["Requires extensive containerization and orchestration knowledge."]}
                ]
            }
        elif "rewrite" in prompt_lower:
            return {
                "original_text": "Worked on database design and speed.",
                "rewritten_text": "Architected normalized relational databases and indexed schemas, improving query execution time by 30%."
            }
        elif "project" in prompt_lower or "enhance" in prompt_lower:
            return {
                "title": "Portfolio Web Application",
                "description": "Redesigned a portfolio project from scratch.",
                "technologies": ["React", "TypeScript", "FastAPI"],
                "impact": "Boosted profile visibility and provided responsive interfaces.",
                "bullets": [
                    "Engineered modular React hooks to manage central dashboard states.",
                    "Optimized FastAPI query parameters to reduce API payload sizes by 25%.",
                    "Implemented responsive Tailwind CSS components for cross-device mobile support."
                ]
            }
        else:
            return {"message": "Success", "details": "Deterministic fallback output returned."}

# Instantiate global singleton
gemini_gateway = GeminiGateway()
