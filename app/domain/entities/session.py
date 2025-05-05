import datetime
from pydantic import BaseModel
from typing import Self, Type

from app.models.models import Session as SessionModel


class Session(BaseModel):
    session_id: str
    user_id: str
    class_id: str
    group_id: str
    created_at: datetime.datetime

    @classmethod
    def from_orm(cls, session: Type[SessionModel]) -> Self:
        return cls(
            session_id=session.session_id,
            user_id=session.user_id,
            class_id=session.class_id,
            group_id=session.group_id,
            created_at=session.created_at
        )

    def to_orm(self) -> SessionModel:
        return SessionModel(
            session_id=self.session_id,
            user_id=self.user_id,
            class_id=self.class_id,
            group_id=self.group_id,
            created_at=self.created_at
        )

    def to_dict(self, exclude=None) -> dict:
        if exclude is None:
            exclude = []

        session = {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "class_id": self.class_id,
            "group_id": self.group_id,
            "created_at": self.created_at
        }

        for key in exclude:
            session.pop(key, None)

        return session
