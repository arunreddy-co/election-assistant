"""Eligibility agent for VoteReady.

Determines voter eligibility based on user profile,
provides personalized guidance for different voter categories.

Args:
    None

Returns:
    None
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.services.gemini_service import get_gemini_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

class VoterCategory:
    """Voter categories based on eligibility check.
    
    Args:
        None
        
    Returns:
        None
    """
    UNDER_18 = "under_18"
    FIRST_TIME = "first_time_voter"
    REGISTERED = "registered_voter"
    NRI = "nri_voter"
    UNREGISTERED = "unregistered"

class EligibilityAgent:
    """Checks voter eligibility and categorizes users.
    
    Args:
        None
        
    Returns:
        None
    """
    
    def __init__(self):
        """Load eligibility rules from JSON.
        
        Args:
            None
            
        Returns:
            None
        """
        self.turnout_stats = {}
        
        turnout_path = Path("src/data/turnout_stats.json")
        if turnout_path.exists():
            with open(turnout_path, "r", encoding="utf-8") as f:
                self.turnout_stats = json.load(f)
                
        self.gemini = get_gemini_service()

    def check_eligibility(self, age: int, voter_id: Optional[str] = None, is_nri: bool = False) -> Dict[str, Any]:
        """Determine voter eligibility and category.
        
        Args:
            age: The user's age in years.
            voter_id: The user's voter ID number, if available.
            is_nri: Whether the user is a Non-Resident Indian.
            
        Returns:
            A dictionary containing eligibility status, category, message, 
            next steps, and years until eligible if applicable.
        """
        if age < 18:
            return {
                "eligible": False,
                "category": VoterCategory.UNDER_18,
                "message": "Not eligible yet.",
                "next_steps": ["Pre-register info", "Learn about elections"],
                "years_until_eligible": 18 - age
            }
            
        if is_nri:
            return {
                "eligible": True,
                "category": VoterCategory.NRI,
                "message": "Eligible as NRI.",
                "next_steps": ["Register via Form 6A", "Check NRI voting rules"]
            }
            
        if not voter_id:
            if age <= 21:
                return {
                    "eligible": True,
                    "category": VoterCategory.FIRST_TIME,
                    "message": "Eligible first-time voter.",
                    "next_steps": ["Register at nvsp.in", "Get Voter ID", "Find booth"]
                }
            return {
                "eligible": True,
                "category": VoterCategory.UNREGISTERED,
                "message": "Eligible but unregistered.",
                "next_steps": ["Register immediately at nvsp.in", "Get Voter ID"]
            }
            
        return {
            "eligible": True,
            "category": VoterCategory.REGISTERED,
            "message": "Eligible registered voter.",
            "next_steps": ["Verify registration", "Find booth", "Check dates"]
        }

    async def get_personalized_guidance(self, category: str, user_context: Dict[str, Any], language: str = "en") -> Dict[str, Any]:
        """Generate personalized guidance based on voter category.
        
        Args:
            category: The voter's eligibility category.
            user_context: Dictionary containing user profile information.
            language: The preferred language for the guidance message.
            
        Returns:
            A dictionary containing the guidance message, a fun fact, 
            and a motivation stat.
        """
        age = user_context.get("age", 18)
        state = user_context.get("state", "India")
        name = user_context.get("name", "Voter")
        
        prompt = (f"Generate a 2-sentence encouraging message for a {category} "
                  f"named {name} from {state}. They are {age} years old. "
                  "Make them feel empowered about participating in democracy.")
        if language == "hi":
            prompt += " Respond in Hindi."
            
        msg = "Your vote is your voice."
        try:
            msg = await self.gemini.generate_response(prompt, user_context, language)
        except Exception as e:
            logger.error(f"Failed to generate guidance: {e}")
            
        return {
            "guidance_message": msg,
            "fun_fact": "India is the world's largest democracy.",
            "motivation_stat": f"Youth turnout in {state} is growing!"
        }

    def get_age_group_stats(self, age: int) -> Dict[str, Any]:
        """Get voting statistics for the user's age group.
        
        Args:
            age: The user's age in years.
            
        Returns:
            A dictionary containing the age group label, turnout 
            percentage, and a comparison message.
        """
        group = "18-25"
        if age > 60: group = "60+"
        elif age > 40: group = "40-60"
        elif age > 25: group = "25-40"
        
        percentage = 50.0  # default fallback
        for entry in self.turnout_stats.get("age_group_turnout", []):
            if entry.get("age_range") == group:
                percentage = entry.get("percentage", 50.0)
                break
        
        return {
            "age_group": group,
            "turnout_percentage": percentage,
            "comparison_message": f"Your age group ({group}) votes at {percentage}%."
        }
