from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.entities.class_topics import ClassTopics
from app.domain.interfaces.class_topics_repository import IClassTopicsRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.topic_progress_repository import ITopicProgressRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException, UnauthorizedException
from app.infra.repository import Repository
from app.models.models import TopicProgress
from app.schemas.add_topics_to_class import AddTopicsToClassRequest, AddTopicsToClassResponse
from app.schemas.add_user_group import AddUserGroupRequest, AddUserGroupResponse
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    class_topics_repo: IClassTopicsRepository
    classes_repo: IClassTopicsRepository
    topic_progress_repo: ITopicProgressRepository
    user_repo: IUserRepository

    def __init__(self):
        self.repository = Repository(class_topics_repo=True, classes_repo=True, topic_progress_repo=True, user_repo=True)
        self.user_repo = self.repository.user_repo
        self.topic_progress_repo = self.repository.topic_progress_repo
        self.classes_repo = self.repository.classes_repo
        self.class_topics_repo = self.repository.class_topics_repo

    def execute(self, schema: AddTopicsToClassRequest, user_id: TokenUser) -> AddTopicsToClassResponse:
        # 1. Verificar se a aula com o título existe
        class_ = self.classes_repo.get_class_by_class_id(schema.class_id)
        if not class_:
            raise NotFoundException(message=f"Aula não encontrada.")

        class_id = class_.class_id
        group_id = class_.group_id

        # 2. Buscar os tópicos existentes dessa aula
        existing_topics = self.class_topics_repo.get_topics_by_class_id(class_id)
        existing_topic_names = {topic.topic.lower() for topic in existing_topics}

        # 3. Verificar se há tópicos repetidos
        duplicates = [t.topic for t in schema.topics if t.topic.lower() in existing_topic_names]
        if duplicates:
            raise UnauthorizedException(message=f"Tópicos já existentes na aula: {', '.join(duplicates)}")

        # 4. Criar entidades com UUID e inserir no banco
        topic_entities = [
            ClassTopics(
                class_topics_id=str(uuid4()),
                class_id=class_id,
                topic=item.topic,
                pdf_url=str(item.pdf_url),
                user_id=user_id.id
            )
            for item in schema.topics
        ]

        self.class_topics_repo.add_topics_to_class(topics=topic_entities)
        
        user_ids = self.repository.user_repo.get_user_ids_by_group_id(group_id)

        topic_progress_entries = []
        for topic in topic_entities:
            for uid in user_ids:
                entry = TopicProgress(
                    topic_progress_id=str(uuid4()),
                    class_topics_id=topic.class_topics_id,
                    user_id=uid,
                    flag=False
                )
                topic_progress_entries.append(entry)

        # Inserir todos em topic_progress
        self.repository.topic_progress_repo.add_topic_progress(entries=topic_progress_entries)

        return AddTopicsToClassResponse(
            message="Tópicos adicionados com sucesso.",
            class_id=schema.class_id,
            topics=schema.topics
        )


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: AddTopicsToClassRequest, user: TokenUser) -> AddTopicsToClassResponse:
        if user.permission < PermissionLevelEnum.PROFESSOR:
            raise UnauthorizedException(message="Usuário não tem permissão para adicionar tópicos a aulas.")
        try:
            return self.use_case.execute(request, user)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))
@router.post("/add_topics", response_model=AddTopicsToClassResponse)
async def add_topics_to_class(
    request: AddTopicsToClassRequest = Body(...),
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.PROFESSOR))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request, user)