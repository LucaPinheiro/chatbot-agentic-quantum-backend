from typing import List
from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_all_classes import GetAllClassesRequest, GetAllClassesResponse
from app.schemas.get_all_users import GetAllUsersRequest, GetAllUsersResponse
from app.schemas.token import TokenUser


router = APIRouter()


class UseCase:
    repository: Repository
    classes_repo: IClassesRepository

    def __init__(self):
        self.repository = Repository(classes_repo=True)
        self.classes_repo = self.repository.classes_repo

    def execute(self, schema: GetAllClassesRequest) -> List[GetAllClassesResponse]:
        classes = self.classes_repo.get_all_classes()
        return [
            GetAllClassesResponse(
                class_id=cls.class_id,
                group_id=cls.group_id,
                title=cls.title,
                pdf_url=cls.pdf_url,
                status=cls.status,
                last_access_class=cls.last_access_class,
                created_at=cls.created_at,
                order=cls.order
            )
            for cls in classes
        ]
    
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetAllClassesRequest) -> List[GetAllClassesResponse]:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/classes/all", response_model=List[GetAllClassesResponse])
async def get_all_classes(
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetAllClassesRequest())