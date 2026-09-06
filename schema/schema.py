from sqlmodel import SQLModel,Field
from typing import Optional
from enum import Enum
from datetime import datetime
from pydantic import EmailStr

class Todostatus(str, Enum):
    PENDING = "Pending"
    IN_PROCESS = "In Process"
    COMPLETED = "Completed"


class Create_todo(SQLModel):
    title: str = Field(max_length=50, min_length=1)
    status:Todostatus
    # user_id:int


class Update_todo(SQLModel):
    title: Optional[str] = Field(default=None, max_length=50, min_length=1)
    status:Optional[Todostatus] = None


class User_register(SQLModel):
    name: str = Field(min_length=5, max_length=50)
    email:EmailStr = Field(max_length=50)
    password:str = Field(max_length=255)



class User_update(SQLModel):
    name: Optional[str] = None
    email:Optional[str] = None
    password_hash:Optional[str] = None
    email_verified:Optional[bool] = None


class UserLogin(SQLModel):
    email:str
    password:str

class GoogleLogin(SQLModel):
    id_token: str


class VerifyEmail(SQLModel):
    email:str
    otp:str

class Resend_otp(SQLModel):
    email:str


