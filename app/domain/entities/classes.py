from typing import Self, Type
from pydantic import BaseModel
from app.models.models import Classes


class Classes(BaseModel):
    class_id: str
    group_id: str
    title: str
    pdf_url: str
    status: bool
    last_access_class: str
    created_at: str
    order: int
    @classmethod  
    def from_orm(cls, classes: Type[Classes]) -> Self:
        return cls(
            class_id=classes.class_id,
            group_id=classes.group_id,
            title=classes.title,
            pdf_url=classes.pdf_url,
            status=classes.status,
            last_access_class=classes.last_access_class,
            created_at=classes.created_at,
            order=classes.order
        )
    def to_orm(self) -> Classes:
        return Classes(
            class_id=self.class_id,
            group_id=self.group_id,
            title=self.title,
            pdf_url=self.pdf_url,
            status=self.status,
            last_access_class=self.last_access_class,
            created_at=self.created_at,
            order=self.order
        )
    
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []
            
            classes = {
                "class_id": self.class_id,
                "group_id": self.group_id,
                "title": self.title,
                "pdf_url": self.pdf_url,
                "status": self.status,
                "last_access_class": self.last_access_class,
                "created_at": self.created_at,
                "order": self.order
            }
            
            for key in exclude:
                del classes[key]
                
            return classes