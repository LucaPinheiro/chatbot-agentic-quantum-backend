from pydantic import BaseModel
from typing import Self, Type

from app.models.models import User as UserModel


class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    
    @classmethod
    def from_orm(cls, user: Type[UserModel]) -> Self:
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password
        )
        
    def to_orm(self) -> UserModel:
        return UserModel(
            id=self.id,
            name=self.name,
            email=self.email,
            password=self.password
        )
        
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []
            
            user = {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "password": self.password
            }
            
            for key in exclude:
                del user[key]
                
            return user