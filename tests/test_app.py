from copy import deepcopy

import src.app as app_module


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant_and_returns_message(client):
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    starting_participants = deepcopy(app_module.activities[activity_name]["participants"])

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert app_module.activities[activity_name]["participants"] == starting_participants + [email]


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}


def test_unregister_removes_participant_and_returns_message(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_rejects_non_member(client):
    activity_name = "Chess Club"
    email = "not.signed.up@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}


def test_unknown_activity_returns_404_for_signup_and_unregister(client):
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    unregister_response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    assert signup_response.status_code == 404
    assert signup_response.json() == {"detail": "Activity not found"}
    assert unregister_response.status_code == 404
    assert unregister_response.json() == {"detail": "Activity not found"}