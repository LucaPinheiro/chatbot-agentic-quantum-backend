from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import EmailStr

from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def create_user(self, user: User) -> User:
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass
    
    @abstractmethod
    def delete_user(self, user_id: str, name: str):
        pass
    
    @abstractmethod
    def update_user(self, user_id: str, name: Optional[str] = None, email: Optional[EmailStr] = None, password: Optional[str] = None) -> User:
        pass
