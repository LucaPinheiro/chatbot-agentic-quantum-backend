from typing import Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ChatMessage(BaseModel):
    session_id: str
    timestamp: datetime
    role: Literal["user", "assistant", "system"]
    message: str
    tokens: int

    @property
    def pk(self) -> str:
        return f"session#{self.session_id}"

    @property
    def sk(self) -> str:
        return self.timestamp.isoformat()
    
    def to_dict(self) -> dict:
        return {
            "PK": self.pk,
            "SK": self.sk,
            "role": self.role,
            "message": self.message,
            "tokens": self.tokens
        }
