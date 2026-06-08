"""
Pytest configuration and fixtures for FastAPI activities API tests.

This module provides fixtures for testing the FastAPI activities management system,
including TestClient setup and test data fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app
import copy


# Original activities state (for resetting between tests)
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Practice teamwork and compete in interschool soccer matches",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["alex@mergington.edu", "lisa@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Improve swimming skills and train for swim meets",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["natalie@mergington.edu", "ryan@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media art projects",
        "schedule": "Wednesdays, 3:00 PM - 4:30 PM",
        "max_participants": 15,
        "participants": ["maya@mergington.edu", "diego@mergington.edu"]
    },
    "Drama Club": {
        "description": "Create and perform short plays and improv scenes",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["oliver@mergington.edu", "zoe@mergington.edu"]
    },
    "Debate Team": {
        "description": "Research current issues and debate with other teams",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["isabella@mergington.edu", "mason@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and learn about scientific discoveries",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "grace@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset activities to original state before each test."""
    from src import app as app_module
    # Reset the activities dictionary to original state
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    # Cleanup after test (optional, but good practice)
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    """Provide a TestClient instance for making requests to the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_email():
    """Provide a test email address not in any initial activities."""
    return "newstudent@mergington.edu"


@pytest.fixture
def existing_email():
    """Provide an email that exists in initial activities."""
    return "michael@mergington.edu"


@pytest.fixture
def activity_name():
    """Provide a valid activity name for testing."""
    return "Chess Club"


@pytest.fixture
def invalid_activity_name():
    """Provide an invalid activity name that doesn't exist."""
    return "Nonexistent Activity"


@pytest.fixture
def all_activities():
    """Provide list of all valid activity names."""
    return list(ORIGINAL_ACTIVITIES.keys())
