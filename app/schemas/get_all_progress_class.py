from pydantic import BaseModel


class GetAllProgressClassRequest(BaseModel):
    title: str
    group_id: str
    
class GetAllProgressClassResponse(BaseModel):
    title: str
    progress: str
    total: int
    done: int