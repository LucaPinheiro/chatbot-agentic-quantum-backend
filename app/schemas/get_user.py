# app/schemas/get_user_request.py

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from app.helpers.enums.enums import PermissionLevelEnum


class GetUserRequest(BaseModel):
    user_id: Optional[str] = None
    email: Optional[EmailStr] = None

    @model_validator(mode="before")
    @classmethod
    def at_least_one_field(cls, data):
        user_id = data.get("user_id")
        email = data.get("email")
        if not user_id and not email:
            raise ValueError("Você deve informar 'user_id' ou 'email'")
        return data


class GetUserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    permission: Optional[PermissionLevelEnum] = None
