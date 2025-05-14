from typing import List, Union
from app.domain.interfaces.classes_repository import IClassesRepository
from app.models.models import ClassModel
from sqlalchemy.orm import Session

from app.schemas.get_all_classes import GetAllClassesResponse
from app.schemas.update_class import UpdateClassResponse


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

    def delete_class(self, group_id: str, title: str):
        group_exists = self.db.query(ClassModel).filter(ClassModel.group_id == group_id).first()
        if not group_exists:
            return {"message": "Grupo não encontrado."}
    
        classes = self.db.query(ClassModel).filter(
            ClassModel.group_id == group_id,
            ClassModel.title == title
        ).all()

        if not classes:
            return {"message": "Nenhuma aula encontrada com esse nome."}
    
        for class_ in classes:
            self.db.delete(class_)

        self.db.commit()
        return {"message": "Aula deletada com sucesso."}
    
    def get_all_classes(self) -> List[GetAllClassesResponse]:
        classes = self.db.query(ClassModel).all()
        return [
            GetAllClassesResponse(
                class_id=cls.class_id,
                group_id=cls.group_id,
                title=cls.title,
                pdf_url=cls.pdf_url,
                status=cls.status,
                last_access_class=cls.last_access_class,
                created_at=cls.created_at,
                order=cls.order
            )
            for cls in classes
        ]

    def update_class(self, class_id: str) -> Union[UpdateClassResponse, dict]:
        class_ = self.db.query(ClassModel).filter(ClassModel.class_id == class_id).first()
        if not class_:
            return {"message": "Aula não encontrada."}
    
        class_.status = True
        self.db.commit()
        return UpdateClassResponse(
            group_id=class_.group_id,
            title=class_.title,
            pdf_url=class_.pdf_url,
            status=class_.status,
            last_access_class=class_.last_access_class,
            created_at=class_.created_at,
            order=class_.order
        )

