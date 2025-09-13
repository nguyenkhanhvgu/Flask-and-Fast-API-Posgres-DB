"""
Unit tests for FastAPI dependencies.
"""
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from app.dependencies import get_current_user, get_current_active_user
from app.database import Base
from app.models import User
from app.auth import get_password_hash, create_access_token

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dependencies.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def setup_database():
    """Set up test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(setup_database):
    """Create database session for testing."""
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session):
    """Create an inactive test user in the database."""
    user = User(
        email="inactive@example.com",
        username="inactiveuser",
        password_hash=get_password_hash("testpassword123"),
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestGetCurrentUser:
    """Test get_current_user dependency."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, test_user, db_session):
        """Test successful user retrieval with valid token."""
        # Create valid token
        token = create_access_token(data={"sub": str(test_user.id)})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        # Get current user
        current_user = await get_current_user(credentials, db_session)
        
        assert current_user.id == test_user.id
        assert current_user.email == test_user.email
        assert current_user.username == test_user.username
        assert current_user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db_session):
        """Test user retrieval with invalid token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", 
            credentials="invalid.token.here"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_sub_in_token(self, db_session):
        """Test user retrieval with token missing 'sub' claim."""
        # Create token without 'sub' claim
        token = create_access_token(data={"user": "test-user-id"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_uuid(self, db_session):
        """Test user retrieval with invalid UUID in token."""
        # Create token with invalid UUID
        token = create_access_token(data={"sub": "not-a-valid-uuid"})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_nonexistent_user(self, db_session):
        """Test user retrieval with token for non-existent user."""
        # Create token with valid UUID but non-existent user
        fake_uuid = str(uuid.uuid4())
        token = create_access_token(data={"sub": fake_uuid})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self, inactive_user, db_session):
        """Test user retrieval with token for inactive user."""
        # Create token for inactive user
        token = create_access_token(data={"sub": str(inactive_user.id)})
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 400
        assert "Inactive user" in exc_info.value.detail


class TestGetCurrentActiveUser:
    """Test get_current_active_user dependency."""
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self, test_user):
        """Test successful active user retrieval."""
        # Since get_current_user already checks is_active, 
        # get_current_active_user just returns the same user
        current_user = await get_current_active_user(test_user)
        
        assert current_user.id == test_user.id
        assert current_user.email == test_user.email
        assert current_user.is_active is True
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_with_active_user(self, test_user):
        """Test that active user is returned as-is."""
        result = await get_current_active_user(test_user)
        assert result is test_user