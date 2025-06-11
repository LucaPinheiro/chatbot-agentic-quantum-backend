from pydantic import BaseModel, EmailStr
from typing import Optional

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UpdateUserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
