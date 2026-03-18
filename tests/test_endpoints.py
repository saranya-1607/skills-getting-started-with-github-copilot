"""
Comprehensive tests for Mergington High School API endpoints
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, isolated_activities):
        """Should return all activities with correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_get_activities_returns_correct_activity_details(self, client, isolated_activities):
        """Should return activity details including participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)
        assert "michael@mergington.edu" in chess_club["participants"]
        
    def test_get_activities_includes_empty_activities(self, client, isolated_activities):
        """Should include activities with no participants"""
        response = client.get("/activities")
        data = response.json()
        
        basketball = data["Basketball"]
        assert basketball["participants"] == []
        assert basketball["max_participants"] == 15


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, isolated_activities):
        """Should successfully sign up a new student"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "alex@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" in activities_data["Basketball"]["participants"]

    def test_signup_adds_to_existing_participants(self, client, isolated_activities):
        """Should append to existing participants list"""
        initial_count = len(isolated_activities["Chess Club"]["participants"])
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Chess Club"]["participants"]) == initial_count + 1
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_duplicate_email_fails(self, client, isolated_activities):
        """Should reject duplicate registrations"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, isolated_activities):
        """Should reject signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_students_same_activity(self, client, isolated_activities):
        """Should allow multiple different students to sign up"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Swimming/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for email in emails:
            assert email in activities_data["Swimming"]["participants"]
        assert len(activities_data["Swimming"]["participants"]) == 3


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, isolated_activities):
        """Should successfully unregister a participant"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_removes_only_target_participant(self, client, isolated_activities):
        """Should remove only the specified participant"""
        initial_participants = isolated_activities["Chess Club"]["participants"].copy()
        
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        remaining = activities_data["Chess Club"]["participants"]
        
        assert "michael@mergington.edu" not in remaining
        assert "daniel@mergington.edu" in remaining
        assert len(remaining) == len(initial_participants) - 1

    def test_unregister_nonexistent_activity_fails(self, client, isolated_activities):
        """Should reject unregister for non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_participant_not_registered_fails(self, client, isolated_activities):
        """Should reject unregister for participant not in activity"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_from_empty_activity_fails(self, client, isolated_activities):
        """Should reject unregister from activity with no participants"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        """Should redirect to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_location_correct(self, client):
        """Should redirect to correct index path"""
        response = client.get("/", follow_redirects=True)
        # When followed, should reach the static HTML file
        assert response.status_code == 200


class TestIntegrationFlows:
    """Integration tests for complete user flows"""

    def test_signup_and_unregister_flow(self, client, isolated_activities):
        """Should handle a complete signup and unregister flow"""
        email = "integration@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Painting/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response1 = client.get("/activities")
        assert email in activities_response1.json()["Painting"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Painting/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response2 = client.get("/activities")
        assert email not in activities_response2.json()["Painting"]["participants"]

    def test_signup_unregister_signup_again_flow(self, client, isolated_activities):
        """Should allow re-registration after unregister"""
        email = "flexible@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Dance/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            "/activities/Dance/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            "/activities/Dance/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify final state
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Dance"]["participants"]

    def test_multiple_concurrent_signups(self, client, isolated_activities):
        """Should handle multiple students signing up for same activity"""
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu",
            "student4@mergington.edu",
        ]
        
        for email in students:
            response = client.post(
                "/activities/Science Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()["Science Club"]["participants"]
        for email in students:
            assert email in participants
        assert len(participants) == len(students)
