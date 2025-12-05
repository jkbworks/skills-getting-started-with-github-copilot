"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before and after each test"""
    original_activities = {
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
        "Basketball Team": {
            "description": "Competitive basketball training and matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and friendly tournaments",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "nina@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["sarah@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Orchestra and band performance group",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "maya@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["rachel@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore physics, chemistry, and biology through experiments",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["tom@mergington.edu", "jessica@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities(self, client, reset_activities):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert data["Chess Club"]["max_participants"] == 12
        assert len(data["Chess Club"]["participants"]) == 2
    
    def test_get_activities_structure(self, client, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignUp:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signup fails"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_participants(self, client, reset_activities):
        """Test signing up multiple different participants"""
        response1 = client.post(
            "/activities/Basketball%20Team/signup?email=student1@mergington.edu"
        )
        response2 = client.post(
            "/activities/Basketball%20Team/signup?email=student2@mergington.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert "student1@mergington.edu" in activities["Basketball Team"]["participants"]
        assert "student2@mergington.edu" in activities["Basketball Team"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant(self, client, reset_activities):
        """Test unregistering a participant"""
        # First verify participant exists
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregistering a participant not in activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that participant can re-signup after unregistering"""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        assert email not in activities["Chess Club"]["participants"]
        
        # Sign up again
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        assert email in activities["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests for multiple operations"""
    
    def test_full_workflow(self, client, reset_activities):
        """Test complete workflow: signup, verify, unregister, verify"""
        email = "integration@mergington.edu"
        activity = "Tennis%20Club"
        
        # Check initial state
        response = client.get("/activities")
        initial_count = len(response.json()["Tennis Club"]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert len(response.json()["Tennis Club"]["participants"]) == initial_count + 1
        assert email in response.json()["Tennis Club"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert len(response.json()["Tennis Club"]["participants"]) == initial_count
        assert email not in response.json()["Tennis Club"]["participants"]
