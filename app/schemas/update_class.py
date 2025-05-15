from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UpdateClassRequest(BaseModel):
    group_id: Optional[str] = None
    title: Optional[str] = None
    pdf_url: Optional[str] = None
    status: Optional[bool] = None
    order: Optional[int] = None


class UpdateClassResponse(BaseModel):
    group_id: str
    title: str
    pdf_url: str
    status: bool
    order: int
