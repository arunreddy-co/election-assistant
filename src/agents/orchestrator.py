"""Orchestrator agent for VoteReady.

Classifies user intent from chat messages and routes
to the appropriate specialist agent. Acts as the single
entry point for all AI-powered interactions.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from src.services.gemini_service import get_gemini_service
from src.utils.cache import ResponseCache
from src.utils.logger import get_logger

from src.agents.process_guide import ProcessGuideAgent
from src.agents.eligibility import EligibilityAgent
from src.agents.timeline import TimelineAgent

logger = get_logger(__name__)
cache = ResponseCache()

class IntentCategory:
    """Valid intent categories for routing."""
    PROCESS = "process"
    ELIGIBILITY = "eligibility"
    TIMELINE = "timeline"
    REGISTRATION = "registration"
    POLLING_BOOTH = "polling_booth"
    SIMULATOR = "simulator"
    FAQ = "faq"
    GENERAL = "general"
    OFF_TOPIC = "off_topic"

class Orchestrator:
    """Routes user queries to specialist agents."""
    
    KEYWORD_MAP = {
        IntentCategory.ELIGIBILITY: ["eligible", "eligibility", "can i vote", "age", "पात्र", "पात्रता"],
        IntentCategory.POLLING_BOOTH: ["booth", "where to vote", "polling station", "location", "find booth", "nearest", "बूथ", "कहां वोट"],
        IntentCategory.PROCESS: ["how to vote", "voting process", "election process", "steps", "procedure", "evm", "vvpat", "polling procedure", "मतदान प्रक्रिया", "कैसे वोट करें"],
        IntentCategory.TIMELINE: ["when", "date", "schedule", "next election", "upcoming", "timeline", "कब", "तारीख", "अगला चुनाव"],
        IntentCategory.REGISTRATION: ["register", "registration", "voter id", "epic", "form 6", "nri vote", "nvsp", "apply", "new voter", "पंजीकरण", "मतदाता पहचान"],
        IntentCategory.SIMULATOR: ["simulate", "practice", "mock", "election day", "what happens", "try voting", "अभ्यास"],
    }
    
    def __init__(self):
        """Initialize orchestrator with FAQ data."""
        faq_path = Path("src/data/faq.json")
        self.faqs = []
        if faq_path.exists():
            with open(faq_path, "r", encoding="utf-8") as f:
                self.faqs = json.load(f)
        self.gemini = get_gemini_service()
        self.process_agent = ProcessGuideAgent()
        self.eligibility_agent = EligibilityAgent()
        self.timeline_agent = TimelineAgent()

    def _keyword_match(self, message: str) -> Optional[str]:
        """Check message against keyword map."""
        msg = message.lower().strip()
        for intent, keywords in self.KEYWORD_MAP.items():
            if any(k in msg for k in keywords):
                return intent
        return None

    def _faq_match(self, message: str) -> Optional[Dict[str, Any]]:
        """Check if message matches a known FAQ question."""
        msg = message.lower().strip()
        for faq in self.faqs:
            q_en = faq.get("question", "").lower()
            q_hi = faq.get("question_hi", "").lower()
            if msg in q_en or q_en in msg or msg in q_hi or q_hi in msg:
                return faq
        return None

    async def classify_intent(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Classify user message into an intent category."""
        matched_intent = self._keyword_match(message)
        if matched_intent:
            return matched_intent
            
        if self._faq_match(message):
            return IntentCategory.FAQ

        prompt = (f"Classify this election-related question into exactly one category: "
                  f"process, eligibility, timeline, registration, polling_booth, general, off_topic. "
                  f"Question: {message}. Respond with ONLY the category name.")
        
        try:
            resp = await self.gemini.model.generate_content_async(prompt)
            cat = resp.text.strip().lower()
            return cat if cat in vars(IntentCategory).values() else IntentCategory.GENERAL
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return IntentCategory.GENERAL

    async def route_and_respond(self, message: str, user_context: Optional[Dict[str, Any]] = None, language: str = "en") -> Dict[str, Any]:
        """Classify intent, route to agent, and return response."""
        intent = await self.classify_intent(message, user_context)
        
        if intent == IntentCategory.FAQ:
            faq = self._faq_match(message)
            resp_text = faq.get(f"answer{'_hi' if language == 'hi' else ''}")
            return {"intent": intent, "response": resp_text, "suggestions": []}
            
        if intent == IntentCategory.OFF_TOPIC:
            resp_text = "I'm here to help with election questions. What would you like to know?"
            return {"intent": intent, "response": resp_text, "suggestions": ["Check my eligibility", "Find upcoming elections"]}
            
        if intent == IntentCategory.PROCESS:
            overview = await self.process_agent.get_overview("lok_sabha", language)
            resp_text = f"Here is an overview of the {overview.get('title')}: {overview.get('description')}"
            return {"intent": intent, "response": resp_text, "suggestions": ["Show me step 1", "Simulator"]}
            
        if intent == IntentCategory.ELIGIBILITY:
            age = user_context.get("age", 18) if user_context else 18
            voter_id = user_context.get("voter_id") if user_context else None
            is_nri = user_context.get("is_nri", False) if user_context else False
            elig = self.eligibility_agent.check_eligibility(age, voter_id, is_nri)
            resp_text = elig.get("message")
            return {"intent": intent, "response": resp_text, "suggestions": ["How to register", "Find booth"]}
            
        if intent == IntentCategory.TIMELINE:
            state = user_context.get("state", "India") if user_context else "India"
            nearest = self.timeline_agent.get_nearest_election(state, language)
            resp_text = f"The nearest election is {nearest.get('title')} in {nearest.get('days_until')} days." if nearest else "No upcoming elections found."
            return {"intent": intent, "response": resp_text, "suggestions": ["Find my booth", "Register to vote"]}
            
        if intent == IntentCategory.REGISTRATION:
            guide = await self.process_agent.get_registration_guide(user_context, language)
            resp_text = f"You can register online at {guide.get('online_link')}. It takes about {guide.get('estimated_time')}."
            return {"intent": intent, "response": resp_text, "suggestions": ["What documents do I need?"]}
            
        if intent == IntentCategory.POLLING_BOOTH:
            return {"intent": intent, "response": "Use our booth finder tool to locate your nearest polling station.", "suggestions": ["Open Booth Finder"], "booth_finder": True}
            
        if intent == IntentCategory.SIMULATOR:
            return {"intent": intent, "response": "Let's practice voting! Launching the simulator...", "suggestions": ["Start Simulator"], "simulator": True}
            
        resp_text = await self.gemini.generate_response(message, user_context, language)
        return {"intent": intent, "response": resp_text, "suggestions": ["How to register", "When is the next election?"]}
