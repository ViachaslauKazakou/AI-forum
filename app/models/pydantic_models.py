from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from enum import Enum as PyEnum

# from src.models.model import LanguageEnum, Status, UserRole


class Status(str, PyEnum):
    pending = "pending"
    active = "active"
    disabled = "disabled"
    blocked = "Забанен"
    deleted = "deleted"


# Enum for user roles
class UserRole(str, PyEnum):
    admin = "admin"
    user = "user"
    ai_bot = "ai_bot"  # AI user with both admin and user capabilities
    mixed = "mixed"  # User with both admin and user capabilities
    mentor = "mentor"  # User with mentor capabilities
    mentee = "mentee"  # User with mentee capabilities


class UserBaseModel(BaseModel):

    username: str
    firstname: str
    lastname: str
    password: str
    email: EmailStr
    user_type: Optional[UserRole] = None  # = UserRole.admin  # Default role is admin
    status: Optional[Status] = None  # = UserStatus.pending  # Default status is pending

    model_config = ConfigDict(from_attributes=True)


class GetUserModel(UserBaseModel):

    id: int