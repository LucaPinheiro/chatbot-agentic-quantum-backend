from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.session import Session


class ISessionRepository(ABC):

    @abstractmethod
    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        """Retrieve session details by session ID."""
        pass

    @abstractmethod
    def get_all_sessions(self) -> Optional[List[Session]]:
        """List all sessions for a given user ID."""
        pass
    
    @abstractmethod
    def create_sessions(self, sessions: List[Session]) -> None:
        """Create a new session in the database."""
        pass