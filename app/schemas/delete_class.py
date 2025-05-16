from pydantic import BaseModel


class DeleteClassRequest(BaseModel):
    group_id: str
    title: str

class DeleteClassResponse(BaseModel):
    message: str