from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.delete_user import DeleteUserRequest, DeleteUserResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    user_repo: IUserRepository

    def __init__(self):
        self.repository = Repository(user_repo=True)
        self.user_repo = self.repository.user_repo

    def execute(self, schema: DeleteUserRequest) -> DeleteUserResponse:
        user = self.user_repo.delete_user(user_id=schema.user_id, name=schema.name)
        if not user:
            raise NotFoundException("User not found")
        return user


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: DeleteUserRequest) -> DeleteUserResponse:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_user", response_model=DeleteUserResponse)
async def delete_user(
    user_id: str,
    name: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN | PermissionLevelEnum.PROFESSOR))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request=DeleteUserRequest(user_id=user_id,name=name))