import datetime
from pydantic import BaseModel
from typing import Self, Type

from app.helpers.enums.enums import PermissionLevelEnum
from app.models.models import User as UserModel


class User(BaseModel):
    id: str
    name: str
    email: str
    password: str
    created_at: datetime.datetime
    permission: PermissionLevelEnum 
    @classmethod
    def from_orm(cls, user: Type[UserModel]) -> Self:
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            created_at=user.created_at,
            permission=user.permission
        )
        
    def to_orm(self) -> UserModel:
        return UserModel(
            id=self.id,
            name=self.name,
            email=self.email,
            password=self.password,
            created_at=self.created_at,
            permission=self.permission
        )
        
    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []
            
            user = {
                "id": self.id,
                "name": self.name,
                "email": self.email,
                "password": self.password,
                "created_at": self.created_at,
                "permission": self.permission
            }
            
            for key in exclude:
                del user[key]
                
            return user