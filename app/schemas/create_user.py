from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    name: str             = Field(..., min_length=2, max_length=80)
    email: EmailStr
    password: str         = Field(..., min_length=6, max_length=128)

class CreateUserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
