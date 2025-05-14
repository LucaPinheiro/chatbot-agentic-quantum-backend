from datetime import datetime
from pydantic import BaseModel


class UpdateClassRequest(BaseModel):
    class_id: str


class UpdateClassResponse(BaseModel):
    group_id: str
    title: str
    pdf_url: str
    status: str
    last_access_class: datetime
    created_at: datetime
    order: int
