from typing import List
from app.domain.interfaces.classes_repository import IClassesRepository
from app.models.models import Classes
from sqlalchemy.orm import Session


class ClassesRepositoryPostgres(IClassesRepository):
    def __init__(self, db: Session):
        self.db = db
    def get_classes_by_group(self, group_id: str) -> List[Classes]:
        classes = self.db.query(Classes).filter(Classes.group_id == group_id).all()
        if not classes:
            return []
        print(f"Consultando banco para group_id={classes}")
        return [Classes.from_orm(classes) for classes in classes]