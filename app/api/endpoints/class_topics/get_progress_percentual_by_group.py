from typing import Optional
from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException, UnauthorizedException
from app.infra.repository import Repository
from app.schemas.get_all_progress_class import GetAllProgressClassRequest, GetAllProgressClassResponse
from app.schemas.get_class_progress_percentual_by_class import GetClassProgressPercentualByClassRequest, GetClassProgressPercentualByClassResponse
from app.schemas.get_progress_percentual_by_group import GetProgressPercentualByGroupRequest, GetProgressPercentualByGroupResponse
from app.schemas.token import TokenUser
from fastapi import APIRouter, Query, Security, HTTPException

router = APIRouter()

# UseCase isolado
class UseCase:
    repository: Repository
    class_topics_repo: IClassesRepository

    def __init__(self, repository: Repository = None):
        # Permitir injeção de dependência para facilitar testes
        self.repository = repository or Repository(class_topics_repo=True)
        self.class_topics_repo = self.repository.class_topics_repo

    def execute(self, schema: GetProgressPercentualByGroupRequest) -> GetProgressPercentualByGroupResponse:
        progress_data = self.class_topics_repo.get_progress_percentual_by_group(
            name=schema.name
        )

        return GetProgressPercentualByGroupResponse(
            name=progress_data.name,
            group_progress_percentual=progress_data.group_progress_percentual,
            total=progress_data.total,
            done=progress_data.done
        )


# Controller isolado
class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(
        self, 
        request: GetProgressPercentualByGroupRequest, 
    ) -> GetProgressPercentualByGroupResponse:
        
        try:
            return self.use_case.execute(request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except UnauthorizedException as e:
            raise HTTPException(status_code=401, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress_group", response_model=GetProgressPercentualByGroupResponse)
async def get_progress_percentual_by_group(
    name: str,
    token_user: TokenUser = Security(RequirePermission(
        PermissionLevelEnum.ADMIN or PermissionLevelEnum.PROFESSOR or PermissionLevelEnum.STUDENT
    ))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(
        GetProgressPercentualByGroupRequest(
            name=name
        )
    )
