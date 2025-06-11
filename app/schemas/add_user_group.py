from typing import List
from pydantic import BaseModel


class AddUserGroupRequest(BaseModel):
    users_id: List[str]
    group_id: str
    
class AddUserGroupResponse(BaseModel):
    users_id: List[str]
    group_id: str