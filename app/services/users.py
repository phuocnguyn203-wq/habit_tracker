from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select

from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.users import CreateUser, UserInDB, TokenData, Token
from app.config import SECRET_KEY

ALGORITHM = 'HS256'
ACCESS_TOKEN_MINUTES = 30

password_hash =PasswordHash.recommended()

DUMMY_HASH = password_hash.hash('dummy string')

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_hashed_password(plain_password):
    return password_hash.hash(plain_password)

def get_user(
    db: Session,
    username: str,
):
    user = db.scalars(
        select(User).where(User.username==username)
    ).one()
    if not user:
        return None
    return UserInDB(
        username=user.username,
        hashed_password=user.hashed_password,
    )

def authenticate_user(
    db: Session,
    username: str,
    password: str,
):
    user = get_user(
        db,
        username
    )
    if not user:
        verify_password(password, DUMMY_HASH) # make both case long approximately equal
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({'expire': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt
