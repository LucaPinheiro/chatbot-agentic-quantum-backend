from abc import ABC, abstractmethod

from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> User:
        pass

    @abstractmethod
    def create_user(self, user: User) -> User:
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> User:
        pass
