import json
from TRAVEL import app  # Make sure your Flask app is named 'app'

def test_signup_success():
    client = app.test_client()

    response = client.post(
        "/signup",
        data=json.dumps({
            "name": "Test User",
            "email": "test@example.com",
            "password": "123456"
        }),
        content_type="application/json"
    )

    assert response.status_code == 201


def test_signup_missing_email():
    client = app.test_client()

    response = client.post(
        "/signup",
        data=json.dumps({
            "name": "Test User",
            "password": "123456"
        }),
        content_type="application/json"
    )

    assert response.status_code == 400
