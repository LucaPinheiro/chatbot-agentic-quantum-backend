from abc import abstractmethod
from app.models.models import Group


class IGroupRepository:
    @abstractmethod
    def delete_group(self, name: str) -> object:
        pass
    @abstractmethod
    def create_group(self, group: Group) -> Group:
        pass