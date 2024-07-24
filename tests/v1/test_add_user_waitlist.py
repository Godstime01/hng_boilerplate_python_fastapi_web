
# Dependencies:
# pip install pytest-mock
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError


from fastapi.testclient import TestClient
from main import app
from api.utils.dependencies import get_current_admin

def mock_deps():
    return MagicMock(is_admin=True)

@pytest.fixture
def client():
    client = TestClient(app)
    yield client

class TestCodeUnderTest:
    @classmethod 
    def setup_class(cls):
        app.dependency_overrides[get_current_admin] = mock_deps
        
    @classmethod
    def teardown_class(cls):
        app.dependency_overrides = {}

    # Successfully adding a user to the waitlist with valid email and full name
    
    @patch('api.v1.routes.waitlist.db')
    def test_add_user_to_waitlist_success(self, mock_db, client):
        app.dependency_overrides[get_current_admin] = mock_deps
    
        response = client.post("/api/v1/waitlist/admin", json={"email": "tes@example.com", "full_name": "Test User"})
    
        assert response.status_code == 201
        assert response.json()["message"] == "User added to waitlist successfully"

    # # Handling empty full_name field and raising appropriate exception
    def test_add_user_to_waitlist_empty_full_name(self, mocker, client):
        app.dependency_overrides[get_current_admin] = mock_deps

        response = client.post("/api/v1/waitlist/admin", json={"email": "test@example.com", "full_name": ""})
    
        assert response.status_code == 400
        assert response.json()["message"] == "full_name field cannot be blank"

    # # Handling invalid email format and raising appropriate exception
    def test_add_user_to_waitlist_invalid_email(self, client):    
        response = client.post("/api/v1/waitlist/admin", json={"email": "invalid-email", "full_name": "Test User"})
    
        assert response.status_code == 422

    # # Handling duplicate email entries and raising IntegrityError
    @patch('api.v1.routes.waitlist.db')
    def test_add_user_to_waitlist_duplicate_email(self, mock_db, client):

        client = TestClient(app)
        mock_db.return_value=MagicMock()
    
        # Simulate IntegrityError when adding duplicate email
        mock_db.add.side_effect = IntegrityError("Duplicate entry", {}, None)

        response = client.post("/api/v1/waitlist/admin", json={"email": "duplicate@example.com", "full_name": "Test User"})
    
        assert response.status_code == 400
        assert response.json()["message"] == "Email already added"