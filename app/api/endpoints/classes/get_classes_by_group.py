from typing import List
from fastapi import APIRouter, HTTPException, Security

from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_classes_by_group import GetClassesRequest, GetClassesResponse
from app.schemas.token import TokenUser


router = APIRouter()


class UseCase:
    repository: Repository
    classes_repo: IClassesRepository

    def __init__(self):
        self.repository = Repository(classes_repo=True)
        self.classes_repo = self.repository.classes_repo
    
    def execute(self, schema: GetClassesRequest) -> List[GetClassesResponse]:
        print(f"Buscando aulas para o grupo: {schema.group_id}")
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

    def handle(self, request: GetClassesRequest) -> List[GetClassesResponse]:
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/classes", response_model=List[GetClassesResponse])
async def get_classes_by_group(
    group_id: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetClassesRequest(group_id=group_id))

