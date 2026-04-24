"""Tests for election data file integrity.

Verifies all JSON data files are properly structured,
complete, bilingual, and internally consistent.
Critical for ensuring the app works for all states.
"""

import json
import pytest
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "src" / "data"


class TestStatesData:
    """Verify states.json completeness."""
    
    def test_file_exists(self):
        """states.json must exist."""
        assert (DATA_DIR / "states.json").exists()
    
    def test_all_states_present(self):
        """Must contain all 28 states and 8 UTs."""
        with open(DATA_DIR / "states.json", "r", encoding="utf-8") as f:
            states = json.load(f)
        # At minimum 36 entries (28 states + 8 UTs)
        assert len(states) >= 36
    
    def test_states_have_required_fields(self):
        """Each state must have name, name_hi, code, districts."""
        with open(DATA_DIR / "states.json", "r", encoding="utf-8") as f:
            states = json.load(f)
        for state in states:
            assert "name" in state, f"Missing name in state entry"
            assert "name_hi" in state, f"Missing name_hi for {state.get('name')}"
            assert "code" in state, f"Missing code for {state.get('name')}"
            assert "districts" in state, f"Missing districts for {state.get('name')}"
            assert len(state["districts"]) > 0, f"No districts for {state.get('name')}"


class TestElectionsData:
    """Verify elections.json completeness."""
    
    def test_file_exists(self):
        """elections.json must exist."""
        assert (DATA_DIR / "elections.json").exists()
    
    def test_elections_have_required_fields(self):
        """Each election must have type, title, tentative_year."""
        with open(DATA_DIR / "elections.json", "r", encoding="utf-8") as f:
            elections = json.load(f)
        for election in elections:
            assert "election_type" in election
            assert "title" in election
            assert "title_hi" in election
            assert "tentative_year" in election
            assert election["tentative_year"] >= 2026
    
    def test_no_null_dates(self):
        """tentative_year must never be null."""
        with open(DATA_DIR / "elections.json", "r", encoding="utf-8") as f:
            elections = json.load(f)
        for election in elections:
            assert election["tentative_year"] is not None


class TestProcessStepsData:
    """Verify process_steps.json completeness."""
    
    def test_file_exists(self):
        """process_steps.json must exist."""
        assert (DATA_DIR / "process_steps.json").exists()
    
    def test_bilingual_content(self):
        """All steps must have both English and Hindi text."""
        with open(DATA_DIR / "process_steps.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            for step in entry.get("steps", []):
                assert "title" in step, f"Missing title in {entry.get('election_type')}"
                assert "title_hi" in step, f"Missing title_hi in {entry.get('election_type')}"
                assert "description" in step
                assert "description_hi" in step


class TestSimulatorData:
    """Verify simulator.json completeness."""
    
    def test_file_exists(self):
        """simulator.json must exist."""
        assert (DATA_DIR / "simulator.json").exists()
    
    def test_minimum_scenarios(self):
        """Must have at least 6 scenarios."""
        with open(DATA_DIR / "simulator.json", "r", encoding="utf-8") as f:
            scenarios = json.load(f)
        assert len(scenarios) >= 6
    
    def test_each_scenario_has_correct_answer(self):
        """Each scenario must have exactly one correct option."""
        with open(DATA_DIR / "simulator.json", "r", encoding="utf-8") as f:
            scenarios = json.load(f)
        for scenario in scenarios:
            correct_count = sum(
                1 for opt in scenario["options"] if opt.get("is_correct")
            )
            assert correct_count == 1, f"Scenario {scenario.get('step_number')} has {correct_count} correct answers"


class TestFAQData:
    """Verify faq.json completeness."""
    
    def test_file_exists(self):
        """faq.json must exist."""
        assert (DATA_DIR / "faq.json").exists()
    
    def test_minimum_entries(self):
        """Must have at least 20 FAQ entries."""
        with open(DATA_DIR / "faq.json", "r", encoding="utf-8") as f:
            faq = json.load(f)
        assert len(faq) >= 20
    
    def test_bilingual_entries(self):
        """Each FAQ must have question and answer in both languages."""
        with open(DATA_DIR / "faq.json", "r", encoding="utf-8") as f:
            faq = json.load(f)
        for entry in faq:
            assert "question" in entry
            assert "question_hi" in entry
            assert "answer" in entry
            assert "answer_hi" in entry
