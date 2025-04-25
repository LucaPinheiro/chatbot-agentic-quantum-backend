from fastapi import APIRouter, HTTPException
from app.core.jwtoken import JWToken
from app.helpers.exceptions.exceptions import UnauthorizedException, DatabaseException
from app.helpers.utils.encrypt import Encrypt
from app.infra.repository import Repository
from app.schemas.login import LoginRequest, LoginResponse

router = APIRouter()


class UseCase:
    def __init__(self):
        self.repository = Repository(user_repo=True)
        self.user_repo = self.repository.user_repo

    def execute(self, schema: LoginRequest) -> LoginResponse:
        user = self.user_repo.get_user_by_email(schema.email)
        if not user:
            raise UnauthorizedException("Usuário não encontrado")
        
        if not Encrypt.verify_password(schema.password, user.password):
            raise UnauthorizedException("Senha inválida")
        
        token = JWToken.encode(user_id=user.user_id, permission=user.permission)
        return LoginResponse(token=token)

class LoginController:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, schema: LoginRequest) -> LoginResponse:
        try:
            return self.use_case.execute(schema)
        except DatabaseException as e:
            raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
        except UnauthorizedException as e:
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    try:
        controller = LoginController(UseCase())
        return controller.handle(request)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na rota de login: {str(e)}")