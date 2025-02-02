import pytest
from datetime import timedelta, datetime
from jose import jwt
from api.auth.auth import create_access_token

# Constants for testing
SECRET_KEY = "testsecret"
ALGORITHM = "HS256"

@pytest.mark.describe("Tests for create_access_token function")
class TestCreateAccessToken:

    @pytest.mark.happy_path
    def test_create_access_token_with_default_expiry(self, monkeypatch):
        """
        Test that a token is created with the default expiry time when no expiry is provided.
        """
        monkeypatch.setattr("api.auth.auth.SECRET_KEY", SECRET_KEY)
        data = {"sub": "testuser"}
        token = create_access_token(data)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    @pytest.mark.happy_path
    def test_create_access_token_with_custom_expiry(self, monkeypatch):
        """
        Test that a token is created with a custom expiry time when provided.
        """
        monkeypatch.setattr("api.auth.auth.SECRET_KEY", SECRET_KEY)
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded
        expected_expiry = datetime.utcnow() + expires_delta
        assert abs(decoded["exp"] - int(expected_expiry.timestamp())) < 5  # Allowing a small time drift

    @pytest.mark.edge_case
    def test_create_access_token_with_empty_data(self, monkeypatch):
        """
        Test that a token is created even when the data dictionary is empty.
        """
        monkeypatch.setattr("api.auth.auth.SECRET_KEY", SECRET_KEY)
        data = {}
        token = create_access_token(data)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    @pytest.mark.edge_case
    def test_create_access_token_with_no_secret_key(self, monkeypatch):
        """
        Test that an error is raised when the secret key is not set.
        """
        monkeypatch.setattr("api.auth.auth.SECRET_KEY", None)
        data = {"sub": "testuser"}
        with pytest.raises(ValueError):
            create_access_token(data)

    @pytest.mark.edge_case
    def test_create_access_token_with_expired_delta(self, monkeypatch):
        """
        Test that a token is created with an already expired expiry time.
        """
        monkeypatch.setattr("api.auth.auth.SECRET_KEY", SECRET_KEY)
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=-1)
        token = create_access_token(data, expires_delta)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert decoded["sub"] == "testuser"
        assert "exp" in decoded
        assert decoded["exp"] < int(datetime.utcnow().timestamp())