from abc import abstractmethod
from typing import List, Optional, Union

from app.domain.entities.classes import ClassModel
from app.schemas.create_class import ClassTopicInput, CreateClassResponse
from app.schemas.update_class import UpdateClassResponse


class IClassesRepository:
    @abstractmethod
    def get_classes_by_group(self, group_id: str) -> Optional[List[ClassModel]]:
        pass
    @abstractmethod
    def delete_class(self, class_id: str, title: str) -> object:
        pass
    @abstractmethod
    def get_all_classes(self) -> List[ClassModel]:
        pass
    # @abstractmethod
    # def update_class(self,
    #                  class_id: str,
    #                  group_id: Optional[str],
    #                  title: Optional[str],
    #                  pdf_url: Optional[str],
    #                  status: Optional[bool],
    #                  order: Optional[int]) -> Union[UpdateClassResponse, dict]:
    #     pass
    @abstractmethod
    def create_class(_class: ClassModel) -> None:
        pass
