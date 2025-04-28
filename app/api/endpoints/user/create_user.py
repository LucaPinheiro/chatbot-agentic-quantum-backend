import datetime
import uuid

from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.utils.encrypt import Encrypt
from app.infra.repository import Repository
from app.schemas.create_user import CreateUserRequest, CreateUserResponse
from app.helpers.exceptions.exceptions import DatabaseException, UnauthorizedException, DuplicatedException
from app.schemas.token import TokenUser

router = APIRouter()

class UseCase:
    repository: Repository
    user_repo: IUserRepository
    
    def __init__(self):
        self.repository = Repository(user_repo=True)
        self.user_repo = self.repository.user_repo
        
    def execute(self, schema: CreateUserRequest) -> CreateUserResponse:
        
        verify_user_exists = self.user_repo.get_user_by_email(schema.email)
        if verify_user_exists:
            raise DuplicatedException("Usuário já existe")
        
        new_id = uuid.uuid4().hex
        hashed_pw = Encrypt.hash_password(schema.password)

        user = User(
            user_id=new_id,
            name=schema.name,
            email=schema.email,
            password=hashed_pw,
            created_at=datetime.datetime.now(),
            permission=schema.permission
        )

        user_created = self.user_repo.create_user(user)

        return CreateUserResponse(
            user_id=user_created.user_id,
            name=user_created.name,
            email=user_created.email,
        )


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: CreateUserRequest, user) -> CreateUserResponse:
        
        if user.permission == PermissionLevelEnum.PROFESSOR:
            
            if request.permission == PermissionLevelEnum.ADMIN:
                raise UnauthorizedException("Usuário não autorizado a criar um admin")
            if request.permission == PermissionLevelEnum.PROFESSOR:
                raise UnauthorizedException("Usuário não autorizado a criar um moderador")
            
        
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


@router.post("/users", response_model=CreateUserResponse, status_code=201)
def create_user(
    request: CreateUserRequest,
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN or PermissionLevelEnum.PROFESSOR))
):

    try:
        controller = Controller(UseCase())
        return controller.handle(request, user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na rota de criação de usuário: {str(e)}")
