from abc import ABC, abstractmethod
from typing import Dict, List, Union

from app.domain.entities.class_topics import ClassTopics

class IClassTopicsRepository(ABC):
    @abstractmethod
    def get_class_progress_percentual_by_class(self, class_id: str, user_id: str, class_topics_id: str) -> Dict:
        pass
    @abstractmethod
    def delete_topics_by_id(self, class_topics_id: Union[str, List[str]], class_id: Union[str, List[str]], topic: Union[str, List[str]]) -> Dict:
        """
        Deleta os tópicos de uma aula
        """
        pass
    @abstractmethod
    def create_class_topics(self, topics: List[ClassTopics]) -> None:
        """
        Cria um tópico de aula
        """
        pass