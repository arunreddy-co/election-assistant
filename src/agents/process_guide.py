"""Process Guide agent for VoteReady.

Provides step-by-step election process guidance,
voter registration walkthroughs, and document checklists.

Args:
    None

Returns:
    None
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from src.services.gemini_service import get_gemini_service
from src.services.translate_service import get_translate_service
from src.utils.cache import ResponseCache
from src.utils.logger import get_logger

logger = get_logger(__name__)
cache = ResponseCache()

class ProcessGuideAgent:
    """Guides users through election processes step by step.
    
    Args:
        None
        
    Returns:
        None
    """
    
    def __init__(self):
        """Load process steps and eligibility data from JSON files.
        
        Args:
            None
            
        Returns:
            None
        """
        self.process_steps = []
        self.eligibility = {}
        
        proc_path = Path("src/data/process_steps.json")
        elig_path = Path("src/data/eligibility.json")
        
        if proc_path.exists():
            with open(proc_path, "r", encoding="utf-8") as f:
                self.process_steps = json.load(f)
                
        if elig_path.exists():
            with open(elig_path, "r", encoding="utf-8") as f:
                self.eligibility = json.load(f)
                
        self.gemini = get_gemini_service()

    async def get_overview(self, election_type: str, language: str = "en") -> Dict[str, Any]:
        """Get complete process overview for an election type.
        
        Args:
            election_type: The type of election (e.g., 'Lok Sabha').
            language: The language for the overview content.
            
        Returns:
            A dictionary containing the election type, title, 
            description, and list of steps.
        """
        for proc in self.process_steps:
            if proc.get("election_type") == election_type:
                return {
                    "election_type": election_type,
                    "title": proc.get(f"title{'_hi' if language == 'hi' else ''}", proc.get("title", "")),
                    "description": proc.get(f"description{'_hi' if language == 'hi' else ''}", proc.get("description", "")),
                    "steps": proc.get("steps", []),
                    "total_steps": len(proc.get("steps", []))
                }
        return {}

    async def get_step_detail(
        self,
        election_type: str,
        step_number: int,
        user_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Get detailed guidance for a specific process step.
        
        Args:
            election_type: The type of election.
            step_number: The sequential number of the step.
            user_context: Optional dictionary with user profile information.
            language: The preferred language for the guidance.
            
        Returns:
            A dictionary containing details for the specific step, 
            including personalized tips if user context is provided.
        """
        overview = await self.get_overview(election_type, language)
        step_data = {}
        for s in overview.get("steps", []):
            if s.get("step_number") == step_number:
                step_data = s.copy()
                break
                
        if not step_data:
            return {}
            
        step_data["title"] = step_data.get(f"title{'_hi' if language == 'hi' else ''}", step_data.get("title", ""))
        step_data["description"] = step_data.get(f"description{'_hi' if language == 'hi' else ''}", step_data.get("description", ""))
        step_data["action_items"] = step_data.get(f"action_items{'_hi' if language == 'hi' else ''}", step_data.get("action_items", []))
        
        if user_context:
            prompt = (f"Given this user profile: {json.dumps(user_context)}, provide a brief "
                      f"personalized tip (max 2 sentences) for this election step: {step_data['title']}. "
                      "Focus on what's specifically relevant to them.")
            if language == "hi":
                prompt += " Respond in Hindi."
            try:
                step_data["personalized_tip"] = await self.gemini.generate_response(prompt, user_context, language)
            except Exception as e:
                logger.error(f"Failed to generate tip: {e}")
                
        return step_data

    async def get_registration_guide(self, user_context: Optional[Dict[str, Any]] = None, language: str = "en") -> Dict[str, Any]:
        """Get voter registration guidance based on user's situation.
        
        Args:
            user_context: Optional dictionary containing user information.
            language: The language for the guidance content.
            
        Returns:
            A dictionary containing registration type, steps, 
            required documents, and online links.
        """
        reg_type = "new"
        if user_context:
            if user_context.get("is_nri"):
                reg_type = "nri"
            elif user_context.get("voter_id"):
                reg_type = "transfer"
                
        guidance = self.eligibility.get("registration_paths", {}).get(reg_type, {})
        if language == "hi" and f"{reg_type}_hi" in self.eligibility.get("registration_paths", {}):
            guidance = self.eligibility["registration_paths"][f"{reg_type}_hi"]
            
        return {
            "registration_type": reg_type,
            "steps": guidance.get("steps", []),
            "required_documents": await self.get_required_documents(reg_type, language),
            "online_link": guidance.get("online_link", "https://voters.eci.gov.in/"),
            "estimated_time": guidance.get("estimated_time", "15 mins")
        }

    async def get_required_documents(self, registration_type: str = "new", language: str = "en") -> List[Dict[str, Any]]:
        """Get list of required documents for registration.
        
        Args:
            registration_type: The type of registration (e.g., 'new', 'nri').
            language: The language for the document descriptions.
            
        Returns:
            A list of dictionaries describing the required documents.
        """
        docs = self.eligibility.get("required_documents", {}).get(registration_type, [])
        # Return docs simplified
        return docs
