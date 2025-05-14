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
        class_updated = self.classes_repo.update_class(class_id=schema.class_id, 
                                                       group_id=schema.group_id, 
                                                       title=schema.title, 
                                                       pdf_url=schema.pdf_url, 
                                                       status=schema.status, order=schema.order)
        return UpdateClassResponse(
                group_id= class_updated.group_id,
                title= class_updated.title,
                pdf_url= class_updated.pdf_url,
                status= class_updated.status,
                last_access_class= class_updated.last_access_class,
                created_at= class_updated.created_at,
                order= class_updated.order
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
    class_id: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(UpdateClassRequest(class_id=class_id))