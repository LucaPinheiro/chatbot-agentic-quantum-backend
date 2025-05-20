from typing import Self, Type
from pydantic import BaseModel
from app.models.models import Group, GroupEnrollment


class GroupEnrollment(BaseModel):
    group_id: str
    student_id: str
    @classmethod
    def from_orm(cls, group_enrollment: Type[GroupEnrollment]) -> Self:
        return cls(
            group_id=group_enrollment.group_id,
            student_id=group_enrollment.student_id
        )
    
    def to_orm(self) -> GroupEnrollment:
        return GroupEnrollment(
            group_id=self.group_id,
            student_id=self.student_id,
        )
    
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []
            
            group_enrollment = {
                "group_id": self.group_id,
                "student_id": self.student_id,
            }
            
            for key in exclude:
                del group_enrollment[key]
                
            return group_enrollment
        
    