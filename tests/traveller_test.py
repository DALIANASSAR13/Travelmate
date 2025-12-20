import pytest
from TRAVEL import app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.get_db_connection')
def test_travellers_with_flight(mock_db, client):
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.return_value = {'flight_id': 1, 'airline': 'AirX', 'from_airport': 'AAA', 'to_airport': 'BBB', 'price': 500}
    mock_conn.cursor.return_value = mock_cur
    mock_db.return_value = mock_conn

    with client.session_transaction() as session:
        session['user_id'] = 1
        session['username'] = 'John Doe'

    response = client.get('/travellers/1')
    assert response.status_code == 200