from datetime import datetime
from pydantic import BaseModel


class GetClassesRequest(BaseModel):
    group_id: str

class GetClassesResponse(BaseModel):
    class_id : str
    group_id : str
    title : str
    pdf_url : str
    status : bool
    last_access_class : datetime
    created_at : datetime
    order : int
