from typing import Self, Type
from pydantic import BaseModel

from app.models.models import ClassTopic


class ClassTopics(BaseModel):
    class_topics_id: str
    topic: str
    flag: bool
    class_id: str
    user_id: str
    @classmethod
    def from_orm(cls, class_topics: Type[ClassTopic]) -> Self:
        return cls(
            class_topics_id=class_topics.class_topics_id,
            topic=class_topics.topic,
            flag=class_topics.flag,
            class_id=class_topics.class_id,
            user_id=class_topics.user_id
        )
    def to_orm(self) -> ClassTopic:
        return ClassTopic(
            class_topics_id=self.class_topics_id,
            topic=self.topic,
            flag=self.flag,
            class_id=self.class_id,
            user_id=self.user_id
        )
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []

        class_topics = {
            "class_topics_id": self.class_topics_id,
            "topic": self.topic,
            "flag": self.flag,
            "class_id": self.class_id,
            "user_id": self.user_id
        }

        for key in exclude:
            class_topics.pop(key, None)
            
        return class_topics