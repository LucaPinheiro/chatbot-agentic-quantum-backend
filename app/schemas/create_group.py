from pydantic import BaseModel, Field


class CreateGroupRequest(BaseModel):
    name: str       = Field(..., min_length=2, max_length=80)
    year_semester: int    = Field(..., ge=100000, le=999999)
    status: bool
    manager_id: str

class CreateGroupResponse(BaseModel):
    group_id: str
    name: str
    year_semester: int
    status: bool
    manager_id: str
