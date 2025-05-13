from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from app.domain.interfaces.chat_repository import IChatRepository
from app.domain.interfaces.class_topics_repository import IClassTopicsRepository
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.file_repository import IFileRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.session_repository import ISessionRepository
from app.domain.interfaces.user_repository import IUserRepository

from app.core.settings import load_settings, StageEnum
from app.helpers.exceptions.exceptions import DatabaseException
from app.infra.external.aws import DynamoConfig, DynamoDBResources
from app.infra.mocks.user_repository_mock import UserRepoMock
from app.infra.repositories.chat_repository_dynamo import ChatRepositoryDynamo
from app.infra.repositories.class_topics_repository_postgres import ClassTopicsRepositoryPostgres
from app.infra.repositories.classes_repository_postgres import ClassesRepositoryPostgres
from app.infra.repositories.file_repository_s3 import FileRepositoryS3
from app.infra.repositories.group_repository_postgres import GroupRepositoryPostgres
from app.infra.repositories.session_repository_postgres import SessionRepositoryPostgres
from app.infra.repositories.user_repository_postgres import UserRepositoryPostgres

settings = load_settings()


class Repository:
    user_repo: IUserRepository
    file_repo: IFileRepository
    session_repo: ISessionRepository
    chat_repo: IChatRepository
    classes_repo: IClassesRepository
    class_topics_repo: IClassTopicsRepository
    group_repo: IGroupRepository

    def __init__(self, user_repo: bool = False, file_repo: bool = False, session_repo: bool = False, chat_repo: bool = False, classes_repo: bool = False, class_topics_repo: bool = False, group_repo: bool = False):
        self.session = None

        if settings.stage == StageEnum.test:
            self._initialize_mock_repositories(user_repo)
        else:
            self._initialize_real_repositories(user_repo, file_repo, session_repo, chat_repo, classes_repo, class_topics_repo, group_repo)

    def _initialize_mock_repositories(self, user_repo):
        if user_repo:
            self.user_repo = UserRepoMock()

    def _initialize_real_repositories(self, user_repo, file_repo, session_repo, chat_repo, classes_repo, class_topics_repo, group_repo):
        self.session = self.__connect_db()
        
        if classes_repo:
            self.classes_repo = ClassesRepositoryPostgres(self.session)

        if user_repo:
            self.user_repo = UserRepositoryPostgres(self.session)

        if file_repo:
            self.file_repo = FileRepositoryS3(settings.s3_bucket)
            
        if session_repo:
            self.session_repo = SessionRepositoryPostgres(self.session)
        
        if class_topics_repo:
            self.class_topics_repo = ClassTopicsRepositoryPostgres(self.session)
        
        if group_repo:
            self.group_repo = GroupRepositoryPostgres(self.session)
            
        if chat_repo:
            dynamo_config = DynamoConfig(table_name=settings.dynamodb_table_messages)
            dynamo = DynamoDBResources(dynamo_config)
            self.chat_repo = ChatRepositoryDynamo(dynamo)
            

    def close_session(self):
        if self.session:
            self.session.close()
            self.session = None

    @staticmethod
    def __connect_db() -> Session:
        print(f"Connecting to DB at: {settings.postgres_url}")
        if not settings.postgres_url or settings.postgres_url == "not_set":
            raise DatabaseException("POSTGRES_URL is not set or is empty.")

        try:
            engine = create_engine(settings.postgres_url, poolclass=NullPool)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            return SessionLocal()
        except (SQLAlchemyError, Exception) as error:
            raise DatabaseException(f"Database connection error: {error}")

    def __del__(self):
        self.close_session()

    def test_connection(self):
        return self.__connect_db()


if __name__ == "__main__":
    import os
    print(f"STAGE: {os.getenv('stage')}")
    print(f"POSTGRES_URL: {settings.postgres_url}")
    print(f"SECRET_KEY: {settings.secret_key}")

    try:
        repo = Repository(user_repo=True)
        print(repo.test_connection())
    except Exception as e:
        print(e)