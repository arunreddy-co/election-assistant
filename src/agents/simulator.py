"""Election Day Simulator agent for VoteReady.

Provides an interactive walkthrough of polling day.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from src.services.gemini_service import get_gemini_service
from src.utils.cache import ResponseCache
from src.utils.logger import get_logger

logger = get_logger(__name__)
cache = ResponseCache()

class SimulatorAgent:
    """Interactive election day simulation engine."""
    
    def __init__(self):
        """Load simulation scenarios from JSON."""
        self.scenarios = []
        sim_path = Path("src/data/simulator.json")
        if sim_path.exists():
            with open(sim_path, "r", encoding="utf-8") as f:
                self.scenarios = json.load(f)
                
        self.gemini = get_gemini_service()

    def get_all_scenarios(self, language: str = "en") -> List[Dict[str, Any]]:
        """Get all simulation scenarios in order."""
        safe_scenarios = []
        for i, sc in enumerate(self.scenarios):
            safe_sc = {
                "id": i,
                "step_number": i + 1,
                "scenario_text": sc.get(f"scenario_text{'_hi' if language == 'hi' else ''}", sc.get("scenario_text", "")),
                "tip": sc.get(f"tip{'_hi' if language == 'hi' else ''}", sc.get("tip", "")),
                "options": []
            }
            for j, opt in enumerate(sc.get("options", [])):
                safe_sc["options"].append({
                    "id": j,
                    "text": opt.get(f"text{'_hi' if language == 'hi' else ''}", opt.get("text", ""))
                })
            safe_scenarios.append(safe_sc)
        return safe_scenarios

    def get_scenario(self, scenario_id: int, language: str = "en") -> Optional[Dict[str, Any]]:
        """Get a single scenario by ID."""
        all_sc = self.get_all_scenarios(language)
        for sc in all_sc:
            if sc["id"] == scenario_id:
                return sc
        return None

    def check_answer(self, scenario_id: int, selected_option_id: int, language: str = "en") -> Dict[str, Any]:
        """Check if the user's answer is correct."""
        if scenario_id < 0 or scenario_id >= len(self.scenarios):
            return {"error": "Invalid scenario"}
            
        sc = self.scenarios[scenario_id]
        options = sc.get("options", [])
        
        if selected_option_id < 0 or selected_option_id >= len(options):
            return {"error": "Invalid option"}
            
        opt = options[selected_option_id]
        is_corr = opt.get("is_correct", False)
        
        correct_id = 0
        for i, o in enumerate(options):
            if o.get("is_correct"):
                correct_id = i
                break
                
        return {
            "is_correct": is_corr,
            "feedback": opt.get(f"feedback{'_hi' if language == 'hi' else ''}", opt.get("feedback", "")),
            "tip": sc.get(f"tip{'_hi' if language == 'hi' else ''}", sc.get("tip", "")),
            "correct_option_id": correct_id
        }

    async def get_dynamic_feedback(self, scenario_text: str, user_choice: str, is_correct: bool, user_name: Optional[str] = None, language: str = "en") -> str:
        """Generate personalized feedback using Gemini."""
        try:
            return await self.gemini.generate_simulator_feedback(scenario_text, user_choice, is_correct, language)
        except Exception as e:
            logger.error(f"Failed dynamic feedback: {e}")
            return "Good effort!"

    def calculate_score(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate final simulation score."""
        total = len(self.scenarios)
        correct = sum(1 for a in answers if a.get("is_correct"))
        pct = (correct / total) * 100 if total > 0 else 0
        
        rating = "Excellent! You're fully prepared for election day!"
        if pct < 50:
            rating = "Keep learning! Try the simulator again."
        elif pct < 70:
            rating = "Good start! Review the steps you missed."
        elif pct < 100:
            rating = "Great job! You know the process well."
            
        return {
            "total_scenarios": total,
            "correct_count": correct,
            "score_percentage": pct,
            "rating": rating,
            "completion_message": rating
        }
