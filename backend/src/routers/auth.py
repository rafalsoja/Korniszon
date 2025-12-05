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

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return TokenData(sub=email)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = pwd_context.hash(user.password)
    pwd_context.verify(user.password, hashed_pw)
    new_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(form_data.username, form_data.password)
    user = db.query(User).filter(
        or_(User.email == form_data.username, User.username == form_data.username)
    ).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=HASHING_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
