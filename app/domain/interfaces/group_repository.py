from abc import abstractmethod
from app.models.models import Group


class IGroupRepository:
    @abstractmethod
    def delete_group(self, name: str) -> object:
        pass
    
    @abstractmethod
    def create_group(self, group: Group) -> Group:
        pass
    
    @abstractmethod
    def is_manager_group(self, group_id: str, user_id: str) -> bool:
        """
        Verifica se o usuário (professor ou admin) é o gerente do grupo
        """
        pass