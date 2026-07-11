from pydantic import BaseModel, ConfigDict

class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str

class CreateUser(BaseUser):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserInDB(BaseUser):
    hashed_password: str