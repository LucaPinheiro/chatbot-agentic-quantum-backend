from typing import List, Optional

from pydantic import BaseModel


class UpdateGroupRequest(BaseModel):
    name: Optional[str] = None
    year_semester: Optional[int] = None
    status: Optional[bool] = None
    manager_id: Optional[str] = None
    user_ids: Optional[List[str]] = None

class UpdateGroupResponse(BaseModel):
    name: str
    year_semester: int
    status: bool
    manager_id: str
    user_ids: List[str]
