from typing import List

from sqlalchemy import Integer, and_, case, func
from app.domain.entities.topics_progress import TopicProgress
from app.models.models import ClassModel, ClassTopic, TopicProgress as TopicProgressORM
from app.models.models import TopicProgress as TopicProgressORM


class TopicProgressRepositoryPostgres:
    
    def __init__(self, db):
        self.db = db
        
    def create_topic_progress(self, topic_progress: List[TopicProgress]) -> None:
        orm_objects = [topic.to_orm() for topic in topic_progress]
        self.db.add_all(orm_objects)  
        self.db.commit()    

    def add_topic_progress(self, entries: List[TopicProgress]) -> None:
      self.db.add_all(entries)
      self.db.commit()             


    def get_progress_by_group_and_user(self, group_id: str, user_id: str):
        print('Executando a consulta de progresso...') # Debug
        return self.db.query(
            ClassModel.class_id,
            ClassModel.title,
            func.count(ClassTopic.class_topics_id).label('total_topics'),
            
            func.coalesce(
                func.sum(
                    case(
                        # Alteração aqui: usando .is_(True) que é mais robusto
                        (TopicProgressORM.flag.is_(True), 1), 
                        else_=0
                    )
                ), 0
            ).label('completed_topics') # Alteração aqui: renomeando o alias
        ).select_from(ClassModel).join(
            ClassTopic, ClassModel.class_id == ClassTopic.class_id, isouter=True
        ).join(
            TopicProgressORM,
            and_(
                TopicProgressORM.class_topics_id == ClassTopic.class_topics_id,
                TopicProgressORM.user_id == user_id
            ),
            isouter=True
        ).filter(
            ClassModel.group_id == group_id
        ).group_by(
            ClassModel.class_id,
            ClassModel.title
        ).order_by(
            ClassModel.order
        ).all()