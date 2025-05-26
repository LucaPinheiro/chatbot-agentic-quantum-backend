from fastapi import APIRouter, Body, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.group_repository import IGroupRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.add_user_group import AddUserGroupRequest, AddUserGroupResponse
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    group_repo: IGroupRepository

    def __init__(self):
        self.repository = Repository(group_repo=True)
        self.group_repo = self.repository.group_repo

    def execute(self, schema: AddUserGroupRequest) -> AddUserGroupResponse:
        new_enrollment = self.group_repo.add_user_group(user_id=schema.user_id, group_id=schema.group_id)
        return new_enrollment


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: AddUserGroupRequest) -> AddUserGroupResponse:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_user_group", response_model=AddUserGroupResponse)
async def add_user_group(
    request: AddUserGroupRequest = Body(...),
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN | PermissionLevelEnum.PROFESSOR))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request=request)