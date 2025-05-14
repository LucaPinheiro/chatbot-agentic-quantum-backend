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
from app.schemas.update_class import UpdateClassRequest, UpdateClassResponse


router = APIRouter()


class UseCase:
    repository: Repository
    classes_repo: IClassesRepository

    def __init__(self):
        self.repository = Repository(classes_repo=True)
        self.classes_repo = self.repository.classes_repo

    def execute(self, schema: UpdateClassRequest) -> List[UpdateClassResponse]:
        classes = self.classes_repo.update_class()
        return UpdateClassResponse(
                group_id=classes.group_id,
                title=classes.title,
                pdf_url=classes.pdf_url,
                status=classes.status,
                last_access_class=classes.last_access_class,
                created_at=classes.created_at,
                order=classes.order
            )
    
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: UpdateClassRequest) -> List[UpdateClassResponse]:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.put("/classes/update", response_model=List[UpdateClassResponse])
async def update_class(
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(UpdateClassRequest())