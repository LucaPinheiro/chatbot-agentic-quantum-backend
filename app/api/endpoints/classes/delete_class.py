from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.delete_class import DeleteClassRequest, DeleteClassResponse
from app.schemas.delete_group import DeleteGroupRequest, DeleteGroupResponse
from app.schemas.token import TokenUser


router = APIRouter()

class UseCase:
    repository: Repository
    classes_repo: IClassesRepository

    def __init__(self):
        self.repository = Repository(classes_repo=True)
        self.classes_repo = self.repository.classes_repo

    def execute(self, schema: DeleteClassRequest) -> DeleteClassResponse:
        classes = self.classes_repo.delete_class(class_id=schema.class_id, title=schema.title)
        return classes
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
    
    def handle(self, request: DeleteClassRequest) -> DeleteClassResponse:
        
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_class", response_model=DeleteClassResponse)
async def delete_class(
    class_id: str,
    title: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(request=DeleteClassRequest(class_id=class_id, title=title))