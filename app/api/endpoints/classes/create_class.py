from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.infra.repository import Repository
from app.schemas.create_class import CreateClassRequest, CreateClassResponse
from app.helpers.exceptions.exceptions import DatabaseException, UnauthorizedException, DuplicatedException
from app.schemas.token import TokenUser

router = APIRouter()

class UseCase:
    repository: Repository
    classes_repo: IClassesRepository
    user_repo: IUserRepository
    
    def __init__(self):
        self.repository = Repository(classes_repo=True, user_repo=True)
        self.classes_repo = self.repository.classes_repo
        self.user_repo = self.repository.user_repo
        
    def execute(self, schema: CreateClassRequest, user_id: str) -> CreateClassResponse:
        return self.classes_repo.create_class(
            group_id=schema.group_id,
            title=schema.title,
            pdf_url=schema.pdf_url,
            topics=schema.topics,
            user_id=user_id
        )



class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: CreateClassRequest, user: TokenUser) -> CreateClassResponse:
        if user.permission != PermissionLevelEnum.PROFESSOR:
            raise UnauthorizedException("Somente professores podem criar aulas.")
                                        
        try:
            return self.use_case.execute(request, user_id=user.id)  
        
        
        except DatabaseException as e:
            raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
        except UnauthorizedException as e:
            raise HTTPException(status_code=401, detail=str(e))
        except DuplicatedException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


@router.post("/class", response_model=CreateClassResponse, status_code=201)
def create_class(
    request: CreateClassRequest,
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.PROFESSOR))
):
    try:
        controller = Controller(UseCase())
        return controller.handle(request, user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na rota de criação de aula: {str(e)}")
