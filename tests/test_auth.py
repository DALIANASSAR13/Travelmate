import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from TRAVEL import app

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    # ================== GET REQUESTS ================== #
    @patch("TRAVEL.render_template")
    def test_signup_get(self, mock_render):
        mock_render.return_value = b"signup page"
        response = self.client.get("/signup")
        self.assertEqual(response.data, b"signup page")

    @patch("TRAVEL.render_template")
    def test_login_get(self, mock_render):
        mock_render.return_value = b"login page"
        response = self.client.get("/login")
        self.assertEqual(response.data, b"login page")

    # ================== POST REQUESTS ================== #
    @patch("TRAVEL.render_template")
    @patch("TRAVEL.get_db_connection")
    def test_signup_post_success(self, mock_db, mock_render):
        mock_render.return_value = b"signup success"

        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [None, (1,)]
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.client.post("/signup", data={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "password"
        }, follow_redirects=True)

        self.assertEqual(response.data, b"signup success")

    @patch("TRAVEL.render_template")
    @patch("TRAVEL.get_db_connection")
    @patch("TRAVEL.check_password_hash")
    def test_login_post_success(self, mock_check, mock_db, mock_render):
        mock_render.return_value = b"login success"
        mock_check.return_value = True

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "hashed_pw", "Test User")
        mock_db.return_value.cursor.return_value = mock_cursor

        response = self.client.post("/login", data={
            "email": "test@example.com",
            "password": "password"
        }, follow_redirects=True)

        self.assertEqual(response.data, b"login success")

if __name__ == "__main__":
    unittest.main()