import requests, time
BASE_URL = "http://localhost:5000"

def test_health_endpoint_returns_healthy():
    response = requests.get(BASE_URL + '/api/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'healthy'}

def test_register_user_creates_new_user():
    username = f"testuser_{int(time.time())}"
    data = {"username": username, "password": "test213"}
    response = requests.post(
        BASE_URL + "/api/auth/register",
        json=data
    )
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["user"]["username"] == username

def test_login_returns_jwt_token():
    username = f"testuser_{int(time.time())}"
    password = "test213"
    requests.post(
        BASE_URL + "/api/auth/register",
        json={
        "username": username,
        "password": password
        }
    )
    response1 = requests.post(
        BASE_URL + "/api/auth/login",
        json={"username": username, "password": password}
    )
    assert response1.status_code == 200

    response_data = response1.json()
    assert "access_token" in response_data

def test_create_public_event_requires_auth_and_succeeds_with_token():
    username = f"testuser_{int(time.time())}"
    password = "test213"
    requests.post(
        BASE_URL + "/api/auth/register",
        json={"username": username, "password": password}
    )
    login_response = requests.post(
        BASE_URL + "/api/auth/login",
        json={"username": username, "password": password}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    event_data = {
        "title": "Test Event",
        "date": "2026-11-15T18:00:00"
    }
    event_response = requests.post(
        BASE_URL + "/api/events",
        json=event_data,
        headers=headers
    )
    assert event_response.status_code == 201
    response_data = event_response.json()
    assert response_data["title"] == event_data["title"]
    assert response_data["date"] == event_data["date"]

def test_rsvp_to_public_event():
    username = f"testuser_{int(time.time())}"
    password = "test213"
    requests.post(
        BASE_URL + "/api/auth/register",
        json={"username": username, "password": password}
    )
    login_response = requests.post(
        BASE_URL + "/api/auth/login",
        json={"username": username, "password": password}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    event_data = {
        "title": "RSVP Test Event",
        "date": "2026-11-20T18:00:00",
        "is_public": True
    }
    event_response = requests.post(
        BASE_URL + "/api/events",
        json=event_data,
        headers=headers
    )
    event_data_response = event_response.json()
    event_id = event_data_response["id"]
    rsvp_response = requests.post(
        BASE_URL + f"/api/rsvps/event/{event_id}",
        json={"attending": True},
        headers=headers
    )
    assert rsvp_response.status_code == 201
    rsvp_data = rsvp_response.json()
    assert rsvp_data["event_id"] == event_id
    assert rsvp_data["attending"]

def test_duplicate_registration_returns_400():
    username = f"testuser_{int(time.time())}"
    password = "test213"
    requests.post(
        BASE_URL + "/api/auth/register",
        json={"username": username, "password": password}
    )
    response =     requests.post(
        BASE_URL + "/api/auth/register",
        json={"username": username, "password": password}
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["error"] == "Username already exists"


def test_create_event_without_auth_returns_401():
    event_data = {
        "title": "Unauthorized Event",
        "date": "2026-11-20T18:00:00"
    }
    event_response = requests.post(
        BASE_URL + "/api/events",
        json=event_data
    )
    assert event_response.status_code == 401


def test_rsvp_private_event_without_auth_returns_401():
    username = f"testuser_{int(time.time())}"
    password = "test213"

    requests.post(
        BASE_URL + "/api/auth/register",
        json={"username": username, "password": password}
    )

    login_response = requests.post(
        BASE_URL + "/api/auth/login",
        json={"username": username, "password": password}
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    event_data = {
        "title": "RSVP Test Event",
        "date": "2026-11-20T18:00:00",
        "is_public": False
    }
    event_response = requests.post(
        BASE_URL + "/api/events",
        json=event_data,
        headers=headers
    )

    event_id = event_response.json()["id"]
    rsvp_response = requests.post(
        BASE_URL + f"/api/rsvps/event/{event_id}",
        json={"attending": True}
    )
    assert rsvp_response.status_code == 401
    assert rsvp_response.json()["error"] == "Authentication required for this event"