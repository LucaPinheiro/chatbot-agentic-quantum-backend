from pydantic import BaseModel
from app.helpers.enums.enums import PermissionLevelEnum


class GetAllUsersRequest(BaseModel):
    pass

class GetAllUsersResponse(BaseModel):
    user_id: str
    name: str
    email: str
    permission: PermissionLevelEnum