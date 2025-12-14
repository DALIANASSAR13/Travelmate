import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from TRAVEL import app


class TestAuth(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "testkey"
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_signup_missing_fields(self):
        response = self.client.post("/signup", data={
            "first_name": "",
            "email": "",
            "password": ""
        })
        self.assertIn(b"All fields are required", response.data)

    @patch("TRAVEL.get_db_connection")
    def test_signup_email_exists(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn

        response = self.client.post("/signup", data={
            "first_name": "Yomna",
            "last_name": "Test",
            "email": "test@test.com",
            "password": "123456"
        })

        self.assertIn(b"Email already registered", response.data)

    @patch("TRAVEL.get_db_connection")
    def test_login_email_not_found(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_db.return_value = mock_conn

        response = self.client.post("/login", data={
            "email": "no@user.com",
            "password": "123"
        })

        self.assertIn(b"Email not found", response.data)


if __name__ == "__main__":
    unittest.main()