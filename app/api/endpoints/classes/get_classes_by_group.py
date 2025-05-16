from typing import List
from fastapi import APIRouter, HTTPException, Security

from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_enrollment_repository import IGroupEnrollmentRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException, UnauthorizedException
from app.infra.repository import Repository
from app.schemas.get_classes_by_group import GetClassesRequest, GetClassesResponse
from app.schemas.token import TokenUser


router = APIRouter()


class UseCase:
    repository: Repository
    classes_repo: IClassesRepository
    group_repo: IGroupRepository
    group_enrollment_repo: IGroupEnrollmentRepository

    def __init__(self):
        self.repository = Repository(classes_repo=True, group_enrollment_repo=True)
        self.classes_repo = self.repository.classes_repo
        self.group_repo = self.repository.group_repo
        self.group_enrollment_repo = self.repository.group_enrollment_repo
    
    def execute(self, schema: GetClassesRequest, token_user: TokenUser) -> List[GetClassesResponse]:
        
        if (token_user.permission == PermissionLevelEnum.STUDENT):
            is_student = self.repository.group_enrollment_repo.is_student(
                group_id=schema.group_id,
                student_id=token_user.user_id
            )
            if is_student is False:
                raise UnauthorizedException("User is not authorized to access this group.")
            
        if (token_user.permission == PermissionLevelEnum.PROFESSOR):
            is_professor = self.repository.group_repo.is_manager_group(
                group_id=schema.group_id,
                manager_id=token_user.user_id
            )
            if is_professor is False:
                raise UnauthorizedException("User is not authorized to access this group.")
        
        classes = self.classes_repo.get_classes_by_group(group_id=schema.group_id)
        return [
            GetClassesResponse(
                class_id=c.class_id,
                group_id=c.group_id,
                title=c.title,
                pdf_url=c.pdf_url,
                status=c.status,
                last_access_class=c.last_access_class,
                created_at=c.created_at,
                order=c.order
            )
            for c in classes
        ]

class Controller:   
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetClassesRequest, token_user: TokenUser) -> List[GetClassesResponse]:
        try:
            return self.use_case.execute(request, token_user)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/classes", response_model=List[GetClassesResponse])
async def get_classes_by_group(
    group_id: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.STUDENT))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetClassesRequest(group_id=group_id), token_user)

