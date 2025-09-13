"""
Unit tests for authentication API endpoints using a simple approach.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func
import uuid

from app.database import get_db
from app.auth import get_password_hash

# Create test database with SQLite-compatible models
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth_simple.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create SQLite-compatible base and User model for testing
TestBase = declarative_base()

class TestUser(TestBase):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the User model in the app for testing
import app.models
app.models.User = TestUser

from app.main import app as fastapi_app
fastapi_app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(fastapi_app)


@pytest.fixture(scope="function")
def setup_database():
    """Set up test database for each test."""
    TestBase.metadata.create_all(bind=engine)
    yield
    TestBase.metadata.drop_all(bind=engine)


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
    user = TestUser(
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