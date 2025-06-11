from openai import BaseModel


class DeleteUserFromGroupRequest(BaseModel):
    user_id: str
    
class DeleteUserFromGroupResponse(BaseModel):
    message: str