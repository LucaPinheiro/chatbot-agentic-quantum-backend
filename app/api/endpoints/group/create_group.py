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
from app.helpers.exceptions.exceptions import DatabaseException, UnauthorizedException, DuplicatedException
from app.schemas.token import TokenUser

router = APIRouter()

class UseCase:
    repository: Repository
    group_repo: IGroupRepository
    
    def __init__(self):
        self.repository = Repository(group_repo=True)
        self.group_repo = self.repository.group_repo
        
    def execute(self, schema: CreateGroupRequest) -> CreateGroupResponse:
        new_id = uuid.uuid4().hex

        group = Group(
            group_id=new_id,
            name=schema.name,
            year_semester=schema.year_semester,
            status=schema.status,
            manager_id=schema.manager_id,
        )

        self.group_repo.create_group(group, schema.user_ids)

        return CreateGroupResponse(
            group_id=new_id,
            name=schema.name,
            year_semester=schema.year_semester,
            status=schema.status,
            manager_id=schema.manager_id,
            user_ids=schema.user_ids
        )


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: CreateGroupRequest, user: TokenUser) -> CreateGroupResponse:
        if user.permission not in (PermissionLevelEnum.ADMIN, PermissionLevelEnum.PROFESSOR):
            raise UnauthorizedException("Somente administradores e professores podem criar grupos.")
                                        
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
        
        
@router.post("/group", response_model=CreateGroupResponse, status_code=201)
def create_group(
    request: CreateGroupRequest,
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.PROFESSOR))
):
    try:
        controller = Controller(UseCase())
        return controller.handle(request, user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na rota de criação de turma: {str(e)}")
