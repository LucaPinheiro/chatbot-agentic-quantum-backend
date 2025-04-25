from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_user_by_email import GetUserByEmailRequest, GetUserByEmailResponse
from app.schemas.token import TokenUser

router = APIRouter()

class UseCase:
     repository: Repository
     user_repo: IUserRepository
     
     def __init__(self):
         self.repository = Repository(user_repo=True)
         self.user_repo = self.repository.user_repo
         
    
     def execute(self, schema: GetUserByEmailRequest) -> GetUserByEmailResponse:
        user = self.user_repo.get_user_by_email(schema.email)
        
        if not user:
            raise NotFoundException("Usuário não encontrado com o email informado")
        
        return GetUserByEmailResponse(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            permission=user.permission
        )


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case
        
    def handle(self, request: GetUserByEmailRequest) -> GetUserByEmailResponse:
        
        try:
            return self.use_case.execute(request)
        
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        

@router.get("/users", response_model=GetUserByEmailResponse)
async def get_user_by_email(email: str, token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.USER))):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetUserByEmailRequest(email=email))

        