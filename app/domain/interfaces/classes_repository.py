from abc import abstractmethod
from typing import List, Optional, Union

from app.domain.entities.classes import ClassModel
from app.schemas.update_class import UpdateClassResponse


class IClassesRepository:
    @abstractmethod
    def get_classes_by_group(self, group_id: str) -> Optional[List[ClassModel]]:
        pass
    @abstractmethod
    def delete_class(self, group_id: str, title: str) -> object:
        pass
    @abstractmethod
    def get_all_classes(self) -> List[ClassModel]:
        pass
    def update_class(self, class_id: str) -> Union[UpdateClassResponse, dict]:
        pass