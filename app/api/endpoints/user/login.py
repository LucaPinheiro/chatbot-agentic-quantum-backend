from fastapi import APIRouter
from app.core.jwtoken import JWToken
from app.helpers.exceptions.exceptions import UnauthorizedException
from app.helpers.utils.encrypt import Encrypt
from app.infra.repository import Repository
from app.schemas.login import LoginRequest, LoginResponse

router = APIRouter()


class LoginUseCase:
    def __init__(self):
        self.repository = Repository(user_repo=True)
        self.user_repo = self.repository.user_repo

    def execute(self, email: str, password: str) -> LoginResponse:
        user = self.user_repo.get_user_by_email(email)
        if not user or not Encrypt.verify_password(password, user.password):
            raise UnauthorizedException("Usuário ou senha inválidos")

        token = JWToken.encode(user_id=user.id, permission=user.permission)
        return LoginResponse(token=token)

class LoginController:
    def __init__(self, use_case: LoginUseCase):
        self.use_case = use_case

    def handle(self, request: LoginRequest) -> LoginResponse:
        return self.use_case.execute(request.email, request.password)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    controller = LoginController(LoginUseCase())
    return controller.handle(request)