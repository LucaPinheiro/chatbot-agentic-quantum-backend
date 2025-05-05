from typing import List
from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_all_users import GetAllUsersRequest, GetAllUsersResponse
from app.schemas.token import TokenUser


router = APIRouter()


class UseCase:
    repository: Repository
    user_repo: IUserRepository

    def __init__(self):
        self.repository = Repository(user_repo=True)
        self.user_repo = self.repository.user_repo

    def execute(self, schema: GetAllUsersRequest) -> List[GetAllUsersResponse]:
        users = self.user_repo.get_all_users()
        return [
            GetAllUsersResponse(
                user_id=user.user_id,
                name=user.name,
                email=user.email,
                permission=user.permission
            )
            for user in users
        ]
    
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetAllUsersRequest) -> List[GetAllUsersResponse]:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/users/all", response_model=List[GetAllUsersResponse])
async def get_all_users(
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetAllUsersRequest())