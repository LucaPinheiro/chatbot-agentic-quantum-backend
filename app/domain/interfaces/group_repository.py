from abc import abstractmethod
from typing import Optional, Union
from app.models.models import Group
from app.schemas.update_group import UpdateGroupResponse


class IGroupRepository:
    @abstractmethod
    def delete_group(self, name: str) -> object:
        pass
    @abstractmethod
    def create_group(self, group: Group) -> Group:
        pass
    @abstractmethod
    def update_group(
        self,
        group_id: str,
        name: Optional[str],
        year_semester: Optional[int],
        status: Optional[bool],
        user_id: Optional[str]
    ) -> Union[UpdateGroupResponse, dict]:
        pass
    @abstractmethod
    def get_group_by_id(self, group_id: str) -> Optional[Group]:
        pass