from datetime import datetime
from pydantic import BaseModel


class GetClassesRequest(BaseModel):
    group_id: str

class GetClassesResponse(BaseModel):
    class_id : str
    group_id : str
    title : str
    manager_id: str
    status : bool
    created_at : datetime
    order : int
