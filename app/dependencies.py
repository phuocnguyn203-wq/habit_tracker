from typing import Annotated

from app.database.database import SessionLocal
from fastapi import Depends, HTTPException, status
from app.routers.users import oauth2_scheme
from app.schemas.users import TokenData
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.config import SECRET_KEY
from app.services.users import ALGORITHM, SECRET_KEY

from app.services.users import get_user
import jwt


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(
        db,
        token_data.username or 'None'
    )
    if user is None:
        raise credentials_exception
    return user