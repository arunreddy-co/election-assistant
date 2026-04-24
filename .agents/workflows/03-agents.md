---
description: Build all five agents — Orchestrator, Process Guide, Eligibility, Timeline, and Simulator. These are the intelligence layer that sits between the API endpoints and the Google service wrappers. Run AFTER workflow 02-services is complete and verified.
---

# Workflow 03: Agent Implementation

## Important Context
- Agents are the BRAIN of the application — they contain business logic
- Agents call services (gemini_service, maps_service, etc.) — never raw APIs
- Agents load data from src/data/ JSON files — never hardcode election content
- Every agent method must check the in-memory cache before calling Gemini
- Every agent must be stateless — all state comes from function parameters
- Follow AGENTS.md coding standards strictly: docstrings, type hints, 30-line max per function

## Step 1: Create src/agents/orchestrator.py

The orchestrator is the router — it classifies user intent and delegates to the right specialist agent.

```python
"""Orchestrator agent for VoteReady.

Classifies user intent from chat messages and routes
to the appropriate specialist agent. Acts as the single
entry point for all AI-powered interactions.
"""

import json
from pathlib import Path

from src.services.gemini_service import get_gemini_service
from src.utils.cache import ResponseCache
from src.utils.logger import get_logger

logger = get_logger(__name__)
cache = ResponseCache()


class IntentCategory:
    """Valid intent categories for routing."""
    PROCESS = "process"           # How elections work
    ELIGIBILITY = "eligibility"   # Am I eligible? How to register?
    TIMELINE = "timeline"         # When are elections?
    REGISTRATION = "registration" # How to get voter ID
    POLLING_BOOTH = "polling_booth"  # Where do I vote?
    SIMULATOR = "simulator"       # Practice election day
    FAQ = "faq"                   # Common questions
    GENERAL = "general"           # Open-ended election chat
    OFF_TOPIC = "off_topic"       # Non-election questions


class Orchestrator:
    """Routes user queries to specialist agents.
    
    Uses a two-tier classification:
    1. Keyword matching for obvious intents (fast, no API call)
    2. Gemini classification for ambiguous queries (slower, cached)
    """
    
    KEYWORD_MAP = {
        IntentCategory.ELIGIBILITY: [
            "eligible", "eligibility", "can i vote", "age", "register",
            "registration", "voter id", "epic", "form 6", "nri vote",
            "पात्र", "पात्रता", "मतदाता", "पंजीकरण"
        ],
        IntentCategory.PROCESS: [
            "how to vote", "voting process", "election process", "steps",
            "procedure", "evm", "vvpat", "polling", "booth process",
            "मतदान प्रक्रिया", "कैसे वोट करें"
        ],
        IntentCategory.TIMELINE: [
            "when", "date", "schedule", "next election", "upcoming",
            "timeline", "कब", "तारीख", "अगला चुनाव"
        ],
        IntentCategory.REGISTRATION: [
            "register", "voter id", "epic", "form 6", "nvsp",
            "apply", "new voter", "पंजीकरण", "मतदाता पहचान"
        ],
        IntentCategory.POLLING_BOOTH: [
            "booth", "where to vote", "polling station", "location",
            "find booth", "nearest", "बूथ", "कहां वोट"
        ],
        IntentCategory.SIMULATOR: [
            "simulate", "practice", "mock", "election day",
            "what happens", "try voting", "अभ्यास"
        ],
    }
    
    def __init__(self):
        """Initialize orchestrator with FAQ data."""
        # Load faq.json for FAQ matching
        # Initialize gemini service reference
    
    async def classify_intent(
        self, 
        message: str, 
        user_context: dict | None = None
    ) -> str:
        """Classify user message into an intent category.
        
        Uses keyword matching first (fast path), falls back
        to Gemini classification for ambiguous queries.
        
        Args:
            message: The user's message text.
            user_context: Optional user profile for context.
            
        Returns:
            IntentCategory string.
        """
        # Step 1: Normalize message (lowercase, strip)
        # Step 2: Check keyword map — if any keyword found, return that category
        # Step 3: Check FAQ — if message closely matches an FAQ question, return FAQ
        # Step 4: Fall back to Gemini classification
        #   Prompt: "Classify this election-related question into exactly
        #            one category: process, eligibility, timeline, registration,
        #            polling_booth, general, off_topic.
        #            Question: {message}
        #            Respond with ONLY the category name, nothing else."
        # Step 5: Cache the classification result
        # Step 6: Return the category (default to "general" if unrecognized)
    
    def _keyword_match(self, message: str) -> str | None:
        """Check message against keyword map.
        
        Args:
            message: Lowercased user message.
            
        Returns:
            IntentCategory if matched, None otherwise.
        """
        # Iterate KEYWORD_MAP
        # Return first category where any keyword is found in message
        # Return None if no match
    
    def _faq_match(self, message: str) -> dict | None:
        """Check if message matches a known FAQ question.
        
        Args:
            message: Lowercased user message.
            
        Returns:
            FAQ entry dict if matched, None otherwise.
        """
        # Simple substring matching against FAQ questions
        # Return the FAQ entry if a strong match is found
        # Return None if no match
    
    async def route_and_respond(
        self,
        message: str,
        user_context: dict | None = None,
        language: str = "en"
    ) -> dict:
        """Classify intent, route to agent, and return response.
        
        This is the main entry point called by the /api/chat endpoint.
        
        Args:
            message: User's message.
            user_context: User profile data.
            language: Response language.
            
        Returns:
            Dict with keys: intent, response, suggestions (list of follow-up prompts)
        """
        # 1. Classify intent
        # 2. If FAQ match, return the pre-written answer (no Gemini call)
        # 3. If OFF_TOPIC, return polite redirect message
        # 4. Route to appropriate agent:
        #    - PROCESS → ProcessGuideAgent.get_overview()
        #    - ELIGIBILITY → EligibilityAgent.check_eligibility()
        #    - TIMELINE → TimelineAgent.get_elections()
        #    - REGISTRATION → ProcessGuideAgent.get_registration_guide()
        #    - POLLING_BOOTH → return booth_finder flag (handled by frontend)
        #    - SIMULATOR → return simulator flag (handled by frontend)
        #    - GENERAL → GeminiService.generate_response()
        # 5. Include 2-3 follow-up suggestions based on intent
        # 6. Return structured response dict
```

