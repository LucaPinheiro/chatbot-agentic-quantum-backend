from typing import Self, Type
from pydantic import BaseModel
from app.models.models import Group, GroupEnrollment, TopicProgress


class TopicProgress(BaseModel):
    topic_progress_id: str
    class_topics_id: str
    user_id: str
    flag: bool
    @classmethod
    def from_orm(cls, topics_progress: Type[TopicProgress]) -> Self:
        return cls(
            topic_progress_id = topics_progress.topic_progress_id,
            class_topics_id = topics_progress.class_topics_id, 
            user_id = topics_progress.user_id,
            flag = topics_progress.flag
        )
    
    def to_orm(self) -> TopicProgress:
        return TopicProgress(
            topic_progress_id = self.topic_progress_id,
            class_topics_id = self.class_topics_id, 
            user_id = self.user_id,
            flag = self.flag
        )
    
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []
            
            topic_progress = {
                "topic_progress_id": self.topic_progress_id,
                "class_topics_id": self.class_topics_id, 
                "user_id": self.user_id,
                "flag": self.flag
            }
            
            for key in exclude:
                if key in topic_progress:
                    del topic_progress[key]
                
            return topic_progress
        
    