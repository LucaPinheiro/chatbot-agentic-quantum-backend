from pydantic import BaseModel


class DeleteGroupRequest(BaseModel):
    group_id: str
    name: str

class DeleteGroupResponse(BaseModel):
    message: str