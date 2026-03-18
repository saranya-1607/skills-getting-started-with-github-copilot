"""
Pytest configuration and fixtures for FastAPI tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provides a FastAPI TestClient for making requests"""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Provides a fresh copy of sample activities for each test"""
    return {
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
        "Basketball": {
            "description": "Team sport focusing on coordination and teamwork",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Swimming": {
            "description": "Learn swimming techniques and water safety",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Painting": {
            "description": "Explore creativity through painting and art",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Dance": {
            "description": "Learn different dance styles and perform",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Improve public speaking and critical thinking",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": []
        }
    }


@pytest.fixture
def isolated_activities(monkeypatch, sample_activities):
    """
    Provides test isolation by replacing the app's activities dictionary
    with a fresh copy for each test
    """
    monkeypatch.setattr("src.app.activities", sample_activities)
    return sample_activities
