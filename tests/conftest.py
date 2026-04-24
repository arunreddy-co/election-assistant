"""Shared test fixtures for VoteReady test suite.

Provides mock user profiles, sample data, and test client
configuration used across all test modules.
"""

import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.main import app


@pytest.fixture
def client():
    """Create a FastAPI test client.
    
    Returns:
        TestClient instance with all middleware active.
    """
    from src.main import app
    from src.agents.orchestrator import Orchestrator
    from src.agents.process_guide import ProcessGuideAgent
    from src.agents.eligibility import EligibilityAgent
    from src.agents.timeline import TimelineAgent
    from src.agents.simulator import SimulatorAgent
    
    app.state.orchestrator = Orchestrator()
    app.state.process_guide = ProcessGuideAgent()
    app.state.eligibility = EligibilityAgent()
    app.state.timeline = TimelineAgent()
    app.state.simulator = SimulatorAgent()
    
    return TestClient(app)


@pytest.fixture
def mock_gemini_service():
    """Mock Gemini service to avoid real API calls in tests.
    
    Returns:
        AsyncMock that returns predictable responses.
    """
    with patch("src.services.gemini_service.get_gemini_service") as mock:
        service = AsyncMock()
        service.generate_response.return_value = "This is a test response about elections."
        service.generate_simulator_feedback.return_value = "Great choice! That's correct."
        service.generate_impact_statement.return_value = "Your vote matters in this constituency."
        mock.return_value = service
        yield service


@pytest.fixture
def mock_firestore_service():
    """Mock Firestore service to avoid real database calls.
    
    Returns:
        AsyncMock with predictable CRUD operations.
    """
    with patch("src.services.firestore_service.get_firestore_service") as mock:
        service = AsyncMock()
        service.create_user.return_value = "test-user-123"
        service.get_user.return_value = {
            "name": "Test User",
            "age": 20,
            "state": "Telangana",
            "district": "Hyderabad",
            "voter_id": None,
            "language": "en",
            "category": "first_time_voter",
        }
        service.get_checklist.return_value = {
            "items": [
                {"id": "check_registration", "title": "Check electoral roll", "completed": False},
                {"id": "get_voter_id", "title": "Get Voter ID", "completed": False},
                {"id": "find_booth", "title": "Find polling booth", "completed": False},
                {"id": "prepare_documents", "title": "Prepare documents", "completed": True},
                {"id": "know_candidates", "title": "Know candidates", "completed": False},
                {"id": "polling_day_ready", "title": "Polling day procedures", "completed": False},
            ]
        }
        service.update_checklist_item.return_value = True
        mock.return_value = service
        yield service


@pytest.fixture
def mock_maps_service():
    """Mock Maps service to avoid real API calls.
    
    Returns:
        AsyncMock with sample polling booth data.
    """
    with patch("src.services.maps_service.get_maps_service") as mock:
        service = AsyncMock()
        service.find_polling_booths.return_value = [
            {
                "name": "Government School Polling Booth",
                "address": "Main Road, Hyderabad, Telangana",
                "latitude": 17.385,
                "longitude": 78.4867,
                "place_id": "ChIJtest123",
            }
        ]
        mock.return_value = service
        yield service


# ---- Sample Data Fixtures ----

@pytest.fixture
def valid_onboard_data():
    """Valid onboarding request data."""
    return {
        "name": "Arun Reddy",
        "age": 20,
        "state": "Telangana",
        "district": "Hyderabad",
        "voter_id": None,
        "language": "en",
    }


@pytest.fixture
def under_18_onboard_data():
    """Onboarding data for an under-18 user."""
    return {
        "name": "Priya Sharma",
        "age": 16,
        "state": "Maharashtra",
        "district": "Mumbai",
        "voter_id": None,
        "language": "en",
    }


@pytest.fixture
def registered_voter_data():
    """Onboarding data for a registered voter."""
    return {
        "name": "Rajesh Kumar",
        "age": 35,
        "state": "Uttar Pradesh",
        "district": "Lucknow",
        "voter_id": "ABC1234567",
        "language": "en",
    }


@pytest.fixture
def nri_voter_data():
    """Onboarding data for an NRI voter."""
    return {
        "name": "Sneha Patel",
        "age": 28,
        "state": "Gujarat",
        "district": "Ahmedabad",
        "voter_id": None,
        "language": "en",
    }


@pytest.fixture
def malicious_input_data():
    """Onboarding data with malicious inputs for security testing."""
    return {
        "name": "<script>alert('xss')</script>",
        "age": 25,
        "state": "Telangana",
        "district": "Hyderabad",
        "language": "en",
    }


@pytest.fixture
def valid_chat_data():
    """Valid chat request data."""
    return {
        "message": "Am I eligible to vote?",
        "user_id": "test-user-123",
        "language": "en",
        "context_screen": "dashboard",
    }


@pytest.fixture
def sample_elections():
    """Sample election data for testing."""
    data_path = Path(__file__).parent.parent / "src" / "data" / "elections.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_states():
    """Sample states data for testing."""
    data_path = Path(__file__).parent.parent / "src" / "data" / "states.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)
