from datetime import datetime
from pydantic import BaseModel

class GetAllClassesByUserRequest(BaseModel):
    user_id: str
    
class GetAllClassesByUserResponse(BaseModel):
    class_id: str
    group_id: str
    title: str
    pdf_url: str
    status: bool
    last_access_class: datetime
    created_at: datetime
    order: int