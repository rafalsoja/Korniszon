import re
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..config import SECRET_KEY, HASHING_ALGORITHM
from ..schemas.users import UserCreate, UserRead, TokenData, Token
from ..models import User
from ..database import get_db
from ..logger import get_logger

logger = get_logger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT exparation time
TOKEN_EXPIRE_MINUTES = 30

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decode JWT and return current user email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        email: str = payload.get("sub")
        exp: int = payload.get("exp")
        
        if email is None:
            logger.warning("Token missing 'sub' claim")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Check expiration
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.info(f"Expired token for user {email}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        
        return TokenData(sub=email)
    
    except JWTError as e:
        logger.warning(f"JWT decode error: {type(e).__name__}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Register attempt for email: {user.email}")
    
    # Validate email
    if not EMAIL_REGEX.match(user.email):
        logger.warning(f"Invalid email format: {user.email}")
        raise HTTPException(status_code=422, detail="Invalid email format")

    # Validate password
    if len(user.password) < 8:
        raise HTTPException(status_code=422, detail="Password too short")

    # Validate username
    if not user.username or len(user.username) < 3:
        raise HTTPException(status_code=422, detail="Username too short")

    # Check for existing email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        hashed_pw = pwd_context.hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_pw,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User registered: {user.email}")
        return new_user
    
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error for {user.email}: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    username_or_email = form_data.username
    logger.info(f"Login attempt: {username_or_email}")
    
    try:
        if not form_data.username or not form_data.password:
            raise HTTPException(status_code=422, detail="Credentials required")

        user = db.query(User).filter(
            or_(User.email == username_or_email, User.username == username_or_email)
        ).first()

        if not user:
            logger.warning(f"Login failed: user not found ({username_or_email})")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not pwd_context.verify(form_data.password, user.hashed_password):
            logger.warning(f"Login failed: wrong password ({username_or_email})")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            logger.warning(f"Login attempt on disabled account: {user.email}")
            raise HTTPException(status_code=403, detail="Account disabled")

        # Create JWT
        expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        token_data = {
            "sub": user.email,
            "exp": expires
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm=HASHING_ALGORITHM)
        
        logger.info(f"Login successful: {user.email}")
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")