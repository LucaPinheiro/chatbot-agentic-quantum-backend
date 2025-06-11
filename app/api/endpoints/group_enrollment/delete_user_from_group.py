from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.class_topics_repository import IClassTopicsRepository
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_enrollment_repository import IGroupEnrollmentRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.delete_class import DeleteClassRequest, DeleteClassResponse
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.delete_topics_by_id import DeleteTopicsByIdRequest, DeleteTopicsByIdResponse
from app.schemas.delete_user_from_group import DeleteUserFromGroupRequest, DeleteUserFromGroupResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    group_enrollment_repo: IGroupEnrollmentRepository

    def __init__(self):
        self.repository = Repository(group_enrollment_repo=True)
        self.group_enrollment_repo = self.repository.group_enrollment_repo

    def execute(self, schema: DeleteUserFromGroupRequest) -> DeleteUserFromGroupResponse:
        user = self.group_enrollment_repo.delete_user_from_group(user_id=schema.user_id)
        if not user:
            raise NotFoundException(message="User not found in the group")
        return {"message": "User removed from group successfully"}
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: DeleteUserFromGroupRequest) -> DeleteUserFromGroupResponse:
        
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_user_from_group", response_model=DeleteUserFromGroupResponse)
async def delete_user_from_group(
    user_id: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.PROFESSOR))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request=DeleteUserFromGroupRequest(user_id=user_id))