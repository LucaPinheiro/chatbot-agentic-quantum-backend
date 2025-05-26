import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


# Schema de entrada para os tópicos da aula (sem class_id)
class ClassTopicInput(BaseModel):
    topic: str


# Schema de resposta para os tópicos da aula
class ClassTopicResponse(BaseModel):
    class_topics_id: str
    topic: str
    user_id: str
    class_id: str

    model_config = ConfigDict(from_attributes=True)


# Schema de entrada para criação da aula
class CreateClassRequest(BaseModel):
    group_id: str
    title: str
    pdf_url: str    
    class_topics: List[ClassTopicInput]


# Schema de resposta completo da criação de uma aula
class CreateClassResponse(BaseModel):
    class_id: str
    group_id: str
    title: str
    pdf_url: str
    status: bool
    last_access_class: datetime.datetime
    created_at: datetime.datetime
    order: int
    class_topics: List[ClassTopicResponse]

    model_config = ConfigDict(from_attributes=True)
