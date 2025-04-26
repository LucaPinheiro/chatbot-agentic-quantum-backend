from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.models.models import User as UserModel
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

    def get_user_by_id(self, user_id: str) -> User:
        user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        if not user:
            raise NotFoundException("Usuário não encontrado pelo ID")
        return User.from_orm(user)

    def get_user_by_email(self, email: str) -> User:
        user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            raise NotFoundException("Usuário não encontrado pelo email")
        return User.from_orm(user)
