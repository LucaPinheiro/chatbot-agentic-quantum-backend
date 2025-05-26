from typing import List
from typing import Optional
from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.models.models import TopicProgress, User as UserModel
from app.helpers.exceptions.exceptions import NotFoundException


class UserRepositoryPostgres(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: User) -> User:
        user_orm = user.to_orm()
        self.db.add(user_orm)
        self.db.commit()
        self.db.refresh(user_orm)
        return User.from_orm(user_orm)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not user:
            return None
        return User.from_orm(user)
    def get_users_by_ids(self, user_ids: List[str]) -> Optional[List[User]]:
        users = self.db.query(UserModel).filter(UserModel.user_id.in_(user_ids)).all()
        if not users:
            return None
        return [User.from_orm(user) for user in users]


    def get_user_by_email(self, email: str) -> Optional[User]:
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
        return User.from_orm(user)

    def get_all_users(self) -> List[User]:
        users = self.db.query(UserModel).all()
        return [User.from_orm(user) for user in users]
    
    def delete_user(self, user_id: str, name: str):
        user = self.db.query(UserModel).filter(UserModel.user_id == user_id, UserModel.name == name).first()
        if not user:
            raise NotFoundException("User not found")

        self.db.delete(user)
        self.db.commit()

        return {"message": "User deleted successfully"}

