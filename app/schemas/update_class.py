from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UpdateClassRequest(BaseModel):
    class_id: str
    group_id: Optional[str]
    title: Optional[str]
    pdf_url: Optional[str]
    status: Optional[bool]
    order: Optional[int]


class UpdateClassResponse(BaseModel):
    group_id: str
    title: str
    pdf_url: str
    status: str
    last_access_class: datetime
    created_at: datetime
    order: int
