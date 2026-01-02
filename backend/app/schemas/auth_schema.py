# api/app/schemas/auth_schema.py
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: EmailStr
    age: int
    can_be_contacted: bool
    can_data_be_shared: bool