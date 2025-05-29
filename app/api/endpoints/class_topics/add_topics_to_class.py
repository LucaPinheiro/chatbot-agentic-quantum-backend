from fastapi import APIRouter, Body, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.class_topics_repository import IClassTopicsRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.add_topics_to_class import AddTopicsToClassRequest, AddTopicsToClassResponse
from app.schemas.add_user_group import AddUserGroupRequest, AddUserGroupResponse
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    class_topics_repo: IClassTopicsRepository

    def __init__(self):
        self.repository = Repository(class_topics_repo=True)
        self.class_topics_repo = self.repository.class_topics_repo

    def execute(self, schema: AddTopicsToClassRequest, user_id: str) -> AddTopicsToClassResponse:
        new_topics = self.class_topics_repo.add_topics_to_class(title=schema.title, topics=schema.topics, user_id=user_id)
        return new_topics


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: AddTopicsToClassRequest, user_id: str) -> AddTopicsToClassResponse:
        try:
            return self.use_case.execute(request, user_id)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))
@router.post("/add_topics", response_model=AddTopicsToClassResponse)
async def add_topics_to_class(
    request: AddTopicsToClassRequest = Body(...),
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN | PermissionLevelEnum.PROFESSOR))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request=request, user_id=token_user.id)