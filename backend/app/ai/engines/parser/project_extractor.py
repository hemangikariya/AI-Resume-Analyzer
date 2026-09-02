import re
from typing import List, Dict, Any

def extract_projects(section_text: str) -> List[Dict[str, Any]]:
    """
    Extracts projects, titles, and descriptions from projects section text.
    """
    if not section_text:
        return []
        
    lines = [line.strip() for line in section_text.split("\n") if line.strip()]
    projects = []
    
    current_project = {}
    current_description = []
    
    for line in lines:
        # If the line is short and doesn't start with bullet characters (- * •),
        # it is likely a new project title
        is_bullet = line.startswith(("-", "*", "•", "▪", "◦"))
        
        if len(line) < 60 and not is_bullet and not any(k in line.lower() for k in ["project link", "github"]):
            if current_project:
                current_project["description"] = "\n".join(current_description).strip()
                projects.append(current_project)
                current_project = {}
                current_description = []
                
            current_project = {
                "title": line,
                "description": ""
            }
        else:
            if current_project:
                # Clean up leading bullet chars
                cleaned_line = re.sub(r"^[-*•▪◦]\s*", "", line)
                current_description.append(cleaned_line)
                
    # Save the last project
    if current_project:
        current_project["description"] = "\n".join(current_description).strip()
        projects.append(current_project)
        
    return projects
