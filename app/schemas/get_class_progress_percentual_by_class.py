from typing import Optional
from pydantic import BaseModel


class GetClassProgressPercentualByClassRequest(BaseModel):
    class_id: str
    user_id: Optional[str] = None
   
class GetClassProgressPercentualByClassResponse(BaseModel):
    class_id: str
    user_id: str
    class_progress_percentual: str
    total: int
    done: int

