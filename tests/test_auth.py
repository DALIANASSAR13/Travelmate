import pytest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
from TRAVEL import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch("Database.get_db_connection")
def test_login_success(mock_get_db, client):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    pw_hash = generate_password_hash("secret123")
    mock_cursor.fetchone.return_value = [1, pw_hash, "Yomna Medhat"]
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    response = client.post("/login", data={
        "email": "yomna@example.com",
        "password": "secret123"
    }, follow_redirects=True)

    assert response.status_code == 200