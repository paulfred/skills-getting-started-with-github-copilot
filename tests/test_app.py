"""Tests for the FastAPI activities application."""
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_success(self, client):
        """Test retrieving all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_returns_correct_count(self, client):
        """Test that we get all 9 activities."""
        response = client.get("/activities")
        data = response.json()
        assert len(data) == 9


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup is rejected."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_invalid_activity(self, client):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Non Existent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_increments_participant_count(self, client):
        """Test that participant count increases after signup."""
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        client.post(
            "/activities/Programming Class/signup?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        assert new_count == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client):
        """Test successful unregister from an activity."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_decrements_participant_count(self, client):
        """Test that participant count decreases after unregister."""
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1
    
    def test_unregister_not_signed_up(self, client):
        """Test unregister for student not signed up."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=noone@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_invalid_activity(self, client):
        """Test unregister from non-existent activity."""
        response = client.delete(
            "/activities/Non Existent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestSignupAndUnregister:
    """Integration tests for signup and unregister."""
    
    def test_signup_then_unregister(self, client):
        """Test signing up then unregistering."""
        email = "integration@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
