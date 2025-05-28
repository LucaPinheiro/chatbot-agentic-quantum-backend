from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    name: str
    user_id: str
    permission: str
    token: str
