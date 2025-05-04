from typing import Literal, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ChatMessage(BaseModel):
    session_id: str
    timestamp: datetime
    role: Literal["user", "assistant", "system"]
    group_id: Optional[str]
    class_id: Optional[str]
    user_id: Optional[str]
    message: str
    tokens: int
    type: Literal["message", "summary"] = Field(default="message")

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
            "group_id": self.group_id,
            "class_id": self.class_id,
            "user_id": self.user_id,
            "message": self.message,
            "tokens": self.tokens,
            "type": self.type,
            "timestamp": self.timestamp.isoformat()
        }
