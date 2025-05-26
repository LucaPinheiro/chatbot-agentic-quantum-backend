from pydantic import BaseModel, Field


class DeleteClassRequest(BaseModel):
    class_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)

class DeleteClassResponse(BaseModel):
    message: str