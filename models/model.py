from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from schema.schema import Todostatus
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100)
    status: Todostatus
    createdat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    user: Optional["User"] = Relationship(back_populates="todos")




class User(SQLModel, table=True):
    id:Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=5, max_length=50)
    email:str = Field(max_length=50, unique=True)
    password_hash:Optional[str] = Field(default=None, max_length=255)
    email_verification_otp_hash: Optional[str] = Field(default=None)
    email_verification_otp_expires_at: Optional[datetime] = None
    email_verification_otp_attempts: int = Field(default=0)
    email_verification_last_sent_at: Optional[datetime] = None
    email_verification_locked_until: Optional[datetime] = None
    email_verified:bool = Field(default=False)
    password_reset_token_hash: Optional[str] = Field(default=None,max_length=255)
    password_reset_token_expires_at: Optional[datetime] = None
    todos:List["Todo"] = Relationship(back_populates="user", cascade_delete=True)
