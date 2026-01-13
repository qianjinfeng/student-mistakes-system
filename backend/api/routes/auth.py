"""
Authentication routes
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Temporarily disabled
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from config.settings import settings
except ImportError:
    # Fallback settings for development
    class FallbackSettings:
        class Security:
            secret_key = "fallback-secret-key"
            algorithm = "HS256"
            access_token_expire_minutes = 30

        class Database:
            url = "postgresql://postgres:postgres@localhost:5432/student_mistakes"

        security = Security()
        database = Database()

    settings = FallbackSettings()
from database.connection import get_db
from models.user import User

router = APIRouter()

# Password hashing
pwd_context = None  # Disabled to avoid bcrypt initialization issue

# OAuth2 scheme - disabled to avoid bcrypt issue
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    # Temporary workaround for bcrypt issue
    import hashlib
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """Hash password"""
    # Simple SHA256 hash to avoid bcrypt issues
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.security.secret_key.get_secret_value(),
        algorithm=settings.security.algorithm
    )
    return encoded_jwt


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current user from token"""
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.security.secret_key.get_secret_value(), algorithms=[settings.security.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    print(f"DEBUG: Registration request for username: {user_data.username}")
    print(f"DEBUG: Password length: {len(user_data.password)}")
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )

    # Create new user
    print(f"DEBUG: About to hash password...")
    hashed_password = get_password_hash(user_data.password)
    print(f"DEBUG: Password hashed successfully")
    user = User(
        id=str(uuid.uuid4()),  # Generate UUID for primary key
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active
    )


@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active
    )