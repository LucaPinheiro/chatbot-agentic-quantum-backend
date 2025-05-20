from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import uuid4

from fastapi import HTTPException
from app.domain.interfaces.classes_repository import IClassesRepository
from app.helpers.exceptions.exceptions import NotFoundException
from app.models.models import ClassModel, ClassTopic, GroupEnrollment, TopicProgress
from sqlalchemy.orm import Session

from app.schemas.create_class import ClassTopicResponse, CreateClassResponse
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

    def update_class(self, class_id: str, group_id: Optional[str], title: Optional[str], 
                     pdf_url: Optional[str], status: Optional[bool], order: Optional[int]) -> Union[UpdateClassResponse, dict]:
        class_ = self.db.query(ClassModel).filter(ClassModel.class_id == class_id).first()
        if not class_:
             raise NotFoundException("Aula não encontrada.")
        if group_id:
            class_.group_id = group_id 
        if title:       
            class_.title = title
        if pdf_url:
            class_.pdf_url = pdf_url
        if status is not None:
            class_.status = status
        if order is not None:   
            class_.order = order

        self.db.commit()
        self.db.refresh(class_) 
        return UpdateClassResponse(
            group_id=class_.group_id,
            title=class_.title,
            pdf_url=class_.pdf_url,
            status=class_.status,
            order=class_.order
        )


    def create_class(
            self,
            group_id: str,
            title: str,
            pdf_url: str,
            topics: List[str],
            user_id: str
        ) -> CreateClassResponse:
            # Verifica duplicidade
            existing_class = (
                self.db.query(ClassModel)
                .filter(ClassModel.group_id == group_id, ClassModel.title == title)
                .first()
            )

            if existing_class:
                raise HTTPException(
                    status_code=400,
                    detail=f"Já existe uma aula com o título '{title}' neste grupo."
                )

            new_class = ClassModel(
                class_id=uuid4().hex,
                group_id=group_id,
                title=title,
                pdf_url=pdf_url,
                created_at=datetime.now(timezone.utc),
                last_access_class=datetime.now(timezone.utc),
                status=True,
                order=self._get_next_order(group_id),
            )

            self.db.add(new_class)
            self.db.commit()
            self.db.refresh(new_class)

            # Cria tópicos
            class_topics: List[ClassTopic] = []
            for topic in topics:
                class_topic = ClassTopic(
                    class_topics_id=uuid4().hex,
                    class_id=new_class.class_id,
                    topic=topic,
                    user_id=user_id
                )
                class_topics.append(class_topic)
                self.db.add(class_topic)
            
            students = (
                self.db.query(GroupEnrollment.student_id)
                    .filter(GroupEnrollment.group_id == group_id)
                    .filter(GroupEnrollment.student_id != user_id)
                    .all()
            )

            topics_progress: List[TopicProgress] = []
            for topic in class_topics:
                for student in students:
                    topic_progress = TopicProgress(
                        topic_progress_id=uuid4().hex,
                        class_topics_id=topic.class_topics_id,
                        user_id=student.student_id,
                        flag=False
                    )
                topics_progress.append(topic_progress)
                self.db.add(topic_progress)

            self.db.commit()

            return CreateClassResponse(
                class_id=new_class.class_id,
                group_id=new_class.group_id,
                title=new_class.title,
                pdf_url=new_class.pdf_url,
                status=new_class.status,
                last_access_class=new_class.last_access_class,
                created_at=new_class.created_at,
                order=new_class.order,
                topics=[ClassTopicResponse.model_validate(ct) for ct in class_topics]
            )


    def _get_next_order(self, group_id: str) -> int:
        # Retorna o próximo valor de ordem para a aula no grupo
        last_class = (
            self.db.query(ClassModel)
            .filter(ClassModel.group_id == group_id)
            .order_by(ClassModel.order.desc())
            .first()
        )
        return (last_class.order + 1) if last_class else 1
