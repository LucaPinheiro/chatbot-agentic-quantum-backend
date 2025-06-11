from datetime import datetime
from pydantic import BaseModel

class GetAllClassesByUserRequest(BaseModel):
    user_id: str
    
class GetAllClassesByUserResponse(BaseModel):
    class_id: str
    group_id: str
    manager_id: str
    title: str
    status: bool
    created_at: datetime
    order: int