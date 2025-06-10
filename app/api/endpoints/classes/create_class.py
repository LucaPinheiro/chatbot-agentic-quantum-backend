from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.entities.class_topics import ClassTopics
from app.domain.entities.classes import ClassModel as ClassEntity
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
    
    
    def __init__(self):
        self.repository = Repository(classes_repo=True, user_repo=True, group_repo=True, class_topics_repo=True)
        self.classes_repo = self.repository.classes_repo
        self.user_repo = self.repository.user_repo
        self.group_repo = self.repository.group_repo
        self.class_topics_repo = self.repository.class_topics_repo
        
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
            raise UnauthorizedException("Usuário não é o professor do grupo.")
        
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
        
        for topic in schema.class_topics:
            topic_id = uuid.uuid4().hex
            saving_topics = ClassTopics(
                class_topics_id=topic_id,
                class_id=class_id,
                user_id=user_id,
                topic=topic.topic,
                pdf_url=topic.topic_pdf_url,
            )
            self.class_topics_repo.create_class_topic(saving_topics)




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
