from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr
from shared_models.schemas import UserRole, Status  # TODO remove after migrate to shared_models


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