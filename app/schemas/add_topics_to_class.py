from typing import List
from pydantic import BaseModel, Field, conlist


class AddTopicsToClassRequest(BaseModel):
    title: str
    topics: List[str] = Field(..., min_length=1)

class AddTopicsToClassResponse(BaseModel):
    message: str
    title: str
    topics: List[str] = Field(..., min_length=1)
