from uuid import uuid4
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    role: Role
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"frozen": True}
