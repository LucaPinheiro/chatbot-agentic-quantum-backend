from pydantic import BaseModel
from typing import Optional

class HealthCheckRequest(BaseModel):
    check: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    message: str
