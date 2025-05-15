from pydantic import BaseModel


class GetGroupByIdRequest(BaseModel):
    group_id: str
    
class GetGroupByIdResponse(BaseModel):
    group_id: str
    name: str
    year_semester: int
    status: bool
    user_id: str
