from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str       = Field(..., min_length=2, max_length=80)
    year_semester: int    = Field(..., length=6)
    status: bool
    user_id: str

class CreateGroupResponse(BaseModel):
    group_id: str
    name: str
    year_semester: int
    status: bool
    user_id: str
