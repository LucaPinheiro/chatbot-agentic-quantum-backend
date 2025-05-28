from pydantic import BaseModel


class GetProgressPercentualByGroupRequest(BaseModel):
    name: str
    
class GetProgressPercentualByGroupResponse(BaseModel):
    name: str
    group_progress_percentual: str
    total: int
    done: int