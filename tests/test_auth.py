import unittest
from unittest.mock import patch, MagicMock
from TRAVEL import app

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    # ================== GET REQUESTS ================== #
    @patch("TRAVEL.render_template")
    @patch("TRAVEL.get_db_connection")
    @patch("pandas.read_excel")
    def test_signup_get(self, mock_read_excel, mock_db, mock_render):
        mock_read_excel.return_value = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_render.return_value = "signup page"

        response = self.client.get("/signup")
        self.assertEqual(response.data, b"signup page")

    @patch("TRAVEL.render_template")
    @patch("TRAVEL.get_db_connection")
    @patch("pandas.read_excel")
    def test_login_get(self, mock_read_excel, mock_db, mock_render):
        mock_read_excel.return_value = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_render.return_value = "login page"

        response = self.client.get("/login")
        self.assertEqual(response.data, b"login page")

    # ================== POST REQUESTS ================== #
    @patch("TRAVEL.get_db_connection")
    @patch("pandas.read_excel")
    def test_signup_post_success(self, mock_read_excel, mock_db):
        mock_read_excel.return_value = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchone.side_effect = [None, [1]]
        mock_db.return_value.cursor.return_value = mock_cursor

        with self.client.session_transaction() as session:
            response = self.client.post("/signup", data={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "password": "password"
            }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @patch("TRAVEL.get_db_connection")
    @patch("pandas.read_excel")
    def test_login_post_success(self, mock_read_excel, mock_db):
        mock_read_excel.return_value = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [1, "hashed_pw", "Test User"]
        mock_db.return_value.cursor.return_value = mock_cursor

        with patch("TRAVEL.check_password_hash") as mock_check:
            mock_check.return_value = True

            response = self.client.post("/login", data={
                "email": "test@example.com",
                "password": "password"
            }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()