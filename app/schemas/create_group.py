from typing import List, Optional
from pydantic import BaseModel, constr, Field, field_validator, validator

class CreateGroupRequest(BaseModel):
    name: str       = Field(..., min_length=2, max_length=80)
    year_semester: int    = Field(..., ge=100000, le=999999)
    status: bool
    manager_id: str
    user_ids: Optional[List[str]] = None  

    @field_validator('year_semester')
    @classmethod
    def check_year_semester(cls, v):
        year = v // 100
        semester = v % 100
        if semester not in (1, 2):
            raise ValueError('semester must be 1 ou 2')
        if year < 2000 or year > 2100:
            raise ValueError('year must be entre 2000 e 2100')
        return v

class CreateGroupResponse(BaseModel):
    group_id: str
    name: str
    year_semester: int
    status: bool
    manager_id: str
    user_ids: Optional[List[str]] = None 
    