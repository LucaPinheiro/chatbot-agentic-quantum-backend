from pydantic import BaseModel


class DeleteUserRequest(BaseModel):
    user_id: str
    name: str
    
class DeleteUserResponse(BaseModel):
    message: str