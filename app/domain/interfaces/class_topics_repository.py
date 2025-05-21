from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class IClassTopicsRepository(ABC):
    @abstractmethod
    def get_class_progress_percentual_by_class(self, class_id: str, user_id: str, class_topics_id: str) -> Dict:
        pass
    
    @abstractmethod
    def get_all_topics_by_class(self, class_id: str) -> Optional[List[Dict[str, str]]]:
        pass
