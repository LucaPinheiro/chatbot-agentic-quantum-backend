from abc import ABC, abstractmethod
from typing import Dict, List, Union

from app.schemas.get_all_progress_class import GetAllProgressClassResponse

class IClassTopicsRepository(ABC):
    @abstractmethod
    def get_class_progress_percentual_by_class(self, class_id: str, user_id: str) -> Dict:
        pass
    @abstractmethod
    def delete_topics_by_id(self, class_topics_id: Union[str, List[str]], class_id: Union[str, List[str]], topic: Union[str, List[str]]) -> Dict:
        """
        Deleta os tópicos de uma aula
        """
        pass
    @abstractmethod
    def add_topics_to_class(self, title: str, topics: List[str]) -> Dict:
        """
        Adiciona tópicos a uma aula
        """
        pass
    @abstractmethod
    def get_all_progress_class(self, title: str, group_id: str) -> GetAllProgressClassResponse:
        """
        Retorna o progresso de uma aula para um grupo específico
        """
        pass
    @abstractmethod
    def get_progress_percentual_by_group(self, name: str) -> Dict:
        """
        Retorna o progresso percentual de grupo
        """
        pass