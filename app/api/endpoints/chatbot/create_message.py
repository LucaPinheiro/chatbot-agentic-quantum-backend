import datetime

from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.domain.entities.chat_message import ChatMessage
from app.domain.interfaces.chat_repository import IChatRepository
from app.domain.interfaces.session_repository import ISessionRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.models.models import Session as SessionModel
from app.infra.repository import Repository
from app.helpers.exceptions.exceptions import NotFoundException
from app.schemas.create_chat_message import CreateChatMessageRequest, CreateChatMessageResponse
from app.schemas.token import TokenUser

router = APIRouter()

from app.schemas.sqs import SQSMessage
from app.infra.external.aws import SQSResources

MESSAGE_SUMMARY_THRESHOLD = 10  # Você pode mover para settings se quiser

class CreateChatMessageUseCase:
    Repository: Repository
    session_repo: ISessionRepository
    chat_repo: IChatRepository

    def __init__(self):
        self.repo = Repository(session_repo=True, user_repo=True, chat_repo=True)
        self.session_repo = self.repo.session_repo
        self.chat_repo = self.repo.chat_repo
        self.sqs = SQSResources()

    def execute(self, session_id: str, schema: CreateChatMessageRequest) -> CreateChatMessageResponse:
        session = self.session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Sessão não encontrada.")

        message = ChatMessage(
            session_id=session_id,
            user_id=session.user_id,
            class_id=session.class_id,
            group_id=session.group_id,
            timestamp=schema.timestamp,
            message=schema.message,
            tokens=schema.tokens,
            role=schema.role,
        )

        self.repo.chat_repo.save_message(message)

        # 🔎 Verifica se é hora de disparar sumarização
        history = self.repo.chat_repo.get_session_message_history(session_id)
        summary_cutoff = self.repo.chat_repo.get_summary(session_id)

        if summary_cutoff:
            filtered = [m for m in history if m.timestamp > datetime.datetime.fromisoformat(summary_cutoff)]
        else:
            filtered = history

        if len(filtered) >= MESSAGE_SUMMARY_THRESHOLD:
            message_to_send = SQSMessage(
                message_id=session_id,
                message_body="Resumo necessário",
                session_id=session_id,
                summary_cutoff=summary_cutoff  # pode ser None
            )
            self.sqs.send_message(message_to_send)

        return CreateChatMessageResponse(saved_at=datetime.datetime.now(datetime.timezone.utc))




class CreateChatMessageController:
    def __init__(self):
        self.use_case = CreateChatMessageUseCase()

    def handle(self, session_id: str, request: CreateChatMessageRequest) -> CreateChatMessageResponse:
        try:
            return self.use_case.execute(session_id, request)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
        
        
@router.post("/chat", response_model=CreateChatMessageResponse)
def create_chat_message(
    session_id: str,
    request: CreateChatMessageRequest,
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.STUDENT)),
):
    controller = CreateChatMessageController()
    return controller.handle(session_id, request)