## Step 2: Create src/agents/process_guide.py

```python
"""Process Guide agent for VoteReady.

Provides step-by-step election process guidance,
voter registration walkthroughs, and document checklists.
Loads static content from JSON, uses Gemini only for personalization.
"""

import json
from pathlib import Path

from src.services.gemini_service import get_gemini_service
from src.services.translate_service import get_translate_service
from src.utils.cache import ResponseCache
from src.utils.logger import get_logger

logger = get_logger(__name__)
cache = ResponseCache()


class ProcessGuideAgent:
    """Guides users through election processes step by step.
    
    Primary data source: process_steps.json and eligibility.json
    Uses Gemini ONLY when personalizing guidance based on user context.
    """
    
    def __init__(self):
        """Load process steps and eligibility data from JSON files."""
        # Load src/data/process_steps.json
        # Load src/data/eligibility.json
    
    async def get_overview(
        self,
        election_type: str,
        language: str = "en"
    ) -> dict:
        """Get complete process overview for an election type.
        
        Args:
            election_type: "lok_sabha", "vidhan_sabha", 
                          "municipal", or "panchayat".
            language: Response language.
            
        Returns:
            Dict with: election_type, title, steps (list of step dicts),
            total_steps count.
        """
        # Look up steps from process_steps.json by election_type
        # Return title and title_hi based on language
        # Return description and description_hi based on language
        # Return all steps with language-appropriate text
    
    async def get_step_detail(
        self,
        election_type: str,
        step_number: int,
        user_context: dict | None = None,
        language: str = "en"
    ) -> dict:
        """Get detailed guidance for a specific process step.
        
        If user_context is provided, uses Gemini to personalize
        the guidance (e.g., "Since you're 19 and from Telangana...").
        Otherwise returns the static content from JSON.
        
        Args:
            election_type: Type of election.
            step_number: Which step (1-indexed).
            user_context: Optional user profile for personalization.
            language: Response language.
            
        Returns:
            Dict with: step_number, title, description, action_items,
            documents_needed, links, personalized_tip (if context provided).
        """
        # 1. Load the step from JSON
        # 2. Select language-appropriate fields
        # 3. If user_context provided:
        #    - Check cache for this user+step combination
        #    - If not cached, call Gemini:
        #      "Given this user profile: {context}, provide a brief
        #       personalized tip (max 2 sentences) for this election step:
        #       {step_title}. Focus on what's specifically relevant to them."
        #    - Cache the result
        #    - Add as personalized_tip field
        # 4. Return complete step dict
    
    async def get_registration_guide(
        self,
        user_context: dict | None = None,
        language: str = "en"
    ) -> dict:
        """Get voter registration guidance based on user's situation.
        
        Determines which registration path applies:
        - New voter (no voter ID) → Form 6 process
        - NRI → Form 6A process
        - Address change → Transfer process
        - Corrections → Form 8 process
        
        Args:
            user_context: User profile with voter_id and state info.
            language: Response language.
            
        Returns:
            Dict with: registration_type, steps, required_documents,
            online_link, estimated_time.
        """
        # Determine registration type from user_context
        # If no voter_id → new registration (Form 6)
        # If NRI flag → Form 6A
        # If has voter_id but address changed → transfer
        # Default → new registration
        # Return appropriate guide from eligibility.json
    
    async def get_required_documents(
        self,
        registration_type: str = "new",
        language: str = "en"
    ) -> list[dict]:
        """Get list of required documents for registration.
        
        Args:
            registration_type: "new", "nri", "transfer", "correction".
            language: Response language.
            
        Returns:
            List of document dicts with: name, description, mandatory flag.
        """
        # Load from eligibility.json
        # Filter by registration_type
        # Return language-appropriate content
```

