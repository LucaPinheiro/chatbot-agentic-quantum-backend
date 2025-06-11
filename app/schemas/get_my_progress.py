from typing import List
from pydantic import BaseModel

class GetMyProgressRequest(BaseModel):
    group_id: str

class ClassProgressResponse(BaseModel):
    class_id: str
    title: str
    progresso: str  

class GetMyProgressResponse(BaseModel):
    user_id: str
    name: str
    group_id: str
    classes: List[ClassProgressResponse]
    progresso_geral: str
