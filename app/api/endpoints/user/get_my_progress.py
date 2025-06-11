import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.classes_repository import IClassesRepository
from app.domain.interfaces.group_enrollment_repository import IGroupEnrollmentRepository
from app.domain.interfaces.group_repository import IGroupRepository
from app.domain.interfaces.topic_progress_repository import ITopicProgressRepository
from app.domain.interfaces.user_repository import IUserRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.exceptions.exceptions import NotFoundException, UnauthorizedException
from app.infra.repository import Repository
from app.schemas.get_my_progress import ClassProgressResponse, GetMyProgressRequest, GetMyProgressResponse
from app.schemas.token import TokenUser

router = APIRouter()


class UseCase:
    def __init__(self):
        self.repository = Repository(user_repo=True, group_enrollment_repo=True, group_repo=True,
                                     classes_repo=True, topic_progress_repo=True)
        self.user_repo = self.repository.user_repo
        self.group_enrrollment_repo = self.repository.group_enrollment_repo
        self.group_repo = self.repository.group_repo
        self.classes_repo = self.repository.classes_repo
        self.topic_progress_repo = self.repository.topic_progress_repo
        
    def execute(self, schema: GetMyProgressRequest, token_user: TokenUser) -> GetMyProgressResponse:
        user = self.user_repo.get_user_by_id(token_user.id)
        if not user:
            raise NotFoundException("Usuário não encontrado com os dados informados")
          
        if schema.group_id:
            group = self.group_repo.get_group_by_id(schema.group_id)
            if not group:
                raise NotFoundException("Grupo desconhecido.")
            
            is_student = self.group_enrrollment_repo.is_student(group_id=group.group_id, student_id=token_user.id)
            if not is_student:
                raise UnauthorizedException("Usuário não autorizado.")
        
        results = self.topic_progress_repo.get_progress_by_group_and_user(schema.group_id, user_id=token_user.id)

        class_progress_data = []
        for result in results:
            # Alteração aqui: usando o novo nome do alias "completed_topics"
            progresso = (result.completed_topics / result.total_topics) * 100 if result.total_topics > 0 else 0
            class_progress_data.append(
                ClassProgressResponse(
                    class_id=result.class_id,
                    title=result.title,
                    progresso=f"{int(progresso)}%" # Convertido para int para um visual mais limpo
                )
            )
            
        return GetMyProgressResponse(
            user_id=user.user_id,
            name=user.name,
            group_id=schema.group_id,
            classes=class_progress_data
        )

class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

    def handle(self, request: GetMyProgressRequest, token_user: TokenUser) -> GetMyProgressResponse:
        try:
            return self.use_case.execute(request, token_user)
        
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)
        except Exception as e:
           # ADICIONE ESTAS LINHAS PARA DEBUG
            print("----------------- ERRO CAPTURADO -----------------")
            print(f"Tipo da exceção: {type(e)}")
            print(f"Representação da exceção (repr): {repr(e)}")
            print("----------------------------------------------------")
            logging.exception(e) 
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-progress", response_model=GetMyProgressResponse)
async def get_user(
    group_id:str,
    token_user: TokenUser = Security(RequirePermission(PermissionLevelEnum.STUDENT))
):
    use_case = UseCase()
    controller = Controller(use_case=use_case)
    return controller.handle(GetMyProgressRequest(group_id=group_id), token_user)
