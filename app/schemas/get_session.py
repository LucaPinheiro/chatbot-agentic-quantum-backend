# app/schemas/get_user_request.py

from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from app.helpers.enums.enums import PermissionLevelEnum


class GetSessionRequest(BaseModel):
    class_id: str

class GetSessionResponse(BaseModel):
    session_id: str