## Step 3: Create src/agents/eligibility.py

```python
"""Eligibility agent for VoteReady.

Determines voter eligibility based on user profile,
provides personalized guidance for different voter categories:
under-18, first-time voter, registered voter, NRI.
"""

import json
from datetime import datetime
from pathlib import Path

from src.services.gemini_service import get_gemini_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VoterCategory:
    """Voter categories based on eligibility check."""
    UNDER_18 = "under_18"
    FIRST_TIME = "first_time_voter"  # 18-21, no voter ID
    REGISTERED = "registered_voter"   # Has voter ID
    NRI = "nri_voter"
    UNREGISTERED = "unregistered"     # 22+, no voter ID


class EligibilityAgent:
    """Checks voter eligibility and categorizes users.
    
    Pure logic agent — does NOT call Gemini for eligibility decisions.
    Uses Gemini only for generating personalized guidance messages.
    """
    
    def __init__(self):
        """Load eligibility rules from JSON."""
        # Load src/data/eligibility.json
        # Load src/data/turnout_stats.json (for motivational data)
    
    def check_eligibility(
        self,
        age: int,
        voter_id: str | None = None,
        is_nri: bool = False
    ) -> dict:
        """Determine voter eligibility and category.
        
        This is PURE LOGIC — no API calls, instant response.
        
        Args:
            age: User's age in years.
            voter_id: Voter ID if available.
            is_nri: Whether user is an NRI.
            
        Returns:
            Dict with:
              - eligible: bool
              - category: VoterCategory string
              - message: Human-readable status
              - next_steps: List of recommended actions
              - years_until_eligible: int (only if under 18)
        """
        # If age < 18:
        #   eligible=False, category=UNDER_18
        #   years_until_eligible = 18 - age
        #   next_steps = ["Pre-register info", "Learn about elections"]
        #
        # If age >= 18 and is_nri:
        #   eligible=True, category=NRI
        #   next_steps = ["Register via Form 6A", "Check NRI voting rules"]
        #
        # If age 18-21 and no voter_id:
        #   eligible=True, category=FIRST_TIME
        #   next_steps = ["Register at nvsp.in", "Get Voter ID", "Find booth"]
        #
        # If voter_id provided:
        #   eligible=True, category=REGISTERED
        #   next_steps = ["Verify registration", "Find booth", "Check dates"]
        #
        # If age > 21 and no voter_id:
        #   eligible=True, category=UNREGISTERED
        #   next_steps = ["Register immediately at nvsp.in", "Get Voter ID"]
    
    async def get_personalized_guidance(
        self,
        category: str,
        user_context: dict,
        language: str = "en"
    ) -> dict:
        """Generate personalized guidance based on voter category.
        
        Uses Gemini to create an encouraging, personalized message
        tailored to the user's specific situation.
        
        Args:
            category: VoterCategory string.
            user_context: Full user profile dict.
            language: Response language.
            
        Returns:
            Dict with: guidance_message, fun_fact, motivation_stat.
        """
        # 1. Get youth turnout stat for user's state
        # 2. Pick a relevant fun fact from motivational.json
        # 3. Call Gemini ONLY for the personalized guidance message:
        #    "Generate a 2-sentence encouraging message for a {category}
        #     named {name} from {state}. They are {age} years old.
        #     Make them feel empowered about participating in democracy."
        # 4. Return combined dict
    
    def get_age_group_stats(self, age: int) -> dict:
        """Get voting statistics for the user's age group.
        
        Args:
            age: User's age.
            
        Returns:
            Dict with: age_group, turnout_percentage, comparison_message.
        """
        # Map age to group: 18-25, 25-40, 40-60, 60+
        # Pull stats from turnout_stats.json
        # Generate comparison: "Your age group votes at X%.
        #   The national average is Y%."
```

