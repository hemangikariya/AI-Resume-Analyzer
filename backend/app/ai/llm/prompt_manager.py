import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.logger import logger

class PromptManager:
    def __init__(self):
        # Resolve path to app/ai/prompts
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        logger.info(f"Initializing PromptManager with templates directory: {self.prompts_dir}")
        
        # Initialize Jinja environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            autoescape=False
        )

    def render_prompt(self, template_name: str, **kwargs) -> str:
        """
        Loads and renders a Jinja template with the provided keyword arguments.
        Example: render_prompt("resume_summary.jinja", resume_data="...")
        """
        try:
            template = self.env.get_template(template_name)
            rendered = template.render(**kwargs)
            return rendered
        except Exception as e:
            logger.error(f"Error rendering prompt template {template_name}: {e}")
            raise RuntimeError(f"Prompt template {template_name} failed to render: {e}")

# Global instance for dependency resolution or direct import
prompt_manager = PromptManager()
