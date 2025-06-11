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
from app.schemas.update_user import UpdateUserRequest, UpdateUserResponse
import bcrypt


router = APIRouter()

# ──────────────── UseCase ────────────────
class UseCase:
    user_repo: IUserRepository

    def __init__(self):
        self.user_repo = Repository(user_repo=True).user_repo

    def execute(self, user_id: str, schema: UpdateUserRequest) -> UpdateUserResponse:
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(f"Usuário com ID {user_id} não foi encontrado.")

        # Validar se o novo nome é igual ao atual
        if schema.name is not None and schema.name == user.name:
            raise HTTPException(status_code=400, detail="O nome informado é igual ao nome atual.")

        # Validar se o novo email é igual ao atual
        if schema.email is not None:
            if schema.email == user.email:
                raise HTTPException(status_code=400, detail="O email informado é igual ao email atual.")
            existing_user = self.user_repo.get_user_by_email(schema.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email já está em uso por outro usuário.")

        # Validar se a nova senha é igual à atual
        if schema.password is not None:
            senha_atual_hash = user.password.encode('utf-8')
            senha_nova = schema.password.encode('utf-8')
            if bcrypt.checkpw(senha_nova, senha_atual_hash):
                raise HTTPException(status_code=400, detail="A senha informada é igual à senha atual.")


        # Atualiza o usuário no repositório
        updated_user = self.user_repo.update_user(user_id=user_id, **schema.model_dump(exclude_unset=True))

        return UpdateUserResponse(
            user_id=updated_user.user_id,
            name=updated_user.name,
            email=updated_user.email,
        )

# ──────────────── Controller ────────────────
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, user_id: str, request: UpdateUserRequest) -> UpdateUserResponse:
        try:
            return self.use_case.execute(user_id=user_id, schema=request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# ──────────────── Rota ────────────────
@router.put("/user/{user_id}/update", response_model=UpdateUserResponse)
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    # Checagem extra manual
    if token_user.permission not in [PermissionLevelEnum.PROFESSOR, PermissionLevelEnum.ADMIN]:
        raise HTTPException(status_code=403, detail="Acesso restrito a professores e administradores.")

    if token_user.id != user_id:
        raise HTTPException(status_code=403, detail="Você só pode atualizar seus próprios dados.")

    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(user_id=user_id, request=body)
