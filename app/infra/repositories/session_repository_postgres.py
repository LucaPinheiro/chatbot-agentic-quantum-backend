from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import ISessionRepository
from app.models.models import Session as SessionModel
from app.helpers.exceptions.exceptions import NotFoundException


class SessionRepositoryPostgres(ISessionRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_sessions(self, sessions: List[Session]) -> None:
        print("entrei no create_sessions")
        orm_objects = [session.to_orm() for session in sessions]
        self.db.add_all(orm_objects)
        print("antes do commit")
        self.db.commit()
        print("depois do commit")

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        session = self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not session:
            return None
        return Session.from_orm(session)

    def get_all_sessions(self) -> Optional[List[Session]]:
        session = self.db.query(SessionModel).all()
        if not session:
            return None
        return [Session.from_orm(session) for session in session]
