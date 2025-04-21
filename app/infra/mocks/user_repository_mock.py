

from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.utils.encrypt import Encrypt


class UserRepoMock(IUserRepository):
    def __init__(self):
        self.users = [
            User(
                id="1",
                name='Luca Pinheiro',
                email='lucapgomes11@gmail.com',
                password=Encrypt.hash_password('123456')
            ),
            User(
                id="2",
                name='Yuri Drapack',
                email='yuridrapack@gmail.com',
                password=Encrypt.hash_password('123456')
            )   
        ]
        
    def create_user(self, user: User) -> None:
        print('chegou aqui no create_user do mock') 
        print("user no db mock", user)
        self.users.append(user)
        
    def get_user_by_id(self, user_id) -> User:
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> User:
        for user in self.users:
            if user.email == email:
                return user
        return None
        