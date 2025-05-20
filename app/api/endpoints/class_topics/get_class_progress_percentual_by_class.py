from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_class_progress_percentual_by_class import GetClassProgressPercentualByClassRequest, GetClassProgressPercentualByClassResponse
from app.schemas.token import TokenUser
from fastapi import APIRouter, Security, HTTPException

router = APIRouter()

class UseCase:
    repository: Repository
    class_topics_repo: IClassesRepository


    def __init__(self):
        self.repository = Repository(class_topics_repo=True)
        self.class_topics_repo = self.repository.class_topics_repo

    def execute(self, schema: GetClassProgressPercentualByClassRequest, token_user: TokenUser) -> GetClassProgressPercentualByClassResponse:
        user_id = token_user.id
        progress_data = self.class_topics_repo.get_class_progress_percentual_by_class(class_id=schema.class_id, user_id=user_id, class_topics_id=schema.class_topics_id)
    
        return GetClassProgressPercentualByClassResponse(
            class_id=progress_data["class_id"],
            class_progress_percentual=progress_data["progress_percentual"],
            total=progress_data["total"],
            done=progress_data["done"],
        )


    
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetClassProgressPercentualByClassRequest, token_user: TokenUser) -> GetClassProgressPercentualByClassResponse:
        try:
            return self.use_case.execute(request, token_user)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            print("Erro interno:", str(e))
            raise HTTPException(status_code=500, detail=str(e))
        

@router.get("/class_progress", response_model=GetClassProgressPercentualByClassResponse)
async def get_class_progress_percentual_by_class(
    class_id: str,
    class_topics_id: str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.ADMIN | PermissionLevelEnum.PROFESSOR | PermissionLevelEnum.STUDENT))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(
        GetClassProgressPercentualByClassRequest(
            class_id=class_id,
            class_topics_id=class_topics_id
        ),
        token_user
    )
