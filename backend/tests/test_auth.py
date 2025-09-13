"""
Unit tests for authentication utilities and functions.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException

from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_refresh_token
)
from app.config import settings


class TestPasswordHashing:
    """Test password hashing and verification functions."""
    
    def test_password_hashing(self):
        """Test password hashing creates different hashes for same password."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0
    
    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_failure(self):
        """Test failed password verification with wrong password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_empty_password_handling(self):
        """Test handling of empty passwords."""
        empty_password = ""
        hashed = get_password_hash(empty_password)
        
        assert verify_password(empty_password, hashed) is True
        assert verify_password("nonempty", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test access token creation with default expiration."""
        data = {"sub": "test-user-id"}
        token = create_access_token(data)
        
        # Decode token to verify contents
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test-user-id"
        assert "exp" in payload
        
        # Check that expiration is in the future
        actual_exp = datetime.fromtimestamp(payload["exp"])
        assert actual_exp > datetime.utcnow()
    
    def test_create_access_token_custom_expiration(self):
        """Test access token creation with custom expiration."""
        data = {"sub": "test-user-id"}
        custom_expiration = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_expiration)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        actual_exp = datetime.fromtimestamp(payload["exp"])
        # Check that expiration is in the future and roughly correct
        assert actual_exp > datetime.utcnow()
        # Should expire more than 50 minutes from now (allowing some tolerance)
        min_exp = datetime.utcnow() + timedelta(minutes=50)
        assert actual_exp > min_exp
    
    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "test-user-id"}
        token = create_refresh_token(data)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "refresh"
        assert "exp" in payload
        
        # Check expiration is in the future and roughly 7 days
        actual_exp = datetime.fromtimestamp(payload["exp"])
        assert actual_exp > datetime.utcnow()
        # Should expire more than 6 days from now (allowing some tolerance)
        min_exp = datetime.utcnow() + timedelta(days=6)
        assert actual_exp > min_exp
    
    def test_verify_token_success(self):
        """Test successful token verification."""
        data = {"sub": "test-user-id", "custom": "data"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "test-user-id"
        assert payload["custom"] == "data"
        assert "exp" in payload
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        data = {"sub": "test-user-id"}
        # Create token that expires immediately
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(expired_token)
        
        assert exc_info.value.status_code == 401
    
    def test_verify_refresh_token_success(self):
        """Test successful refresh token verification."""
        data = {"sub": "test-user-id"}
        token = create_refresh_token(data)
        
        payload = verify_refresh_token(token)
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "refresh"
    
    def test_verify_refresh_token_wrong_type(self):
        """Test refresh token verification with access token."""
        data = {"sub": "test-user-id"}
        access_token = create_access_token(data)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(access_token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail
    
    def test_verify_refresh_token_invalid(self):
        """Test refresh token verification with invalid token."""
        invalid_token = "invalid.refresh.token"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_refresh_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate refresh token" in exc_info.value.detail
    
    def test_token_contains_no_sensitive_data(self):
        """Test that tokens don't contain sensitive information."""
        data = {"sub": "test-user-id", "email": "test@example.com"}
        token = create_access_token(data)
        
        # Token should be opaque - no readable sensitive data
        assert "test@example.com" not in token
        assert "test-user-id" not in token
        
        # But should be decodable with secret
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test-user-id"
        assert payload["email"] == "test@example.com"


class TestTokenSecurity:
    """Test security aspects of token handling."""
    
    def test_different_tokens_for_different_data(self):
        """Test that creating tokens with different data produces different tokens."""
        data1 = {"sub": "test-user-id-1"}
        data2 = {"sub": "test-user-id-2"}
        token1 = create_access_token(data1)
        token2 = create_access_token(data2)
        
        # Tokens should be different due to different data
        assert token1 != token2
    
    def test_token_cannot_be_decoded_without_secret(self):
        """Test that tokens cannot be decoded without the secret key."""
        data = {"sub": "test-user-id"}
        token = create_access_token(data)
        
        with pytest.raises(Exception):
            jwt.decode(token, "wrong-secret", algorithms=[settings.algorithm])
    
    def test_token_algorithm_verification(self):
        """Test that tokens are rejected with wrong algorithm."""
        data = {"sub": "test-user-id"}
        token = create_access_token(data)
        
        with pytest.raises(Exception):
            jwt.decode(token, settings.secret_key, algorithms=["HS512"])  # Wrong algorithm