from typing import List
from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_all_classes import GetAllClassesRequest, GetAllClassesResponse
from app.schemas.get_all_groups import GetAllGroupsRequest, GetAllGroupsResponse
from app.schemas.get_all_users import GetAllUsersRequest, GetAllUsersResponse
from app.schemas.token import TokenUser


router = APIRouter()


class UseCase:
    repository: Repository
    group_repo: IGroupRepository

    def __init__(self):
        self.repository = Repository(group_repo=True)
        self.group_repo = self.repository.group_repo

    def execute(self) -> List[GetAllGroupsResponse]:
        return self.group_repo.get_all_groups()
    
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self) -> List[GetAllGroupsResponse]:
        try:
            return self.use_case.execute()
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/groups/all", response_model=List[GetAllGroupsResponse])
async def get_all_groups(
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    if token_user.permission not in [PermissionLevelEnum.PROFESSOR, PermissionLevelEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Acesso restrito a professores e administradores.")

    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle()