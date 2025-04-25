from pydantic import BaseModel

from app.helpers.enums.enums import PermissionLevelEnum


class GetUserByEmailRequest(BaseModel):
    email: str
    
    
class GetUserByEmailResponse(BaseModel):
    user_id: str
    name: str
    email: str
    permission: PermissionLevelEnum
    
    
    
