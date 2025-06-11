import unittest
import datetime
from unittest.mock import patch, MagicMock, ANY

# Importe as classes do seu projeto que serão testadas ou usadas no teste
# O caminho exato pode precisar de ajuste dependendo da estrutura do seu projeto.
# Supondo que o UseCase está em 'app.api.endpoints.chat.create_chat_message'
from app.api.endpoints.chat.create_chat_message import UseCase, MESSAGE_SUMMARY_THRESHOLD
from app.schemas.create_chat_message import CreateChatMessageRequest, CreateChatMessageResponse
from app.domain.entities.chat_message import ChatMessage
from app.helpers.exceptions.exceptions import NotFoundException

# Definição de uma classe falsa para simular a sessão retornada pelo repositório
class FakeSession:
    def __init__(self, session_id, user_id, class_id, group_id):
        self.session_id = session_id
        self.user_id = user_id
        self.class_id = class_id
        self.group_id = group_id

class TestCreateChatMessageUseCase(unittest.TestCase):

    # O patch intercepta as chamadas para essas classes no módulo especificado
    # e as substitui por Mocks durante a execução dos testes.
    @patch('app.api.endpoints.chat.create_chat_message.Repository')
    @patch('app.api.endpoints.chat.create_chat_message.OpenAIService')
    @patch('app.api.endpoints.chat.create_chat_message.SQSResources')
    def setUp(self, mock_sqs_resources, mock_openai_service, mock_repository):
        """
        Configura o ambiente para cada teste.
        Este método é executado antes de cada método de teste.
        """
        # Criamos instâncias de MagicMock para simular os objetos reais
        self.mock_repo_instance = mock_repository.return_value
        self.mock_session_repo = MagicMock()
        self.mock_chat_repo = MagicMock()
        
        # Atribuímos os mocks de repositório ao mock principal
        self.mock_repo_instance.session_repo = self.mock_session_repo
        self.mock_repo_instance.chat_repo = self.mock_chat_repo

        self.mock_llm = mock_openai_service.return_value
        self.mock_sqs = mock_sqs_resources.return_value

        # Instanciamos a classe que queremos testar.
        # Seu __init__ agora usará nossos mocks em vez das classes reais.
        self.use_case = UseCase()

        # Dados falsos para usar nos testes
        self.session_id = "test-session-123"
        self.fake_session = FakeSession(
            session_id=self.session_id,
            user_id="test-user-456",
            class_id="test-class-789",
            group_id="test-group-000"
        )
        self.request_schema = CreateChatMessageRequest(message="Olá, mundo!")

    def test_execute_happy_path_no_summarization(self):
        """
        Testa o caso de sucesso onde a sumarização não é necessária.
        """
        # --- Configuração do Mock (Arrange) ---
        # Simula que a sessão existe
        self.mock_session_repo.get_session_by_id.return_value = self.fake_session
        
        # Simula um histórico com menos mensagens que o necessário para sumarizar
        mock_history = [ChatMessage(role="user", message="Msg 1", timestamp=datetime.datetime.now()) for _ in range(3)]
        self.mock_chat_repo.get_session_message_history.return_value = mock_history
        self.mock_chat_repo.get_summary.return_value = None
        self.mock_chat_repo.get_timestamp_from_last_summary.return_value = None
        
        # Simula a resposta da LLM
        llm_response = {"content": "Olá! Como posso ajudar?", "total_tokens": 25}
        self.mock_llm.generate_chat_response.return_value = llm_response

        # --- Execução (Act) ---
        response = self.use_case.execute(self.session_id, self.request_schema)

        # --- Verificações (Assert) ---
        # Verifica se a sessão foi buscada corretamente
        self.mock_session_repo.get_session_by_id.assert_called_once_with(self.session_id)
        
        # Verifica se a mensagem do usuário e a resposta da LLM foram salvas (2 chamadas)
        self.assertEqual(self.mock_chat_repo.save_message.call_count, 2)
        
        # Verifica se a LLM foi chamada
        self.mock_llm.generate_chat_response.assert_called_once()
        
        # Verifica se a SQS NÃO foi chamada
        self.mock_sqs.send_message.assert_not_called()
        
        # Verifica o conteúdo da resposta
        self.assertIsInstance(response, CreateChatMessageResponse)
        self.assertEqual(response.llm_response, "Olá! Como posso ajudar?")
        self.assertEqual(response.llm_tokens, 25)

    def test_execute_triggers_summarization(self):
        """
        Testa o caso onde o histórico atinge o limite e a sumarização é disparada.
        """
        # --- Arrange ---
        self.mock_session_repo.get_session_by_id.return_value = self.fake_session
        
        # Simula um histórico que excede o limite
        history_count = MESSAGE_SUMMARY_THRESHOLD + 1
        mock_history = [ChatMessage(role="user", message=f"Msg {i}", timestamp=datetime.datetime.now()) for i in range(history_count)]
        self.mock_chat_repo.get_session_message_history.return_value = mock_history
        self.mock_chat_repo.get_summary.return_value = None
        self.mock_chat_repo.get_timestamp_from_last_summary.return_value = None
        
        llm_response = {"content": "Continuando...", "total_tokens": 10}
        self.mock_llm.generate_chat_response.return_value = llm_response

        # --- Act ---
        self.use_case.execute(self.session_id, self.request_schema)

        # --- Assert ---
        # A verificação principal aqui é se a mensagem foi enviada para a SQS
        self.mock_sqs.send_message.assert_called_once()
        # Verificamos se o session_id correto foi passado para a SQS
        self.mock_sqs.send_message.assert_called_with(ANY) # ANY para não se preocupar com o objeto SQSMessage
        call_args, _ = self.mock_sqs.send_message.call_args
        self.assertEqual(call_args[0].session_id, self.session_id)

    def test_execute_with_existing_summary(self):
        """
        Testa se um resumo existente é corretamente adicionado ao contexto da LLM.
        """
        # --- Arrange ---
        self.mock_session_repo.get_session_by_id.return_value = self.fake_session
        self.mock_chat_repo.get_session_message_history.return_value = []
        
        summary_text = "O usuário perguntou sobre Python."
        self.mock_chat_repo.get_summary.return_value = summary_text
        self.mock_chat_repo.get_timestamp_from_last_summary.return_value = datetime.datetime.now().isoformat()
        
        llm_response = {"content": "Ok, entendi.", "total_tokens": 5}
        self.mock_llm.generate_chat_response.return_value = llm_response

        # --- Act ---
        self.use_case.execute(self.session_id, self.request_schema)

        # --- Assert ---
        self.mock_llm.generate_chat_response.assert_called_once()
        
        # Verifica se o contexto enviado para a LLM continha o resumo
        call_args, _ = self.mock_llm.generate_chat_response.call_args
        context_messages = call_args[0]['messages']
        
        self.assertEqual(context_messages[0]['role'], 'system')
        self.assertIn(summary_text, context_messages[0]['content'])

    def test_execute_session_not_found(self):
        """
        Testa o caso onde a sessão não é encontrada, esperando uma exceção.
        """
        # --- Arrange ---
        # Simula que a sessão não existe
        self.mock_session_repo.get_session_by_id.return_value = None

        # --- Act & Assert ---
        # Verifica se o código dentro do 'with' levanta a exceção esperada
        with self.assertRaises(NotFoundException) as context:
            self.use_case.execute(self.session_id, self.request_schema)
        
        self.assertEqual(str(context.exception), "Sessão não encontrada.")


# Isso permite que você execute o teste diretamente do terminal
if __name__ == '__main__':
    unittest.main()

