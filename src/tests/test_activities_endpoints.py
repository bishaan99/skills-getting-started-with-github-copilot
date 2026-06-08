"""
Integration tests for FastAPI Activities Management API.

This test suite covers all endpoints of the Mergington High School Activities API
using the AAA (Arrange-Act-Assert) testing pattern.

Test Structure:
- Arrange: Set up preconditions (test data, initial state)
- Act: Execute the API call via TestClient
- Assert: Verify response status, body content, and side effects

Test Coverage:
- GET /activities: Verify activities list endpoint
- POST /activities/{activity_name}/signup: Verify signup functionality
- DELETE /activities/{activity_name}/signup: Verify unregister functionality
- Error cases: Missing activities, duplicate signups, invalid emails
- Edge cases: Multiple signups, state persistence, response structure
"""

import pytest


# ============================================================================
# GET /activities Tests
# ============================================================================

class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities_returns_9_activities(self, client):
        """Test that GET /activities returns all 9 activities."""
        # Arrange: Client is ready
        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Status code is 200 and response contains 9 activities
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9

    def test_get_activities_includes_all_activity_names(self, client, all_activities):
        """Test that response includes all expected activity names."""
        # Arrange: List of expected activity names
        expected_names = all_activities

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Response includes all expected activity names
        activities = response.json()
        actual_names = list(activities.keys())
        assert actual_names == expected_names

    def test_get_activities_returns_correct_structure(self, client):
        """Test that each activity has correct structure with required fields."""
        # Arrange: Expected fields for activity structure
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Each activity has required fields
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert set(activity_data.keys()) == expected_fields

    def test_get_activities_returns_correct_max_participants(self, client):
        """Test that max_participants values are correct."""
        # Arrange: Expected max_participants for Chess Club
        chess_club_max = 12

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Chess Club has correct max_participants
        activities = response.json()
        assert activities["Chess Club"]["max_participants"] == chess_club_max

    def test_get_activities_initial_participants_list(self, client):
        """Test that activities have correct initial participants."""
        # Arrange: Expected initial participants for Chess Club
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Chess Club has correct participants
        activities = response.json()
        assert activities["Chess Club"]["participants"] == expected_participants

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is a list for all activities."""
        # Arrange: Client ready

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: All participants fields are lists
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_single_student_success(self, client, activity_name, test_email):
        """Test successful signup of a single student to an activity."""
        # Arrange: Valid activity name and new student email
        # Act: Make POST request to signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Response status is 200 and contains success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]

    def test_signup_student_added_to_participants(self, client, activity_name, test_email):
        """Test that student is added to activity's participants list."""
        # Arrange: Valid activity and email, get initial state
        initial_activities = client.get("/activities").json()
        initial_participants = initial_activities[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act: Make signup request
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Student is in participants and count increased
        updated_activities = client.get("/activities").json()
        updated_participants = updated_activities[activity_name]["participants"]
        assert test_email in updated_participants
        assert len(updated_participants) == initial_count + 1

    def test_signup_multiple_students_same_activity(self, client, activity_name):
        """Test signup of multiple different students to same activity."""
        # Arrange: Multiple test emails
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act: Signup both students
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert: Both signups successful and both in participants
        assert response1.status_code == 200
        assert response2.status_code == 200
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants

    def test_signup_duplicate_email_returns_400(self, client, activity_name, existing_email):
        """Test that duplicate signup returns 400 error."""
        # Arrange: Email already in Chess Club participants
        # Act: Attempt to signup with existing email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert: Response status is 400 (Bad Request)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower() or "signed up" in data["detail"].lower()

    def test_signup_invalid_activity_returns_404(self, client, invalid_activity_name, test_email):
        """Test that signup to non-existent activity returns 404."""
        # Arrange: Invalid activity name
        # Act: Make signup request to non-existent activity
        response = client.post(
            f"/activities/{invalid_activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Response status is 404 (Not Found)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_response_structure(self, client, activity_name, test_email):
        """Test that signup response has correct JSON structure."""
        # Arrange: Valid activity and email
        # Act: Make signup request
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Response JSON has expected structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


# ============================================================================
# DELETE /activities/{activity_name}/signup Tests
# ============================================================================

class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_student_success(self, client, activity_name, test_email):
        """Test successful unregistration of a student from activity."""
        # Arrange: Student signed up to activity
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Act: Make DELETE request to unregister
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Response status is 200 and contains success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]

    def test_unregister_student_removed_from_participants(self, client, activity_name, test_email):
        """Test that student is removed from participants list after unregister."""
        # Arrange: Student signed up, verify in participants
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        activities_after_signup = client.get("/activities").json()
        assert test_email in activities_after_signup[activity_name]["participants"]

        # Act: Make DELETE request to unregister
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Student no longer in participants
        activities_after_unregister = client.get("/activities").json()
        assert test_email not in activities_after_unregister[activity_name]["participants"]

    def test_unregister_maintains_other_participants(self, client, activity_name):
        """Test that unregistering one student doesn't affect others."""
        # Arrange: Add two new students
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})

        # Act: Unregister first student
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )

        # Assert: Second student still in participants, first student removed
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        assert email1 not in participants
        assert email2 in participants

    def test_unregister_non_participant_returns_400(self, client, activity_name, test_email):
        """Test that unregistering non-participant returns 400 error."""
        # Arrange: test_email never signed up
        # Act: Attempt to unregister non-participant
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Response status is 400
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()

    def test_unregister_invalid_activity_returns_404(self, client, invalid_activity_name, test_email):
        """Test that unregister from non-existent activity returns 404."""
        # Arrange: Invalid activity name
        # Act: Make DELETE request to non-existent activity
        response = client.delete(
            f"/activities/{invalid_activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Response status is 404
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_response_structure(self, client, activity_name, test_email):
        """Test that unregister response has correct JSON structure."""
        # Arrange: Student signed up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Act: Make DELETE request
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Response has expected structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)


