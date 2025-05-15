import datetime
import uuid

from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.entities.user import User
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.utils.encrypt import Encrypt
from app.infra.repository import Repository
from app.models.models import Group
from app.schemas.create_group import CreateGroupRequest, CreateGroupResponse
from app.schemas.create_user import CreateUserRequest, CreateUserResponse
from app.helpers.exceptions.exceptions import DatabaseException, NotFoundException, UnauthorizedException, DuplicatedException
from app.schemas.get_group_by_id import GetGroupByIdRequest, GetGroupByIdResponse
from app.schemas.token import TokenUser

router = APIRouter()

class UseCase:
    repository: Repository
    group_repo: IGroupRepository
    
    def __init__(self):
        self.repository = Repository(group_repo=True)
        self.group_repo = self.repository.group_repo
        
    def execute(self, schema: GetGroupByIdRequest) -> GetGroupByIdResponse:
        group = self.group_repo.get_group_by_id(schema.group_id)
        if not group:
            raise NotFoundException("Grupo não encontrado.")
        return GetGroupByIdResponse(
            group_id=group.group_id,
            name=group.name,
            year_semester=group.year_semester,
            status=group.status,
            user_id=group.user_id
        )


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetGroupByIdRequest) -> GetGroupByIdResponse:
                                        
        try:
            return self.use_case.execute(request)
        except DatabaseException as e:
            raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
        except UnauthorizedException as e:
            raise HTTPException(status_code=401, detail=str(e))
        except DuplicatedException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@router.get("/group", response_model=GetGroupByIdResponse)
async def get_group_by_id(
    group_id: str,
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetGroupByIdRequest(group_id=group_id))
