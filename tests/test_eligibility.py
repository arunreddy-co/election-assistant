"""Tests for the Eligibility agent.

Covers all voter categories: under-18, first-time voter, 
registered voter, NRI, unregistered adult.
Tests boundary conditions and edge cases.
"""

import pytest
from src.agents.eligibility import EligibilityAgent, VoterCategory


@pytest.fixture
def agent():
    """Create an EligibilityAgent instance."""
    return EligibilityAgent()


class TestCheckEligibility:
    """Test the core eligibility check logic."""
    
    def test_under_18_not_eligible(self, agent):
        """Users under 18 should not be eligible."""
        result = agent.check_eligibility(age=16)
        assert result["eligible"] is False
        assert result["category"] == VoterCategory.UNDER_18
        assert "years_until_eligible" in result
        assert result["years_until_eligible"] == 2
    
    def test_exactly_18_eligible(self, agent):
        """Users exactly 18 should be eligible."""
        result = agent.check_eligibility(age=18)
        assert result["eligible"] is True
    
    def test_boundary_17_not_eligible(self, agent):
        """Age 17 — boundary case, should not be eligible."""
        result = agent.check_eligibility(age=17)
        assert result["eligible"] is False
        assert result["years_until_eligible"] == 1
    
    def test_first_time_voter_18_to_21(self, agent):
        """18-21 without voter ID should be categorized as first-time voter."""
        result = agent.check_eligibility(age=19, voter_id=None)
        assert result["eligible"] is True
        assert result["category"] == VoterCategory.FIRST_TIME
    
    def test_registered_voter_with_id(self, agent):
        """User with voter ID should be categorized as registered."""
        result = agent.check_eligibility(age=30, voter_id="ABC1234567")
        assert result["eligible"] is True
        assert result["category"] == VoterCategory.REGISTERED
    
    def test_young_registered_voter(self, agent):
        """18-year-old with voter ID should be registered, not first-time."""
        result = agent.check_eligibility(age=18, voter_id="XYZ9876543")
        assert result["eligible"] is True
        assert result["category"] == VoterCategory.REGISTERED
    
    def test_nri_voter(self, agent):
        """NRI should have NRI category regardless of age/voter ID."""
        result = agent.check_eligibility(age=28, is_nri=True)
        assert result["eligible"] is True
        assert result["category"] == VoterCategory.NRI
    
    def test_unregistered_adult(self, agent):
        """Adult over 21 without voter ID should be unregistered."""
        result = agent.check_eligibility(age=35, voter_id=None)
        assert result["eligible"] is True
        assert result["category"] == VoterCategory.UNREGISTERED
    
    def test_elderly_voter(self, agent):
        """Very old voter should still be eligible."""
        result = agent.check_eligibility(age=95, voter_id="ABC1234567")
        assert result["eligible"] is True
        assert result["category"] == VoterCategory.REGISTERED
    
    def test_next_steps_always_present(self, agent):
        """Every result must include next_steps list."""
        for age in [16, 18, 20, 35, 60]:
            result = agent.check_eligibility(age=age)
            assert "next_steps" in result
            assert isinstance(result["next_steps"], list)
            assert len(result["next_steps"]) > 0
    
    def test_message_always_present(self, agent):
        """Every result must include a human-readable message."""
        result = agent.check_eligibility(age=20)
        assert "message" in result
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0


class TestAgeGroupStats:
    """Test age group statistics lookup."""
    
    def test_youth_group(self, agent):
        """18-25 should return youth turnout stats."""
        result = agent.get_age_group_stats(20)
        assert result["age_group"] == "18-25"
        assert "turnout_percentage" in result
    
    def test_middle_group(self, agent):
        """30 should fall in 25-40 group."""
        result = agent.get_age_group_stats(30)
        assert result["age_group"] == "25-40"
    
    def test_senior_group(self, agent):
        """65 should fall in 60+ group."""
        result = agent.get_age_group_stats(65)
        assert result["age_group"] == "60+"
