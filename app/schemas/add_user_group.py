from pydantic import BaseModel


class AddUserGroupRequest(BaseModel):
    user_id: str
    group_id: str
    
class AddUserGroupResponse(BaseModel):
    user_id: str
    group_id: str
    message: str