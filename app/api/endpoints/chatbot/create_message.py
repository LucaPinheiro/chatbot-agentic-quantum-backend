import datetime
import os

from fastapi import APIRouter, HTTPException, Security
from app.core.permissions import RequirePermission
from app.core.settings import load_settings
from app.domain.entities.chat_message import ChatMessage
from app.domain.interfaces.chat_repository import IChatRepository
from app.domain.interfaces.session_repository import ISessionRepository
from app.helpers.enums.enums import PermissionLevelEnum
from app.helpers.functions.openai_service import OpenAIService
from app.models.models import Session as SessionModel
from app.infra.repository import Repository
from app.helpers.exceptions.exceptions import NotFoundException
from app.schemas.create_chat_message import CreateChatMessageRequest, CreateChatMessageResponse
from app.schemas.token import TokenUser
from app.schemas.sqs import SQSMessage
from app.infra.external.aws import SQSResources

router = APIRouter()

MESSAGE_SUMMARY_THRESHOLD = 10 

settings = load_settings()


class UseCase:
    def __init__(self):
        self.repo = Repository(session_repo=True, user_repo=True, chat_repo=True)
        self.session_repo: ISessionRepository = self.repo.session_repo
        self.chat_repo: IChatRepository = self.repo.chat_repo
        self.sqs = SQSResources()
        self.llm = OpenAIService(api_key=settings.openai_api_key)

    def execute(self, session_id: str, schema: CreateChatMessageRequest) -> CreateChatMessageResponse:
        session = self.session_repo.get_session_by_id(session_id)
        if not session:
            raise NotFoundException("Sessão não encontrada.")

        # 1. Salva mensagem do usuário
        user_msg = ChatMessage(
            session_id=session_id,
            user_id=session.user_id,
            class_id=session.class_id,
            group_id=session.group_id,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            message=schema.message,
            tokens=schema.tokens,
            role=schema.role,
            type="message"
        )
        self.chat_repo.save_message(user_msg)
        print(f"📝 Mensagem do usuário salva com sucesso: \"{schema.message}\"")

        # 2. Histórico e resumo
        history = self.chat_repo.get_session_message_history(session_id)
        history_sorted = sorted(history, key=lambda m: m.timestamp)
        print(f"📜 Total de mensagens no histórico da sessão: {len(history_sorted)}")

        last_10 = history_sorted[-10:]
        context_messages = [{"role": m.role, "content": m.message} for m in last_10]

        summary_cutoff = self.chat_repo.get_timestamp_from_last_summary(session_id)
        summary_content = self.chat_repo.get_summary(session_id)
        print(f"🔍 Resumo anterior encontrado: {summary_content}")

        if summary_cutoff:
            print(f"🕒 Timestamp do último sumário: {summary_cutoff}")
            try:
                cutoff_dt = datetime.datetime.fromisoformat(summary_cutoff)
                messages_after_summary = [m for m in history_sorted if m.timestamp > cutoff_dt]
                print(f"📬 Mensagens após o último sumário: {len(messages_after_summary) + 1}")
            except ValueError:
                print("⚠️ Erro ao converter timestamp do sumário (formato inválido).")
        else:
            print("🔄 Nenhum sumário anterior encontrado.")

        if summary_content:
            context_messages.insert(0, {
                "role": "system",
                "content": f"Resumo da conversa até agora:\n{summary_content}"
            })

        # 3. Geração com OpenAI
        print("🤖 Enviando contexto para a LLM...")
        llm_result = self.llm.generate_chat_response(messages=context_messages)
        if not llm_result:
            raise RuntimeError("Falha ao gerar resposta da LLM.")

        system_reply = llm_result["content"]
        total_tokens = llm_result["total_tokens"]
        print(f"✅ Resposta da LLM gerada com sucesso ({total_tokens} tokens): \"{system_reply}\"")

        # 4. Salva resposta da LLM
        system_msg = ChatMessage(
            session_id=session_id,
            user_id=session.user_id,
            class_id=session.class_id,
            group_id=session.group_id,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            message=system_reply,
            tokens=total_tokens,
            role="system",
            type="message"
        )
        self.chat_repo.save_message(system_msg)
        print("💾 Resposta da LLM salva no banco de dados.")

        # 5. Checa necessidade de sumarizar
        if summary_cutoff:
            try:
                cutoff_dt = datetime.datetime.fromisoformat(summary_cutoff)
                filtered = [m for m in history_sorted if m.timestamp > cutoff_dt]
            except ValueError:
                filtered = history_sorted
        else:
            filtered = history_sorted

        if len(filtered) >= MESSAGE_SUMMARY_THRESHOLD:
            self.sqs.send_message(SQSMessage(
                session_id=session_id,
                summary_cutoff=summary_cutoff,
                message_group_id="summarization"
            ))
            print("📤 Mensagem enviada à fila SQS para sumarização.")

        # 6. Retorno
        return CreateChatMessageResponse(
            saved_at=datetime.datetime.now(datetime.timezone.utc),
            llm_response=system_reply,
            llm_tokens=total_tokens,
            llm_role="system"
        )



class Controller:
    def __init__(self, use_case: UseCase):
        self.use_case = use_case

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
    controller = Controller(UseCase())
    return controller.handle(session_id, request)
