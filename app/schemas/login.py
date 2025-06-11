from pydantic import BaseModel
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    name: str
    user_id: str
    permission: str
    created_at: datetime
    token: str
