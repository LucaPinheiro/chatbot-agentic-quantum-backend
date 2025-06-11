from typing import Optional
from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.session_repository import ISessionRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException
from app.infra.repository import Repository
from app.schemas.get_session import GetSessionRequest, GetSessionResponse
from app.schemas.token import TokenUser

router = APIRouter()


class UseCase:
    repository: Repository
    session_repo: ISessionRepository

    def __init__(self):
        self.repository = Repository(user_repo=True, session_repo=True)
        self.user_repo = self.repository.user_repo
        self.session_repo = self.repository.session_repo

    def execute(self, schema: GetSessionRequest, user: TokenUser) -> GetSessionResponse:
        # Se a consulta pelo class_id retornar uma sessão, então retorna
        session = None
        print('helo')
        if schema.class_id:
            print(schema.class_id)
            session = self.session_repo.get_session_by_class_id(schema.class_id, user.id)
        if not session:
            print("caiu aqui")
            raise NotFoundException("Sessão não encontrada com os dados informados")
            
        return GetSessionResponse(session_id=session.session_id)


class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetSessionRequest, user: TokenUser) -> GetSessionResponse:
        try:
            return self.use_case.execute(request, user=user)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/session", response_model=GetSessionResponse)
async def get_session(
  class_id: str,
  token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.STUDENT)) 
):
  use_case = UseCase()
  controller = Controller(use_case=use_case)
  request = GetSessionRequest(class_id=class_id)  
  return controller.handle(request, user=token_user) 