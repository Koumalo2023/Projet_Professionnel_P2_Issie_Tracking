# api/app/schemas/user_schema.py
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    age: int
    can_be_contacted: bool
    can_data_be_shared: bool

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id:int
    username: str
    email: EmailStr
    age: Optional[int] 
    can_be_contacted: bool
    can_data_be_shared: bool

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    can_be_contacted: Optional[bool] = None
    can_data_be_shared: Optional[bool] = None