from typing import Optional
from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.models.models import User as UserModel


class UserRepositoryPostgres(IUserRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def create_user(self, user: User) -> None:
        user_orm = user.to_orm()
        self.db.add(user_orm)
        self.db.commit()
        self.db.refresh(user_orm)
        return User.from_orm(user_orm)
        
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        user = self.db.query(User).filter(User.user_id == user_id).first()
        return User.from_orm(user) if user else None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return User.from_orm(user) if user else None
