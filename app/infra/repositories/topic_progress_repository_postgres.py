from typing import List
from app.domain.entities.topics_progress import TopicProgress


class TopicProgressRepositoryPostgres:
    
    def __init__(self, db):
        self.db = db
        
    def create_topic_progress(self, topic_progress: List[TopicProgress]) -> None:
        orm_objects = [topic.to_orm() for topic in topic_progress]
        self.db.add_all(orm_objects)  
        self.db.commit()               


    