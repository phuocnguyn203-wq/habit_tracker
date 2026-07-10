from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    prefix='/users',
    tags=['users']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/token')

