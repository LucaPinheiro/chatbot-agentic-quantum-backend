from typing import Optional

from pydantic import BaseModel


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = None
    year_semester: Optional[int] = None
    status: Optional[bool] = None
    user_id: Optional[str] = None

class UpdateGroupResponse(BaseModel):
    name: str
    year_semester: int
    status: bool
    user_id: str