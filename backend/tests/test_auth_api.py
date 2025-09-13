"""
Unit tests for authentication API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.main import app
from app.database import get_db, Base
from app.models import User
from app.auth import get_password_hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Override UUID columns for SQLite compatibility
from sqlalchemy import String
from app.models import User
# Monkey patch the UUID column to use String for testing
User.__table__.columns['id'].type = String(36)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Set up test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    """Test user data for registration."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }


@pytest.fixture
def existing_user(setup_database):
    """Create an existing user in the database."""
    db = TestingSessionLocal()
    user = User(
        email="existing@example.com",
        username="existinguser",
        password_hash=get_password_hash("existingpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


class TestUserRegistration:
    """Test user registration endpoint."""
    
    def test_register_user_success(self, setup_database, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "password" not in data  # Password should not be returned
        assert "id" in data
        assert "created_at" in data
        assert data["is_active"] is True
    
    def test_register_user_duplicate_email(self, existing_user, test_user_data):
        """Test registration with duplicate email."""
        test_user_data["email"] = existing_user.email
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_register_user_duplicate_username(self, existing_user, test_user_data):
        """Test registration with duplicate username."""
        test_user_data["username"] = existing_user.username
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]
    
    def test_register_user_invalid_email(self, setup_database, test_user_data):
        """Test registration with invalid email format."""
        test_user_data["email"] = "invalid-email"
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_short_password(self, setup_database, test_user_data):
        """Test registration with password too short."""
        test_user_data["password"] = "short"
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_short_username(self, setup_database, test_user_data):
        """Test registration with username too short."""
        test_user_data["username"] = "ab"
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, existing_user):
        """Test successful user login."""
        login_data = {
            "email": existing_user.email,
            "password": "existingpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0
    
    def test_login_wrong_email(self, existing_user):
        """Test login with wrong email."""
        login_data = {
            "email": "wrong@example.com",
            "password": "existingpassword123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_wrong_password(self, existing_user):
        """Test login with wrong password."""
        login_data = {
            "email": existing_user.email,
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, setup_database):
        """Test login with inactive user."""
        # Create inactive user
        db = TestingSessionLocal()
        user = User(
            email="inactive@example.com",
            username="inactiveuser",
            password_hash=get_password_hash("password123"),
            is_active=False
        )
        db.add(user)
        db.commit()
        db.close()
        
        login_data = {
            "email": "inactive@example.com",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 400
        assert "Inactive user" in response.json()["detail"]


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token_success(self, existing_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_data = {
            "email": existing_user.email,
            "password": "existingpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Use refresh token to get new tokens
        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # New tokens should be different from original
        assert data["access_token"] != tokens["access_token"]
        assert data["refresh_token"] != tokens["refresh_token"]
    
    def test_refresh_token_invalid(self, existing_user):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid.token.here"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "Could not validate refresh token" in response.json()["detail"]
    
    def test_refresh_with_access_token(self, existing_user):
        """Test refresh using access token instead of refresh token."""
        # Login to get tokens
        login_data = {
            "email": existing_user.email,
            "password": "existingpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        tokens = login_response.json()
        
        # Try to use access token as refresh token
        refresh_data = {"refresh_token": tokens["access_token"]}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "Invalid token type" in response.json()["detail"]


class TestProtectedEndpoints:
    """Test protected endpoints that require authentication."""
    
    def test_get_current_user_success(self, existing_user):
        """Test getting current user info with valid token."""
        # Login to get token
        login_data = {
            "email": existing_user.email,
            "password": "existingpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Get current user info
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == existing_user.email
        assert data["username"] == existing_user.username
        assert "password" not in data
    
    def test_get_current_user_no_token(self, existing_user):
        """Test getting current user info without token."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden due to missing token
    
    def test_get_current_user_invalid_token(self, existing_user):
        """Test getting current user info with invalid token."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_logout_success(self, existing_user):
        """Test successful logout."""
        # Login to get token
        login_data = {
            "email": existing_user.email,
            "password": "existingpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/v1/auth/logout", headers=headers)
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
    
    def test_logout_no_token(self, existing_user):
        """Test logout without token."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 403  # Forbidden due to missing token