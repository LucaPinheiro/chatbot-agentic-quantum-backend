from abc import ABC, abstractmethod
from typing import Dict

class IClassTopicsRepository(ABC):
    @abstractmethod
    def get_class_progress_percentual_by_class(self, class_id: str, user_id: str, class_topics_id: str) -> Dict:
        pass
