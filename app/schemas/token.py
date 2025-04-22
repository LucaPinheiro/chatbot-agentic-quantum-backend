# app/schemas/token_user.py
from pydantic import BaseModel

class TokenUser(BaseModel):
    id: str
    permission: int
