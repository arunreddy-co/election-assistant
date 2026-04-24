"""Tests for the Orchestrator agent.

Covers intent classification via keyword matching
and routing to correct specialist agents.
"""

import pytest
from src.agents.orchestrator import Orchestrator, IntentCategory


@pytest.fixture
def orchestrator():
    """Create an Orchestrator instance."""
    return Orchestrator()


class TestKeywordClassification:
    """Test keyword-based intent classification."""
    
    def test_eligibility_intent(self, orchestrator):
        """Eligibility keywords should route correctly."""
        result = orchestrator._keyword_match("am i eligible to vote")
        assert result == IntentCategory.ELIGIBILITY
    
    def test_process_intent(self, orchestrator):
        """Process keywords should route correctly."""
        result = orchestrator._keyword_match("how to vote in elections")
        assert result == IntentCategory.PROCESS
    
    def test_timeline_intent(self, orchestrator):
        """Timeline keywords should route correctly."""
        result = orchestrator._keyword_match("when is the next election")
        assert result == IntentCategory.TIMELINE
    
    def test_booth_intent(self, orchestrator):
        """Polling booth keywords should route correctly."""
        result = orchestrator._keyword_match("where is my polling booth")
        assert result == IntentCategory.POLLING_BOOTH
    
    def test_simulator_intent(self, orchestrator):
        """Simulator keywords should route correctly."""
        result = orchestrator._keyword_match("i want to practice voting")
        assert result == IntentCategory.SIMULATOR
    
    def test_hindi_eligibility(self, orchestrator):
        """Hindi keywords should also classify correctly."""
        result = orchestrator._keyword_match("क्या मैं मतदान के पात्र हूं")
        assert result == IntentCategory.ELIGIBILITY
    
    def test_no_match_returns_none(self, orchestrator):
        """Unrecognized input should return None for Gemini fallback."""
        result = orchestrator._keyword_match("tell me something interesting")
        assert result is None
    
    def test_registration_intent(self, orchestrator):
        """Registration keywords should route correctly."""
        result = orchestrator._keyword_match("how to register for voter id")
        assert result == IntentCategory.REGISTRATION
