from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import uuid4

from fastapi import HTTPException
from app.domain.interfaces.classes_repository import IClassesRepository
from app.helpers.exceptions.exceptions import NotFoundException
from app.domain.entities.classes import ClassModel as ClassEntity
from app.models.models import ClassModel as ClassORM, GroupEnrollment
from sqlalchemy.orm import Session
from app.models.models import User as UserModel

from app.schemas.get_all_classes import GetAllClassesResponse
from app.schemas.get_all_classes_by_user import GetAllClassesByUserResponse
from app.schemas.update_class import UpdateClassResponse


class ClassesRepositoryPostgres(IClassesRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_classes_by_group(self, group_id: str) -> List[ClassORM]:
        # Debug: verifica se o group_id está sendo passado corretamente
        print(f"[DEBUG] Buscando classes para group_id: {group_id!r}")

        # Certifique-se de que está utilizando a entidade do SQLAlchemy, não o modelo Pydantic.
        classes = self.db.query(ClassORM).filter(ClassORM.group_id == group_id).all()

        # Caso não haja classes, retorna uma lista vazia
        if not classes:
            return []

        # Debug: Mostra as classes encontradas
        print(f"[DEBUG] Resultado da query: {classes}")
        
        # Retorna a lista de classes encontradas
        return classes

    def delete_class(self, class_id: str, title: str):
        class_instance = self.db.query(ClassEntity).filter(
            ClassEntity.class_id == class_id,
            ClassEntity.title == title
        ).first()

        if not class_instance:
            return {"message": "Aula não encontrada."}

        self.db.delete(class_instance)
        self.db.commit()

        return {"message": "Aula deletada com sucesso."}

    
    def get_all_classes(self) -> List[GetAllClassesResponse]:
        classes = self.db.query(ClassORM).all()
        result = []

        for cls in classes:
            result.append(
                GetAllClassesResponse(
                    class_id=cls.class_id,
                    group_id=cls.group_id,
                    manager_id=cls.manager_id,
                    title=cls.title,
                    status=cls.status,
                    created_at=cls.created_at,
                    order=cls.order
                )
            )

        return result

    # def update_class(self, class_id: str, group_id: Optional[str], title: Optional[str], 
    #                  pdf_url: Optional[str], status: Optional[bool], order: Optional[int]) -> Union[UpdateClassResponse, dict]:
    #     class_ = self.db.query(ClassEntity).filter(ClassEntity.class_id == class_id).first()
    #     if not class_:
    #          raise NotFoundException("Aula não encontrada.")
    #     if group_id:
    #         class_.group_id = group_id 
    #     if title:       
    #         class_.title = title
    #     if pdf_url:
    #         class_.pdf_url = pdf_url
    #     if status is not None:
    #         class_.status = status
    #     if order is not None:   
    #         class_.order = order

    #     self.db.commit()
    #     self.db.refresh(class_) 
    #     return UpdateClassResponse(
    #         group_id=class_.group_id,
    #         title=class_.title,
    #         pdf_url=class_.pdf_url,
    #         status=class_.status,
    #         order=class_.order
    #     )


    def create_class(self, entity: ClassEntity) -> None:
            orm_obj: ClassORM = entity.to_orm()
            self.db.add(orm_obj)
            self.db.commit()
            self.db.refresh(orm_obj)

    def _get_next_order(self, group_id: str) -> int:
        # Retorna o próximo valor de ordem para a aula no grupo
        last_class = (
            self.db.query(ClassEntity)
            .filter(ClassEntity.group_id == group_id)
            .order_by(ClassEntity.order.desc())
            .first()
        )
        return (last_class.order + 1) if last_class else 1
    
    def get_all_classes_by_user(self, user_id: str) -> List[GetAllClassesByUserResponse]:
        group = self.db.query(GroupEnrollment).filter(GroupEnrollment.student_id == user_id).first()
        if not group:
            raise NotFoundException("Nenhuma inscrição de grupo encontrada para o usuário.")
        classes = self.db.query(ClassORM).filter(ClassORM.group_id == group.group_id).all()
        if not classes:
            raise NotFoundException("Nenhuma aula encontrada para o usuário.")
        return [
            GetAllClassesByUserResponse(
                class_id=cls.class_id,
                group_id=cls.group_id,
                manager_id=cls.manager_id,
                title=cls.title,
                status=cls.status,
                created_at=cls.created_at,
                order=cls.order
            )
                for cls in classes
        ] 

    def get_class_by_class_id(self, class_id: str) -> ClassORM | None:
        return (
            self.db.query(ClassORM)
            .filter(ClassORM.class_id == class_id)
            .first()
        )
