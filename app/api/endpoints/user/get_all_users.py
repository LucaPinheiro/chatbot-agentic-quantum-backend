from typing import List
from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.group_enrollment_repository import IGroupEnrollmentRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_all_users import GetAllUsersRequest, GetAllUsersResponse
from app.schemas.token import TokenUser


router = APIRouter()


class UseCase:
    repository: Repository
    user_repo: IUserRepository
    group_repo: IGroupRepository
    group_enrollment_repo: IGroupEnrollmentRepository

    def __init__(self):
        self.repository = Repository(user_repo=True, group_repo=True, group_enrollment_repo=True)
        self.user_repo = self.repository.user_repo
        self.group_repo = self.repository.group_repo
        self.group_enrollment_repo = self.repository.group_enrollment_repo

    def execute(self, schema: GetAllUsersRequest) -> List[GetAllUsersResponse]:
        users = self.user_repo.get_all_users()
        if not users:
            raise NotFoundException("No users found")

        response: List[GetAllUsersResponse] = []

        for user in users:
            group_id = None

            if user.permission == PermissionLevelEnum.PROFESSOR:
                group = self.group_repo.get_group_by_manager_id(user.user_id)
                group_id = group.group_id if group else None

            elif user.permission == PermissionLevelEnum.STUDENT:
                enrollment = self.group_enrollment_repo.get_enrollment_by_student_id(user.user_id)
                group_id = enrollment.group_id if enrollment else None

            # Admin → manter group_id como None

            response.append(GetAllUsersResponse(
                user_id=user.user_id,
                name=user.name,
                email=user.email,
                permission=user.permission,
                group_id=group_id
            ))

        return response
    
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetAllUsersRequest) -> List[GetAllUsersResponse]:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/users/all", response_model=List[GetAllUsersResponse])
async def get_all_users(
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetAllUsersRequest())