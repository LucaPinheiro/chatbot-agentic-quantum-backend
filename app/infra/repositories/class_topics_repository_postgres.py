from typing import List, Union
from sqlalchemy import func
from app.domain.entities.class_topics import ClassTopics as ClassTopicsEntity
from app.models.models import ClassTopic, TopicProgress
from app.helpers.exceptions.exceptions import NotFoundException

class ClassTopicsRepositoryPostgres:
    def __init__(self, db):
        self.db = db

    def get_class_progress_percentual_by_class(self, class_id: str, user_id: str):
        print(f"Class ID: {class_id}")

        # Pega todos os IDs dos tópicos dessa aula
        class_topic_id = self.db.query(ClassTopic.class_topics_id).filter(
            ClassTopic.class_id == class_id
        ).all()

        class_topic_id = [ct[0] for ct in class_topic_id]

        total = len(class_topic_id)

        print(f"Total Class Topics: {total}")

        if total == 0:
            raise NotFoundException("Nenhum tópico encontrado para esta aula.")

        # Conta quantos desses tópicos foram concluídos
        done = self.db.query(func.count(TopicProgress.class_topics_id)).filter(
            TopicProgress.class_topics_id.in_(class_topic_id),
            TopicProgress.user_id == user_id,
            TopicProgress.flag == True
        ).scalar()

        percentual = int((done / total) * 100)

        return {
            "class_id": class_id,
            "class_progress_percentual": f"{percentual}%",
            "total": total,
            "done": done,
        }
    
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

        return {"message": "Tópico deletado com sucesso"}\
            
    def create_class_topics(self, topics: List[ClassTopicsEntity]) -> None:
        orm_objects = [topic.to_orm() for topic in topics]
        self.db.add_all(orm_objects)
        self.db.commit()

