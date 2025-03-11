from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class UserCreate(BaseModel):
    login: str
    email: EmailStr
    password: constr(min_length=6)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class UserOut(BaseModel):
    id: int
    login: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    birth_date: Optional[str]
    phone: Optional[str]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str