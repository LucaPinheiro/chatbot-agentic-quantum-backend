from typing import List
from fastapi import APIRouter, Body, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_all_classes import GetAllClassesRequest, GetAllClassesResponse
from app.schemas.get_all_users import GetAllUsersRequest, GetAllUsersResponse
from app.schemas.token import TokenUser
from app.schemas.update_class import UpdateClassRequest, UpdateClassResponse
from app.schemas.update_group import UpdateGroupRequest, UpdateGroupResponse


router = APIRouter()


class UseCase:
    repository: Repository
    group_repo: IGroupRepository

    def __init__(self):
        self.repository = Repository(group_repo=True, user_repo=True)
        self.group_repo = self.repository.group_repo
        self.user_repo = self.repository.user_repo


    def execute(self, group_id: str,  schema: UpdateGroupRequest) -> UpdateGroupResponse:
        if schema.user_id:
            user = self.user_repo.get_user_by_id(schema.user_id)
            if not user:
                raise NotFoundException(f"Usuário com id '{schema.user_id}' não encontrado.")
        group_updated = self.group_repo.update_group(group_id=group_id, 
                                                       name=schema.name, 
                                                       year_semester=schema.year_semester, 
                                                       status=schema.status, user_id=schema.user_id)
        return group_updated

class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, group_id: str, request: UpdateGroupRequest) -> UpdateGroupResponse:
        try:
            return self.use_case.execute(group_id, request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.put("/group/{group_id}/update", response_model=UpdateGroupResponse)
async def update_group(
    group_id: str,
    body: UpdateGroupRequest = Body(...),
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(group_id=group_id, request=body)
