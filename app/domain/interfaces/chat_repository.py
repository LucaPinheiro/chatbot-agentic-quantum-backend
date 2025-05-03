from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.chat_message import ChatMessage

class IChatRepository(ABC):
    @abstractmethod
    def save_message(self, message: ChatMessage) -> None:
        pass

    @abstractmethod
    def get_session_message_history(self, session_id: str) -> List[ChatMessage]:
        pass

    @abstractmethod
    def save_summary(self, session_id: str, summary: str) -> None:
        pass

    @abstractmethod
    def get_summary(self, session_id: str) -> Optional[str]:
        pass
