"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

# Create a test client
client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_activities(self):
        """Test that we can retrieve all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_have_required_fields(self):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""
    
    def setup_method(self):
        """Reset activities before each test"""
        # Clear participants from all activities except initial ones
        activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
        activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
        activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
        activities["Basketball Team"]["participants"] = ["alex@mergington.edu"]
        activities["Soccer Club"]["participants"] = ["jordan@mergington.edu", "taylor@mergington.edu"]
        activities["Drama Club"]["participants"] = ["grace@mergington.edu"]
        activities["Art Studio"]["participants"] = ["maya@mergington.edu", "lucas@mergington.edu"]
        activities["Debate Team"]["participants"] = ["isabella@mergington.edu"]
        activities["Science Club"]["participants"] = ["noah@mergington.edu", "ava@mergington.edu"]
    
    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_student(self):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_adds_to_participants(self):
        """Test that signup actually adds student to participants list"""
        email = "testuser@mergington.edu"
        initial_count = len(activities["Programming Class"]["participants"])
        
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert len(activities["Programming Class"]["participants"]) == initial_count + 1


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""
    
    def setup_method(self):
        """Reset activities before each test"""
        activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
        activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
        activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
        activities["Basketball Team"]["participants"] = ["alex@mergington.edu"]
        activities["Soccer Club"]["participants"] = ["jordan@mergington.edu", "taylor@mergington.edu"]
        activities["Drama Club"]["participants"] = ["grace@mergington.edu"]
        activities["Art Studio"]["participants"] = ["maya@mergington.edu", "lucas@mergington.edu"]
        activities["Debate Team"]["participants"] = ["isabella@mergington.edu"]
        activities["Science Club"]["participants"] = ["noah@mergington.edu", "ava@mergington.edu"]
    
    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        initial_count = len(activities["Chess Club"]["participants"])
        
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1
    
    def test_unregister_from_nonexistent_activity(self):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_signed_up(self):
        """Test unregister for student not in activity returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_removes_from_participants(self):
        """Test that unregister actually removes student from participants"""
        email = "daniel@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self):
        """Test that root endpoint redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