## Step 4: Create src/agents/timeline.py

```python
"""Timeline agent for VoteReady.

Provides personalized election schedules based on
user's state and district. Calculates countdowns
and determines which elections are relevant.
"""

import json
from datetime import datetime
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class TimelineAgent:
    """Generates personalized election timelines.
    
    Pure data agent — loads elections from JSON,
    filters by state, sorts by date, adds countdowns.
    No Gemini calls needed.
    """
    
    def __init__(self):
        """Load election schedule data."""
        # Load src/data/elections.json
        # Load src/data/states.json
    
    def get_elections_for_state(
        self,
        state: str,
        language: str = "en"
    ) -> list[dict]:
        """Get all upcoming elections for a user's state.
        
        Args:
            state: User's state name.
            language: Response language.
            
        Returns:
            List of election dicts sorted by tentative date (nearest first).
            Each dict: election_type, title, tentative_year, 
            tentative_month, last_held, total_seats, description,
            days_until (approximate), countdown_message.
        """
        # 1. Filter elections.json by state
        # 2. Add Lok Sabha 2029 (national, applies to all)
        # 3. Calculate approximate days_until for each
        # 4. Sort by tentative date ascending
        # 5. Generate countdown_message:
        #    "Approximately X days away" or "Approximately X months away"
        # 6. Return language-appropriate fields
    
    def get_election_detail(
        self,
        state: str,
        election_type: str,
        language: str = "en"
    ) -> dict | None:
        """Get detailed information about a specific election.
        
        Args:
            state: User's state.
            election_type: Type of election.
            language: Response language.
            
        Returns:
            Detailed election dict or None if not found.
            Includes: full description, historical context,
            seat count, last results summary.
        """
        # Look up specific election from elections.json
        # Return comprehensive detail with language-appropriate text
    
    def get_nearest_election(
        self,
        state: str,
        language: str = "en"
    ) -> dict | None:
        """Get the single nearest upcoming election.
        
        Args:
            state: User's state.
            language: Response language.
            
        Returns:
            The nearest election dict or None.
        """
        # Get all elections for state
        # Return the first one (already sorted by date)
    
    def calculate_countdown(
        self, 
        tentative_year: int, 
        tentative_month: int | None
    ) -> dict:
        """Calculate days/months until an election.
        
        Args:
            tentative_year: Expected election year.
            tentative_month: Expected month (1-12) or None.
            
        Returns:
            Dict with: days_until, months_until, countdown_text,
            is_within_year (bool).
        """
        # If month known: calculate from today to year-month-01
        # If only year: calculate from today to year-01-01
        # Return human-readable countdown
```

## Step 5: Create src/agents/simulator.py

