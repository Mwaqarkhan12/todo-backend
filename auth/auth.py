from argon2 import PasswordHasher
import secrets
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from config.database import get_session
from models.model import User
import hashlib
from sqlmodel import Session,  select

auth_token = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET = secrets.token_hex(32)
ALGORETHM = "HS256"

# verif_token = secrets.token_urlsafe(32)

def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"

authentication = PasswordHasher()

def verify_password(hash:str, password:str):
    return authentication.verify(hash, password)


def password_hasher(password:str):
    return authentication.hash(password)


ACCESS_TOKEN_EXPIRE_MINUTES = 5
def create_token(email:str):
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire_time.timestamp()}
    return jwt.encode(payload, SECRET, algorithm=ALGORETHM)


def decode_token(token:str):
    return jwt.decode(token, SECRET, algorithms=[ALGORETHM])


OTP_EXPIRATION_MINUTES = 2

def get_otp_expiry():
    return datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRATION_MINUTES)


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_current_user(token: str = Depends(auth_token), session: Session = Depends(get_session)):
    try:
        decoded = jwt.decode(token, SECRET, algorithms=[ALGORETHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials (signature verification failed)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = session.exec(select(User).where(User.email == decoded.get("sub"))).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No user email exist"
        )
    
    return user

