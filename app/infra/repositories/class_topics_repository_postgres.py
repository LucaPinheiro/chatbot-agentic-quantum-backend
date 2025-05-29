from typing import List, Union
import uuid
from fastapi import HTTPException
from sqlalchemy import func
from app.models.models import ClassModel, ClassTopic, Group, GroupEnrollment, TopicProgress
from app.helpers.exceptions.exceptions import NotFoundException
from app.schemas.add_topics_to_class import AddTopicsToClassResponse
from app.schemas.get_all_progress_class import GetAllProgressClassResponse
from app.schemas.get_class_progress_percentual_by_class import GetClassProgressPercentualByClassResponse
from app.schemas.get_progress_percentual_by_group import GetProgressPercentualByGroupResponse

class ClassTopicsRepositoryPostgres:
    def __init__(self, db):
        self.db = db


    def get_progress_percentual_by_class(self, class_id: str, user_id: str) -> GetClassProgressPercentualByClassResponse:
        # 1. Verifica se existe o class_id na tabela class_topics
        class_topics = self.db.query(ClassTopic).filter(ClassTopic.class_id == class_id).all()
        
        if not class_topics:
            raise HTTPException(status_code=404, detail="Class ID não encontrado na tabela class_topics")
        
        # 2. Extrai os class_topics_id
        class_topics_ids = [ct.class_topics_id for ct in class_topics]
        
        # 3. Busca os registros na tabela topic_progress
        topic_progress_list = self.db.query(TopicProgress).filter(
            TopicProgress.class_topics_id.in_(class_topics_ids),
            TopicProgress.user_id == user_id
        ).all()
        
        # 4. Total de tópicos
        total = len(topic_progress_list)
        
        if total == 0:
            # Para evitar divisão por zero
            percentual = 0
            done = 0
        else:
            # 5. Conta os que estão com flag=True
            done = sum(1 for tp in topic_progress_list if tp.flag is True)
            
            # 6. Calcula percentual
            percentual = (done / total) * 100
        
        # 7. Retorna o schema de resposta
        return GetClassProgressPercentualByClassResponse(
            class_id=class_id,
            user_id=user_id,
            class_progress_percentual=f"{percentual:.2f}%",
            total=total,
            done=done
        )

    
    def delete_topics_by_id(
        self,
        class_topics_id: Union[str, List[str]],
        class_id: Union[str, List[str]],
        topic: Union[str, List[str]]
    ):
        filters = []

        # class_topics_id
        if isinstance(class_topics_id, list):
            filters.append(ClassTopic.class_topics_id.in_(class_topics_id))
        else:
            filters.append(ClassTopic.class_topics_id == class_topics_id)

        # class_id
        if isinstance(class_id, list):
            filters.append(ClassTopic.class_id.in_(class_id))
        else:
            filters.append(ClassTopic.class_id == class_id)

        # topic
        if isinstance(topic, list):
            filters.append(ClassTopic.topic.in_(topic))
        else:
            filters.append(ClassTopic.topic == topic)

        class_topic = self.db.query(ClassTopic).filter(*filters).first()

        if not class_topic:
            raise NotFoundException("Tópico não encontrado")

        self.db.delete(class_topic)
        self.db.commit()

        return {"message": "Tópico deletado com sucesso"}
    
    
    def add_topics_to_class(
        self,
        title: str,
        topics: List[str],
        user_id: str
    ):
        existing_class = self.db.query(ClassModel).filter(ClassModel.title == title).first()

        if not existing_class:
            raise NotFoundException("Aula não encontrada")

        class_id = existing_class.class_id
        group_id = existing_class.group_id

        group_users = (
            self.db.query(GroupEnrollment)
            .filter(GroupEnrollment.group_id == group_id)
            .all()
        )

        if not group_users:
            raise NotFoundException("Nenhum usuário encontrado para o grupo da aula.")

        # ✅ Verificar previamente se já existem tópicos com mesmo nome
        existing_topics = (
            self.db.query(ClassTopic)
            .filter(ClassTopic.class_id == class_id, ClassTopic.topic.in_(topics))
            .all()
        )

        if existing_topics:
            existing_topic_names = [et.topic for et in existing_topics]
            raise NotFoundException(
                f"Os seguintes tópicos já existem nesta aula: {existing_topic_names}"
            )

        added_topics = []

        for topic in topics:
            new_topic = ClassTopic(
                class_topics_id=str(uuid.uuid4()),
                class_id=class_id,
                topic=topic,
                user_id=user_id
            )
            self.db.add(new_topic)
            added_topics.append(topic)

            for group_user in group_users:
                new_progress = TopicProgress(
                    topic_progress_id=str(uuid.uuid4()),
                    class_topics_id=new_topic.class_topics_id,
                    user_id=group_user.student_id,
                    flag=False
                )
                self.db.add(new_progress)

        self.db.commit()

        return AddTopicsToClassResponse(
            message="Tópicos adicionados com sucesso.",
            title=title,
            topics=added_topics
        )
    
    def get_all_progress_class(self, title: str, group_id: str) -> GetAllProgressClassResponse:
        # 1. Busca a aula
        class_model = self.db.query(ClassModel).filter(
            ClassModel.title == title,
            ClassModel.group_id == group_id
        ).first()

        if not class_model:
            raise NotFoundException("Aula não encontrada")

        class_id = class_model.class_id

        # 2. Busca tópicos
        topics = self.db.query(ClassTopic).filter(ClassTopic.class_id == class_id).all()
        if not topics:
            raise NotFoundException("Nenhum tópico encontrado para esta aula")

        topic_ids = [topic.class_topics_id for topic in topics]

        # 3. Busca progresso dos tópicos
        all_progress = self.db.query(TopicProgress).filter(
            TopicProgress.class_topics_id.in_(topic_ids)
        ).all()

        if not all_progress:
            raise NotFoundException("Nenhum progresso encontrado para os tópicos desta aula")

        total_flags = len(all_progress)  # total esperado (total de tópicos * total de alunos)
        done_flags = sum(1 for p in all_progress if p.flag)

        percentage = (done_flags / total_flags) * 100 if total_flags > 0 else 0

        return GetAllProgressClassResponse(
            message="Progresso geral da aula recuperado com sucesso.",
            title=title,
            progress=f"{round(percentage, 2)}%",
            total=total_flags,
            done=done_flags
        )
        


    def get_progress_percentual_by_group(self, name: str) -> GetProgressPercentualByGroupResponse:
        # 1. Buscar o grupo pelo nome
        group = self.db.query(Group).filter(Group.name == name).first()

        if not group:
            raise NotFoundException("Grupo não encontrado")

        group_id = group.group_id

        # 2. Buscar todas as aulas (classes) associadas ao group_id
        classes = self.db.query(ClassModel).filter(ClassModel.group_id == group_id).all()

        if not classes:
            raise NotFoundException("Nenhuma aula encontrada para este grupo")

        total_flags = 0
        done_flags = 0

        # 3. Para cada aula, buscar tópicos e progresso
        for class_model in classes:
            class_id = class_model.class_id

            # Buscar tópicos da aula
            topics = self.db.query(ClassTopic).filter(ClassTopic.class_id == class_id).all()

            if not topics:
                continue  # Se a aula não tiver tópicos, pula para a próxima

            topic_ids = [topic.class_topics_id for topic in topics]

            # Buscar progresso dos tópicos
            all_progress = self.db.query(TopicProgress).filter(
                TopicProgress.class_topics_id.in_(topic_ids)
            ).all()

            # Acumular total e feitos
            total_flags += len(all_progress)
            done_flags += sum(1 for p in all_progress if p.flag)

        # 4. Calcular porcentagem
        percentage = (done_flags / total_flags) * 100 if total_flags > 0 else 0

        # 5. Retornar resposta
        return GetProgressPercentualByGroupResponse(
            name=name,
            group_progress_percentual=f"{round(percentage, 2)}%",
            total=total_flags,
            done=done_flags
        )






