from abc import abstractmethod
from typing import List, Optional, Union
from app.models.models import Group
from app.schemas.add_user_group import AddUserGroupResponse
from app.schemas.update_group import UpdateGroupResponse


class IGroupRepository:
    @abstractmethod
    def delete_group(self, group_id: str, name: str) -> object:
        pass
    
    @abstractmethod
    def create_group(self, group: Group, user_ids: Optional[List[str]] = None) -> Group:
        pass
    @abstractmethod
    def update_group(
        self,
        group_id: str,
        name: Optional[str],
        year_semester: Optional[int],
        status: Optional[bool],
        manager_id: Optional[str],
        user_ids: Optional[List[str]] = None
    ) -> Union[UpdateGroupResponse, dict]:
        pass
    @abstractmethod
    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        pass
    @abstractmethod
    def is_manager_group(self, group_id: str, user_id: str) -> bool:
        """
        Verifica se o usuário (professor ou admin) é o gerente do grupo
        """ 
        pass
    @abstractmethod
    def add_user_group(self, user_id: str, group_id: str) -> AddUserGroupResponse:
        """
        Adiciona um usuário a um grupo
        """
        pass
    @abstractmethod
    def get_all_groups(self) -> List[Group]:
        """
        Retorna todos os grupos
        """
        pass