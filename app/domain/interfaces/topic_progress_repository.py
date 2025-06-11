from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.topics_progress import TopicProgress


class ITopicProgressRepository(ABC):

    @abstractmethod
    def create_topic_progress(self, topic_progress: List[TopicProgress]) -> None:
        """Create class topics in the database."""
        pass