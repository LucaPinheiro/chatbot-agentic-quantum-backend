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


router = APIRouter()


class UseCase:
    repository: Repository
    classes_repo: IClassesRepository
    # group_repo: IGroupRepository

    def __init__(self):
        self.repository = Repository(classes_repo=True, group_repo=True)
        self.classes_repo = self.repository.classes_repo
        self.group_repo = self.repository.group_repo

    def execute(self, class_id: str,  schema: UpdateClassRequest) -> List[UpdateClassResponse]:
        if schema.group_id:
            group = self.group_repo.get_group_by_id(schema.group_id)
            if not group:
                raise NotFoundException("Grupo não encontrado.")
        class_updated = self.classes_repo.update_class(class_id=class_id, 
                                                       group_id=schema.group_id, 
                                                       title=schema.title, 
                                                       pdf_url=schema.pdf_url, 
                                                       status=schema.status, order=schema.order)
        return class_updated
    
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, class_id: str, request: UpdateClassRequest) -> UpdateClassResponse:
        try:
            return self.use_case.execute(class_id, request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.put("/classes/{class_id}/update", response_model=UpdateClassResponse)
async def update_class(
    class_id: str,
    body: UpdateClassRequest = Body(...),
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(class_id=class_id, request=body)
