from typing import List, Optional
from langchain.agents import AgentExecutor, BaseSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.tools import BaseTool

class SupervisorAgent:
    """Agente supervisor que coordena outros agentes e ferramentas."""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        tools: Optional[List[BaseTool]] = None,
        agent: Optional[BaseSingleActionAgent] = None,
        memory: Optional[ConversationBufferMemory] = None,
        system_message: str = "Você é um agente supervisor inteligente que coordena outros agentes e ferramentas para resolver tarefas complexas.",
        verbose: bool = False
    ):
        self.llm = llm or ChatOpenAI(temperature=0)
        self.tools = tools or []
        self.memory = memory or ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Configuração do prompt do sistema
        self.system_message = SystemMessage(content=system_message)
        self.prompt = MessagesPlaceholder(variable_name="chat_history")
        
        # Configuração do executor
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=verbose,
            handle_parsing_errors=True
        )

    def add_tool(self, tool: BaseTool) -> None:
        """Adiciona uma nova ferramenta ao conjunto de ferramentas do agente."""
        self.tools.append(tool)
        
    def add_tools(self, tools: List[BaseTool]) -> None:
        """Adiciona múltiplas ferramentas ao conjunto de ferramentas do agente."""
        self.tools.extend(tools)

    async def execute(self, task: str) -> str:
        """
        Executa uma tarefa utilizando o agente e suas ferramentas.
        
        Args:
            task: A tarefa a ser executada
            
        Returns:
            Resultado da execução da tarefa
        """
        try:
            result = await self.agent_executor.arun(input=task)
            return result
        except Exception as e:
            return f"Erro ao executar tarefa: {str(e)}"

    def get_memory(self) -> List[dict]:
        """Retorna o histórico de conversas armazenado na memória."""
        return self.memory.chat_memory.messages

    def clear_memory(self) -> None:
        """Limpa o histórico de conversas da memória."""
        self.memory.clear()
