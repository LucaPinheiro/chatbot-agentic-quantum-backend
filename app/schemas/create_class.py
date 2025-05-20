import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class CreateClassRequest(BaseModel):
    group_id: str
    title: str
    pdf_url: str
    topics: List[str]  # Apenas os nomes dos tópicos (strings)


# Schema de resposta para os tópicos da aula
class ClassTopicResponse(BaseModel):
    class_topics_id: str
    topic: str
    user_id: str
    class_id: str

    model_config = ConfigDict(from_attributes=True)


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
    topics: List[ClassTopicResponse]  # agora é uma lista de objetos, não só strings

    model_config = ConfigDict(from_attributes=True)
