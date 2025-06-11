from typing import List
from pydantic import BaseModel, Field, HttpUrl

class TopicItem(BaseModel):
    topic: str = Field(..., min_length=1)
    pdf_url: HttpUrl  # Garante que seja uma URL válida

class AddTopicsToClassRequest(BaseModel):
    class_id: str = Field(..., min_length=1)
    topics: List[TopicItem] = Field(..., min_items=1)

class AddTopicsToClassResponse(BaseModel):
    message: str
    class_id: str
    topics: List[TopicItem] = Field(..., min_items=1) 