```python
"""Election Day Simulator agent for VoteReady.

Provides an interactive walkthrough of polling day
with scenario-based learning. Users make choices
and receive feedback on correct/incorrect actions.
This is the key differentiator of VoteReady.
"""

import json
from pathlib import Path

from src.services.gemini_service import get_gemini_service
from src.utils.cache import ResponseCache
from src.utils.logger import get_logger

logger = get_logger(__name__)
cache = ResponseCache()


class SimulatorAgent:
    """Interactive election day simulation engine.
    
    Loads scenarios from simulator.json and optionally
    uses Gemini for dynamic feedback generation.
    Tracks user progress through simulation steps.
    """
    
    def __init__(self):
        """Load simulation scenarios from JSON."""
        # Load src/data/simulator.json
    
    def get_all_scenarios(
        self, 
        language: str = "en"
    ) -> list[dict]:
        """Get all simulation scenarios in order.
        
        Args:
            language: Response language.
            
        Returns:
            List of scenario dicts with: id, step_number,
            scenario_text, options (list with text and id),
            tip. Does NOT include is_correct — that would
            reveal answers to frontend.
        """
        # Load all scenarios from simulator.json
        # Strip is_correct and feedback from options
        #   (those are revealed only after user answers)
        # Return language-appropriate fields
    
    def get_scenario(
        self,
        scenario_id: int,
        language: str = "en"
    ) -> dict | None:
        """Get a single scenario by ID.
        
        Args:
            scenario_id: The scenario step number.
            language: Response language.
            
        Returns:
            Scenario dict without answers, or None if not found.
        """
    
    def check_answer(
        self,
        scenario_id: int,
        selected_option_id: int,
        language: str = "en"
    ) -> dict:
        """Check if the user's answer is correct.
        
        Args:
            scenario_id: Which scenario.
            selected_option_id: Which option the user picked.
            language: Response language.
            
        Returns:
            Dict with: is_correct, feedback, tip,
            correct_option_id (revealed after answering).
        """
        # Look up scenario
        # Find selected option
        # Return is_correct, language-appropriate feedback and tip
        # Include the correct_option_id so frontend can highlight it
    
    async def get_dynamic_feedback(
        self,
        scenario_text: str,
        user_choice: str,
        is_correct: bool,
        user_name: str | None = None,
        language: str = "en"
    ) -> str:
        """Generate personalized feedback using Gemini.
        
        Only called if static feedback isn't engaging enough
        or for variety. Check cache first.
        
        Args:
            scenario_text: The scenario description.
            user_choice: What the user selected.
            is_correct: Whether correct.
            user_name: User's name for personalization.
            language: Response language.
            
        Returns:
            Personalized feedback string.
        """
        # Check cache first
        # Call gemini_service.generate_simulator_feedback()
        # Cache result
        # Return feedback
    
    def calculate_score(
        self, 
        answers: list[dict]
    ) -> dict:
        """Calculate final simulation score.
        
        Args:
            answers: List of {scenario_id, selected_option_id, is_correct}.
            
        Returns:
            Dict with: total_scenarios, correct_count,
            score_percentage, rating (Excellent/Good/Keep Learning),
            completion_message.
        """
        # Count correct answers
        # Calculate percentage
        # Assign rating:
        #   100% → "Excellent! You're fully prepared for election day!"
        #   70-99% → "Great job! You know the process well."
        #   50-69% → "Good start! Review the steps you missed."
        #   <50% → "Keep learning! Try the simulator again."
        # Return score dict
```

## Step 6: Git Commit

```
git add src/agents/
git commit -m "feat: implement orchestrator, process guide, eligibility, timeline, and simulator agents"
git push origin main
```

## Verification Checklist
Before moving to the next workflow, verify:
- [ ] orchestrator.py has keyword matching + Gemini fallback classification
- [ ] orchestrator.py routes to all 5 agents correctly
- [ ] orchestrator.py includes follow-up suggestions in responses
- [ ] process_guide.py loads from JSON, uses Gemini ONLY for personalization
- [ ] process_guide.py handles 4 registration types (new, NRI, transfer, correction)
- [ ] eligibility.py check_eligibility is PURE LOGIC — no API calls
- [ ] eligibility.py handles all 5 voter categories correctly
- [ ] timeline.py filters by state and sorts by nearest date
- [ ] timeline.py calculates countdowns accurately
- [ ] simulator.py strips answers before sending scenarios to frontend
- [ ] simulator.py check_answer reveals correct answer after submission
- [ ] simulator.py calculates score with rating tiers
- [ ] ALL agents use services via singleton getters (never instantiate directly)
- [ ] ALL agents load data from JSON files (never hardcode election content)
- [ ] ALL functions have Google-style docstrings and type hints
- [ ] ALL functions are under 30 lines
- [ ] NO circular imports
- [ ] Clean commit pushed to GitHub
