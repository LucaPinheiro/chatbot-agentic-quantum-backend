from datetime import datetime
from typing import Self, Type
from pydantic import BaseModel
from app.models.models import ClassModel as ClassModelORM


class ClassModel(BaseModel):
    class_id: str
    group_id: str
    manager_id: str
    title: str
    status: bool
    created_at: datetime
    order: int
    
    @classmethod  
    def from_orm(cls, classes: Type[ClassModelORM]) -> Self:
        return cls(
            class_id=classes.class_id,
            group_id=classes.group_id,
            manager_id=classes.manager_id,
            title=classes.title,
            status=classes.status,
            created_at=classes.created_at,
            order=classes.order
        )
        
    def to_orm(self) -> ClassModelORM:
        return ClassModel(
            class_id=self.class_id,
            group_id=self.group_id,
            manager_id=self.manager_id,
            title=self.title,
            status=self.status,
            created_at=self.created_at,
            order=self.order
        )
    
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []
        
        classes = {
            "class_id": self.class_id,
            "group_id": self.group_id,
            "manager_id": self.manager_id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at,
            "order": self.order
        }
        
        for key in exclude:
            classes.pop(key, None)
        
        return classes