from sqlalchemy import func
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
