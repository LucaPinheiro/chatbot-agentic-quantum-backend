import datetime
from typing import List, Literal
from pydantic import BaseModel, Field

class GetChatHistoryRequest(BaseModel):
    session_id: str = Field(..., example="session-12345")

class ChatMessageResponse(BaseModel):
    role: Literal["user", "assistant", "system"]
    message: str
    timestamp: datetime.datetime
    tokens: int

class GetChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageResponse]