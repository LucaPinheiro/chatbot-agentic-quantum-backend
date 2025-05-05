from abc import abstractmethod
from typing import List, Optional

from app.domain.entities.classes import ClassModel


class IClassesRepository:
    @abstractmethod
    def get_classes_by_group(self, group_id: str) -> Optional[List[ClassModel]]:
        pass