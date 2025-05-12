from pydantic import BaseModel


class DeleteGroupRequest(BaseModel):
    name: str

class DeleteGroupResponse(BaseModel):
    message: str