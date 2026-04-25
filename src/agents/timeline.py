"""Timeline agent for VoteReady.

Provides personalized election schedules based on user's state.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from src.utils.logger import get_logger

logger = get_logger(__name__)

class TimelineAgent:
    """Generates personalized election timelines."""
    
    def __init__(self):
        """Load election schedule and state data from JSON files.
        
        Args:
            None
            
        Returns:
            None
        """
        self.elections = []
        self.states = []
        
        elec_path = Path("src/data/elections.json")
        state_path = Path("src/data/states.json")
        
        if elec_path.exists():
            with open(elec_path, "r", encoding="utf-8") as f:
                self.elections = json.load(f)
                
        if state_path.exists():
            with open(state_path, "r", encoding="utf-8") as f:
                self.states = json.load(f)

    def calculate_countdown(self, tentative_year: int, tentative_month: Optional[int]) -> Dict[str, Any]:
        """Calculate the remaining time until an election date.
        
        Args:
            tentative_year: The year the election is expected to occur.
            tentative_month: The month the election is expected to occur.
            
        Returns:
            A dictionary with days remaining, months remaining, and countdown text.
        """
        now = datetime.now()
        target_month = tentative_month or 1
        target_date = datetime(tentative_year, target_month, 1)
        
        diff = target_date - now
        days = max(0, diff.days)
        months = days // 30
        
        return {
            "days_until": days,
            "months_until": months,
            "countdown_text": f"Approximately {months} months away" if months > 2 else f"Approximately {days} days away",
            "is_within_year": days <= 365
        }

    def get_elections_for_state(self, state: str, language: str = "en") -> List[Dict[str, Any]]:
        """Get all upcoming national and state-specific elections for a given state.
        
        Args:
            state: The name of the Indian state.
            language: The language for the election titles and descriptions.
            
        Returns:
            A list of election dictionaries sorted by proximity.
        """
        state_elecs = []
        for e in self.elections:
            st = e.get("state", "")
            if st == state or st == "National":
                cd = self.calculate_countdown(e.get("tentative_year", 2029), e.get("tentative_month"))
                e_copy = e.copy()
                e_copy.update(cd)
                e_copy["title"] = e.get(f"title{'_hi' if language == 'hi' else ''}", e.get("title", ""))
                e_copy["description"] = e.get(f"description{'_hi' if language == 'hi' else ''}", e.get("description", ""))
                state_elecs.append(e_copy)
                
        state_elecs.sort(key=lambda x: x.get("days_until", 9999))
        return state_elecs

    def get_election_detail(self, state: str, election_type: str, language: str = "en") -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific election type for a state.
        
        Args:
            state: The name of the Indian state.
            election_type: The category of election (e.g., 'lok_sabha').
            language: The language for the content.
            
        Returns:
            The election detail dictionary if found, otherwise None.
        """
        elecs = self.get_elections_for_state(state, language)
        for e in elecs:
            if e.get("election_type") == election_type:
                return e
        return None

    def get_nearest_election(self, state: str, language: str = "en") -> Optional[Dict[str, Any]]:
        """Identify the single closest upcoming election for a user's location.
        
        Args:
            state: The name of the Indian state.
            language: The response language.
            
        Returns:
            The dictionary of the nearest election, or None if none exist.
        """
        elecs = self.get_elections_for_state(state, language)
        return elecs[0] if elecs else None
