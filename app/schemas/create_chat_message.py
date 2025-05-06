from pydantic import BaseModel, Field
from typing import Literal
import datetime

class CreateChatMessageRequest(BaseModel):
    message: str = Field(..., example="O que é superposição?")
    role: Literal["user", "system"] = Field(..., example="user")
    tokens: int = Field(..., example=12)
    type: Literal["message", "summary"] = Field(default="message")

class CreateChatMessageResponse(BaseModel):
    status: str = "success"
    saved_at: datetime.datetime
    llm_response: str
    llm_role: Literal["system"] = "system"
    llm_tokens: int

