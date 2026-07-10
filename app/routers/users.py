from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



from sqlalchemy.orm import Session
from app.schemas.users import Token, BaseUser

from app.services.users import authenticate_user, create_access_token
from datetime import timedelta

ACCESS_TOKEN_MINUTES = 30

router = APIRouter(
    prefix='/users',
    tags=['users']
)

from app.dependencies import get_db, get_current_user

@router.post('/token')
async def login_for_access_token(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type='bearer'
    )
    
@router.get('/user/me/')
async def read_users_me(
    current_user: Annotated[BaseUser, Depends(get_current_user)]
):
    return current_user