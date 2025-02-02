import pytest
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta
from api.auth.auth import verify_token, create_access_token

# Constants for testing
SECRET_KEY = "testsecret"
ALGORITHM = "HS256"

@pytest.mark.describe("verify_token function")
class TestVerifyToken:

    @pytest.mark.happy_path
    def test_valid_token(self):
        """Test that a valid token returns the correct username."""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(minutes=5))
        username = verify_token(token)
        assert username == "testuser"

    @pytest.mark.happy_path
    def test_token_with_different_expiry(self):
        """Test that a token with a different expiry time is still valid."""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(minutes=10))
        username = verify_token(token)
        assert username == "testuser"

    @pytest.mark.edge_case
    def test_token_with_no_subject(self):
        """Test that a token with no subject raises an HTTPException."""
        data = {}
        token = create_access_token(data, expires_delta=timedelta(minutes=5))
        with pytest.raises(HTTPException) as excinfo:
            verify_token(token)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Token invalide"

    @pytest.mark.edge_case
    def test_expired_token(self):
        """Test that an expired token raises an HTTPException."""
        data = {"sub": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as excinfo:
            verify_token(token)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Token invalide"

    @pytest.mark.edge_case
    def test_invalid_signature(self):
        """Test that a token with an invalid signature raises an HTTPException."""
        data = {"sub": "testuser"}
        token = jwt.encode(data, "wrongsecret", algorithm=ALGORITHM)
        with pytest.raises(HTTPException) as excinfo:
            verify_token(token)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Token invalide"

    @pytest.mark.edge_case
    def test_malformed_token(self):
        """Test that a malformed token raises an HTTPException."""
        malformed_token = "this.is.not.a.jwt"
        with pytest.raises(HTTPException) as excinfo:
            verify_token(malformed_token)
        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "Token invalide"