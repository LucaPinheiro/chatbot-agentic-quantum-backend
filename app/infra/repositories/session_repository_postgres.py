from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import ISessionRepository
from app.models.models import Session as SessionModel
from app.helpers.exceptions.exceptions import NotFoundException


class SessionRepositoryPostgres(ISessionRepository):
    def __init__(self, db: Session):
        self.db = db

    # def create_session(self, session: Session) -> Session:
    #     session_orm = session.to_orm()
    #     self.db.add(session_orm)
    #     self.db.commit()
    #     self.db.refresh(session_orm)
    #     return Session.from_orm(session_orm)

    def get_session_by_id(self, session_id: str) -> Optional[Session]:
        session = self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not session:
            return None
        return Session.from_orm(session)

    def get_all_sessions(self) -> Optional[List[Session]]:
        session = self.db.query(SessionModel).all()
        if not session:
            return None
        return [Session.from_orm(session_model) for session_model in session]
