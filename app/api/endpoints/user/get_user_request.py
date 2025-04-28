from typing import Optional
from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_user_request import GetUserRequest, GetUserResponse
from app.schemas.token import TokenUser

router = APIRouter()


class UseCase:
    repository: Repository
    user_repo: IUserRepository

    def __init__(self):
        self.repository = Repository(user_repo=True)
        self.user_repo = self.repository.user_repo

    def execute(self, schema: GetUserRequest) -> GetUserResponse:
        user = None
        if schema.email:
            user = self.user_repo.get_user_by_email(schema.email)
        elif schema.user_id:
            user = self.user_repo.get_user_by_id(schema.user_id)

        if not user:
            raise NotFoundException("Usuário não encontrado com os dados informados")

        return GetUserResponse(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            permission=user.permission
        )


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetUserRequest) -> GetUserResponse:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", response_model=GetUserResponse)
async def get_user(
    email: Optional[str] = None, 
    user_id: Optional[str] = None,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetUserRequest(email=email, user_id=user_id))
