from typing import Self, Type
from pydantic import BaseModel
from app.models.models import Group


class Group(BaseModel):
    group_id: str
    name: str
    year_semester: int
    status: bool
    manager_id: str
    @classmethod
    def from_orm(cls, group: Type[Group]) -> Self:
        return cls(
            group_id=group.group_id,
            name=group.name,
            year_semester=group.year_semester,
            status=group.status,
            manager_id=group.manager_id
        )
    
    def to_orm(self) -> Group:
        return Group(
            group_id=self.group_id,
            name=self.name,
            year_semester=self.year_semester,
            status=self.status,
            manager_id=self.manager_id
        )
    
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []
            
            group = {
                "group_id": self.group_id,
                "name": self.name,
                "year_semester": self.year_semester,
                "status": self.status,
                "manager_id": self.manager_id
            }
            
            for key in exclude:
                del group[key]
                
            return group
        
    