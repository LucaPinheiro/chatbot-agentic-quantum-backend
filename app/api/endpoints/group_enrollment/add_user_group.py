from fastapi import APIRouter, Body, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.group_repository import IGroupRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.add_user_group import AddUserGroupRequest, AddUserGroupResponse
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    group_enrollment_repo: IGroupRepository

    def __init__(self):
        self.repository = Repository(group_enrollment_repo=True)
        self.group_enrollment_repo = self.repository.group_enrollment_repo

    def execute(self, schema: AddUserGroupRequest) -> AddUserGroupResponse:
        # supondo que add_user_group aceita lista de user_id e cria vários
        new_enrollments = self.group_enrollment_repo.add_user_group(users_id=schema.users_id, group_id=schema.group_id)
        added_user_ids = [enrollment.student_id for enrollment in new_enrollments]
        
        # Retornar no formato esperado do seu schema AddUserGroupResponse
        return AddUserGroupResponse(
            group_id=schema.group_id,
            user_id=added_user_ids
        )


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: AddUserGroupRequest) -> AddUserGroupResponse:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_user_group", response_model=AddUserGroupResponse)
async def add_user_group(
    request: AddUserGroupRequest = Body(...),
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.PROFESSOR))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request=request)