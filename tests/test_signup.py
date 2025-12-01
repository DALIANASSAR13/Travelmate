import requests

BASE_URL = "http://127.0.0.1:5000"

def test_signup_success():
    payload = {"username": "testuser", "email": "testuser@example.com", "password": "Test1234"}
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 201
    assert "success" in response.json()["message"].lower()

def test_signup_missing_field():
    payload = {"username": "testuser2"}  # missing email & password
    response = requests.post(f"{BASE_URL}/signup", json=payload)
    assert response.status_code == 400
    assert "error" in response.json()["message"].lower()
