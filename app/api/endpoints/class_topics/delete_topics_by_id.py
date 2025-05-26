from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.class_topics_repository import IClassTopicsRepository
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.delete_class import DeleteClassRequest, DeleteClassResponse
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.delete_topics_by_id import DeleteTopicsByIdRequest, DeleteTopicsByIdResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    class_topics_repo: IClassTopicsRepository

    def __init__(self):
        self.repository = Repository(class_topics_repo=True)
        self.class_topics_repo = self.repository.class_topics_repo

    def execute(self, schema: DeleteTopicsByIdRequest) -> DeleteTopicsByIdResponse:
        class_topics = self.class_topics_repo.delete_topics_by_id(class_topics_id=schema.class_topics_id,
                                                                  class_id=schema.class_id,
                                                                  topic=schema.topic)
        return class_topics
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: DeleteTopicsByIdRequest) -> DeleteTopicsByIdResponse:
        
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_topic", response_model=DeleteTopicsByIdResponse)
async def delete_topics_by_id(
    class_topics_id: str,
    class_id: str,
    topic: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request=DeleteTopicsByIdRequest(class_topics_id=class_topics_id,
                                                              class_id=class_id,
                                                              topic=topic))