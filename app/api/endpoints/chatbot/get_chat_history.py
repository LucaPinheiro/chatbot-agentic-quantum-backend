from fastapi import APIRouter, Security
from app.core.permissions import RequirePermission
from app.domain.interfaces.chat_repository import IChatRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.infra.repository import Repository
from app.schemas.get_chat_history import GetChatHistoryResponse, ChatMessageResponse
from app.domain.entities.chat_message import ChatMessage
from app.schemas.token import TokenUser

router = APIRouter()

class GetChatHistoryUseCase:
    repository: Repository
    chat_repo: IChatRepository
    
    def __init__(self):
        self.repo = Repository(chat_repo=True)
        self.chat_repo = self.repo.chat_repo

    def execute(self, session_id: str) -> GetChatHistoryResponse:
        messages: list[ChatMessage] = self.repo.chat_repo.get_session_message_history(session_id)
        response = GetChatHistoryResponse(
            session_id=session_id,
            messages=[
                ChatMessageResponse(
                    role=msg.role,
                    message=msg.message,
                    timestamp=msg.timestamp,
                    tokens=msg.tokens
                ) for msg in messages
            ]
        )
        return response
    

class GetChatHistoryController:
    def __init__(self):
        self.use_case = GetChatHistoryUseCase()

    def handle(self, session_id: str) -> GetChatHistoryResponse:
        return self.use_case.execute(session_id)
    

@router.get("/chat", response_model=GetChatHistoryResponse)
def get_chat_history(
    session_id: str,
    user: TokenUser = Security(RequirePermission(PermissionLevelEnum.STUDENT))
):
    controller = GetChatHistoryController()
    return controller.handle(session_id)


