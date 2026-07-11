from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.users import UserInDB, CreateUser
from app.config import SECRET_KEY

ALGORITHM = 'HS256'

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
    return db.scalars(
        select(User).where(User.username==username)
    ).first()

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
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_user(
    db: Session,
    create_user: CreateUser
):
    hashed_password = password_hash.hash(create_user.password)
    user = User(
        username=create_user.username,
        hashed_password=hashed_password
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f'Username {create_user.username} is already taken')
    db.refresh(user)
    return user