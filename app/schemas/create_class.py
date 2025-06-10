from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict

class ClassTopicInput(BaseModel):
    topic: str
    topic_pdf_url: str

class CreateClassRequest(BaseModel):
    group_id: str
    title: str
    order: int
    class_topics: List[ClassTopicInput]
    
    
class ClassTopicResponse(BaseModel):
    topic: str
    topic_pdf_url: str


class CreateClassResponse(BaseModel):
    message: str
    group_id: str
    title: str
    order: int
    class_id: str
    created_at: datetime
    class_topics: List[ClassTopicResponse]

    
