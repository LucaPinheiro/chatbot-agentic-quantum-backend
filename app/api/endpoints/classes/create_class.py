from datetime import datetime
from typing import List
import uuid

from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.entities.class_topics import ClassTopics
from app.domain.entities.classes import ClassModel as ClassEntity
from app.domain.entities.session import Session as SessionEntity
from app.domain.entities.topics_progress import TopicProgress
from app.domain.interfaces.group_enrollment_repository import IGroupEnrollmentRepository
from app.domain.interfaces.topic_progress_repository import ITopicProgressRepository
from app.models.models import ClassModel as ClassORM
from app.domain.interfaces.class_topics_repository import IClassTopicsRepository
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.infra.repository import Repository
from app.schemas.create_class import ClassTopicResponse, CreateClassRequest, CreateClassResponse
from app.helpers.exceptions.exceptions import DatabaseException, UnauthorizedException, DuplicatedException
from app.schemas.token import TokenUser

router = APIRouter()

class UseCase:
    repository: Repository
    classes_repo: IClassesRepository
    user_repo: IUserRepository
    group_repo: IGroupRepository
    class_topics_repo: IClassTopicsRepository
    topic_progress_repo: ITopicProgressRepository
    group_enr_repo: IGroupEnrollmentRepository 
    
    def __init__(self):
        self.repository = Repository(classes_repo=True, user_repo=True, group_repo=True,
                                     class_topics_repo=True, session_repo=True, topic_progress_repo=True,
                                     group_enrollment_repo=True)
        self.group_enr_repo = self.repository.group_enrollment_repo
        self.session_repo = self.repository.session_repo
        self.classes_repo = self.repository.classes_repo
        self.user_repo = self.repository.user_repo
        self.group_repo = self.repository.group_repo
        self.class_topics_repo = self.repository.class_topics_repo
        self.topic_progress_repo = self.repository.topic_progress_repo
        
    def execute(self, schema: CreateClassRequest, user_id: TokenUser) -> CreateClassResponse:
        
        # Validating if the class already exists
        # existing_class = self.classes_repo.get_by_name(schema.name)
        # if existing_class:
        #     raise DuplicatedException("Já existe uma aula com esse nome.")
        
        group = self.group_repo.get_group_by_id(schema.group_id)
        if not group:
            raise UnauthorizedException("Grupo não encontrado.")
        
        manager = self.user_repo.get_user_by_id(user_id)
        
        if not manager:
            raise UnauthorizedException("Usuário não encontrado.")
        
        if group.manager_id != user_id:
            raise UnauthorizedException("Usuário não é o professor do grupo.") # Professor correto esta criando a aula
        
        students_from_group = self.group_enr_repo.get_all_students_by_group_id(schema.group_id)
        
        class_id = uuid.uuid4().hex
        
        new_class = ClassEntity(
            class_id=class_id,
            group_id=schema.group_id,
            manager_id=user_id,
            title=schema.title,
            status=True,
            created_at=datetime.now().isoformat(),
            order=schema.order,
        )
        self.classes_repo.create_class(new_class)
        
        topics_to_save = []
        topics_progress_to_save = []
        sessions_to_save = []
        
        for topic in schema.class_topics:
            topic_id = uuid.uuid4().hex
            saving_topics = ClassTopics(
                class_topics_id=topic_id,
                class_id=class_id,
                user_id=user_id,
                topic=topic.topic, #topic name
                pdf_url=topic.topic_pdf_url,
            )
            topics_to_save.append(saving_topics)
            
            topic_progress = TopicProgress(
                topic_progress_id=uuid.uuid4().hex,
                class_topics_id=topic_id,
                user_id=user_id,
                flag=False
            )
            topics_progress_to_save.append(topic_progress)
            
        if topics_to_save:
            self.class_topics_repo.create_class_topics(topics_to_save)
            
        if topics_progress_to_save:
            self.topic_progress_repo.create_topic_progress(topics_progress_to_save)        
        
        for student_id in students_from_group:
            new_session = SessionEntity(
                session_id=uuid.uuid4().hex,
                user_id=student_id,
                class_id=new_class.class_id,
                group_id=group.group_id,
                created_at=datetime.now().isoformat(),
            )
            sessions_to_save.append(new_session)   
        self.session_repo.create_sessions(sessions_to_save)

        return CreateClassResponse(
            message="Aula criada com sucesso.",
            group_id=new_class.group_id,
            title=new_class.title,
            order=new_class.order,
            class_id=new_class.class_id,
            created_at=new_class.created_at,
            class_topics=[
                ClassTopicResponse(
                    topic=topic.topic,
                    topic_pdf_url=topic.topic_pdf_url
                )
                for topic in schema.class_topics
            ]
        )  


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: CreateClassRequest, user: TokenUser) -> CreateClassResponse:
        if user.permission < PermissionLevelEnum.PROFESSOR:
            raise UnauthorizedException("Somente professores podem criar aulas.")
                                        
        try:
            return self.use_case.execute(request, user_id=user.id)  
        
        except DatabaseException as e:
            raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
        except UnauthorizedException as e:
            raise HTTPException(status_code=401, detail=str(e))
        except DuplicatedException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@router.post("/class", response_model=CreateClassResponse, status_code=201)
def create_class(
    request: CreateClassRequest,
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.PROFESSOR))
):
    try:
        controller = Controller(UseCase())
        return controller.handle(request, user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na rota de criação de aula: {str(e)}")
