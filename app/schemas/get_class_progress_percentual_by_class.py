from pydantic import BaseModel


class GetClassProgressPercentualByClassRequest(BaseModel):
    class_id: str
   
class GetClassProgressPercentualByClassResponse(BaseModel):
    class_id: str
    class_progress_percentual: str
    total: int
    done: int

