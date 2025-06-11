from typing import Optional
from pydantic import BaseModel
from app.helpers.enums.enums import PermissionLevelEnum


class GetAllUsersRequest(BaseModel):
    pass

class GetAllUsersResponse(BaseModel):
    user_id: str
    name: str
    email: str
    group_id: Optional[str]
    permission: PermissionLevelEnum