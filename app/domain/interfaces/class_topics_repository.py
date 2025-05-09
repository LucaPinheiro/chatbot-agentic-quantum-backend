from abc import abstractmethod

from app.models.models import ClassTopic


class IClassTopicsRepository:
    @abstractmethod
    def get_class_progress_percentual_by_class(self, class_id: str, user_id: str) -> ClassTopic:
        pass