# ============================================================================
# Edge Case and Integration Tests
# ============================================================================

class TestActivitySignupEdgeCases:
    """Tests for edge cases and integration scenarios."""

    def test_signup_unregister_signup_same_student(self, client, activity_name, test_email):
        """Test that student can signup, unregister, and signup again."""
        # Arrange: Valid activity and email
        # Act: Signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert response1.status_code == 200

        # Act: Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        assert response2.status_code == 200

        # Act: Signup again
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert: Final signup is successful
        assert response3.status_code == 200
        activities = client.get("/activities").json()
        assert test_email in activities[activity_name]["participants"]

    def test_signup_to_multiple_activities(self, client):
        """Test that student can signup to multiple different activities."""
        # Arrange: Two different activities and one email
        email = "multisport@mergington.edu"
        activity1 = "Soccer Team"
        activity2 = "Swimming Club"

        # Act: Signup to first activity
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )

        # Act: Signup to second activity
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert: Both signups successful and email in both activities
        assert response1.status_code == 200
        assert response2.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

    def test_initial_participants_unchanged(self, client):
        """Test that initial participants remain unchanged after operations."""
        # Arrange: Get initial state
        initial = client.get("/activities").json()
        chess_initial = initial["Chess Club"]["participants"].copy()

        # Act: Signup and unregister a student
        test_email = "temporary@mergington.edu"
        client.post("/activities/Chess Club/signup", params={"email": test_email})
        client.delete("/activities/Chess Club/signup", params={"email": test_email})

        # Assert: Original participants are intact (plus test_email was removed)
        final = client.get("/activities").json()
        chess_final = final["Chess Club"]["participants"]
        assert chess_final == chess_initial

    def test_email_case_sensitivity(self, client, activity_name):
        """Test email handling with different cases."""
        # Arrange: Email in different cases
        email_lower = "teststudent@mergington.edu"
        email_upper = "TESTSTUDENT@MERGINGTON.EDU"

        # Act: Signup with lowercase
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_lower}
        )

        # Assert: Signup successful
        assert response1.status_code == 200

        # Act: Attempt signup with uppercase (different string)
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_upper}
        )

        # Assert: Uppercase is treated as different email and signup succeeds
        # (Tests current behavior; app doesn't normalize case)
        assert response2.status_code == 200
        activities = client.get("/activities").json()
        participants = activities[activity_name]["participants"]
        assert email_lower in participants
        assert email_upper in participants

    def test_activity_name_case_sensitivity(self, client, test_email):
        """Test activity name handling with different cases."""
        # Arrange: Activity name in different cases
        activity_correct = "Chess Club"
        activity_wrong_case = "chess club"

        # Act: Signup with correct case
        response1 = client.post(
            f"/activities/{activity_correct}/signup",
            params={"email": test_email}
        )

        # Assert: Correct case works
        assert response1.status_code == 200

        # Act: Attempt signup with different email to wrong case activity
        test_email2 = "another@mergington.edu"
        response2 = client.post(
            f"/activities/{activity_wrong_case}/signup",
            params={"email": test_email2}
        )

        # Assert: Wrong case returns 404 (case-sensitive)
        assert response2.status_code == 404

    def test_special_characters_in_email(self, client, activity_name):
        """Test that emails with special characters are accepted."""
        # Arrange: Email with special characters (but valid format)
        special_email = "student+test@mergington.edu"

        # Act: Attempt signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": special_email}
        )

        # Assert: Signup accepted
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert special_email in activities[activity_name]["participants"]

    def test_very_long_email(self, client, activity_name):
        """Test that very long but valid emails are handled."""
        # Arrange: Long but valid email
        long_email = "verylongemailaddresswithnumberandspecialchars1234567890@mergington.edu"

        # Act: Attempt signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": long_email}
        )

        # Assert: Signup accepted
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert long_email in activities[activity_name]["participants"]
