from pydantic import BaseModel


class GetAllGroupsRequest(BaseModel):
    pass

class GetAllGroupsResponse(BaseModel):
    group_id: str
    name: str
    year_semester: int
    status: bool
    manager_id: str