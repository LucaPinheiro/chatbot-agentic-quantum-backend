from typing import List
from app.domain.interfaces.classes_repository import IClassesRepository
from app.models.models import ClassModel
from sqlalchemy.orm import Session


class ClassesRepositoryPostgres(IClassesRepository):
    def __init__(self, db: Session):
        self.db = db
    def get_classes_by_group(self, group_id: str) -> List[ClassModel]:
        classes = self.db.query(ClassModel).filter(ClassModel.group_id == group_id).all()
        if not classes:
            return []
        print(f"Consultando banco para group_id={classes}")
        return [ClassModel.from_orm(classes) for classes in classes]