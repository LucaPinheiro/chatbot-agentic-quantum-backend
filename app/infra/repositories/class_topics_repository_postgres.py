from sqlalchemy import func
from app.models.models import ClassTopic
from app.helpers.exceptions.exceptions import NotFoundException

class ClassTopicsRepositoryPostgres:
    def __init__(self, db):
        self.db = db

    def get_class_progress_percentual_by_class(self, class_id: str, user_id: str):
        print(f"Class ID: {class_id}")
        total = self.db.query(func.count(ClassTopic.class_topics_id)).filter(
            ClassTopic.class_id == class_id,
            ClassTopic.user_id == user_id,
        ).scalar()

        print(f"Total Class Topics: {total}")

        done = self.db.query(func.count(ClassTopic.class_topics_id)).filter(
            ClassTopic.class_id == class_id,
            ClassTopic.user_id == user_id,
            ClassTopic.flag == True
        ).scalar()

        if total == 0:
            raise NotFoundException("Nenhum tópico encontrado para esta aula.")

        percentual = int((done / total) * 100)

        return {
            "class_id": class_id,
            "progress_percentual": f"{percentual}%",
            "total": total,
            "done": done,
        }
