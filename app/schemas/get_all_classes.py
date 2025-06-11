from datetime import datetime
from pydantic import BaseModel

class GetAllClassesRequest(BaseModel):
    pass

class GetAllClassesResponse(BaseModel):
    class_id: str
    group_id: str
    manager_id: str
    title: str
    status: bool
    created_at: datetime
    order: int
