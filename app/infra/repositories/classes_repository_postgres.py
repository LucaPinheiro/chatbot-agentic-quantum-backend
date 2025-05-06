from typing import List
from app.domain.interfaces.classes_repository import IClassesRepository
from app.models.models import ClassModel
from sqlalchemy.orm import Session


class ClassesRepositoryPostgres(IClassesRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_classes_by_group(self, group_id: str) -> List[ClassModel]:
        print(f"[DEBUG] Buscando classes para group_id: {group_id!r}")
        classes = self.db.query(ClassModel).filter(ClassModel.group_id == group_id).all()
        if not classes:
            return []
        print(f"[DEBUG] Resultado da query: {classes}")
        print(type(group_id))
        return classes
